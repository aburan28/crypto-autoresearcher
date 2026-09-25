# TASK-20260924-be2daf: red-team review of the attcount draft's difference from gapattr

- Task: TASK-20260924-be2daf (red-team, zero runs, static only). Card: `ledger/handoffs/TASK-20260924-be2daf.yaml`, sha256 recorded under section 3.
- Draft under review: AMD-EXP-GFPN-05ff43-20260924-attcount, `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml`, sha256 `4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48`, status draft, approved_by null, approval_decision null (lines 175-177).
- Object of the review: the difference RI-1..RI-6, RGL-8, RGL-9 from AMD-EXP-GFPN-05ff43-20260924-gapattr, and that difference's interaction with everything incorporated, on joints BJ-0..BJ-6.
- Recorded: 2026-09-25 (UTC). Review started 2026-09-24T23:34:43Z.
- Observations only. This report makes no approval recommendation. It states nothing about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT, and no finding here is evidence about them. Every constructed sequence is a construction from source text and rule text, not an observed event.

## 1. Verdicts at a glance

| joint | verdict | one-line basis |
|---|---|---|
| BJ-0 known-answer control | **holds** | the method flagged (a)-(e) as the card requires, at record level and package level; (f) listed 0 unattributed files in 683, 0 named gaps, with the launch sets reconstructed |
| BJ-1 counts, no fail-open | **breaks** | CX-A: a callgrind child that fails before it creates its stdout file (v2_solver.py 188 -> 206-208), with its launch record absent (carried lost-record premise), leaves no file and no count that RI-1 reads; PASS while definition (ii) holds under the literal reading. Not opened by the difference: the same object is PASS under failclosed and gapattr. RI-1 closes every msolve and health variant examined |
| BJ-2 counts, no planned-basis refusal | **holds** | every ordinary solver and health launch is counted exactly once; no ordinary path reuses a stdout path; 85 reconstructed (site, tag) rows and 8 site rows all satisfy RI-1 (a); N-1..N-13 and every RKR-4 (b) PASS / PASS_ZL row keep their verdicts |
| BJ-3 definitional scope and statements | **holds** | every cap-mismatch mixture FAILs by v2_check_run.py 68-70 in every version; no dependant is admitted on it under r4 (RL-4). RI-5 (a)'s "before any dependant reads it" is accurate for r4 only (OB-4) |
| BJ-4 development harness | **holds**, with fail-closed findings | (19)-(27) are derivable; (25) separates gapattr from attcount at gap level; its "PASS" is unattainable if the scratch evaluator applies the V-7 integrity item to an in-place alteration (FC-1); RI-4's list is incomplete as a list but covered by its general clause, and its strict "path prefix" wording STOPs on values RI-4 itself names (FC-2) |
| BJ-5 reads, reach and readers | **holds** | RFR-4 confirmed in this report's own words (section 9); RLR-2 / RKR-2 stand (no change since dd1034553); no reader of the RI-1 inputs computes differently |
| BJ-6 value classes and neutrality | **holds** | RI-1 reads files after the driver exits; one class each; the label-only classes are read by no verdict function |

Counterexamples: CX-A (fail-open, BJ-1; reachable only under the carried lost-record premise and documented open(2) failure; verdict dependence stated in section 11). Planned-basis refusals: none on any path of the repository's code. Fail-closed findings: FC-1..FC-7 (section 12).

## 2. Method

One rule evaluator, written in scratch outside the repository, applied UNCHANGED to every object of BJ-0..BJ-4. It imports only the Python standard library (collections, itertools, json, os, re, sys), reads no module of the scanned trees and no third-party module, and computes from rule text as transcribed in its source (reproduced verbatim in the appendix).

- Rule sets: RK (readbackclose RK-1 / RK-3 as worded), RF (failclosed as worded), RG (childend as worded), RH (gapattr as worded), RI (attcount as worded: RH-1 with RI-1 (a)-(d)), RIw (attcount with RI-1 (a) weakened to "N >= 1", for CRI-4 (e) only), RIx (attcount with RI-1 (a) and (d) disabled, for RI-3 (25) only).
- Definitions evaluated per object: (i) a pair the parent read (v2_solver.py 227 executed) is in no launch record; (ii-LR) a created or possibly created child that is not in class (A) or (C) (a child with NO launch record counts as "not class (A) or (C)"; this is the reading the archived review TASK-20260924-94cc33 used) has no launch-record pair equal to the cap; (ii-ANY) the same with a pair found in no source at all; (iii) a created child recorded child_created false; (iv) read LITERALLY: a record written in another process goes undetected by any rule; (v) the outcome is wrapper-recorded.
- Two frozen-checker variants per package: Mr (the pair set the manifest collects as r3 collects it) and Mc (the cap compared as requested); k = number of collected pairs in the known-answer objects. Package verdicts: PASS, PASS_ZL, FAIL. A package is flagged FAIL-OPEN when its verdict is PASS or PASS_ZL and at least one definition holds; PLANNED-BASIS REFUSAL when a planned basis outcome is FAIL by design.
- Versions (CRI-4): `rteval_v1.py` (the rule functions and the BJ-0 objects; edited once BEFORE its first run, to add the weak-mode COUNT GAP for N = 0; no output existed before that edit) and `rteval_v2.py` = version 1 with one `exec` of `rteval_v2_objects.py` (the BJ-1..BJ-4 objects) appended before the final write. Every rule function is unchanged between versions; the complete diff is:

```text
2c2
< """TASK-20260924-be2daf rule evaluator, version 1 (scratch; zero runs). ONE method, used UNCHANGED for BJ-0..BJ-3.
---
> """TASK-20260924-be2daf rule evaluator, version 2 (scratch; zero runs). = version 1 with objects APPENDED after the BJ-0 section; every rule function unchanged. ONE method, used UNCHANGED for BJ-0..BJ-3.
6c6
< the repository and no third-party module. Writes rteval_v1.json next to itself; prints its report on stdout.
---
> the repository and no third-party module. Writes rteval_v2.json next to itself; prints its report on stdout.
1021c1021,1022
< with open(os.path.join(SCR, "rteval_v1.json"), "w") as fh:
---
> exec(compile(open(os.path.join(SCR, 'rteval_v2_objects.py')).read(), 'rteval_v2_objects.py', 'exec'))
> with open(os.path.join(SCR, "rteval_v2.json"), "w") as fh:
1023c1024
< P("\nWROTE rteval_v1.json with %d keys" % len(OUT))
---
> P("\nWROTE rteval_v2.json with %d keys" % len(OUT))
```

  The executed file `rteval_v2_objects.py` is this review's own scratch file, not a module of any scanned tree or third-party package. Every output of every version is kept under its own name (`rteval_v1.out`, `rteval_v1.json`, `rteval_v2.out`, `rteval_v2.json`); nothing was overwritten.
- Supporting scans: `pkgread.py` (O_NOATIME listing and read-only reads of solver-events.json, raw-result.json, command.txt and child/*.spec.json of the four archived r3 gate packages; lstat before and after: 77 checked, 0 changed), `scan.py` (ast / dis of the three implementation trees, under an audit hook refusing imports of scanned modules and every process launch: 0 refused of either), `scan2.py` (ast scan for process-ending, exec, spawn and hook calls; its third-party part was deliberately given no directory, section 14), `rdscan.py` (every recorded value carrying the run directory in the four packages; O_NOATIME; 602 lstat checked, 0 changed), `tables.py` (copies the listing and count tables out of `rteval_v2.json`), `selfcheck.py` (the name self-check), `appendix.py` (writes the appendix).
- Launch sets of the archived r3 packages are RECONSTRUCTED (CRI-9) by the rule stated with the tables; every listing or count check is a reading of r3 artifacts under r4 rule text, never a result about any package's verdict and never evidence about D.

## 3. CRI-2 integrity (first, before any joint; repeated at report time)

All checks passed at 2026-09-24T23:35Z (before any joint), at 2026-09-25T00:12:56Z, and the receipt comparison (c) again at report assembly (every recorded path_sha256 EQUAL). No failure; the review was not stopped. The card `ledger/handoffs/TASK-20260924-be2daf.yaml` hashes to faaaa3c5f0b9ed13efa9295e9f8646991f0ebb9ba5482d7f1036fcb26074b848; `agents/red-team.md` to c66633c45ccacb2779bbcb291227703d8f0c0d8ee79fa5669d22bc214e7ff8ee; `AGENTS.md` to 16b87c767e698a15f988ad8d6f03b07b2c0e5ac7e2738846d0084c2473288a56. HEAD ec77282a897db7b97c502a96ce46e48fefde9a85 throughout.

| item | path | expected | observed | result |
|---|---|---|---|---|
| (a) attcount draft | experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml | 4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48 (the TASK-20260924-2a7c7f receipt's addendum_sha256, as given by the dispatching session; the receipt was not opened) | 4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48; status draft (175), approved_by null (176), approval_decision null (177) | PASS |
| (b) gapattr | amendments/v2_addendum_gapattr.yaml | 919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7 | same | PASS |
| (b) childend | amendments/v2_addendum_childend.yaml | e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b | same | PASS |
| (b) failclosed | amendments/v2_addendum_failclosed.yaml | 1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c | same | PASS |
| (b) readbackclose | amendments/v2_addendum_readbackclose.yaml | f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c | same | PASS |
| (b) readbackfull | amendments/v2_addendum_readbackfull.yaml | 0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1 | same | PASS |
| (b) readbackcover | amendments/v2_addendum_readbackcover.yaml | dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e | same | PASS |
| (c) f5631b yaml | coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml | b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f (TASK-20260924-0c2fdc receipt path_sha256) | same | PASS |
| (c) f5631b md | .../TASK-20260924-f5631b/review-report.md | 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8 | same | PASS |
| (c) 1ecb7d yaml | .../TASK-20260924-1ecb7d/review-report.yaml | 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4 (TASK-20260924-7e8a5d) | same | PASS |
| (c) 1ecb7d md | .../TASK-20260924-1ecb7d/review-report.md | 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055 | same | PASS |
| (c) 94cc33 yaml | .../TASK-20260924-94cc33/review-report.yaml | 0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7 (TASK-20260924-93f3ca) | same | PASS |
| (c) 94cc33 md | .../TASK-20260924-94cc33/review-report.md | 02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21 | same | PASS |
| (c) census (TASK-20260924-71d070) | dev-evidence/readbackclose-census/readbackclose-census.json | 9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa | equal | PASS |
| (c) census (71d070) | dev-evidence/readbackclose-census/readbackclose-census.md | ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838 | equal | PASS |
| (c) census (71d070) | dev-evidence/readbackclose-census/rk_check.py | 00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c | equal | PASS |
| (c) census (TASK-20260924-ddfb69) | dev-evidence/readbackfull-census/readbackfull-census.json | 36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158 | equal | PASS |
| (c) census (ddfb69) | dev-evidence/readbackfull-census/readbackfull-census.md | 5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7 | equal | PASS |
| (c) census (ddfb69) | dev-evidence/readbackfull-census/rf_check.py | ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558 | equal | PASS |
| (c) census (TASK-20260924-a01341) | dev-evidence/readback-census/readback-census.json | 49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4 | equal | PASS |
| (c) census (a01341) | dev-evidence/readback-census/readback-census.md | 2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3 | equal | PASS |
| (c) census (a01341) | dev-evidence/readback-census/rb_check.py | 3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64 | equal | PASS |
| (d) diff | `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json' <the four run directories>` | prints nothing | printed nothing, exit 0; `git cat-file -t` of dd1034... is commit; it is an ancestor of HEAD ec77282a897db7b97c502a96ce46e48fefde9a85 | PASS |

The six snapshot receipts (TASK-20260924-0c2fdc, -7e8a5d, -93f3ca, -71d070, -ddfb69, -a01341) were read for their `path_sha256` field only, by a program that printed nothing else. Card: `ledger/handoffs/TASK-20260924-be2daf.yaml`. The three released frozen files hash to: `k4a_anchor_system.py` 3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b, `square_analogue_n3.json` 22550c2f4ede32a41d7b8134f2c72c04121d20065eacd6604640b0ef0e8a81ba, `square_analogue_n4.json` e3bc6d120a52a898fd84e47efe54f727f20e2013c906522cd41a73303ae595a2. DP-5 observed: 54 run directories under runs/; no implementation-v2-r4*, trial-plan-v2-r4.json or trial-plan-v2-a1-r4.json; the write-scope directory did not exist before this report was written. `git status` of experiments/EXP-GFPN-05ff43 printed nothing at start and at report time.

## 4. BJ-0 known-answer control: HOLDS

Method applied unchanged, in the order (a)-(f). Record level first, then package level.

**(a) readbackclose RK-1 / RK-3 as worded (RK).**
- KA-a1, P-16 (fork at v2_solver.py 181 created the child; the raise lands before STORE_FAST pid, as `dis` of line 181 shows: LOAD_GLOBAL os, LOAD_ATTR fork, PRECALL, CALL, STORE_FAST pid): record level RK child_created **False** for a created child (definition (iii)). Package level: k = 1, Mc: **PASS, FAIL-OPEN** (ii-ANY), (ii-LR), (iii), (v). Contrast RF: child_created `undetermined`; FAIL in every variant.
- KA-a2, P-F2 after P-14a (raise at 214, then SolverLock.release raises in run_child's finally, so the final traceback lacks _run_child_locked): record level RK child_created **False** for a created child ((iii)). Package level: k = 1, Mc: **PASS, FAIL-OPEN** (ii-ANY), (ii-LR), (iii), (v). Contrast RF: child_created true, no class; FAIL.
- KA-a3, W-1 (driver exits before any launch; the wrapper writes raw-result.json): package level RK **PASS_ZL, FAIL-OPEN (v)** in both variants. Contrast RF: FAIL.

**(b) failclosed as worded (RF), FO-1 in both variants, foreign-file write failed or interrupted, escaped exit 1 or -2.**
- Variant C (the escaped child's launch record class (C)): record level RF class C, "(iv)-relevant record in another process; detected by: NOTHING". Package level: k = 1: **PASS, FAIL-OPEN (iv)** in all four sub-cases (failed/interrupted x exit 1/-2); k = 0: FAIL (item 66-67). Contrast RG, RH, RI: record child_end `undetermined`; FAIL in every variant (k = 0 is an infrastructure stop, RG-2).
- Variant B (class (B)): record level RF class B, detected by NOTHING. Package level: k = 0 and k = 1: **PASS, FAIL-OPEN (iv)** in all four sub-cases. Contrast RG, RH, RI: child_end `undetermined`; FAIL.

**(c) childend as worded (RG), PB-3 (a cells m = 5 package with one SE-3 re-solve of S5_t1).** Package level RG: **FAIL, PLANNED-BASIS REFUSAL** (basis X-08 m = 4 _condition_met, v2_driver.py 1110-1127; X-09 / X-10 aggregates), gaps `solver/S5_t1.ms.err.ssf-attempt1`, `.ms.log.ssf-attempt1`, `.ms.out.ssf-attempt1`. Contrast RF, RH, RI: PASS.

**(d) gapattr as worded (RH), CX-1 objects of review TASK-20260924-94cc33.** LR-1 (S-1, 2 attempts, final record absent), LR-2 (attempt 1's record absent), LR-3 (3 attempts, attempt 2's record absent), LR-5 (S-2 HR-3 re-solve in controls_a1, final record absent): package level **PASS, FAIL-OPEN (i), (ii-LR)** in both variants. LR-4 (3 attempts, attempts 2 and 3 absent): **FAIL**, gaps the three `.ssf-attempt2` files.

**(e) attcount with RI-1 (a) weakened to "N >= 1" (RIw) and as worded (RI).** RIw: LR-1, LR-2, LR-3, LR-5 **PASS, FAIL-OPEN (i), (ii-LR)**; LR-4 FAIL (gaps). RI as worded: each of LR-1..LR-5 **FAIL** with a named **COUNT GAP** and a **SITE COUNT GAP**, e.g. LR-1: "COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2" and "SITE COUNT GAP (S-1): 2 launch records vs counters attempts_total 3". Every single removal among 2, 3 and 6 attempts (11 objects): RH PASS (i), (ii-LR); RIw PASS (i), (ii-LR); RI FAIL with 2 named gaps each.

**(f) Listing check under attcount (launch sets reconstructed, CRI-9).** RUN-GFPN-f6a21a: 284 files in the five directories, 88 reconstructed launch records (callgrind 36, child job 16, msolve 36), 0 named gaps, **0 unattributed**. RUN-GFPN-902222: 284, 88, 0, **0**. RUN-GFPN-f5412a: 32, 7 (child job 1, comparator 1, msolve 5), 0, **0**. RUN-GFPN-bfe956: 83, 19 (child job 11, msolve 8), 0, **0**. Total 683 files, 0 unattributed (review TASK-20260924-94cc33 reported 0 of 683 under gapattr; gapattr as worded gives the same here). Every file is listed with its first applying clause in the listing tables.

Verdict: the method flagged every object the card names in the required way, at record and package level. BJ-1 and BJ-2 are therefore reported on their merits.

## 5. BJ-1 counts, no fail-open: BREAKS

Reading: failclosed RFR-1 (definitions (i)-(v); (iv) literally) applied to RI-1 and RI-2 with RH-1, RG-1, RF-0..RF-3, RL-1, RL-2, RL-3 and RB-1.

**(1) Lost-record constructions against each count RI-1 (a) reads** (objects LN-*, LE-*; all FAIL under RI unless noted):

| object | construction | RH (gapattr) | RI (attcount) |
|---|---|---|---|
| LN-1 | non-event S-1 tag, launch record absent | FAIL (file gaps) | FAIL: COUNT GAP (i) N=0 != RB-1 1; SITE COUNT GAP |
| LN-2 | launch record and its RB-1 attempt record absent | FAIL (gaps) | FAIL: SITE COUNT GAP; file gaps |
| LN-3 | launch record, RB-1 record and one attempts_total increment absent (consistent, RGL-9) | FAIL (gaps) | FAIL (file gaps; no named gap) |
| LN-4 | gb_only pass-through anchor_comparator_system, launch record absent | FAIL (gaps) | FAIL: COUNT GAP (i) N=0 != RL-2 1; SITE COUNT GAP |
| LN-4b | the same with its RL-2 record and passthrough increment absent (consistent) | FAIL (gaps) | FAIL (gaps) |
| LN-5 | S-2 non-event health tag d222, launch record absent | FAIL (gaps) | FAIL: COUNT GAP; SITE COUNT GAP (S-2) |
| LE-1 | event tag, attempt 2's launch record and RB-1 record absent | **PASS, FAIL-OPEN (i), (ii-LR)** | FAIL: COUNT GAP (ii) N=1 attempts=2 accepted=2; SITE COUNT GAP |
| LE-2 | event tag, attempt 1's launch record and renamed_files['attempt1'] absent | FAIL (renamed-file gaps) | FAIL: COUNT GAP (i) and (ii); SITE COUNT GAP |
| LE-3 | event tag, final attempt lost consistently (record, RB-1 k=2, attempts entry, accepted_attempt -> 1, renamed key, attempts_total - 1) | FAIL (renamed-file gaps) | FAIL (renamed-file gaps) |
| LN-6 | non-event S-1 launch refused before fork (class A), record, RB-1 and attempts_total consistently absent | PASS, no definition | PASS, no definition (no child) |
| LN-7a | non-event S-1 msolve child that fails before creating its stdout file ("P-7" shape), input not retained, launch record absent | **PASS, FAIL-OPEN (ii-ANY), (ii-LR)** | FAIL: COUNT GAP; SITE COUNT GAP |
| LN-7b | LN-7a with its RB-1 record and attempts_total increment also absent (RGL-9's declared premise) | PASS, FAIL-OPEN (ii) | **PASS, FAIL-OPEN (ii-ANY), (ii-LR)** |

Whether every count must be lost with the record: yes. To pass RI-1 at a non-event tag, the launch record, its RB-1 attempt record (or RL-2 record) and the site counter increment must all be absent; at an event tag additionally the event's attempts entry, accepted_attempt and a renamed_files key. Even then, any file the launch left is a gap (LN-3, LE-3), so the undetected class under the whole rule set is a consistent loss of a launch that left NO file (LN-6: no child, no definition; LN-7b: a child created and ended before line 188 completed). Whether any count is derived from the launch records: in the r3 base, none is. The attempt records, event fields and counters are written by the SE-3 / HR-3 wrapper around the frozen solve / run_system from the result the frozen function returned (r3_resolve.py 253, 263-273, 276-279, 310, 313, 383), a different code path from any run_child recorder; RB-1 and RL-2 require "copied from the result the frozen function RETURNED ... and from nothing else" (readbackcover 199-203; readbackfull 256-265). All of them go through one single event writer that rewrites the file atomically (readbackfull RL-1 (c), 223-227; r3_resolve.py `_write`), so they are independent in code path, not in writer. One note: at an event tag the event's attempts list IS the list of attempt records (r3_resolve.py 270, 277), so RI-1 (a) (i) and the attempts clause of (a) (ii) read one list twice; accepted_attempt (313), the renamed_files keys (310) and the counters (273) are separate writes (OB-10).

**(2) Launch kinds outside solver/ and health/ .ms.log.** LC-1 (a callgrind child that exec'd normally, its record absent): FAIL, gaps `.callgrind.stdout`, `.callgrind.stderr` (no other record names them). LCJ-1 (a child job whose child failed before creating its stdout file, record absent): FAIL, the driver-written `child/<tag>.spec.json` (v2_driver.py 98-99) is a gap. CX-A-cmp (the comparator child failing before its stdout file, record absent): FAIL by frozen item 66-67 (anchor-identity is a gate package; PASS_ZL never applies). **CX-A** (a callgrind child failing before its stdout file, record absent): **PASS, FAIL-OPEN (ii-ANY), (ii-LR)** under RF, RH and RI alike; full sequence in section 11. Variants: CX-A-G2 (the same in a fixture package of G2 shape) PASS, FAIL-OPEN (ii); CX-A-gp (the gp child of controls_a1, same shape) receives the package label PASS with (ii) holding, but its own run_status is "failed" with gate_pass false (a1_driver.py 208), so X-02 (r3_run_wrapper.py 190-196) and X-13 (a1_check_run.py 79-84) refuse every dependant: no admission. Whether RI-1 (b) covers stderr and argv paths: it names stdout_path only. In the frozen launch set every launch's stderr_path is paired one-to-one with its stdout_path by the call site (v2_driver.py 101, 166, 650; v2_solver.py 517; a1_health.py 145; a1_pari.py 95), so a duplicated stdout path and a duplicated stderr path coincide; argv paths ARE shared between records of different stdout paths: the callgrind child's argv names `<dir>/<tag>.ms` (v2_solver.py 516 + v2_driver.py 209) exactly as the msolve record's argv does, and RI-1 (d) keeps that attribution (attcount 317-319). That sharing cannot hide a lost record: the .ms file is also the msolve launch's own input, and the msolve record's loss is caught by the count, not by the .ms file. The frozen code also starts uncapped children outside run_child: callgrind_annotate (v2_solver.py 533), `gp --version-short` (a1_pari.py 121) and the shell helper v2_common.sh (55-59, used by host_record and the msolve version read, 129-136). They are not capped children, write no file in the five directories (their output is captured by a pipe) and are outside the definitions.

**(3) RI-1 (d).** With (a) holding, (d) removes attributions of the final files from every record but the last of L(<dir>, <tag>) and attributes nothing new ((e)). No construction examined (LR-1..LR-5, LE-1..LE-3, N-5, N-5b, N-5c) found a file attributed by (d) to a record of another launch. A tag solved twice (TW-1..TW-3) needs code the repository lacks (BJ-2 (1)): TW-1 (every record present) FAILs by a DUPLICATE-PATH GAP on `<tag>.callgrind.stdout`; TW-3 (the first msolve record absent) FAILs by COUNT GAP; TW-2 (the first of two callgrind records absent) PASSes with (i), (ii-LR) under RH and RI: RI-1's WHY sentence ("(b) covers a tag solved twice", attcount 344-345) covers duplication, not loss (OB-2). TW-2 is a residual premise (code the repository lacks), not a counterexample of the repository's paths.

**(4) Definition (iv), literally, for the records RI-1 newly reads.** RI-1 reads the RB-1 attempt records, RL-2 pass-through records, SE-3 / HR-3 events and site counters. Each is written by the installing process's resolve layer in the installing process, after the frozen function returned (the frozen parent reaps the child before returning: v2_solver.py 223, 230, 243-271). A process other than the installing one could write them only by running the resolve layer's code in an escaped child; such a child's launch is `undetermined` under RG-1 (c) and FAILs the package (childend 315-329). No new (iv) route found.

**(5) Residuals.** X1, X6b, X10: `scan2.py` finds, in the three trees, os._exit only at v2_solver.py 196 (97), 201 (98), 208 (99); exec only at 204-205; SystemExit raised only with string arguments or in development / plan scripts; no signal.signal, atexit.register or os.register_at_fork call; no supplying code. The optional third-party source text was NOT read (section 14), so the RGL-6 residual stays exactly as the draft states it. IV-1 / RGL-8: the comparator script `k4a_anchor_system.py` (released, read as text) writes into its output directory only four `.ms` files and `k4a_results.json` (lines 56-57, 279-281, 318) and starts no subprocess in its own text; the Sage runtime it runs under was not read, so a writer under comparator/ from that runtime stays unshown either way.

**(6) Classification.** CX-A: fail-open (a break), found under BJ-1 (2); LN-7b: fail-open under RGL-9's own declared premise (consistent loss of three independent entries plus a no-file launch); both are the same physical shape: a child that ended before v2_solver.py 188 completed and so could not have executed argv (section 11). All other objects of (1)-(3): fail-closed or no definition.

**What would change the verdict.** If the approval act reads definition (ii) as presupposing that the child HAS a launch record (an absent record then is "not a child that may have executed argv"), CX-A and LN-7b meet no definition and BJ-1 holds. If a count of callgrind and gp launches independent of the launch records were bound (section 11, cheapest mutation), CX-A becomes a named gap and FAIL.

## 6. BJ-2 counts, no planned-basis refusal: HOLDS

Reading: failclosed RFR-2 applied to RI-1 and RI-3.

**(1) From the frozen code.** v2_driver.solve is called at 358, 565, 693, 711, 786, 787, 841 and 1174-1175 (`scan.py`: 8 `solve` call sites in v2_driver.py, and one `D.solve` in a1_driver.py resolved through the module attribute at call time); each call launches exactly one msolve child through run_child (166) and at most one callgrind child (207-209, outcome "ok" and callgrind_timeout set). Tags: cells `"%s_t%d" % (arm, i)` (1157), grids `"grid_" + tag` (1161), fixture / f4 / anchor / controls tags carry the target index or label; the trial plans have no duplicate cell arms and no duplicate builds per package (parsed at cmdlog 38). a1_health.run tags are `health_p<p>_d<degs>` with the suffixes `_reinvoke`, `_seed2`, `_seed2_reinvoke` (a1_health.py 233, 237, 241, 244), each distinct; run is called once per controls_a1 package (a1_driver.py 129, at the function level of cmd_controls_a1). a1_pari.curve_facts launches one gp child per tag (96). No ordinary path of either plan launches two children with one stdout_path in one package outside an SE-3 / HR-3 event. Counting: every attempt at S-1 and S-2 increments attempts_total (r3_resolve.py 273), including a refused_to_start attempt (the frozen solve and run_system both return a result after run_child returns a refusal record: v2_driver.py 184-186; a1_health.py 147-220); every gb_only call increments passthrough_calls_gb_only_true (383) and gets an RL-2 record; there is no health solve outside HR-3 in the a1 entry; the consistency-violation path raises (r3_resolve.py 283-294) and the package fails as implementation_error, which is not a planned basis outcome. An exception inside the frozen solve after run_child returned (none is caught in v2_driver.py; the only try blocks are 143, 172, 210) propagates out of the driver: the package fails anyway.

**(2) Count check on the four archived r3 gate packages** (reconstructed, CRI-9; full per-tag table after section 16):

| package | (site, tag) rows | (i) holds | S-1 launch records vs attempts_total + passthrough | S-2 | events | callgrind reconstructed vs r3 S-3 records | mismatches |
|---|---|---|---|---|---|---|---|
| RUN-GFPN-f6a21a | 36 | 36 | 36 = 36 + 0 | 0 = 0 | 0 | 36 = 36, per tag equal | none |
| RUN-GFPN-902222 | 36 | 36 | 36 = 36 + 0 | 0 = 0 | 0 | 36 = 36, per tag equal | none |
| RUN-GFPN-f5412a | 5 | 5 | 5 = 0 + 5 | 0 = 0 | 0 | 0 = 0 | none |
| RUN-GFPN-bfe956 | 8 | 8 | 8 = 8 + 0 | 0 = 0 | 0 | 0 = 0 | none |

No SE-3 or HR-3 event exists in any of the four, so (a) (ii) has no event tag to evaluate there; (b): no other stdout path is carried by two reconstructed records. RB-1 / RL-2 per-tag counts are reconstructed independently of the listing, from the raw-result.json solver argv of the tag (-P 1: one attempt record; -g 1: one pass-through record) or, where raw-result.json carries no solver argv (controls), from the frozen call site's gb_only argument.

**(3) N-1..N-13 and RKR-4 (b).** Under RI: N-1..N-12 PASS (including N-5 re-solve with 2 attempts, N-5b with 6 attempts still SSF after the last, N-5c a re-solve on the callgrind target, N-6 / N-6b controls_a1 with an HR-3 re-solve and a `_seed2` retry, N-7 / N-8 failing and timed-out callgrind children, N-11 / N-11b refusal paths); N-13 (Z-C5) PASS_ZL. Every PASS or PASS_ZL row of readbackclose-census.md 476-492 (rows 478, 480, 481, 482, 483, 485, 485b, 486, 488, 489) keeps its verdict under RI. Z-C5 is PASS_ZL in both run_status variants because RK-3 (b) reads no run_status (census row 491).

**(4) msolve flags.** Every msolve argv comes from one function, v2_solver.msolve_argv (331-334): `-v 2 -t 1 -f IN -o OUT` plus `-P 1`, or `-g 1` when gb_only. Cells, health (a1_health.py 144) and controls use `-P 1`, as the fixture gate packages recorded (raw-result.json argv of f6a21a / 902222); anchor-identity uses `-g 1` as G3 recorded. The flags therefore equal the gate invocations'. Review 94cc33 B-9's residual (msolve writing further input-dependent auxiliary files at shapes the gate never ran) stays an untested transfer assumption: it would appear as a gap, i.e. fail-closed.

**What would change the verdict.** A frozen path that solves one tag twice in one package outside an event (TW-1 shows it would FAIL by a DUPLICATE-PATH GAP); an S-1 / S-2 attempt the counters do not count.

## 7. BJ-3 definitional scope and statements: HOLDS

Reading: failclosed RFR-2 applied to RH-2 with RI-5 (a); RI-5 (b), (c) as wording.

- Every cap-mismatch object FAILs by the frozen item v2_check_run.py 68-70 under RF, RH and RI: cells m = 5 every launch P-8 / every launch P-9 / one P-9 mixed with a measured launch; the same at m = 4; a build package mixing a P-9 build child with a built child; a controls gate package with one P-9 build child. RF reports each as a PLANNED-BASIS REFUSAL; RH and RI class each as a cap-mismatch stop (RH-2), which is the definitional exclusion RH-2 introduced. In both shapes the child's own check at v2_solver.py 200-201 (soft or hard differs from the cap) ends it with status 98 before the go-byte wait (202) and exec (204-205); for P-8 (soft differs) the parent also refuses at 228-232. Neither releases a workload.
- Whether a frozen dependant reads a mixture's measured data as a basis before 68-70 stops it: under r4, RL-4 (readbackfull 286-306) admits every reading package only on the checker's exit 0 at admission time, so no dependant is admitted on it. Under v2 and r3, R-8 admits on a manifest's existence alone (readbackfull RLF-5, 192-198; r3_run_wrapper.py 199-203), so an m = 4 cells package or an aggregate could have read the mixture's data there. RI-5 (a)'s "in every protocol version of the lineage it FAILs by the frozen item ... before any dependant reads it" is accurate for the FAIL in every version and for "before any dependant reads it" under r4 only (OB-4). Inside one package, the conditional `measured_in_this_package:<arm>` (v2_driver.py 1115-1118) reads the package's own measured cell before any checker runs; that package FAILs as a whole and is no other package's basis.
- "As DEC-20260924-61b22c applied it to PB-4": not verifiable here (the decision is withheld from this reviewer); the reading is taken as the draft states it.
- RI-5 (b) changes the expected DV-11 VC-3 inventory (it now lists the RI-1 counts, class epsilon), not a package rule (OB-6). RI-5 (c) changes no rule: it states the scope of RH-4's mark; its H4-d statement relies on the recalled interpreter behaviour that an exception escaping an after-fork callback is reported and not propagated (section 14).
- No other planned basis outcome that FAILs by design was found.

## 8. BJ-4 development harness: HOLDS (with fail-closed findings)

Reading: failclosed RFR-3 applied to RI-3 and RI-4 with RH-3 and RG-3.

**(1) RI-3 (19)-(27) derived** on development objects altered IN PLACE after the driver exits, each evaluated twice: with the V-7 integrity item (the whole-file sha256 of solver-events.json against the manifest's recorded sha256; r3_check_run.py 153-158; recorded at r3_run_wrapper.py 395 after the driver exits; valueclose VC-1 (e) 316-335) and without it (a scratch evaluator of the gap computation only).

| check | object | RI gaps / named | with V-7 | without V-7 | expected by the draft |
|---|---|---|---|---|---|
| (19) | unaltered, SE-3 re-solve at S-1 | none | PASS | PASS | renamed attempt-1 files attributed |
| (19) | renamed_files['attempt1'] removed | gaps + COUNT GAP (ii) | FAIL | FAIL | gap and FAIL |
| (19) | one launch record of the tag removed | gaps + COUNT GAP + SITE COUNT GAP | FAIL | FAIL | COUNT GAP and FAIL (RI-3) |
| (20) | unaltered HR-3 re-solve at S-2 | none | PASS | PASS | attributed |
| (20) | one S-2 launch record removed | COUNT GAP + SITE COUNT GAP | FAIL | FAIL | COUNT GAP and FAIL |
| (22) | uncached build child job record removed | .spec.json, .stdout, .stderr, .npz, .meta.json | FAIL | FAIL | five gaps |
| (22) | raw_grid child job record removed | .spec.json, .stdout, .stderr, .meta.json | FAIL | FAIL | four gaps |
| (24) | LR-1, LR-2, LR-3, LR-5 (and LR-4) under RI | COUNT GAP + SITE COUNT GAP each | FAIL | FAIL | COUNT GAP and FAIL |
| (25) | the same under RIx (RI-1 (a), (d) disabled) | LR-1, -2, -3, -5: no gap; LR-4: gaps | **FAIL** | PASS (LR-4 FAIL) | "no gap and PASS" on LR-1, -2, -3, -5 |
| (26) | unaltered N-5 and N-6 shapes | none | PASS | PASS | no recorder gap |
| (27) | RB-1 record removed at a non-event tag | COUNT GAP (i) | FAIL | FAIL | named gap and FAIL |
| (27) | a launch record duplicated | COUNT GAP + SITE COUNT GAP | FAIL | FAIL | named gap and FAIL |
| (27) | a site counter decremented | SITE COUNT GAP | FAIL | FAIL | named gap and FAIL |
| (27) | a child-job launch record duplicated | DUPLICATE-PATH GAP | FAIL | FAIL | named gap and FAIL |

Record level and package level agree in every row. (25) separates gapattr from attcount at the GAP level on LR-1, LR-2, LR-3 and LR-5 (RIx: no gap; RI: COUNT GAP). Its "PASS" is unattainable if the scratch evaluator applies V-7 to an in-place alteration, because every in-place alteration of solver-events.json after the wrapper recorded its hash fails V-7 (FC-1). The IN PLACE rule (attcount 400-405) removes the FC-3 DV-18 face (no absolute-root move). (26)'s stand-in solve level: a stand-in that replaced solve itself would bypass the SE-3 wrapper and yield no RB-1 record (a COUNT GAP on the positive control); RF-6 words stand-ins as callees and primitives resolved at call time, which reads as a stand-in beneath solve (FC-6).

**(2) RI-4 against every recorded value carrying the run directory** (`rdscan.py`; archived packages, O_NOATIME):
- anchor-identity RUN-GFPN-f5412a: raw-result.json `/build/child/argv[]` (prefix), `/build/npz` (prefix), `/comparator/child/argv[]` (prefix), `/targets[]/solver/argv[]` (8, prefix); `child/anchor_S4.spec.json` `out` (prefix); `command.txt` line 2 (embedded, `# GFPN_RUN_DIR=<rd>`, r3_run_wrapper.py 469-471).
- controls RUN-GFPN-bfe956: 11 `child/*.spec.json` `out` (prefix); `command.txt` line 2 (embedded). Its raw-result.json carries NO value with the run directory: cmd_controls discards the build info (v2_driver.py 768, 816) and records checks without argv (792-795, 924).
- fixture packages (not development kinds, for completeness): raw builds' child argv and npz, 72 solver argv, spec outs, and line 4 of every `solver/*.callgrind.stderr` (valgrind's own command line, embedded).
- controls-a1 (no archived package; from code): a1_pari.py 97 `script` (prefix) and `command` (embedded in a space-joined string); a1_health.py 148 `input.path` (prefix) and 149 `command` (embedded); the r3 S-2 attempt record copies `command` (r3_resolve.py 198; embedded). The S-2 event head records `out_dir` relative (r3_resolve.py 404).

Comparison with RI-4's list: covered by the particular list: raw build npz, _slim argv, comparator child argv, a1_pari `script`, a1_health `input.path`, and (RH-3 (a)) spec `out`. Not in the particular list but covered by its general clause ("every recorded value that carries the development run directory as a path prefix"): the r4 launch records' stdout_path / stderr_path (RG-4 (a)). Not in the list and NOT a path prefix: `command.txt` line 2, the S-2 attempt record's `command`, and the two `command` fields RI-4 itself names. Over-included: "the controls builds" `raw["build"]["npz"]`, which the controls raw-result does not carry. Under a strict reading of "as a path prefix" (the value starts with the run directory), RI-4's own named `command` fields are "a recorded value carrying the development run directory other than as a path prefix" and STOP (FC-2); under a token reading (a prefix of a path token inside the value) they pass. No frozen read of a substituted value or of the label that changes a computed value was found (the substitution is an output-comparison device).

**(3) RG-3 (a)-(d) with RH-3 (b)** re-checked: the ladder read at r3_run_wrapper.py 464 and recorded at 546; phase-A commits read at 437-443; RH-3 (b)'s withdrawal of "as r3_dv12.py 119 does" is consistent with r3_check_run.py 255-256 testing presence only; RG-3 (d)'s three expected items are exactly r3_check_run.py 329-330, 331-332 and 333-334. No change.

**What would change the verdict.** A frozen read of a substituted value that alters a seed, stream, target, argv, cap, watchdog or thread count; a (19)-(27) expectation that the full rule set cannot produce on any evaluator reading.

## 9. BJ-5 reads, reach and readers: HOLDS

**RFR-4 confirmation, in this report's own words.** X-13 is the a1 frozen checker's cross-package read (a1_check_run.py 79-84): when the package's plan entry has controls_a1_gate_required, it takes the run id at `plan["gate"]["addendum_blocking_package"]` of the plan AC.PLAN_A1_PATH names (set to trial-plan-v2-a1-r3.json by r3_check_run.py 65 in the r3 checker process; the id there is RUN-GFPN-2c4862), opens `<EXP_DIR>/runs/<id>/raw-result.json`, and fails unless its `run_status` is "completed_valid" and its `gate_pass` is True. X-02 is the r3 wrapper's admission read (r3_run_wrapper.py 190-196, called at 288-289 when the plan is the a1-r3 plan and the package has controls_a1_gate_required): it takes the same plan field, reads `RUNS/<id>/raw-result.json` through `_raw` (97-104), and refuses unless the same two fields have the same two values. The roots coincide (r3_common.py 31 `RUNS_DIR = os.path.join(EXP_DIR, "runs")`; r3_run_wrapper.py 68 `RUNS = R.RUNS_DIR`; v2_common.py 30 `EXP_DIR`), so both read one file and the same two fields with the same predicate. A missing file fails both (X-13 reads `{}`; X-02 refuses "has not run"); an unparseable file fails both (X-13's json.load raises, so the checker exits non-zero; X-02 refuses on "unparseable"). The values X-13 reads are the fields X-02 reads.

The carried RLR-2 / RKR-2 findings stand: `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- <implementation trees, trial plans, four run directories>` printed nothing at start and at report time; `scan.py` finds one definition of run_child (v2_solver.py 149) and of _run_child_locked (177), every caller reaching it as `V.run_child` at call time (v2_driver.py 101, 166, 650; a1_health.py 147; a1_pari.py 96) or the module global at v2_solver.py 517, no `from v2_solver import`, no default-argument capture; the only module-level references are r3_resolve.py 393 and 412 (attribute stores on the wrappers themselves).

**RFR-6 readers (informational).** RI-1 named gaps -> the RL-3 recorder-gap list -> RF-3 (a) (PASS refused), RF-3 (b) (stop record), RL-4 (admission via the checker verdict), DV-18, DV-11. RB-1 attempt records -> RB-2 (c) collector, RB-3 enumeration, RI-1. RL-2 records -> RL-3 (e), RI-1. SE-3 / HR-3 events -> RH-1 (vi), RI-1, r3_run_wrapper.py watchdog_after_resolve (354-368) and _site_block (371-378), REG-1's SE-4 (e) test. Site counters -> the wrapper's manifest copy (374), r3_check_run.py's epsilon comparison of SITE_COUNT_KEYS only (47, 178-183; attempts_total and passthrough_calls_gb_only_true are not among them). raw_result_writer, the recorder-foreign file and `undetermined`: unchanged by the difference. tools/ and harness/: no reader (a grep for the record names over both directories printed nothing). None of these readers computes differently because of RI-1: RI-1 only reads, and only adds FAIL conditions.

## 10. BJ-6 value classes and neutrality: HOLDS

RI-1 reads the launch records, RB-1 / RL-2 records, events and counters read-only after the driver has exited (RI-1 (f), attcount 323-329); it changes no argv, env, limit, value or order of any frozen step, and it writes nothing the frozen parent or the resolve layer reads. RI-1 (f) assigns class epsilon (SE-2 (5) recording), exactly one class; RI-5 (b) lists the RI-1 counts (epsilon), the RH-4 mark (gamma), and the RH-2 and RG-2 labels as classification labels with no value class. The labels are read only by the RF-3 (b) stop record and the planned-basis scope; no verdict function (RF-3 (a), RK-3 (b), the frozen checkers) reads them.

## 11. Counterexamples

### CX-A: a lost callgrind launch record that leaves no file (FAIL-OPEN, definition (ii); found under BJ-1 (2))

Sequence (cells m = 4 package; the same holds for any package whose solve runs callgrind):
1. v2_driver.py 1174-1175: the cells loop calls `solve(... callgrind_timeout=cg_timeout if i == 0 ...)` for target 0; it resolves to the SE-3 wrapper (r3_resolve.py 373-390; r4 counterpart), which calls the frozen solve.
2. v2_driver.py 166: msolve launch L1 through run_child; the child execs; outcome ok; the pair is read at v2_solver.py 227; L1's launch record is written (class B, child_end exec).
3. v2_driver.py 207-209: outcome "ok" and callgrind_timeout set, so `V.callgrind_instructions(...)` runs; v2_solver.py 517: `run_child(vargv, <sd>/<tag>.callgrind.stdout, <sd>/<tag>.callgrind.stderr, ...)` through the recorder.
4. v2_solver.py 181: fork; the child is created.
5. v2_solver.py 188: in the child, `os.open(stdout_path, O_WRONLY|O_CREAT|O_TRUNC)` fails (documented open(2) errors that create no file: ENOSPC or EDQUOT when a new inode cannot be allocated, ENFILE, EMFILE, EIO, EROFS). 206-207: the exception is caught; 208: `os._exit(99)`. No file is created; the child never reaches setrlimit (193), the OK report (198), the go-byte wait (202) or exec (204-205).
6. v2_solver.py 212-225: the parent reads EOF, report "" (220), not "OK" (221), reaps the child (223) and returns `refused_to_start` with returncode 99. Under RG-1 (c) this is ("", 99): child_end "frozen_pre_exec_exit", class (C).
7. PREMISE: this launch record (L2) is absent, without RL-1 (d) firing (the lost-record premise that attcount's carried decision (4), lines 565-570, puts inside RFR-1's search).
8. v2_solver.py 519-524: callgrind_instructions records the child fields (outcome refused_to_start, returncode 99, rlimit None) in raw-result.json and returns; solve returns; the package completes with raw_result_writer "driver", run_status completed_valid.
9. The r3 / r4 resolve layer's S-3 record for the callgrind child (r3_resolve.py 323-369) records it, files "absent"; it is RECORDED ONLY (VA-6 (c); r3_check_run.py 164) and RI-1 does not read it (WHY, attcount 340-345).
10. RH-1: no file of L2 exists, so no recorder gap. RI-1 (a) counts only `<dir>/<tag>.ms.log` launches at S-1 / S-2: N = 1 = RB-1 1; site counters equal; no named gap. RI-1 (b): no duplicate. RF-3 (a): every present record is class A, B or C; no gap; no recorder-foreign file; no `undetermined`. The frozen checker collects L1's pair (the raw callgrind child's rlimit None is skipped at r3_run_wrapper.py 510), so items 66-67 and 68-70 pass. Verdict **PASS**.
11. Definitions: the callgrind child was created; it has no launch record, so it is "not class (A) or (C)", hence "a child that may have executed argv", and it has no recorded pair: definition **(ii)** holds (ii-LR and ii-ANY). (i) does not hold (line 227 did not execute for it); (iii), (iv), (v) do not hold.

Reachability: only under the named lost-record premise, together with documented operating-system behaviour (an open(2) failure in the child). Not through ordinary operation.

Physical content: the child could not have executed argv. The frozen child opens its stdout file at 188 before any exec (204-205); no stdout file means the child never passed 188, and no frozen code removes `.callgrind.stdout` (callgrind_instructions removes only `<tag>.callgrind.out` at 549; solve removes only `<tag>.cg.ms.out` at 211). CX-A is therefore a fail-open under the definitions' wording, not a cap exposure.

Verdict dependence: it rests on reading definition (ii) with an absent launch record as "not class (A) or (C)" (the reading this review and review 94cc33 applied to every lost-record object). If (ii) presupposes an existing record, no definition holds and CX-A is not a counterexample.

Relation to the difference: not opened by it. The same object is PASS with (ii) under failclosed (RF) and gapattr (RH). RI-1 closes the msolve and health analogue (LN-7a: RH PASS, RI COUNT GAP and FAIL) but not the callgrind or gp launch, because RI-1 binds counts to `.ms.log` launches only and its WHY sentence states that "the callgrind launch needs no count of its own" (attcount 340-345). That sentence is true of duplication and false of loss (OB-2).

Variants: CX-A-G2 (fixture package of G2 shape) PASS with (ii). On G1 the same object would likely differ from the REG-1 reference in the CG-3-compared child fields (r3_resolve.py 48-51); not derived here. CX-A-gp (controls_a1 gp child) receives the label PASS with (ii) holding, but the package's run_status is "failed" with gate_pass false, so X-02 and X-13 admit no dependant. CX-A-cmp (comparator) FAILs by item 66-67 (fail-closed). LCJ-1 (child job) FAILs by the spec-file gap (fail-closed). LN-7b (msolve child of the same shape with its counts consistently lost) is the same physical shape under RGL-9's own premise.

Cheapest mutation: bind, per tag, the number of launch records with stdout_path `<dir>/<tag>.callgrind.stdout` to a count written independently of the launch recorder, for example the presence of `instructions_callgrind` in the frozen solve result (v2_driver.py 209, key presence, RB-1-style, read from the returned result) or the S-3 records of the resolve layer (r3_resolve.py 355-363, 365). The S-3 route needs VA-6 (c) (S-3 recorded only) and RL-5's V-3 disposition checked, since the S-3 records would become a gap input. For gp: its launch count follows from the controls_a1 raw record written by the frozen code (a1_pari.py 97-99 `child`). Alternatively, remove `pari/<tag>.gp` from the non-launch list: the gp argv names it exactly (a1_pari.py 94), so RH-1 (ii) attributes it to the gp record and a lost gp record leaves the script as a gap (OB-8).

Cheapest discriminating control: a development package whose callgrind child fails its stdout open (a stand-in os.open, resolved at call time in the child, raising for names ending ".callgrind.stdout"), then its launch record removed in place: attcount as worded should report no gap and PASS; the mutation should report a named gap and FAIL.

### Residual premise objects (not counterexamples of the repository's paths)

- TW-2: a tag solved twice with callgrind both times, the first callgrind record lost: PASS with (i), (ii-LR) under RH and RI. Needs code the repository lacks (no frozen path solves one tag twice in one package).
- LN-7b: RGL-9's declared premise (consistent loss of the launch record, its RB-1 record and the counter increment) on a no-file msolve child: PASS with (ii). The draft declares this limit (attcount 497-505).

### Planned-basis refusals

None on any path of the repository's code. TW-1 would be one (DUPLICATE-PATH GAP on a planned basis outcome) only with code the repository lacks.

## 12. Fail-closed findings (never a bar; each with its cost)

- **FC-1 RI-3 (25) "PASS" versus V-7.** Every object of (19)-(27) is altered in place after the driver exits (attcount 400-405); the manifest's solver_events sha256 is recorded after the driver exits (r3_run_wrapper.py 395) and compared by V-7 (r3_check_run.py 153-158; valueclose VC-1 (e)). An evaluator that applies V-7 yields FAIL on (25)'s LR-1, -2, -3, -5, where (25) expects PASS, and "if they do not ... it is a STOP". Cost: a DV-18 STOP at (25) and a Coordinator decision, unless the scratch evaluator is read as the gap computation without V-7. The same tension exists for the carried failclosed RF-6 (i) (11) and (12) ("yields PASS") if their copies are made by in-place alteration; not opened by the difference.
- **FC-2 RI-4 strict reading.** RI-4 names a1_pari.py 97 `command` and a1_health.py 149 `command`, whose run directory sits inside a space-joined command string, not as the value's prefix; with "as a path prefix" read as "the value starts with", RI-4's own last sentence makes them a STOP; the S-2 attempt record's `command` copy (r3_resolve.py 198) and command.txt line 2 do the same. Cost: a DV-18 STOP on the controls-a1 development package.
- **FC-3 absolute roots in RI-1.** RI-1 compares recorded absolute stdout paths; evaluating a package at another absolute root leaves L(<dir>, <tag>) empty for every tag, so every tag with a count is a COUNT GAP and the package FAILs. The IN PLACE rule removes the DV-18 face; any other re-evaluation of a package at another root (a moved checkout) refuses it. Cost: re-evaluation must run at the recorded root.
- **FC-4 comparator no-file launch lost.** CX-A-cmp FAILs by item 66-67 (anchor-identity never PASS_ZL). Cost: a FAIL on a package whose only launch failed anyway.
- **FC-5 consistent losses with files.** LN-3, LN-4b, LE-3 FAIL by file gaps although RI-1 is silent. Cost: none beyond the FAIL (these are lost-record packages).
- **FC-6 stand-in level in (24) / (26).** A stand-in that replaced solve itself would bypass the SE-3 wrapper and produce no RB-1 record: (26)'s positive control would show COUNT GAPs. The draft's "a stand-in solve returning the SSF signature" does not say at which level. Cost: a DV-18 STOP until the level is fixed as a callee beneath the wrapper.
- **FC-7 hypothetical duplicate path.** TW-1 (a tag solved twice, every record present) FAILs by a DUPLICATE-PATH GAP. No frozen path exists; cost only if such code is added.

## 13. Observations

- **OB-1 RGL-9's undetected class is narrower than stated.** RGL-9 says a consistent loss "is not detected by RI-1"; under the whole rule set such a loss still FAILs whenever the launch left a file (LN-3, LE-3). The only undetected consistent losses are no-file launches (LN-6 without a definition; LN-7b with (ii)).
- **OB-2 RI-1's WHY sentence on callgrind.** "The callgrind launch needs no count of its own ... and (b) covers a tag solved twice" (attcount 340-345): (b) covers duplication (TW-1 FAIL) but not a lost record, either of two callgrind launches of a tag solved twice (TW-2) or of a single no-file callgrind launch (CX-A).
- **OB-3 V-7 already detects a post-manifest alteration.** RGL-7 and RGL-9 say an alteration after the launch is visible "after the fact" through RL-3's listing hashes; the carried V-7 item (r3_check_run.py 153-158) already FAILs a package whose solver-events.json changed after the manifest recorded its hash. An alteration between the launch and the manifest write remains undetected by V-7.
- **OB-4 RI-5 (a)'s temporal clause** holds under r4 (RL-4), not under v2 / r3 (R-8 existence admission).
- **OB-5 RI-4's list** is incomplete as a list (launch-record stdout / stderr paths, the S-2 attempt record `command`, command.txt line 2) and over-inclusive (controls raw build npz, which does not exist); its general clause covers the prefix values.
- **OB-6 RI-5 (b)** changes DV-11's expected inventory (adds the RI-1 counts, epsilon); "no rule changes" holds for package verdicts.
- **OB-7 RGL-8 / option HI.** The comparator script's own text writes exactly four `.ms` files and `k4a_results.json` into its directory (k4a_anchor_system.py 56-57, 279-281, 318) and starts no subprocess; whether its runtime writes further files was not read.
- **OB-8 non-launch list redundancy.** `pari/<tag>.gp` (a1_pari.py 91-93) is named exactly by the gp argv (94) and `health/<tag>.ms` (a1_health.py 141-143) by the msolve argv `-f` (144), so both are attributable by RH-1 (ii); listing them as non-launch writes removes the only file a lost gp record would leave.
- **OB-9 RI-3 (19)** "the two renamed attempt-1 files present": `_rename` renames each of `.ms.out`, `.ms.log`, `.ms.err` that exists and records an `absent` entry for one that does not (r3_resolve.py 228-237); "two" is descriptive of a solve whose `.ms.out` is absent, not a rule.
- **OB-10 one list read twice.** At an event tag the event's attempts list is the attempt-record list itself (r3_resolve.py 270, 277), so RI-1 (a) (i) and the attempts clause of (a) (ii) are one count; the independent counts there are accepted_attempt, the renamed_files keys and the site counters.

### 13.1-13.4 Method checks

- 13.1 Every scratch file is listed with its sha256 in the attestation (section 16).
- 13.2 Guards: `scan.py` and `scan2.py` ran under an audit hook refusing imports of scanned module names and every process launch: 0 refused in each.
- 13.3 lstat before and after every archived-package read: `pkgread.py` 77 checked, 0 changed; `rdscan.py` 602 checked, 0 changed.
- 13.4 `rteval_v1.out` (546 lines) and `rteval_v2.out` (1350 lines): lines 1-544 are identical (a one-line Python comparison printed `546 1350 True`); line 546 of version 1 is its file-writing message.

## 14. Behaviours relied on (provenance; verdict dependence)

| behaviour | provenance | verdict dependence |
|---|---|---|
| open(2) with O_CREAT can fail without creating the file (ENOSPC / EDQUOT, ENFILE, EMFILE, EIO, EROFS) | recalled operating-system behaviour | CX-A's reachability (BJ-1). Without it CX-A needs a signal delivered in the child before 188 |
| os._exit(n) ends the process with status n without handlers, finally clauses or interpreter shutdown | recalled interpreter behaviour; childend RG-1 (c) states the same | CX-A step 5, RG-1 classes |
| a pipe read returns EOF once every write end is closed, including by process exit | recalled operating-system behaviour | CX-A step 6 (report "") |
| O_NOATIME reads leave atime unchanged for files the caller owns | used; lstat before / after unchanged (13.3) | none (integrity of the reading only) |
| GIT_OPTIONAL_LOCKS=0 stops `git status` from refreshing the index | recalled git behaviour | none (no repository write) |
| audit hooks (sys.addaudithook) see import and process-launch events | recalled interpreter behaviour | guard strength only |
| an exception escaping an os.register_at_fork callback is reported and not propagated | recalled interpreter behaviour (as review 94cc33 B-2) | BJ-3 reading of RI-5 (c) only |
| SystemExit with a string argument exits with status 1 | recalled interpreter behaviour | BJ-1 (5) residual X1 |
| the frozen code execs only at v2_solver.py 204-205 | read (scan2.py) | BJ-1 (5), CX-A physical content |
| V-7 compares the whole-file sha256 recorded after the driver exits | read (r3_check_run.py 153-158; r3_run_wrapper.py 395) | FC-1 |

The optional third-party source text (flint, numpy, cypari2 and its signal layer, yaml) was NOT read. Reason: `rdscan.py` and the YAML parse checks import the yaml package, and CRI-1 forbids importing a third-party module read under BJ-1; `scan2.py`'s third-party part was therefore given a nonexistent directory. RGL-6 stays as the draft states it.

## 15. red_team_report (readable form; the YAML carries the same block)

- id: TASK-20260924-be2daf; task_id: TASK-20260924-be2daf (no RT id minted).
- claim_under_review: the attcount draft's difference from gapattr (RI-1..RI-6, RGL-8, RGL-9) and its interaction with everything incorporated: that binding launch-record multiplicity to the resolve layer's counts closes the lost-record route CX-1 without refusing a planned basis outcome; that RI-3's checks are derivable and discriminating; that RI-4 and RI-5 hold on the r3 base; that the carried residuals and RFR-4 hold.
- objections: (1) CX-A: a lost callgrind (or gp) launch record whose child left no file is detected by nothing, because RI-1 binds counts to `.ms.log` launches only; definition (ii) holds under the literal reading; pre-existing, not opened by the difference. (2) RI-1's WHY sentence treats duplication and loss alike for callgrind (OB-2). (3) RI-3 (25)'s PASS conflicts with V-7 on in-place alterations (FC-1). (4) RI-4's "as a path prefix" STOPs on the values RI-4 names (FC-2). (5) RI-5 (a)'s temporal clause is accurate for r4 only (OB-4). (6) RGL-9 overstates the undetected class (OB-1).
- required_controls: the CX-A discriminating control (section 11); RI-3 (25) evaluated with and without V-7, with the evaluator's reading stated in the DV-18 output; the (24) / (26) stand-in placed beneath the SE-3 wrapper.
- counterexample_or_mutation: CX-A (section 11). Cheapest mutation: bind per-tag callgrind launch records to the key presence of `instructions_callgrind` in the returned solve result (v2_driver.py 209) or to the S-3 records (r3_resolve.py 355-365, after checking VA-6 (c) and RL-5's V-3 disposition); for gp, drop `pari/<tag>.gp` from the non-launch list (a1_pari.py 94 names it in argv).
- baseline_comparison: not applicable to a recording and verdict rule; the comparison made is gapattr as worded (RH) and failclosed as worded (RF) on every object. On every object examined, attcount is at least as strict as gapattr and strictly stricter on LR-1, LR-2, LR-3, LR-5, the eleven single-removal objects, LE-1, LN-7a and TW-3 (LR-4 FAILs under both).
- heuristic_challenges: none (no heuristic is stated or used by the difference); HEUR-GFPN-DFLAT untouched.
- cost_model_challenges: FC-1..FC-7 costs (section 12); no research cost path is claimed.
- reduction_and_scope_challenges: RGL-9 scope (OB-1); RI-4 list scope (OB-5); RI-5 (a) temporal scope (OB-4).
- proof_architecture_challenges: nearby-object control run: LN-7a (msolve, closed by RI-1) against CX-A (callgrind, not closed); the separator is the absence of an independent count for non-`.ms.log` launches.
- narrowest_supported_statement: On the frozen code, the r3 base and the rule text as worded, and under the reconstructed launch sets of the four archived r3 gate packages, attcount's RI-1 turns every lost-record construction at an msolve or health launch examined here into a named gap and FAIL, unless the loss removes the record and every count RI-1 reads together, and even then any file the launch left is a gap; it refuses no ordinary outcome examined (N-1..N-13, every RKR-4 (b) PASS / PASS_ZL row, 85 reconstructed (site, tag) rows). A lost callgrind or gp launch record whose child left no file stays undetected (CX-A), a definitional fail-open whose child could not have executed argv. Nothing here is evidence about D.
- next_concrete_action: a check step: evaluate the CX-A discriminating control, and the RI-3 (25) objects with and without V-7, on a development package in scratch, and record which reading of definition (ii) (absent record) the evaluator applies.
- artifact_paths: the two files of this report.

## 16. review_attestation (readable form)

- task_id TASK-20260924-be2daf; role red-team; joints_owned BJ-0, BJ-1, BJ-2, BJ-3, BJ-4, BJ-5, BJ-6.
- verdicts: BJ-0 holds; BJ-1 breaks; BJ-2 holds; BJ-3 holds; BJ-4 holds; BJ-5 holds; BJ-6 holds.
- read_sibling_reports: none (there are no sibling reports in this round; the archived reviews f5631b, 1ecb7d and 94cc33 are inputs and were read as such: 94cc33 in part; f5631b and 1ecb7d hashed only).
- blind_from, NOT opened (19): ledger/decisions/DEC-20260924-1d7614.yaml; ledger/corrections/CORR-20260924-5c3086.yaml; ledger/handoffs/TASK-20260924-9ba862.yaml; ledger/handoffs/TASK-20260924-2a7c7f.yaml; ledger/goals/GOAL-GFPN-380702/goal.yaml; knowledge/techniques/KN-TECH-175a62.md; knowledge/techniques/KN-TECH-79d6b9.md; ledger/decisions/DEC-20260924-61b22c.yaml; ledger/corrections/CORR-20260924-3c831f.yaml; ledger/handoffs/TASK-20260924-c9218d.yaml; ledger/handoffs/TASK-20260924-27ea14.yaml; ledger/decisions/DEC-20260924-844896.yaml; ledger/corrections/CORR-20260924-862f7d.yaml; ledger/handoffs/TASK-20260924-64c8fe.yaml; ledger/handoffs/TASK-20260924-5816cd.yaml; ledger/decisions/DEC-20260924-8fa3d4.yaml; ledger/corrections/CORR-20260924-7fcbd2.yaml; ledger/handoffs/TASK-20260924-7e9d3e.yaml; ledger/handoffs/TASK-20260924-eb2540.yaml.
- withheld by the dispatching session, NOT opened: ledger/handoffs/TASK-20260924-682890.yaml; coordination/goals/GOAL-GFPN-380702/batches/; coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-2a7c7f/ (not even its one field: the value was taken from the dispatching session's message); archives/TASK-20260924-27ea14/, -5816cd/, -eb2540/; every field other than path_sha256 of the six snapshot receipts; coordination/bus/ and coordination/events/; every directory under reviews/ other than TASK-20260924-f5631b/, -1ecb7d/, -94cc33/ and the three released files; git commit messages; pull requests and the web. No repository-wide search included a withheld path (every search named explicit paths inside experiments/EXP-GFPN-05ff43/, the three review directories, tools/ and harness/).
- blindness disclosures: the draft summarizes and cites DEC-20260924-1d7614 (header lines 4-24; findings_carried 215-262; options 572-612), CORR-20260924-5c3086 (RIF-5), DEC-20260924-61b22c and DEC-20260924-844896 (carried decisions, 557-561; RI-5 (a)); this was read as part of the draft, as the card anticipates. The incorporated drafts (gapattr, childend, failclosed) and the archived review 94cc33 name further withheld decisions and corrections in their own text; those mentions were read as part of those inputs. No withheld file was opened.
- inference: requested_policy review-adversarial; agent_binding red-team, at the policy's default reasoning effort, as the dispatching session arranged; resolved_model_id null (none supplied by the dispatching session; none invented); model_verified false; fallback_used false; bedrock_used false.
- deviations: listed in the YAML `review_attestation.deviations` and here: (DV-1) CONTEXT COMPACTION of the working context occurred once (after the tables were written, before the deliverables); after it every line a verdict cites was re-read (command log entries 63-79); (DV-2) twice a read-only command's output exceeded the display limit and the session harness persisted that output to a file under the session-configuration directory outside the repository (command log 17 and 65); neither file was opened; the same bytes were re-read in smaller parts; (DV-3) `rteval_v1.py` was edited once before its first run; (DV-4) `rteval_v2.py` executes this review's own scratch file `rteval_v2_objects.py`; (DV-5) the yaml package was imported (rdscan.py; the parse checks), so the optional third-party source text was not read at all, and one `ls -d` listed two names under the interpreter's dist-packages directory (not present there; names only, nothing read); (DV-6) the CRI-2 (a) value was taken from the dispatching session's message; (DV-7) card inputs not read: DEC-20260924-a789e1, DEC-20260924-650068, DEC-20260924-1ce186, DEC-20260924-15a77a, CORR-20260924-217903, CORR-20260924-80009d, CORR-20260924-b3cd63, implementation-v2-r3.md, and the amendments other than attcount, gapattr, childend, failclosed, readbackclose, readbackfull, readbackcover and valueclose (the last in part); (DV-8) the exact argv of the inline `python3 -B -c` programs and several `sed` / `grep` argument lists run before the compaction are recorded in the command log in summary form only, because the verbatim session transcript lies in a directory this task forbids reading; every git child is recorded with its exact argv; the CRI-8 id checks are recorded with the eight ids replaced by a placeholder so that no written file carries them; (DV-9) in the evaluator output the CX-A-control object lists its RI rows twice (the rule tuple named RI twice); cosmetic.
- files written outside the repository: only in the scratch directory `<scratch>/rt_be2daf/` (listed with sha256 in the YAML `review_attestation.scratch_files`), plus the two harness-persisted outputs of DV-2, written by the session harness, not opened.
- commands: the running command log follows verbatim (every entry up to the assembly). Post-write checks, run after the final write of both files, are listed in the YAML `review_attestation.post_write_checks` with their exact argv; their results are reported in the hand-back to the dispatching session, not in these files.

### 16.1 Running command log (verbatim at assembly; `<scratch>` stands for the session scratch directory, `<repo>` for /home/user/crypto-autoresearcher)

```text
# running command log for TASK-20260924-be2daf red-team review
# format: N | utc | argv/summary
1 | 2026-09-24T23:34:43Z | mkdir -p <scratch>/rt_be2daf && ls -la <scratch>/rt_be2daf/ && date -u
2 | now | create cmdlog.txt (this file)
3 | 2026-09-24T23:35:07Z | wc -l ; sha256sum ledger/handoffs/TASK-20260924-be2daf.yaml ; cat agents/red-team.md ; wc/grep/sed AGENTS.md (156-213, 573-626)
4 | 2026-09-24T23:35:24Z | ls -la coordination/goals/GOAL-GFPN-380702/archives/{0c2fdc,7e8a5d,93f3ca,71d070,ddfb69,a01341,f1fb0e}/
5 | 2026-09-24T23:35:24Z | python3 -B -c <recursive print of only path_sha256 key> <each of the six snapshot-receipt.json>
6 | 2026-09-24T23:35:24Z | sha256sum <CRI-2 files>; ls -la amendments, review dirs, census dirs
7 | 2026-09-24T23:35:37Z | GIT_OPTIONAL_LOCKS=0 git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json' experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956 ; echo rc; GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD; GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- <same pathspecs>
8 | 2026-09-24T23:35:53Z | wc -l amendments/*.yaml; ls -la experiments/EXP-GFPN-05ff43; ls runs; ls runs|wc -l
9 | 2026-09-24T23:35:53Z | Read tool: amendments/v2_addendum_attcount.yaml (1-687)
10 | 2026-09-24T23:35:53Z | wc -l on review reports and implementation files
11 | 2026-09-24T23:36:01Z | Read tool: amendments/v2_addendum_gapattr.yaml (1-633)
12 | 2026-09-24T23:36:01Z | Read tool: amendments/v2_addendum_failclosed.yaml (1-809)
13 | 2026-09-24T23:36:06Z | Read tool: reviews/TASK-20260924-94cc33/review-report.yaml (in chunks)
14 | 2026-09-24T23:36:26Z | grep/sed of 94cc33 review-report.yaml outline + lines 2151-2170,2735-2863,3053-3066; grep -n '^#' 94cc33 review-report.md
15 | 2026-09-24T23:36:39Z | Read tool: 94cc33 review-report.md 1-829; sed -n 4542,5413p of the same
16 | 2026-09-24T23:36:49Z | sed -n '4542,4870p' 94cc33 review-report.md
17 | 2026-09-24T23:36:49Z | sed -n '4870,5413p' 94cc33 review-report.md -> output >30KB was persisted by the session harness to a file under the session-configuration directory (NOT opened; only the 2KB preview of repository bytes was displayed). DEVIATION candidate DV: harness-persisted output.
18 | 2026-09-24T23:36:57Z | Read tool: 94cc33 review-report.md 4870-5418; grep -n '^### ' 94cc33 md (5849-6999)
19 | 2026-09-24T23:37:09Z | awk outline + sed -n 5849-5900,6030-6070,6138-6290,6950-6999p 94cc33 md | cut -c1-260
20 | 2026-09-24T23:37:09Z | Read tool: implementation-v2-r3/r3_resolve.py (1-513)
21 | 2026-09-24T23:37:51Z | Read tool: amendments/v2_addendum_readbackfull.yaml (full)
22 | 2026-09-24T23:38:02Z | Read tool: readbackfull 150-626; now readbackcover full
23 | 2026-09-24T23:39:17Z | Read tool: readbackcover 60-389; now v2_driver.py
24 | 2026-09-24T23:39:44Z | Read tool: v2_driver.py 1-1353 (three chunks); now a1_driver.py, a1_health.py, a1_pari.py
25 | 2026-09-24T23:39:58Z | Read tool: a1_driver.py (full), a1_health.py (full); sed -n 80,148p a1_pari.py
26 | 2026-09-24T23:40:03Z | sed -n 1,60p;140,320p;490,552p v2_solver.py
27 | 2026-09-24T23:40:18Z | sed -n 1,60p;480,552p v2_solver.py
28 | 2026-09-24T23:40:38Z | wrote <scratch>/rt_be2daf/pkgread.py (Write tool); run: PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread.py pkgread.json > pkgread.out (cwd <scratch>/rt_be2daf)
29 | 2026-09-24T23:40:46Z | PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<print solver-events.json of bfe956 in full; for others: top keys, sites counters, events count, records count>' (reads pkgread.json)
30 | 2026-09-24T23:41:10Z | PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<walk raw-result.json of each package; print every argv list found, with its json path>' (reads pkgread.json)
31 | 2026-09-24T23:41:37Z | grep -n headings of readbackclose and childend
32 | 2026-09-24T23:41:41Z | sed -n 201,535p readbackclose
33 | 2026-09-24T23:41:45Z | sed -n 205,622p childend
34 | 2026-09-24T23:48:19Z | sed -n 440,582p childend; Read r3_check_run.py (full)
35 | 2026-09-24T23:48:53Z | Read tool: r3_check_run.py (full); Read r3_run_wrapper.py (full)
36 | 2026-09-24T23:49:16Z | Read r3_run_wrapper.py (full); grep -n -i 'V-7\|events_file_integrity\|sha256 disagrees\|VA-6 (a)\|whole-file' in the three archived review yamls/mds and five amendments
37 | 2026-09-24T23:49:24Z | sed -n 296,345p valueclose
38 | 2026-09-24T23:49:37Z | PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<parse the four trial plans as JSON; per package: kind, cells arms, builds items, duplicates; gate block>'
39 | 2026-09-24T23:49:43Z | sed -n 1,120p v2_common.py; python3 -B -c '<keys and regression index list of square_analogue_n3.json>'
40 | 2026-09-24T23:49:51Z | sed -n 1,114p v2_check_run.py; sed -n 70,90p a1_check_run.py; sed -n 18,40p;84,100p r3_common.py; sed -n 55,84p r3_entry_v2.py; sed -n 85,115p r3_entry_a1.py
41 | 2026-09-24T23:50:14Z | cat -n a1_check_run 1-100, a1_common 20-60, r3_common 18-40/84-104, r3_entry_v2 1-84, v2_check_run 1-114; python3 -B -c '<print a1-r3 plan gate.addendum_blocking_package and packages controls_a1_gate_required>'; sed -n 555,602p readbackclose
42 | 2026-09-24T23:50:52Z | wrote scan.py (Write tool); run: PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan.py scan.json > scan.out 2>&1 (cwd <scratch>/rt_be2daf)
43 | 2026-09-24T23:51:03Z | PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<print calls, refs with role call for run_child/solve/run_system, events_file_mentions and counter_mentions from scan.json>'
44 | 2026-09-24T23:52:23Z | wc/sha256sum/grep of reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py (released file)
45 | 2026-09-24T23:57:14Z | sed -n 321,346p v2_solver.py
46 | 2026-09-24T23:57:20Z | sed -n 470,495p readbackclose-census.md
47 | 2026-09-25T00:00:51Z | wrote rteval_v1.py (Write tool; one Edit before its first run: weak-mode COUNT GAP for N=0); run: PYTHONDONTWRITEBYTECODE=1 timeout 600 python3 -B rteval_v1.py > rteval_v1.out 2>&1
48 | 2026-09-25T00:01:45Z | sha256sum rteval_v1.*; cp rteval_v1.py rteval_v2.py (v2 = v1 with objects appended; rule functions unchanged)
49 | 2026-09-25T00:01:54Z | python3 -B - <<heredoc (string edit of rteval_v2.py: header, output name, exec of rteval_v2_objects.py before the final write)
50 | 2026-09-25T00:03:19Z | wrote rteval_v2_objects.py (Write tool); run: PYTHONDONTWRITEBYTECODE=1 timeout 600 python3 -B rteval_v2.py > rteval_v2.out 2>&1
51 | 2026-09-25T00:03:27Z | grep -n package lines of rteval_v2.out lines 546-900 (BJ-1 objects)
52 | 2026-09-25T00:03:42Z | awk NR>=900 rteval_v2.out | grep -v record lines
53 | 2026-09-25T00:05:55Z | wrote rdscan.py (Write tool); run: PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan.py rdscan.json > rdscan.out 2>&1
54 | 2026-09-25T00:07:28Z | ls -d /usr/local/lib/python3.11/dist-packages/yaml /usr/local/lib/python3.11/dist-packages/PyYAML*  (listing names only)
55 | 2026-09-25T00:07:41Z | PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan2.py scan2.json /nonexistent-dir-for-B > scan2.out 2>&1 (part B deliberately given a nonexistent directory: PyYAML was imported by rdscan.py, so it is NOT read under BJ-1)
56 | 2026-09-25T00:07:58Z | grep -rn -l -e 'solver-events' -e 'launch_records' -e 'attempts_total' -e 'passthrough_calls_gb_only_true' -e 'renamed_files' -e 'accepted_attempt' -e 'raw_result_writer' -e 'recorder-foreign' tools/ harness/ (explicit paths; neither withheld)
57 | 2026-09-25T00:08:06Z | cat -n v2_solver.py 149-236 and 512-552 (line-number verification)
58 | 2026-09-25T00:09:56Z | grep -n anchors in attcount/gapattr/failclosed/readbackfull/readbackcover/readbackclose/valueclose; cat -n a1_pari.py 86-113
59 | 2026-09-25T00:10:18Z | wrote selfcheck.py; PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B selfcheck.py <scratch scripts and outputs>
60 | 2026-09-25T00:11:31Z | ls -la; wc -c -l scratch files; test -e <write scope>; ls experiments/EXP-GFPN-05ff43 | grep r4
61 | 2026-09-25T00:12:14Z | wrote tables.py; PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables.py; python3 -B -c '<yaml.safe_load(tables.yaml.part) key check>'
62 | 2026-09-25T00:12:56Z | report-time re-check: sha256sum <CRI-2 files + released frozen files + card>; GIT_OPTIONAL_LOCKS=0 git diff --stat dd1034... -- <pathspecs>; GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD; GIT_OPTIONAL_LOCKS=0 git cat-file -t dd1034...; GIT_OPTIONAL_LOCKS=0 git merge-base --is-ancestor dd1034... HEAD; GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf
63 | 2026-09-25T00:15:58Z | CONTEXT COMPACTION of the working context (CRI-5 deviation). After it: re-reading every verdict-cited line before writing. Read tool: appendix.py, tables.py, selfcheck.py, scan2.py, rdscan.py (scratch); tail cmdlog; ls -la scratch; date -u
64 | 2026-09-25T00:17:26Z | re-read (post-compaction): cat -n attcount (Read tool, full); cat -n card 1-531; cat -n agents/red-team.md; gapattr 243-476; failclosed 370-410, 600-712; childend grep + 250-437; readbackfull 190-335; readbackcover 194-242; v2_solver 140-300, 326-336, 505-552; v2_driver 88-215
65 | 2026-09-25T00:17:26Z | sed -n 546,870p rteval_v2.out | cut -c1-400 -> output >30KB persisted by the session harness to a file under the session-configuration directory (NOT opened; 2KB preview of scratch bytes displayed). DEVIATION (second instance of the harness-persisted output).
66 | 2026-09-25T00:20:35Z | re-read (post-compaction): rteval_v2.out 546-640, 640-760, 760-870 (cut -c1-300/330), 214-354, 862-1166, 1164-1350 (grep -v record lines); BJ-0 headings; rteval_v2.py 564-637; rteval_v2_objects.py grep CX-A-gp; r3_resolve 40-75, 190-240, 240-412; r3_check_run 40-70, 150-186, 248-258, 320-336; a1_check_run 76-86; valueclose 310-336; r3_run_wrapper 60-70, 95-105, 186-204, 282-294, 350-400, 434-475, 505-515, 540-552; readbackclose 246-300, 307-373; readbackclose-census.md 470-495; a1_pari 84-130; a1_health 125-165, 220-255; v2_driver 640-662, 1105-1130, 1150-1180, call sites; grep except/try in drivers; grep run_status in checkers; v2_driver 766-800, 812-845, awk 752-934; rdscan.out head
67 | 2026-09-25T00:20:35Z | PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B appendix.py (cwd <scratch>/rt_be2daf); wc -c -l appendix.md.part
68 | 2026-09-25T00:22:29Z | diff rteval_v1.py rteval_v2.py; PYTHONDONTWRITEBYTECODE=1 python3 -B -c "<compare rteval_v1.out and rteval_v2.out lines 1-544>" (cwd <scratch>/rt_be2daf)
69 | 2026-09-25T00:23:43Z | grep RUNS_DIR/EXP/PLAN_A1_R3 in r3_common.py; grep EXP_DIR/REPO/HERE in v2_common.py; grep PLAN_A1_PATH/EXP_DIR in a1_common.py; PYTHONDONTWRITEBYTECODE=1 python3 -B -c "<print a1-r3 plan gate.addendum_blocking_package and the set of controls_a1_gate_required values>"
70 | 2026-09-25T00:23:49Z | grep import/plan/PLAN_A1_PATH/def main in a1_check_run.py
71 | 2026-09-25T00:23:54Z | sed -n 26,34p and 60,70p a1_check_run.py
72 | 2026-09-25T00:24:01Z | writing body.md.part and body.yaml.part in <scratch>/rt_be2daf (Write tool)
73 | 2026-09-25T00:27:49Z | sed -n 165,220p a1_health.py
74 | 2026-09-25T00:27:59Z | sed -n 55,62p v2_common.py; grep -n "C.sh(|sh(" implementation-v2/*.py implementation-v2-a1/*.py
75 | 2026-09-25T00:28:16Z | grep -n "H.run(|health.run(|.run(p" implementation-v2-a1/*.py implementation-v2-r3/*.py
76 | 2026-09-25T00:28:22Z | awk enclosing def of a1_driver.py 129; grep callers
77 | 2026-09-25T00:28:29Z | awk loops/assignments in a1_driver.py 56-135
78 | 2026-09-25T00:29:20Z | ls archives/TASK-20260924-{71d070,ddfb69,a01341}/; PYTHONDONTWRITEBYTECODE=1 python3 -B - <<heredoc (recursive read of ONLY the path_sha256 key of the six snapshot-receipt.json files; sha256 of each named path; prints path, recorded hash, EQUAL/DIFFERS)
79 | 2026-09-25T00:29:26Z | sha256sum ledger/handoffs/TASK-20260924-be2daf.yaml agents/red-team.md AGENTS.md; GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD
80 | 2026-09-25T00:35:21Z | wrote body.md.part, attest.md.part, body.yaml.part, assemble.py (Write tool; two Edit calls on body.md.part for the P-8 sentence and the uncapped-children sentence, two for the section-3 census rows and hashes, one on attest.md.part, one on body.yaml.part for LC-1 quoting); PYTHONDONTWRITEBYTECODE=1 python3 -B -c "<yaml.safe_load(body.yaml.part + tables.yaml.part); print keys, inference, verdicts>"; PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B selfcheck.py body.md.part attest.md.part body.yaml.part assemble.py tables.md.part tables.yaml.part appendix.md.part cmdlog.txt
81 | 2026-09-25T00:35:28Z | sed -n 713p body.yaml.part; sed -n 26p attest.md.part | cut -c1-120 (confirm the one hit per part is the inference prohibition flag)
82 | 2026-09-25T00:35:37Z | for each of the eight CRI-8 ids: cat <the parts and cmdlog> | grep -c <id>
83 | 2026-09-25T00:36:12Z | Edit calls: body.yaml.part DV-8 text and command_log_note; attest.md.part DV-8 text and entry-range text; PYTHONDONTWRITEBYTECODE=1 python3 -B -c "<replace a1_health.py 147-156 by 147-220 and qualify a1_driver.py 129 in body.md.part>"
84 | 2026-09-25T00:36:17Z | grep -n import lines of rteval_v2.py rteval_v2_objects.py
85 | 2026-09-25T00:36:23Z | PYTHONDONTWRITEBYTECODE=1 python3 -B -c "<correct the evaluator import list in body.md.part to collections, itertools, json, os, re, sys>"
86 | 2026-09-25T00:36:30Z | PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B assemble.py (cwd <scratch>/rt_be2daf): creates the write-scope directory and writes review-report.yaml and review-report.md once each, whole
```

### 16.2 Scratch files (sha256 at assembly)

| file | sha256 | bytes | purpose |
|---|---|---|---|
| `<scratch>/rt_be2daf/appendix.md.part` | 3bc640b1d59112dbf5ba61148705a7ca629eca06c9266b33ee6d7df2cdf43640 | 336073 | md part: the verbatim appendix written by appendix.py |
| `<scratch>/rt_be2daf/appendix.py` | bd8bcc44a70797a2208677ac0287396091b39ecaad2ee080b522ef1f257b6710 | 3889 | appendix writer |
| `<scratch>/rt_be2daf/assemble.py` | 3d7575a2bc381f90f4f939ef308da7110d0621a4e278c738ae7f3f37ff53a229 | 4886 | this assembler |
| `<scratch>/rt_be2daf/attest.md.part` | bd936abbc8d6f3704be0cdb6ba0311f2d5ea0c68df616fa87b57af08bec98b57 | 9306 | md part: red_team_report and attestation (readable) |
| `<scratch>/rt_be2daf/body.md.part` | 3c77120460de01ce2f9f382ff73278ca0a85cdf28cbcde37e6e5b2905cb7c258 | 57187 | md part: sections 1-14 |
| `<scratch>/rt_be2daf/body.yaml.part` | 4e4a7f55a0030fd07a1f5fe5bf5444e577f8cdfc3871eb8dde3fe5a078250661 | 64551 | yaml part: everything except the tables |
| `<scratch>/rt_be2daf/cmdlog.txt` | 6549909c7b1af2643d64810b66242c3c51b123c67d958e3177d6b5688f5a8568 | 13696 | running command log (hash at assembly; later entries are the post-write checks) |
| `<scratch>/rt_be2daf/pkgread.json` | 94b94580d9f5569e3f109acb2c1f25832a398ea41318716acbb2a8f0eda0b90c | 834521 | pkgread.py data (archived-package listings and records) |
| `<scratch>/rt_be2daf/pkgread.out` | 5004bbb36a66601058e41b3e466274afa072482078885c325c573f5652cad200 | 1377 | pkgread.py printed summary |
| `<scratch>/rt_be2daf/pkgread.py` | ea817d16e0e12caaf5a50e9e5f10a7e14fb4b3dc097cf1c5d95bda84190c8a3e | 3620 | archived-package reader (O_NOATIME) |
| `<scratch>/rt_be2daf/rdscan.json` | 50214e924122a8f9f4b1643f378d69fb0116e1cc21507ca22631b84df88a777f | 66158 | rdscan.py data |
| `<scratch>/rt_be2daf/rdscan.out` | 75479e306c36411088b3f5ff0586731c6a1ddf1b5a279baa47f089e03d4035e7 | 16477 | rdscan.py printed summary |
| `<scratch>/rt_be2daf/rdscan.py` | fe573d4255457b538279c5e3f56cc1d3887c4e998eb32a536b9644dac8ef3e7c | 4203 | run-directory value scan (O_NOATIME) |
| `<scratch>/rt_be2daf/rteval_v1.json` | 126f0e9a6c8895e3f9ef496e7f96163a167f07cc279a618d530443ee59020528 | 288985 | evaluator version 1 data |
| `<scratch>/rt_be2daf/rteval_v1.out` | b20bb1d9d5c7831d9c1bcb74b3d47a945179266cb44f715ade741c56739c6ce8 | 67551 | evaluator version 1 output (BJ-0) |
| `<scratch>/rt_be2daf/rteval_v1.py` | f142a388c79d80353d295f36fac2c128fbea1ea8d47c2436ada7b04868d73272 | 52488 | evaluator version 1 |
| `<scratch>/rt_be2daf/rteval_v2.json` | 4795a995563bc2c73cae2b5b0b46e4ef3033bfab01b572a8df2e6f3bd78d6bbd | 363969 | evaluator version 2 data (listing and count tables) |
| `<scratch>/rt_be2daf/rteval_v2.out` | cd9880535dd04e0abb2e42f5579cc805bc67e7f0d12316cf321aeef28887f724 | 144055 | evaluator version 2 output (final) |
| `<scratch>/rt_be2daf/rteval_v2.py` | fb74f767763aa4962896b1742d434e8dc1ef049dd5ad04e45ac2c2a451ecfdfa | 52679 | evaluator version 2 (= version 1 + exec of the objects file) |
| `<scratch>/rt_be2daf/rteval_v2_objects.py` | ce59195533c0ff85ca25c88e6f4d22d55bb91e8a6504bf629ad1469de0067151 | 20677 | BJ-1..BJ-4 objects executed inside rteval_v2.py |
| `<scratch>/rt_be2daf/scan.json` | 65b63fd28a6168031e1758155150ac57d5d19e352bba74d008b0cd09161f582f | 42849 | scan.py data |
| `<scratch>/rt_be2daf/scan.out` | 97956ff9a4635eb58142c526d3c70b037128684e052bbcf72243e2a864c01d8e | 1698 | scan.py output |
| `<scratch>/rt_be2daf/scan.py` | 10b643f94618d9bc84263a0b316662590eb3f8290a3818f38a6327d2815d676e | 7062 | ast / dis scan of the implementation trees |
| `<scratch>/rt_be2daf/scan2.json` | 1874d87921734140fe339aceaa299217c59535f133d83c1e78d7981ee3731439 | 11177 | scan2.py data |
| `<scratch>/rt_be2daf/scan2.out` | 68c66c51f477031ed834cc60871c55789993f16cdd3a28c2b0cfa7f7f47d1924 | 8844 | scan2.py output |
| `<scratch>/rt_be2daf/scan2.py` | 0db70c769a075189d36aef8f1fdc310ae35741e998185ddc479df8f4e7b66eab | 4498 | process-ending / exec / hook scan |
| `<scratch>/rt_be2daf/selfcheck.py` | 6e6acce83a95bdb6c2ad03aabb3b5e0c869ae1b61b6f7c569ce13265c5f85101 | 1231 | CRI-7 name self-check |
| `<scratch>/rt_be2daf/tables.md.part` | 131937ccb85f40fbf5c93d11d928be3ef5a4585d5a20195db4d862510ec4c4f4 | 67262 | md part: listing and count tables |
| `<scratch>/rt_be2daf/tables.py` | 86e56fffa5def8bb583815542fc187a8dbe7ce94d0e60e012c53342491558c2e | 7984 | table writer |
| `<scratch>/rt_be2daf/tables.yaml.part` | 0ad45ece425a2a6233680578130b764d6ac6cb33882a3924d19a89ba8b30b52b | 73809 | yaml part: listing and count tables |
| `<scratch>/rt_be2daf/words.txt` | c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 | 113 | word list placed by the dispatching session (read only by selfcheck.py; never printed) |

## Listing and count tables (BJ-0 (f), BJ-2 (2))

Reconstruction rule (CRI-9): CRI-9 RECONSTRUCTION (rteval_v2.py reconstruct()): child/<tag>.spec.json -> one child-job launch record (argv [python, -B, implementation-v2/v2_child.py, <rd>/child/<tag>.spec.json]; stdout/stderr child/<tag>.stdout/.stderr; v2_driver.py 92-102); solver|health/<tag>.ms.log -> one msolve launch record (argv -f <dir>/<tag>.ms -o <dir>/<tag>.ms.out, -g 1 or -P 1; stdout/stderr <tag>.ms.log/.ms.err; v2_driver.py 161-166, a1_health.py 141-147); solver/<tag>.callgrind.stdout -> one callgrind record (v2_solver.py 515-518, v2_driver.py 208-209); comparator/stdout.log -> one comparator record (v2_driver.py 647-651); pari/<tag>.gp.stdout -> one gp record (a1_pari.py 91-96). child_end exec where the child's outputs exist. PER-TAG RB-1 / RL-2 counts (the records do not exist in r3) are taken INDEPENDENTLY of the listing: from the raw-result.json solver argv of the tag where recorded (-P 1: one RB-1 attempt record; -g 1: one RL-2 pass-through record), else from the frozen call site's gb_only argument (v2_driver.py 711 gb_only=True; 786, 787, 841 gb_only default False). Events and site counters are the archived r3 solver-events.json's (sites v2_driver.solve and a1_health.run_system). Paths are compared as absolute paths under each package's recorded GFPN_RUN_DIR, equal to its current path (command.txt line 2). A listing or count check is a reading of r3 artifacts under r4 rule text: never a result about any package's verdict and never evidence about D.

### Listing check under attcount (RH-1 with RI-1 (a)-(d) as worded)

| package | files in the five directories | reconstructed launch records | files by first clause | named gaps | unattributed |
|---|---|---|---|---|---|
| RUN-GFPN-f6a21a | 284 | 88 {"callgrind": 36, "childjob": 16, "msolve": 36} | {"(i)": 176, "(ii)": 88, "(v)": 20} | 0 | **0** |
| RUN-GFPN-902222 | 284 | 88 {"callgrind": 36, "childjob": 16, "msolve": 36} | {"(i)": 176, "(ii)": 88, "(v)": 20} | 0 | **0** |
| RUN-GFPN-f5412a | 32 | 7 {"childjob": 1, "comparator": 1, "msolve": 5} | {"(i)": 14, "(ii)": 11, "(iv)": 5, "(v)": 2} | 0 | **0** |
| RUN-GFPN-bfe956 | 83 | 19 {"childjob": 11, "msolve": 8} | {"(i)": 38, "(ii)": 27, "(v)": 18} | 0 | **0** |

Unattributed files under RI, each listed: RUN-GFPN-f6a21a: none; RUN-GFPN-902222: none; RUN-GFPN-f5412a: none; RUN-GFPN-bfe956: none.

### Listing check under gapattr RH-1 as worded (contrast)

| package | files in the five directories | reconstructed launch records | files by first clause | named gaps | unattributed |
|---|---|---|---|---|---|
| RUN-GFPN-f6a21a | 284 | 88 {"callgrind": 36, "childjob": 16, "msolve": 36} | {"(i)": 176, "(ii)": 88, "(v)": 20} | 0 | **0** |
| RUN-GFPN-902222 | 284 | 88 {"callgrind": 36, "childjob": 16, "msolve": 36} | {"(i)": 176, "(ii)": 88, "(v)": 20} | 0 | **0** |
| RUN-GFPN-f5412a | 32 | 7 {"childjob": 1, "comparator": 1, "msolve": 5} | {"(i)": 14, "(ii)": 11, "(iv)": 5, "(v)": 2} | 0 | **0** |
| RUN-GFPN-bfe956 | 83 | 19 {"childjob": 11, "msolve": 8} | {"(i)": 38, "(ii)": 27, "(v)": 18} | 0 | **0** |

Unattributed files under RH, each listed: RUN-GFPN-f6a21a: none; RUN-GFPN-902222: none; RUN-GFPN-f5412a: none; RUN-GFPN-bfe956: none.

### Per-file attribution under attcount (first applying clause and record; every file of the five directories)

#### RUN-GFPN-f6a21a (284 files)

| file | first clause, record |
|---|---|
| `child/fixture_S3.meta.json` | (v) childjob:fixture_S3 |
| `child/fixture_S3.npz` | (v) childjob:fixture_S3 |
| `child/fixture_S3.spec.json` | (ii) childjob:fixture_S3 |
| `child/fixture_S3.stderr` | (i) childjob:fixture_S3 |
| `child/fixture_S3.stdout` | (i) childjob:fixture_S3 |
| `child/fixture_S3_rescaled.meta.json` | (v) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.npz` | (v) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.spec.json` | (ii) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.stderr` | (i) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.stdout` | (i) childjob:fixture_S3_rescaled |
| `child/fixture_torsion_S3_norm.meta.json` | (v) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.npz` | (v) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.spec.json` | (ii) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.stderr` | (i) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.stdout` | (i) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_rq.meta.json` | (v) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.npz` | (v) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.spec.json` | (ii) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.stderr` | (i) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.stdout` | (i) childjob:fixture_torsion_S3_rq |
| `child/fx_fresh1_raw_u.meta.json` | (v) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.spec.json` | (ii) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.stderr` | (i) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.stdout` | (i) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_x.meta.json` | (v) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.spec.json` | (ii) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.stderr` | (i) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.stdout` | (i) childjob:fx_fresh1_raw_x |
| `child/fx_fresh2_raw_u.meta.json` | (v) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.spec.json` | (ii) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.stderr` | (i) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.stdout` | (i) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_x.meta.json` | (v) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.spec.json` | (ii) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.stderr` | (i) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.stdout` | (i) childjob:fx_fresh2_raw_x |
| `child/fx_planted0_raw_u.meta.json` | (v) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.spec.json` | (ii) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.stderr` | (i) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.stdout` | (i) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_x.meta.json` | (v) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.spec.json` | (ii) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.stderr` | (i) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.stdout` | (i) childjob:fx_planted0_raw_x |
| `child/fx_planted1_raw_u.meta.json` | (v) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.spec.json` | (ii) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.stderr` | (i) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.stdout` | (i) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_x.meta.json` | (v) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.spec.json` | (ii) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.stderr` | (i) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.stdout` | (i) childjob:fx_planted1_raw_x |
| `child/fx_reg0_raw_u.meta.json` | (v) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.spec.json` | (ii) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.stderr` | (i) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.stdout` | (i) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_x.meta.json` | (v) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.spec.json` | (ii) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.stderr` | (i) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.stdout` | (i) childjob:fx_reg0_raw_x |
| `child/fx_reg1_raw_u.meta.json` | (v) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.spec.json` | (ii) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.stderr` | (i) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.stdout` | (i) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_x.meta.json` | (v) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.spec.json` | (ii) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.stderr` | (i) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.stdout` | (i) childjob:fx_reg1_raw_x |
| `solver/fx_fresh1_S3.callgrind.stderr` | (i) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.callgrind.stdout` | (i) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms` | (ii) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.err` | (i) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.log` | (i) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.out` | (ii) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms` | (ii) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.err` | (i) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.log` | (i) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_raw_u.callgrind.stderr` | (i) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.callgrind.stdout` | (i) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms` | (ii) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.err` | (i) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.log` | (i) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.out` | (ii) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_x.callgrind.stderr` | (i) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.callgrind.stdout` | (i) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms` | (ii) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.err` | (i) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.log` | (i) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.out` | (ii) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms` | (ii) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms` | (ii) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh2_S3.callgrind.stderr` | (i) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.callgrind.stdout` | (i) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms` | (ii) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.err` | (i) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.log` | (i) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.out` | (ii) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms` | (ii) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.err` | (i) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.log` | (i) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.out` | (ii) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_raw_u.callgrind.stderr` | (i) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.callgrind.stdout` | (i) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms` | (ii) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.err` | (i) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.log` | (i) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.out` | (ii) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_x.callgrind.stderr` | (i) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.callgrind.stdout` | (i) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms` | (ii) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.err` | (i) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.log` | (i) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.out` | (ii) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms` | (ii) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms` | (ii) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_planted0_S3.callgrind.stderr` | (i) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.callgrind.stdout` | (i) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.ms` | (ii) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.err` | (i) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.log` | (i) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.out` | (ii) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms` | (ii) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.err` | (i) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.log` | (i) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.out` | (ii) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_raw_u.callgrind.stderr` | (i) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.callgrind.stdout` | (i) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms` | (ii) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.err` | (i) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.log` | (i) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.out` | (ii) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_x.callgrind.stderr` | (i) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.callgrind.stdout` | (i) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms` | (ii) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.err` | (i) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.log` | (i) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.out` | (ii) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms` | (ii) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms` | (ii) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted1_S3.callgrind.stderr` | (i) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.callgrind.stdout` | (i) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.ms` | (ii) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.err` | (i) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.log` | (i) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.out` | (ii) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms` | (ii) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.err` | (i) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.log` | (i) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_raw_u.callgrind.stderr` | (i) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.callgrind.stdout` | (i) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms` | (ii) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.err` | (i) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.log` | (i) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.out` | (ii) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_x.callgrind.stderr` | (i) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.callgrind.stdout` | (i) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms` | (ii) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.err` | (i) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.log` | (i) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.out` | (ii) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms` | (ii) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms` | (ii) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_reg0_S3.callgrind.stderr` | (i) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.callgrind.stdout` | (i) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.ms` | (ii) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.err` | (i) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.log` | (i) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.out` | (ii) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms` | (ii) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.err` | (i) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.log` | (i) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.out` | (ii) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_raw_u.callgrind.stderr` | (i) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.callgrind.stdout` | (i) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms` | (ii) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.err` | (i) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.log` | (i) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.out` | (ii) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_x.callgrind.stderr` | (i) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.callgrind.stdout` | (i) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms` | (ii) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.err` | (i) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.log` | (i) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.out` | (ii) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms` | (ii) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms` | (ii) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg1_S3.callgrind.stderr` | (i) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.callgrind.stdout` | (i) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.ms` | (ii) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.err` | (i) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.log` | (i) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.out` | (ii) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms` | (ii) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.err` | (i) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.log` | (i) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_raw_u.callgrind.stderr` | (i) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.callgrind.stdout` | (i) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms` | (ii) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.err` | (i) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.log` | (i) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.out` | (ii) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_x.callgrind.stderr` | (i) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.callgrind.stdout` | (i) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms` | (ii) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.err` | (i) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.log` | (i) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.out` | (ii) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms` | (ii) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms` | (ii) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_reg1_torsion_S3_rq |

#### RUN-GFPN-902222 (284 files)

| file | first clause, record |
|---|---|
| `child/fixture_S3.meta.json` | (v) childjob:fixture_S3 |
| `child/fixture_S3.npz` | (v) childjob:fixture_S3 |
| `child/fixture_S3.spec.json` | (ii) childjob:fixture_S3 |
| `child/fixture_S3.stderr` | (i) childjob:fixture_S3 |
| `child/fixture_S3.stdout` | (i) childjob:fixture_S3 |
| `child/fixture_S3_rescaled.meta.json` | (v) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.npz` | (v) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.spec.json` | (ii) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.stderr` | (i) childjob:fixture_S3_rescaled |
| `child/fixture_S3_rescaled.stdout` | (i) childjob:fixture_S3_rescaled |
| `child/fixture_torsion_S3_norm.meta.json` | (v) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.npz` | (v) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.spec.json` | (ii) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.stderr` | (i) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_norm.stdout` | (i) childjob:fixture_torsion_S3_norm |
| `child/fixture_torsion_S3_rq.meta.json` | (v) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.npz` | (v) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.spec.json` | (ii) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.stderr` | (i) childjob:fixture_torsion_S3_rq |
| `child/fixture_torsion_S3_rq.stdout` | (i) childjob:fixture_torsion_S3_rq |
| `child/fx_fresh1_raw_u.meta.json` | (v) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.spec.json` | (ii) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.stderr` | (i) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_u.stdout` | (i) childjob:fx_fresh1_raw_u |
| `child/fx_fresh1_raw_x.meta.json` | (v) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.spec.json` | (ii) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.stderr` | (i) childjob:fx_fresh1_raw_x |
| `child/fx_fresh1_raw_x.stdout` | (i) childjob:fx_fresh1_raw_x |
| `child/fx_fresh2_raw_u.meta.json` | (v) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.spec.json` | (ii) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.stderr` | (i) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_u.stdout` | (i) childjob:fx_fresh2_raw_u |
| `child/fx_fresh2_raw_x.meta.json` | (v) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.spec.json` | (ii) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.stderr` | (i) childjob:fx_fresh2_raw_x |
| `child/fx_fresh2_raw_x.stdout` | (i) childjob:fx_fresh2_raw_x |
| `child/fx_planted0_raw_u.meta.json` | (v) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.spec.json` | (ii) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.stderr` | (i) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_u.stdout` | (i) childjob:fx_planted0_raw_u |
| `child/fx_planted0_raw_x.meta.json` | (v) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.spec.json` | (ii) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.stderr` | (i) childjob:fx_planted0_raw_x |
| `child/fx_planted0_raw_x.stdout` | (i) childjob:fx_planted0_raw_x |
| `child/fx_planted1_raw_u.meta.json` | (v) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.spec.json` | (ii) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.stderr` | (i) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_u.stdout` | (i) childjob:fx_planted1_raw_u |
| `child/fx_planted1_raw_x.meta.json` | (v) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.spec.json` | (ii) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.stderr` | (i) childjob:fx_planted1_raw_x |
| `child/fx_planted1_raw_x.stdout` | (i) childjob:fx_planted1_raw_x |
| `child/fx_reg0_raw_u.meta.json` | (v) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.spec.json` | (ii) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.stderr` | (i) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_u.stdout` | (i) childjob:fx_reg0_raw_u |
| `child/fx_reg0_raw_x.meta.json` | (v) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.spec.json` | (ii) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.stderr` | (i) childjob:fx_reg0_raw_x |
| `child/fx_reg0_raw_x.stdout` | (i) childjob:fx_reg0_raw_x |
| `child/fx_reg1_raw_u.meta.json` | (v) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.spec.json` | (ii) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.stderr` | (i) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_u.stdout` | (i) childjob:fx_reg1_raw_u |
| `child/fx_reg1_raw_x.meta.json` | (v) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.spec.json` | (ii) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.stderr` | (i) childjob:fx_reg1_raw_x |
| `child/fx_reg1_raw_x.stdout` | (i) childjob:fx_reg1_raw_x |
| `solver/fx_fresh1_S3.callgrind.stderr` | (i) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.callgrind.stdout` | (i) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms` | (ii) callgrind:fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.err` | (i) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.log` | (i) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3.ms.out` | (ii) msolve:solver/fx_fresh1_S3 |
| `solver/fx_fresh1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms` | (ii) callgrind:fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.err` | (i) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.log` | (i) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_fresh1_S3_rescaled |
| `solver/fx_fresh1_raw_u.callgrind.stderr` | (i) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.callgrind.stdout` | (i) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms` | (ii) callgrind:fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.err` | (i) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.log` | (i) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_u.ms.out` | (ii) msolve:solver/fx_fresh1_raw_u |
| `solver/fx_fresh1_raw_x.callgrind.stderr` | (i) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.callgrind.stdout` | (i) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms` | (ii) callgrind:fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.err` | (i) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.log` | (i) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_raw_x.ms.out` | (ii) msolve:solver/fx_fresh1_raw_x |
| `solver/fx_fresh1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms` | (ii) callgrind:fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| `solver/fx_fresh1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms` | (ii) callgrind:fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| `solver/fx_fresh2_S3.callgrind.stderr` | (i) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.callgrind.stdout` | (i) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms` | (ii) callgrind:fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.err` | (i) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.log` | (i) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3.ms.out` | (ii) msolve:solver/fx_fresh2_S3 |
| `solver/fx_fresh2_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms` | (ii) callgrind:fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.err` | (i) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.log` | (i) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_S3_rescaled.ms.out` | (ii) msolve:solver/fx_fresh2_S3_rescaled |
| `solver/fx_fresh2_raw_u.callgrind.stderr` | (i) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.callgrind.stdout` | (i) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms` | (ii) callgrind:fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.err` | (i) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.log` | (i) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_u.ms.out` | (ii) msolve:solver/fx_fresh2_raw_u |
| `solver/fx_fresh2_raw_x.callgrind.stderr` | (i) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.callgrind.stdout` | (i) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms` | (ii) callgrind:fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.err` | (i) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.log` | (i) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_raw_x.ms.out` | (ii) msolve:solver/fx_fresh2_raw_x |
| `solver/fx_fresh2_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms` | (ii) callgrind:fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| `solver/fx_fresh2_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms` | (ii) callgrind:fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_fresh2_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| `solver/fx_planted0_S3.callgrind.stderr` | (i) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.callgrind.stdout` | (i) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.ms` | (ii) callgrind:fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.err` | (i) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.log` | (i) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3.ms.out` | (ii) msolve:solver/fx_planted0_S3 |
| `solver/fx_planted0_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms` | (ii) callgrind:fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.err` | (i) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.log` | (i) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_S3_rescaled.ms.out` | (ii) msolve:solver/fx_planted0_S3_rescaled |
| `solver/fx_planted0_raw_u.callgrind.stderr` | (i) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.callgrind.stdout` | (i) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms` | (ii) callgrind:fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.err` | (i) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.log` | (i) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_u.ms.out` | (ii) msolve:solver/fx_planted0_raw_u |
| `solver/fx_planted0_raw_x.callgrind.stderr` | (i) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.callgrind.stdout` | (i) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms` | (ii) callgrind:fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.err` | (i) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.log` | (i) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_raw_x.ms.out` | (ii) msolve:solver/fx_planted0_raw_x |
| `solver/fx_planted0_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms` | (ii) callgrind:fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| `solver/fx_planted0_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms` | (ii) callgrind:fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted0_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| `solver/fx_planted1_S3.callgrind.stderr` | (i) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.callgrind.stdout` | (i) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.ms` | (ii) callgrind:fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.err` | (i) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.log` | (i) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3.ms.out` | (ii) msolve:solver/fx_planted1_S3 |
| `solver/fx_planted1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms` | (ii) callgrind:fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.err` | (i) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.log` | (i) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_planted1_S3_rescaled |
| `solver/fx_planted1_raw_u.callgrind.stderr` | (i) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.callgrind.stdout` | (i) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms` | (ii) callgrind:fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.err` | (i) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.log` | (i) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_u.ms.out` | (ii) msolve:solver/fx_planted1_raw_u |
| `solver/fx_planted1_raw_x.callgrind.stderr` | (i) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.callgrind.stdout` | (i) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms` | (ii) callgrind:fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.err` | (i) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.log` | (i) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_raw_x.ms.out` | (ii) msolve:solver/fx_planted1_raw_x |
| `solver/fx_planted1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms` | (ii) callgrind:fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| `solver/fx_planted1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms` | (ii) callgrind:fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_planted1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| `solver/fx_reg0_S3.callgrind.stderr` | (i) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.callgrind.stdout` | (i) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.ms` | (ii) callgrind:fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.err` | (i) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.log` | (i) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3.ms.out` | (ii) msolve:solver/fx_reg0_S3 |
| `solver/fx_reg0_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms` | (ii) callgrind:fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.err` | (i) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.log` | (i) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_S3_rescaled.ms.out` | (ii) msolve:solver/fx_reg0_S3_rescaled |
| `solver/fx_reg0_raw_u.callgrind.stderr` | (i) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.callgrind.stdout` | (i) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms` | (ii) callgrind:fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.err` | (i) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.log` | (i) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_u.ms.out` | (ii) msolve:solver/fx_reg0_raw_u |
| `solver/fx_reg0_raw_x.callgrind.stderr` | (i) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.callgrind.stdout` | (i) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms` | (ii) callgrind:fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.err` | (i) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.log` | (i) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_raw_x.ms.out` | (ii) msolve:solver/fx_reg0_raw_x |
| `solver/fx_reg0_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms` | (ii) callgrind:fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| `solver/fx_reg0_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms` | (ii) callgrind:fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg0_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| `solver/fx_reg1_S3.callgrind.stderr` | (i) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.callgrind.stdout` | (i) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.ms` | (ii) callgrind:fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.err` | (i) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.log` | (i) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3.ms.out` | (ii) msolve:solver/fx_reg1_S3 |
| `solver/fx_reg1_S3_rescaled.callgrind.stderr` | (i) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.callgrind.stdout` | (i) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms` | (ii) callgrind:fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.err` | (i) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.log` | (i) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_S3_rescaled.ms.out` | (ii) msolve:solver/fx_reg1_S3_rescaled |
| `solver/fx_reg1_raw_u.callgrind.stderr` | (i) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.callgrind.stdout` | (i) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms` | (ii) callgrind:fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.err` | (i) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.log` | (i) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_u.ms.out` | (ii) msolve:solver/fx_reg1_raw_u |
| `solver/fx_reg1_raw_x.callgrind.stderr` | (i) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.callgrind.stdout` | (i) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms` | (ii) callgrind:fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.err` | (i) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.log` | (i) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_raw_x.ms.out` | (ii) msolve:solver/fx_reg1_raw_x |
| `solver/fx_reg1_torsion_S3_norm.callgrind.stderr` | (i) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.callgrind.stdout` | (i) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms` | (ii) callgrind:fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.err` | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.log` | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_norm.ms.out` | (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| `solver/fx_reg1_torsion_S3_rq.callgrind.stderr` | (i) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.callgrind.stdout` | (i) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms` | (ii) callgrind:fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.err` | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.log` | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| `solver/fx_reg1_torsion_S3_rq.ms.out` | (ii) msolve:solver/fx_reg1_torsion_S3_rq |

#### RUN-GFPN-f5412a (32 files)

| file | first clause, record |
|---|---|
| `child/anchor_S4.meta.json` | (v) childjob:anchor_S4 |
| `child/anchor_S4.npz` | (v) childjob:anchor_S4 |
| `child/anchor_S4.spec.json` | (ii) childjob:anchor_S4 |
| `child/anchor_S4.stderr` | (i) childjob:anchor_S4 |
| `child/anchor_S4.stdout` | (i) childjob:anchor_S4 |
| `comparator/anchor17_planted.ms` | (iv) comparator |
| `comparator/anchor17_random.ms` | (iv) comparator |
| `comparator/anchor25_planted.ms` | (iv) comparator |
| `comparator/anchor25_random.ms` | (iv) comparator |
| `comparator/k4a_results.json` | (iv) comparator |
| `comparator/stderr.log` | (i) comparator |
| `comparator/stdout.log` | (i) comparator |
| `solver/anchor_comparator_random.ms` | (ii) msolve:solver/anchor_comparator_random |
| `solver/anchor_comparator_random.ms.err` | (i) msolve:solver/anchor_comparator_random |
| `solver/anchor_comparator_random.ms.log` | (i) msolve:solver/anchor_comparator_random |
| `solver/anchor_comparator_random.ms.out` | (ii) msolve:solver/anchor_comparator_random |
| `solver/anchor_comparator_system.ms` | (ii) msolve:solver/anchor_comparator_system |
| `solver/anchor_comparator_system.ms.err` | (i) msolve:solver/anchor_comparator_system |
| `solver/anchor_comparator_system.ms.log` | (i) msolve:solver/anchor_comparator_system |
| `solver/anchor_comparator_system.ms.out` | (ii) msolve:solver/anchor_comparator_system |
| `solver/anchor_v2_t0.ms` | (ii) msolve:solver/anchor_v2_t0 |
| `solver/anchor_v2_t0.ms.err` | (i) msolve:solver/anchor_v2_t0 |
| `solver/anchor_v2_t0.ms.log` | (i) msolve:solver/anchor_v2_t0 |
| `solver/anchor_v2_t0.ms.out` | (ii) msolve:solver/anchor_v2_t0 |
| `solver/anchor_v2_t1.ms` | (ii) msolve:solver/anchor_v2_t1 |
| `solver/anchor_v2_t1.ms.err` | (i) msolve:solver/anchor_v2_t1 |
| `solver/anchor_v2_t1.ms.log` | (i) msolve:solver/anchor_v2_t1 |
| `solver/anchor_v2_t1.ms.out` | (ii) msolve:solver/anchor_v2_t1 |
| `solver/anchor_v2_t2.ms` | (ii) msolve:solver/anchor_v2_t2 |
| `solver/anchor_v2_t2.ms.err` | (i) msolve:solver/anchor_v2_t2 |
| `solver/anchor_v2_t2.ms.log` | (i) msolve:solver/anchor_v2_t2 |
| `solver/anchor_v2_t2.ms.out` | (ii) msolve:solver/anchor_v2_t2 |

#### RUN-GFPN-bfe956 (83 files)

| file | first clause, record |
|---|---|
| `child/ctl_S3.meta.json` | (v) childjob:ctl_S3 |
| `child/ctl_S3.npz` | (v) childjob:ctl_S3 |
| `child/ctl_S3.spec.json` | (ii) childjob:ctl_S3 |
| `child/ctl_S3.stderr` | (i) childjob:ctl_S3 |
| `child/ctl_S3.stdout` | (i) childjob:ctl_S3 |
| `child/ctl_S3_rescaled.meta.json` | (v) childjob:ctl_S3_rescaled |
| `child/ctl_S3_rescaled.npz` | (v) childjob:ctl_S3_rescaled |
| `child/ctl_S3_rescaled.spec.json` | (ii) childjob:ctl_S3_rescaled |
| `child/ctl_S3_rescaled.stderr` | (i) childjob:ctl_S3_rescaled |
| `child/ctl_S3_rescaled.stdout` | (i) childjob:ctl_S3_rescaled |
| `child/ctl_identity_n3.meta.json` | (v) childjob:ctl_identity_n3 |
| `child/ctl_identity_n3.npz` | (v) childjob:ctl_identity_n3 |
| `child/ctl_identity_n3.spec.json` | (ii) childjob:ctl_identity_n3 |
| `child/ctl_identity_n3.stderr` | (i) childjob:ctl_identity_n3 |
| `child/ctl_identity_n3.stdout` | (i) childjob:ctl_identity_n3 |
| `child/ctl_identity_n5_m3.meta.json` | (v) childjob:ctl_identity_n5_m3 |
| `child/ctl_identity_n5_m3.npz` | (v) childjob:ctl_identity_n5_m3 |
| `child/ctl_identity_n5_m3.spec.json` | (ii) childjob:ctl_identity_n5_m3 |
| `child/ctl_identity_n5_m3.stderr` | (i) childjob:ctl_identity_n5_m3 |
| `child/ctl_identity_n5_m3.stdout` | (i) childjob:ctl_identity_n5_m3 |
| `child/ctl_identity_n5_m4.meta.json` | (v) childjob:ctl_identity_n5_m4 |
| `child/ctl_identity_n5_m4.npz` | (v) childjob:ctl_identity_n5_m4 |
| `child/ctl_identity_n5_m4.spec.json` | (ii) childjob:ctl_identity_n5_m4 |
| `child/ctl_identity_n5_m4.stderr` | (i) childjob:ctl_identity_n5_m4 |
| `child/ctl_identity_n5_m4.stdout` | (i) childjob:ctl_identity_n5_m4 |
| `child/ctl_raw_n5_m3.meta.json` | (v) childjob:ctl_raw_n5_m3 |
| `child/ctl_raw_n5_m3.spec.json` | (ii) childjob:ctl_raw_n5_m3 |
| `child/ctl_raw_n5_m3.stderr` | (i) childjob:ctl_raw_n5_m3 |
| `child/ctl_raw_n5_m3.stdout` | (i) childjob:ctl_raw_n5_m3 |
| `child/ctl_raw_n5_m4.meta.json` | (v) childjob:ctl_raw_n5_m4 |
| `child/ctl_raw_n5_m4.spec.json` | (ii) childjob:ctl_raw_n5_m4 |
| `child/ctl_raw_n5_m4.stderr` | (i) childjob:ctl_raw_n5_m4 |
| `child/ctl_raw_n5_m4.stdout` | (i) childjob:ctl_raw_n5_m4 |
| `child/ctl_raw_planted.meta.json` | (v) childjob:ctl_raw_planted |
| `child/ctl_raw_planted.spec.json` | (ii) childjob:ctl_raw_planted |
| `child/ctl_raw_planted.stderr` | (i) childjob:ctl_raw_planted |
| `child/ctl_raw_planted.stdout` | (i) childjob:ctl_raw_planted |
| `child/ctl_raw_random.meta.json` | (v) childjob:ctl_raw_random |
| `child/ctl_raw_random.spec.json` | (ii) childjob:ctl_raw_random |
| `child/ctl_raw_random.stderr` | (i) childjob:ctl_raw_random |
| `child/ctl_raw_random.stdout` | (i) childjob:ctl_raw_random |
| `child/ctl_torsion_S3_norm.meta.json` | (v) childjob:ctl_torsion_S3_norm |
| `child/ctl_torsion_S3_norm.npz` | (v) childjob:ctl_torsion_S3_norm |
| `child/ctl_torsion_S3_norm.spec.json` | (ii) childjob:ctl_torsion_S3_norm |
| `child/ctl_torsion_S3_norm.stderr` | (i) childjob:ctl_torsion_S3_norm |
| `child/ctl_torsion_S3_norm.stdout` | (i) childjob:ctl_torsion_S3_norm |
| `child/ctl_torsion_S3_rq.meta.json` | (v) childjob:ctl_torsion_S3_rq |
| `child/ctl_torsion_S3_rq.npz` | (v) childjob:ctl_torsion_S3_rq |
| `child/ctl_torsion_S3_rq.spec.json` | (ii) childjob:ctl_torsion_S3_rq |
| `child/ctl_torsion_S3_rq.stderr` | (i) childjob:ctl_torsion_S3_rq |
| `child/ctl_torsion_S3_rq.stdout` | (i) childjob:ctl_torsion_S3_rq |
| `solver/ctl_identity_planted.ms` | (ii) msolve:solver/ctl_identity_planted |
| `solver/ctl_identity_planted.ms.err` | (i) msolve:solver/ctl_identity_planted |
| `solver/ctl_identity_planted.ms.log` | (i) msolve:solver/ctl_identity_planted |
| `solver/ctl_identity_planted.ms.out` | (ii) msolve:solver/ctl_identity_planted |
| `solver/ctl_identity_random.ms` | (ii) msolve:solver/ctl_identity_random |
| `solver/ctl_identity_random.ms.err` | (i) msolve:solver/ctl_identity_random |
| `solver/ctl_identity_random.ms.log` | (i) msolve:solver/ctl_identity_random |
| `solver/ctl_identity_random.ms.out` | (ii) msolve:solver/ctl_identity_random |
| `solver/ctl_planted_S3.ms` | (ii) msolve:solver/ctl_planted_S3 |
| `solver/ctl_planted_S3.ms.err` | (i) msolve:solver/ctl_planted_S3 |
| `solver/ctl_planted_S3.ms.log` | (i) msolve:solver/ctl_planted_S3 |
| `solver/ctl_planted_S3.ms.out` | (ii) msolve:solver/ctl_planted_S3 |
| `solver/ctl_planted_S3_rescaled.ms` | (ii) msolve:solver/ctl_planted_S3_rescaled |
| `solver/ctl_planted_S3_rescaled.ms.err` | (i) msolve:solver/ctl_planted_S3_rescaled |
| `solver/ctl_planted_S3_rescaled.ms.log` | (i) msolve:solver/ctl_planted_S3_rescaled |
| `solver/ctl_planted_S3_rescaled.ms.out` | (ii) msolve:solver/ctl_planted_S3_rescaled |
| `solver/ctl_planted_torsion_S3_norm.ms` | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| `solver/ctl_planted_torsion_S3_norm.ms.err` | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| `solver/ctl_planted_torsion_S3_norm.ms.log` | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| `solver/ctl_planted_torsion_S3_norm.ms.out` | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| `solver/ctl_planted_torsion_S3_rq.ms` | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| `solver/ctl_planted_torsion_S3_rq.ms.err` | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| `solver/ctl_planted_torsion_S3_rq.ms.log` | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| `solver/ctl_planted_torsion_S3_rq.ms.out` | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| `solver/ctl_rawx_planted.ms` | (ii) msolve:solver/ctl_rawx_planted |
| `solver/ctl_rawx_planted.ms.err` | (i) msolve:solver/ctl_rawx_planted |
| `solver/ctl_rawx_planted.ms.log` | (i) msolve:solver/ctl_rawx_planted |
| `solver/ctl_rawx_planted.ms.out` | (ii) msolve:solver/ctl_rawx_planted |
| `solver/ctl_rawx_random.ms` | (ii) msolve:solver/ctl_rawx_random |
| `solver/ctl_rawx_random.ms.err` | (i) msolve:solver/ctl_rawx_random |
| `solver/ctl_rawx_random.ms.log` | (i) msolve:solver/ctl_rawx_random |
| `solver/ctl_rawx_random.ms.out` | (ii) msolve:solver/ctl_rawx_random |

### BJ-2 (2) count table: every (site, tag) and site count RI-1 (a) evaluates (reconstructed)

#### RUN-GFPN-f6a21a

| site | tag | N launch records | RB-1 attempt records | RL-2 pass-through records | SE-3/HR-3 event | (i) holds | source of the RB-1 / RL-2 count |
|---|---|---|---|---|---|---|---|
| S-1 | `fx_fresh1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |

| site | launch records at <dir>/<tag>.ms.log | r3 site counters | (iii) holds |
|---|---|---|---|
| S-1 | 36 | {"attempts_total": 36, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 36} | True |
| S-2 | 0 | {"attempts_total": 0, "wrapped_calls": 0} | True |

Events: 0 (no SE-3 / HR-3 event recorded; (ii) not evaluable). (b): other stdout paths carried by more than one reconstructed record: none. Callgrind, an independent count RI-1 does NOT read: {"S3_callgrind_children_observed": 36, "S3_records_in_r3_solver_events": 36, "callgrind_records_reconstructed": 36, "per_tag_equal": true}. Mismatches: none.

#### RUN-GFPN-902222

| site | tag | N launch records | RB-1 attempt records | RL-2 pass-through records | SE-3/HR-3 event | (i) holds | source of the RB-1 / RL-2 count |
|---|---|---|---|---|---|---|---|
| S-1 | `fx_fresh1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_fresh2_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted0_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_planted1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg0_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_S3` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_S3_rescaled` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_raw_u` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_raw_x` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |
| S-1 | `fx_reg1_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | raw-result.json solver argv (-P 1) |

| site | launch records at <dir>/<tag>.ms.log | r3 site counters | (iii) holds |
|---|---|---|---|
| S-1 | 36 | {"attempts_total": 36, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 36} | True |
| S-2 | 0 | {"attempts_total": 0, "wrapped_calls": 0} | True |

Events: 0 (no SE-3 / HR-3 event recorded; (ii) not evaluable). (b): other stdout paths carried by more than one reconstructed record: none. Callgrind, an independent count RI-1 does NOT read: {"S3_callgrind_children_observed": 36, "S3_records_in_r3_solver_events": 36, "callgrind_records_reconstructed": 36, "per_tag_equal": true}. Mismatches: none.

#### RUN-GFPN-f5412a

| site | tag | N launch records | RB-1 attempt records | RL-2 pass-through records | SE-3/HR-3 event | (i) holds | source of the RB-1 / RL-2 count |
|---|---|---|---|---|---|---|---|
| S-1 | `anchor_comparator_random` | 1 | 0 | 1 | 0 | True | raw-result.json solver argv (-g 1) |
| S-1 | `anchor_comparator_system` | 1 | 0 | 1 | 0 | True | frozen call site v2_driver.py 711 (gb_only=True) |
| S-1 | `anchor_v2_t0` | 1 | 0 | 1 | 0 | True | raw-result.json solver argv (-g 1) |
| S-1 | `anchor_v2_t1` | 1 | 0 | 1 | 0 | True | raw-result.json solver argv (-g 1) |
| S-1 | `anchor_v2_t2` | 1 | 0 | 1 | 0 | True | raw-result.json solver argv (-g 1) |

| site | launch records at <dir>/<tag>.ms.log | r3 site counters | (iii) holds |
|---|---|---|---|
| S-1 | 5 | {"attempts_total": 0, "passthrough_calls_gb_only_true": 5, "wrapped_calls": 0} | True |
| S-2 | 0 | {"attempts_total": 0, "wrapped_calls": 0} | True |

Events: 0 (no SE-3 / HR-3 event recorded; (ii) not evaluable). (b): other stdout paths carried by more than one reconstructed record: none. Callgrind, an independent count RI-1 does NOT read: {"S3_callgrind_children_observed": 0, "S3_records_in_r3_solver_events": 0, "callgrind_records_reconstructed": 0, "per_tag_equal": true}. Mismatches: none.

#### RUN-GFPN-bfe956

| site | tag | N launch records | RB-1 attempt records | RL-2 pass-through records | SE-3/HR-3 event | (i) holds | source of the RB-1 / RL-2 count |
|---|---|---|---|---|---|---|---|
| S-1 | `ctl_identity_planted` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_identity_random` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_planted_S3` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_planted_S3_rescaled` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_planted_torsion_S3_norm` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_planted_torsion_S3_rq` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_rawx_planted` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |
| S-1 | `ctl_rawx_random` | 1 | 1 | 0 | 0 | True | frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False) |

| site | launch records at <dir>/<tag>.ms.log | r3 site counters | (iii) holds |
|---|---|---|---|
| S-1 | 8 | {"attempts_total": 8, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 8} | True |
| S-2 | 0 | {"attempts_total": 0, "wrapped_calls": 0} | True |

Events: 0 (no SE-3 / HR-3 event recorded; (ii) not evaluable). (b): other stdout paths carried by more than one reconstructed record: none. Callgrind, an independent count RI-1 does NOT read: {"S3_callgrind_children_observed": 0, "S3_records_in_r3_solver_events": 0, "callgrind_records_reconstructed": 0, "per_tag_equal": true}. Mismatches: none.

## Appendix: computation scripts and outputs, verbatim

Every script below ran in this review's scratch directory (`<scratch>/rt_be2daf/`, outside the repository). Each is reproduced verbatim with its sha256, size and argv. rteval_v1.out (sha256 given in the attestation) is not reproduced: its lines 1-544 equal rteval_v2.out lines 1-544 (checked by a one-line Python comparison, section 13.4 of this report), and its remaining line is the file-writing message.

### `pkgread.py`

- sha256: `ea817d16e0e12caaf5a50e9e5f10a7e14fb4b3dc097cf1c5d95bda84190c8a3e`
- bytes: 3620; lines: 90
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread.py pkgread.json > pkgread.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: O_NOATIME listing of the four archived r3 gate packages and read-only reads of solver-events.json, raw-result.json, command.txt and the child/*.spec.json files (lstat before / after)

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf scratch (zero runs). Lists the four archived r3 gate packages and reads, READ-ONLY and with
# O_NOATIME, exactly these files of each: solver-events.json, raw-result.json, command.txt, and every
# child/*.spec.json (for RH-1 (v)'s "out"). Every directory and every file read is lstat'ed before and after;
# the script reports any difference (none may occur). Imports only json, os, sys, hashlib. Imports nothing from
# the repository. Writes ONE JSON file (argv[1]) in the scratch directory.
import hashlib
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
RUNS = REPO + "/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
FL = os.O_RDONLY | getattr(os, "O_NOATIME", 0)


def st(p):
    s = os.lstat(p)
    return [s.st_mode, s.st_size, s.st_atime_ns, s.st_mtime_ns, s.st_ctime_ns]


def listdir(path, rel, out, stats):
    stats[path] = st(path)
    fd = os.open(path, FL | os.O_DIRECTORY)
    try:
        ents = sorted(os.scandir(fd), key=lambda e: e.name)
        for e in ents:
            r = (rel + "/" + e.name) if rel else e.name
            s = e.stat(follow_symlinks=False)
            if e.is_dir(follow_symlinks=False):
                out.append({"path": r + "/", "type": "dir"})
                listdir(os.path.join(path, e.name), r, out, stats)
            else:
                out.append({"path": r, "type": "file" if e.is_file(follow_symlinks=False) else "other", "size": s.st_size})
    finally:
        os.close(fd)


def readbytes(p, stats):
    stats[p] = st(p)
    fd = os.open(p, FL)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    return b"".join(chunks)


res = {"packages": {}, "o_noatime": hasattr(os, "O_NOATIME")}
before = {}
for pk in PKGS:
    rd = RUNS + "/" + pk
    ents = []
    listdir(rd, "", ents, before)
    files = {}
    for name in ("solver-events.json", "raw-result.json", "command.txt"):
        p = rd + "/" + name
        if os.path.exists(p):
            b = readbytes(p, before)
            files[name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
            if name.endswith(".json"):
                files[name]["json"] = json.loads(b.decode())
            else:
                files[name]["text"] = b.decode(errors="replace")
    specs = {}
    for e in ents:
        if e["type"] == "file" and e["path"].startswith("child/") and e["path"].endswith(".spec.json"):
            b = readbytes(rd + "/" + e["path"], before)
            try:
                specs[e["path"]] = {"parses": True, "json": json.loads(b.decode()), "sha256": hashlib.sha256(b).hexdigest()}
            except Exception as ex:                      # noqa: BLE001
                specs[e["path"]] = {"parses": False, "error": repr(ex)}
    res["packages"][pk] = {"entries": ents, "files": files, "specs": specs}
after = {p: st(p) for p in before}
diff = [p for p in before if before[p] != after[p]]
res["lstat_checked"] = len(before)
res["lstat_changed"] = diff
with open(sys.argv[1], "w") as fh:
    json.dump(res, fh, indent=1, sort_keys=True)
print("o_noatime", res["o_noatime"], "lstat_checked", len(before), "lstat_changed", len(diff))
for pk in PKGS:
    P = res["packages"][pk]
    print(pk, "entries", len(P["entries"]), "files", sum(1 for e in P["entries"] if e["type"] == "file"),
          "specs", len(P["specs"]), {k: (v["sha256"], v["bytes"]) for k, v in P["files"].items()})
````

### `pkgread.out`

- sha256: `5004bbb36a66601058e41b3e466274afa072482078885c325c573f5652cad200`
- bytes: 1377; lines: 5
- argv: `(stdout of pkgread.py)`
- role: its printed summary; pkgread.json (the data) is kept in scratch, hash in the attestation

````text
o_noatime True lstat_checked 77 lstat_changed 0
RUN-GFPN-f6a21a entries 341 files 337 specs 16 {'solver-events.json': ('32aea434aabf91a8db4826ca238a405c97526707831bf70080e1b152d5f3595d', 61284), 'raw-result.json': ('f6f54870a5b6370ca6c527b528ebb18936fd19f96da3298af4bc9622d1219dc5', 225793), 'command.txt': ('75b5449ec50ec26a2defdb1f193f18d5c2929e738051da7fe1855d12c01b78f8', 457)}
RUN-GFPN-902222 entries 323 files 319 specs 16 {'solver-events.json': ('a23e30b6b84a99605698ee697d3e33ebd6b06bbd678f5bca02b115ab38b7d759', 61284), 'raw-result.json': ('3f9f575b8eea88bda8e8385b5683392fb7fbc7cf8d0009bdd2052fa3e3b9e8a4', 218967), 'command.txt': ('22162d41dc0e787144c021708bd6f9dd9930306e9e33d743d52168fde77cd4a8', 461)}
RUN-GFPN-f5412a entries 48 files 43 specs 1 {'solver-events.json': ('b927b44f1ed584a0d39d10c0bc898493620e93678efc3ffb81f82914c5cd3162', 2544), 'raw-result.json': ('af5d5d2f375d384912e375e704fda0d397c07e94dbc8147614eb7cdff8879290', 21225), 'command.txt': ('25d86fc12fc6bc3c90b53dfa5e33608b00860d291786fe023b998affb9caef9a', 456)}
RUN-GFPN-bfe956 entries 105 files 101 specs 11 {'solver-events.json': ('1b09e5a19ec54ba1541f6d8dcbcb4060a5080c43b1ef20027d3d4f3a88803511', 2544), 'raw-result.json': ('5b1ccdd41ce9dbc04e441750b8dfd92b1a5c5ec7398c02f6e2e1b73929a49c85', 12386), 'command.txt': ('039efb514c47747b1d4845ac82811120a3cb1e7f7ccd64766fd059916cf1824e', 449)}
````

### `scan.py`

- sha256: `10b643f94618d9bc84263a0b316662590eb3f8290a3818f38a6327d2815d676e`
- bytes: 7062; lines: 135
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan.py scan.json > scan.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: ast scan of the three implementation trees (run_child / solve / run_system definitions, references and call sites; dis of v2_solver.py line 181), under an audit-hook guard

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf scratch (zero runs). STATIC scan of the SOURCE TEXT of implementation-v2/, implementation-v2-a1/
# and implementation-v2-r3/ with ast (text parsed in this process; nothing imported, nothing executed). An audit hook
# refuses any import of a scanned module name and any process launch (defence in depth; counts printed).
# Imports only ast, os, sys, json, collections. Writes JSON to argv[1] (scratch) and a summary to stdout.
import ast
import collections
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
TREES = ["implementation-v2", "implementation-v2-a1", "implementation-v2-r3"]
FILES = []
for t in TREES:
    d = os.path.join(EXP, t)
    for name in sorted(os.listdir(d)):
        if name.endswith(".py"):
            FILES.append(os.path.join(d, name))
SCANNED = {os.path.basename(f)[:-3] for f in FILES}
GUARD = {"import_refused": 0, "launch_refused": 0}


def hook(event, args):
    if event == "import" and args and str(args[0]).split(".")[0] in SCANNED:
        GUARD["import_refused"] += 1
        raise RuntimeError("guard: import of scanned module %s refused" % args[0])
    if event in ("os.fork", "os.forkpty", "os.exec", "os.posix_spawn", "os.spawn", "os.system", "subprocess.Popen"):
        GUARD["launch_refused"] += 1
        raise RuntimeError("guard: process launch refused (%s)" % event)


sys.addaudithook(hook)

NAMES = {"run_child", "_run_child_locked", "solve", "run_system", "child_job", "build_poly", "raw_grid",
         "callgrind_instructions", "curve_facts", "run", "_bounded", "_write", "_rename"}
out = {"files": [os.path.relpath(f, REPO) for f in FILES], "defs": [], "refs": [], "import_from": [], "module_level_capture": [],
       "default_arg_capture": [], "calls": [], "events_file_mentions": [], "counter_mentions": []}
KEYS = ("attempts_total", "passthrough_calls_gb_only_true", "renamed_files", "accepted_attempt", "wrapped_calls",
        "launch_records", "passthrough_records", "events", "attempts")


def dotted(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        b = dotted(n.value)
        return (b + "." if b else "") + n.attr
    return None


for f in FILES:
    rel = os.path.relpath(f, REPO)
    src = open(f).read()
    tree = ast.parse(src, filename=rel)
    parents = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parents[ch] = node
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in NAMES:
            out["defs"].append({"file": rel, "name": node.name, "line": node.lineno})
            for dflt in list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]:
                for sub in ast.walk(dflt):
                    if isinstance(sub, (ast.Name, ast.Attribute)) and (dotted(sub) or "").split(".")[-1] in NAMES:
                        out["default_arg_capture"].append({"file": rel, "func": node.name, "line": sub.lineno, "ref": dotted(sub)})
        if isinstance(node, ast.ImportFrom) and node.module in ("v2_solver", "v2_driver", "a1_health", "a1_pari", "r3_resolve"):
            out["import_from"].append({"file": rel, "line": node.lineno, "module": node.module, "names": [a.name for a in node.names]})
        if isinstance(node, (ast.Name, ast.Attribute)):
            nm = dotted(node)
            last = (nm or "").split(".")[-1]
            if last in ("run_child", "_run_child_locked", "solve", "run_system"):
                par = parents.get(node)
                role = "call" if isinstance(par, ast.Call) and par.func is node else (
                    "store" if isinstance(getattr(node, "ctx", None), ast.Store) else "load_other")
                # enclosing function
                p, fn = node, None
                while p in parents:
                    p = parents[p]
                    if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn = p.name
                        break
                out["refs"].append({"file": rel, "line": node.lineno, "ref": nm, "role": role, "enclosing": fn})
                if fn is None and role != "call":
                    out["module_level_capture"].append({"file": rel, "line": node.lineno, "ref": nm, "role": role})
        if isinstance(node, ast.Call):
            nm = dotted(node.func) or ""
            last = nm.split(".")[-1]
            if last in ("solve", "run_system", "child_job", "build_poly", "raw_grid", "callgrind_instructions", "curve_facts", "run_child"):
                kws = {k.arg: (ast.unparse(k.value) if hasattr(ast, "unparse") else "?") for k in node.keywords if k.arg}
                args = [ast.unparse(a) for a in node.args] if hasattr(ast, "unparse") else []
                out["calls"].append({"file": rel, "line": node.lineno, "func": nm, "args": args, "kwargs": kws})
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "solver-events" in node.value:
                out["events_file_mentions"].append({"file": rel, "line": node.lineno, "text": node.value[:80]})
            if node.value in KEYS:
                out["counter_mentions"].append({"file": rel, "line": node.lineno, "key": node.value})
        if isinstance(node, ast.Name) and node.id == "EVENTS_FILE":
            out["events_file_mentions"].append({"file": rel, "line": node.lineno, "text": "EVENTS_FILE"})
        if isinstance(node, ast.Attribute) and node.attr == "EVENTS_FILE":
            out["events_file_mentions"].append({"file": rel, "line": node.lineno, "text": dotted(node)})

# dis of v2_solver.py's TEXT compiled here (never imported): what follows the os.fork call at line 181
import dis                                                  # noqa: E402
vs = EXP + "/implementation-v2/v2_solver.py"
code = compile(open(vs).read(), vs, "exec")
fork_seq = []


def walk_code(co):
    for c in co.co_consts:
        if hasattr(c, "co_code"):
            walk_code(c)
    if co.co_name == "_run_child_locked":
        ins = list(dis.get_instructions(co))
        for i, x in enumerate(ins):
            if x.positions and x.positions.lineno == 181:
                fork_seq.append("%s %s" % (x.opname, x.argrepr))


walk_code(code)
out["dis_v2_solver_line_181"] = fork_seq
out["guard"] = GUARD
with open(sys.argv[1], "w") as fh:
    json.dump(out, fh, indent=1)
print("files", len(FILES), "guard", GUARD)
print("defs:", [(d["file"].split("/")[-1], d["name"], d["line"]) for d in out["defs"] if d["name"] in ("run_child", "_run_child_locked", "solve", "run_system", "child_job", "_bounded", "_write", "_rename")])
print("import_from:", out["import_from"])
print("module_level_capture:", out["module_level_capture"])
print("default_arg_capture:", out["default_arg_capture"])
print("dis 181:", fork_seq)
rc = collections.Counter((r["file"].split("/")[-1], r["ref"], r["role"]) for r in out["refs"])
for k, v in sorted(rc.items()):
    print("ref", k, v)
````

### `scan.out`

- sha256: `97956ff9a4635eb58142c526d3c70b037128684e052bbcf72243e2a864c01d8e`
- bytes: 1698; lines: 23
- argv: `(stdout of scan.py)`
- role: its output

````text
files 38 guard {'import_refused': 0, 'launch_refused': 0}
defs: [('v2_driver.py', 'child_job', 92), ('v2_driver.py', 'solve', 158), ('v2_solver.py', 'run_child', 149), ('v2_solver.py', '_run_child_locked', 177), ('a1_health.py', 'run_system', 140), ('r3_resolve.py', '_write', 153), ('r3_resolve.py', '_rename', 224), ('r3_resolve.py', '_bounded', 248), ('r3_resolve.py', 'solve', 373), ('r3_resolve.py', 'run_system', 397)]
import_from: []
module_level_capture: [{'file': 'experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py', 'line': 393, 'ref': 'solve', 'role': 'load_other'}, {'file': 'experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py', 'line': 412, 'ref': 'run_system', 'role': 'load_other'}]
default_arg_capture: []
dis 181: ['LOAD_GLOBAL NULL + os', 'LOAD_ATTR fork', 'PRECALL ', 'CALL ', 'STORE_FAST pid']
ref ('a1_driver.py', 'D.solve', 'call') 1
ref ('a1_health.py', 'V.run_child', 'call') 1
ref ('a1_health.py', 'run_system', 'call') 4
ref ('a1_pari.py', 'V.run_child', 'call') 1
ref ('r3_devchecks.py', 'V.run_child', 'call') 1
ref ('r3_devchecks_more.py', 'V.run_child', 'call') 1
ref ('r3_resolve.py', 'a1_health_module.run_system', 'load_other') 1
ref ('r3_resolve.py', 'a1_health_module.run_system', 'store') 1
ref ('r3_resolve.py', 'run_system', 'load_other') 5
ref ('r3_resolve.py', 'solve', 'load_other') 5
ref ('r3_resolve.py', 'v2_driver_module.solve', 'load_other') 1
ref ('r3_resolve.py', 'v2_driver_module.solve', 'store') 1
ref ('v2_arms.py', 'Msq.solve', 'call') 1
ref ('v2_driver.py', 'V.run_child', 'call') 3
ref ('v2_driver.py', 'solve', 'call') 8
ref ('v2_solver.py', '_run_child_locked', 'call') 1
ref ('v2_solver.py', 'run_child', 'call') 1
````

### `scan2.py`

- sha256: `0db70c769a075189d36aef8f1fdc310ae35741e998185ddc479df8f4e7b66eab`
- bytes: 4498; lines: 87
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan2.py scan2.json /nonexistent-dir-for-B > scan2.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: ast scan for process-ending, exec, spawn and hook calls (BJ-1 (5)); part B deliberately given no directory

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf scratch (zero runs). BJ-1 (5): re-examine the residuals X1, X6b, X10 against the r3 base.
# (A) ast over the SOURCE TEXT of implementation-v2/, -v2-a1/, -v2-r3/ (nothing imported): every call of os._exit,
#     sys.exit / exit / quit, raise SystemExit(...), os.exec*, os.spawn*, os.posix_spawn*, os.system, os.popen,
#     subprocess.*, os.fork / os.forkpty, os.register_at_fork, signal.signal, atexit.register, threading.Thread /
#     multiprocessing, with file, line, enclosing function and the literal argument where there is one.
# (B) TEXT ONLY of the installed PyYAML package (argv[2], a directory of .py files): the same call names by regular
#     expression, with file, line and the text. PyYAML is not imported by this script.
# An audit hook refuses imports of scanned module names and every process launch. Imports only ast, os, re, sys, json.
import ast
import json
import os
import re
import sys

EXP = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43"
TREES = ["implementation-v2", "implementation-v2-a1", "implementation-v2-r3"]
FILES = [os.path.join(EXP, t, n) for t in TREES for n in sorted(os.listdir(os.path.join(EXP, t))) if n.endswith(".py")]
SCANNED = {os.path.basename(f)[:-3] for f in FILES} | {"yaml", "_yaml"}
G = {"import_refused": 0, "launch_refused": 0}


def hook(ev, args):
    if ev == "import" and args and str(args[0]).split(".")[0] in SCANNED:
        G["import_refused"] += 1
        raise RuntimeError("guard: import refused %s" % args[0])
    if ev in ("os.fork", "os.forkpty", "os.exec", "os.posix_spawn", "os.spawn", "os.system", "subprocess.Popen"):
        G["launch_refused"] += 1
        raise RuntimeError("guard: launch refused")


sys.addaudithook(hook)
NAMES = re.compile(r"^(os\._exit|sys\.exit|exit|quit|os\.exec\w*|os\.spawn\w*|os\.posix_spawn\w*|os\.system|os\.popen|subprocess\.\w+|"
                   r"os\.fork|os\.forkpty|os\.register_at_fork|signal\.signal|atexit\.register|threading\.Thread|multiprocessing\.\w+)$")


def dotted(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        b = dotted(n.value)
        return (b + "." if b else "") + n.attr
    return None


out = {"A": [], "B": [], "guard": G}
for f in FILES:
    tree = ast.parse(open(f).read(), filename=f)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}

    def enclosing(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return n.name
        return "<module>"
    for n in ast.walk(tree):
        nm = None
        if isinstance(n, ast.Call):
            nm = dotted(n.func)
            if nm and NAMES.match(nm):
                arg = ast.unparse(n.args[0])[:60] if n.args else ""
                out["A"].append({"file": os.path.relpath(f, EXP), "line": n.lineno, "call": nm, "arg": arg, "in": enclosing(n)})
        if isinstance(n, ast.Raise) and n.exc is not None:
            e = n.exc
            en = dotted(e.func) if isinstance(e, ast.Call) else dotted(e)
            if en == "SystemExit":
                arg = ast.unparse(e.args[0])[:60] if isinstance(e, ast.Call) and e.args else ""
                out["A"].append({"file": os.path.relpath(f, EXP), "line": n.lineno, "call": "raise SystemExit", "arg": arg, "in": enclosing(n)})
ydir = sys.argv[2]
pat = re.compile(r"\b(os\._exit|sys\.exit|exit\(|quit\(|os\.exec|os\.spawn|posix_spawn|os\.system|os\.popen|subprocess|os\.fork|register_at_fork|signal\.signal|atexit|os\.kill|raise_signal|SystemExit)")
for dp, dn, fn in os.walk(ydir):
    dn.sort()
    for n in sorted(fn):
        if n.endswith(".py"):
            p = os.path.join(dp, n)
            for i, line in enumerate(open(p, errors="replace"), start=1):
                if pat.search(line):
                    out["B"].append({"file": os.path.relpath(p, ydir), "line": i, "text": line.strip()[:120]})
out["yaml_files"] = sorted(os.path.relpath(os.path.join(dp, n), ydir) for dp, dn, fn in os.walk(ydir) for n in fn if n.endswith(".py"))
with open(sys.argv[1], "w") as fh:
    json.dump(out, fh, indent=1)
print("guard", G, "A hits", len(out["A"]), "B hits", len(out["B"]), "yaml .py files", len(out["yaml_files"]))
for h in out["A"]:
    print("A %-40s %4d %-24s %-36s in %s" % (h["file"], h["line"], h["call"], h["arg"], h["in"]))
for h in out["B"]:
    print("B %-30s %4d %s" % (h["file"], h["line"], h["text"]))
````

### `scan2.out`

- sha256: `68c66c51f477031ed834cc60871c55789993f16cdd3a28c2b0cfa7f7f47d1924`
- bytes: 8844; lines: 69
- argv: `(stdout of scan2.py)`
- role: its output

````text
guard {'import_refused': 0, 'launch_refused': 0} A hits 68 B hits 0 yaml .py files 0
A implementation-v2/v2_check_run.py         114 sys.exit                 main(sys.argv[1])                    in <module>
A implementation-v2/v2_child.py              60 sys.exit                 96                                   in main
A implementation-v2/v2_child.py              69 sys.exit                 0                                    in main
A implementation-v2/v2_child.py              81 sys.exit                 0                                    in main
A implementation-v2/v2_common.py            100 raise SystemExit         'GFPN_RUN_DIR not set: launch through v2_run_wrapper.py' in run_dir
A implementation-v2/v2_common.py             59 subprocess.run           cmd                                  in sh
A implementation-v2/v2_run_wrapper.py        54 sys.exit                 2                                    in refuse
A implementation-v2/v2_run_wrapper.py       243 sys.exit                 main()                               in <module>
A implementation-v2/v2_run_wrapper.py       182 subprocess.run           cmd                                  in main
A implementation-v2/v2_run_wrapper.py        49 subprocess.run           ['git', '-C', C.REPO] + list(args)   in git
A implementation-v2/v2_solver.py            181 os.fork                                                       in _run_child_locked
A implementation-v2/v2_solver.py            208 os._exit                 99                                   in _run_child_locked
A implementation-v2/v2_solver.py            205 os.execv                 argv[0]                              in _run_child_locked
A implementation-v2/v2_solver.py            533 subprocess.run           ['callgrind_annotate', '--inclusive=yes', out] in callgrind_instructions
A implementation-v2/v2_solver.py            201 os._exit                 98                                   in _run_child_locked
A implementation-v2/v2_solver.py            204 os.execve                argv[0]                              in _run_child_locked
A implementation-v2/v2_solver.py            196 os._exit                 97                                   in _run_child_locked
A implementation-v2/v2_verify_independent.py  280 sys.exit                 1 if bad else 0                      in <module>
A implementation-v2-a1/a1_check_run.py      145 sys.exit                 main(sys.argv[1])                    in <module>
A implementation-v2-a1/a1_devchecks.py      433 raise SystemExit         'REFUSING: development outputs never go under experiments/' in main
A implementation-v2-a1/a1_devchecks.py      439 sys.exit                 main()                               in <module>
A implementation-v2-a1/a1_driver.py          52 raise SystemExit         "REFUSING: --p %s does not match the plan package's p %s" %  in _check_package_p
A implementation-v2-a1/a1_driver.py         224 raise SystemExit         "REFUSING: --p %s does not match the plan package's p %s" %  in cmd_build
A implementation-v2-a1/a1_driver.py         233 raise SystemExit         'REFUSING: arguments do not match the plan package' in cmd_cells
A implementation-v2-a1/a1_health.py         297 sys.exit                 main()                               in <module>
A implementation-v2-a1/a1_make_trial_plan.py   69 raise SystemExit         'only the 31-bit plan is implemented as a writer; the FB-1 p in main
A implementation-v2-a1/a1_pari.py           148 sys.exit                 0                                    in <module>
A implementation-v2-a1/a1_pari.py           121 subprocess.run           [GP, '--version-short']              in gp_version
A implementation-v2-a1/a1_run_wrapper.py    378 sys.exit                 main()                               in <module>
A implementation-v2-a1/a1_run_wrapper.py    303 subprocess.run           cmd                                  in main
A implementation-v2-a1/a1_run_wrapper.py     61 subprocess.run           ['git', '-C', REPO] + list(args)     in git
A implementation-v2-a1/a1_run_wrapper.py    372 subprocess.run           cmd                                  in V_sh
A implementation-v2-a1/a1_toy.py            334 subprocess.run           [sys.executable, '-B', shim]         in dev_a
A implementation-v2-r3/r3_check_run.py      372 subprocess.run           FROZEN_LAUNCHER + [mode, rd]         in main
A implementation-v2-r3/r3_check_run.py      417 sys.exit                 main(args[0], aj)                    in <module>
A implementation-v2-r3/r3_check_run.py      406 sys.exit                 r3_reg1.main(sys.argv[2:])           in <module>
A implementation-v2-r3/r3_check_run.py      408 sys.exit                 frozen_v2(sys.argv[2])               in <module>
A implementation-v2-r3/r3_check_run.py      410 sys.exit                 frozen_a1(sys.argv[2])               in <module>
A implementation-v2-r3/r3_devchecks.py      298 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_devchecks.py      205 subprocess.run           cmd                                  in run_worker
A implementation-v2-r3/r3_devchecks_more.py  278 subprocess.run           [sys.executable, '-B', os.path.join(HERE, 'r3_make_plans.py' in dv5
A implementation-v2-r3/r3_devchecks_more.py   93 subprocess.run           ['callgrind_annotate', '--version']  in dv1_static
A implementation-v2-r3/r3_devchecks_more.py  538 subprocess.run           [sys.executable, '-B', os.path.join(R.REPO, 'tools', 'alloca in dv10
A implementation-v2-r3/r3_devchecks_more.py  100 subprocess.run           ['dpkg-query', '-W', '-f=${Package} ${Version}\n', 'msolve', in dv1_static
A implementation-v2-r3/r3_devchecks_more.py  492 subprocess.run           ['git', '-C', R.REPO, 'status', '--porcelain', '--untracked- in dv9
A implementation-v2-r3/r3_devchecks_more.py  502 subprocess.run           ['git', '-C', R.REPO, 'rev-parse', 'HEAD'] in dv9
A implementation-v2-r3/r3_devchecks_more.py   96 subprocess.run           ['valgrind', '--version']            in dv1_static
A implementation-v2-r3/r3_devchecks_more.py   99 subprocess.run           ['gp', '--version-short']            in dv1_static
A implementation-v2-r3/r3_dv12.py           131 raise SystemExit         'REFUSING: %s exists (a case is run once; a re-run needs a r in run_cases
A implementation-v2-r3/r3_dv6.py            324 subprocess.run           [sys.executable, '-B', shim] + args  in dv6
A implementation-v2-r3/r3_dv7.py            434 raise SystemExit         'REFUSING: %s exists (DV-7 runs once; a re-run needs a recor in dv7
A implementation-v2-r3/r3_entry_a1.py       115 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_entry_v2.py        84 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_make_plans.py     141 raise SystemExit         'REFUSING: expected 42 distinct minted ids, 31 v2 and 11 v2- in inputs
A implementation-v2-r3/r3_make_plans.py     152 raise SystemExit         'REFUSING: M is not a bijection from the 42 frozen ids onto  in inputs
A implementation-v2-r3/r3_make_plans.py     154 raise SystemExit         'REFUSING: the r1 / r2 plan ids differ from the retirement l in inputs
A implementation-v2-r3/r3_make_plans.py     157 raise SystemExit         'REFUSING: retirement lists differ from the paristack PS-3 e in inputs
A implementation-v2-r3/r3_make_plans.py     333 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_make_plans.py     135 raise SystemExit         'REFUSING: %s sha256 %s != bound %s' % (path, got, want) in inputs
A implementation-v2-r3/r3_make_plans.py     295 raise SystemExit         'REFUSING: %s fails the RC-4 (c) equality (%s != %s)' % (nam in build
A implementation-v2-r3/r3_make_plans.py     297 raise SystemExit         'REFUSING: %s watchdogs differ from trial-plan-v2.json' % na in build
A implementation-v2-r3/r3_make_plans.py     299 raise SystemExit         'REFUSING: %s carries a forbidden task id' % name in build
A implementation-v2-r3/r3_make_plans.py     318 raise SystemExit         'REFUSING: %s exists; plans are written once' % path in main
A implementation-v2-r3/r3_reg1.py           352 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_run_wrapper.py    583 sys.exit                 main()                               in <module>
A implementation-v2-r3/r3_run_wrapper.py    477 subprocess.run           cmd                                  in launch
A implementation-v2-r3/r3_run_wrapper.py     73 subprocess.run           ['git', '-C', R.REPO] + list(args)   in git
A implementation-v2-r3/r3_run_wrapper.py    341 subprocess.run           cmd                                  in sh
````

### `rteval_v1.py`

- sha256: `f142a388c79d80353d295f36fac2c128fbea1ea8d47c2436ada7b04868d73272`
- bytes: 52488; lines: 1023
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 600 python3 -B rteval_v1.py > rteval_v1.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: evaluator version 1: the rule functions and the BJ-0 objects (a)-(f); edited once before its first run (weak-mode COUNT GAP for N = 0); no output existed before that edit

````text
#!/usr/bin/env python3
"""TASK-20260924-be2daf rule evaluator, version 1 (scratch; zero runs). ONE method, used UNCHANGED for BJ-0..BJ-3.

Imports only json, os, re, sys, itertools, collections. Reads one scratch file (pkgread.json: the O_NOATIME listings
and the archived solver-events.json / raw-result.json / spec files of the four r3 gate packages). Imports nothing from
the repository and no third-party module. Writes rteval_v1.json next to itself; prints its report on stdout.

TRUTH MODEL. A package is built by simulating, in order, the frozen launches of a command (v2_driver.py,
a1_health.py, a1_pari.py, v2_solver.py) and the r3 / r4 resolve layer (r3_resolve.py _bounded 248-319, solve 373-390,
run_system 397-409): files written (by whom), SE-3 / HR-3 events with attempts, accepted_attempt, renamed_files,
the site counters attempts_total (273) and passthrough_calls_gb_only_true (383), RB-1 attempt records (readbackcover
RB-1: one per attempt of every wrapped non-gb_only call at S-1 and every call at S-2), RL-2 pass-through records
(readbackfull RL-2: one per gb_only S-1 call), and RL-1 launch records (one per run_child call). A CONSTRUCTED
premise is applied afterwards (a record absent, a count altered); such a package is not "designed".

RULE SETS (package level):
  RK   readbackclose RK-1 / RK-3 (b) as worded (RL-3 gaps gate nothing: readbackfull RL-3).
  RF   failclosed as worded: RF-0 (b), RF-1 (a), RF-2, RF-3 (a); an RL-3 gap is a file of RL-3's globs (child/*.meta.json,
       solver/*.ms.log, health/, comparator/, pari/) whose writing launch has no launch record (readbackfull RL-3).
  RG   childend: RF with RG-1 (c)/(d) child_end, RG-2 (a)/(b), RG-4 (b) attribution; a gap FAILs.
  RH   gapattr: RG with RH-1 (i)-(vi) in place of RG-4 (b)'s sentence, RH-2 (a)/(b), RH-4.
  RI   attcount: RH with RI-1 (a)-(d) as worded (named COUNT / SITE COUNT / DUPLICATE-PATH gaps; (d) restriction).
  RIw  RI with RI-1 (a) WEAKENED to "N >= 1" (CRI-4 (e)); (b), (c), (d) as worded.
  RIx  RI with RI-1 (a) and (d) DISABLED (RI-3 (25)'s scratch evaluator); (b), (c) as worded.
The frozen checker items evaluated: v2_check_run.py 65-67 (collected read-back list empty) and 68-70 (a collected pair
!= requested cap). Requested cap variants: Mr (r3 base, r3_run_wrapper.py 550: raw envelope cap; None if the wrapper
wrote raw-result.json) and Mc (an r4 wrapper recording the requested cap independently). k = number of added other
class-B S-1 launches. The r4 checks other than the rule under test are taken as passing, except V-7 (valueclose VC-1
(e); r3_check_run.py 153-158) which fails iff solver-events.json was altered after the manifest recorded its sha256.

DEFINITIONS (failclosed 604-621) on TRUTH: FAIL-OPEN iff PASS / PASS_ZL while (i) a pair the parent read is in no
launch record; (ii) a child that may have executed argv (created, and its launch record not class A or C -- an
ABSENT record is not class A or C) has no recorded pair equal to the cap [LR: in a launch record; ANY: in any RB-2 /
RL-3 source]; (iii) a created child recorded child_created false; (iv) a record written in another process goes
undetected (read LITERALLY); (v) the outcome is wrapper-recorded. PLANNED-BASIS REFUSAL iff a driver-logic outcome
(as the rule set reads RF-0 (b)) acted on by a dependant's frozen logic (basis) or enumerated by RFR-2 (row),
designed, receives FAIL.
"""
import collections
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "/usr/local/bin/python3"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}                 # childend RG-1 (c)
REN = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
DIR_OF = {"msolve": "solver", "health": "health", "childjob": "child", "callgrind": "solver", "comparator": "comparator", "gp": "pari"}
SITE_OF_DIR = {"solver": "S-1", "health": "S-2"}
OUT = {}
LINES = []


def P(*a):
    s = " ".join(str(x) for x in a)
    LINES.append(s)
    print(s)


# =============================================================================================== truth: launches
def L(lid, kind, tag, **kw):
    d = dict(lid=lid, kind=kind, tag=tag, dirn=DIR_OF[kind], gb=False, created=True, opened=True, p227=True, pair=CP,
             exec_=True, report="OK", rc=0, raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False,
             foreign_write=None, callback="normal", fired=None, new_pids=None, t_en=None, value=None, outcome="ok",
             job="build", cached=False, partial_npz=False, cg_out_left=False, retained=True, in_raw=True, recorded=True)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if not d["created"]:
        d["opened"] = False
    return d


def paths(l, rd):
    t, dn, k = l["tag"], rd + "/" + l["dirn"], l["kind"]
    if k in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"] +
                (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if k == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2", "-t",
                 "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if k == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if k == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if k == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(k)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch: rel -> (writer, note)."""
    t, dn, k, me = l["tag"], l["dirn"], l["kind"], l["lid"]
    f = {}
    op = l["created"] and l["opened"]                                  # the fork child opened stdout/stderr (v2_solver 188-189)
    if k in ("msolve", "health"):
        if l["retained"] or k == "health":
            f[dn + "/" + t + ".ms"] = ("driver", "v2_driver 161-162 / a1_health 141-143")
        if op:
            f[dn + "/" + t + ".ms.log"] = (me, "stdout")
            f[dn + "/" + t + ".ms.err"] = (me, "stderr")
        if l["exec_"] and l["outcome"] in ("ok", "ssf", "positive_dimensional", "degenerate_parametrisation"):
            f[dn + "/" + t + ".ms.out"] = (me, "-o")
    elif k == "childjob":
        f[dn + "/" + t + ".spec.json"] = ("driver", "v2_driver 98-99")
        if op:
            f[dn + "/" + t + ".stdout"] = (me, "stdout")
            f[dn + "/" + t + ".stderr"] = (me, "stderr")
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f[dn + "/" + t + ".npz"] = (me, "v2_child 38")
                    f[dn + "/" + t + ".meta.json"] = (me, "v2_child 41")
                else:
                    f[dn + "/" + t + ".meta.json"] = (me, "v2_child 104 (.npz removed v2_driver 144)")
            elif l["outcome"] == "refused_meta":
                f[dn + "/" + t + ".meta.json"] = (me, "v2_child 68/80")
            elif l["partial_npz"]:
                f[dn + "/" + t + ".npz"] = (me, "partial")
    elif k == "callgrind":
        if op:
            f[dn + "/" + t + ".callgrind.stdout"] = (me, "stdout")
            f[dn + "/" + t + ".callgrind.stderr"] = (me, "stderr")
        if l["cg_out_left"]:
            f[dn + "/" + t + ".callgrind.out"] = (me, "left by v2_solver 521-524 path")
    elif k == "comparator":
        if op:
            f[dn + "/stdout.log"] = (me, "stdout")
            f[dn + "/stderr.log"] = (me, "stderr")
        if l["exec_"] and l["outcome"] == "ok":
            for x in ("anchor25_random.ms", "anchor25_planted.ms", "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json"):
                f[dn + "/" + x] = (me, "k4a 279-281, 318")
    elif k == "gp":
        f[dn + "/" + t + ".gp"] = ("driver", "a1_pari 91-93")
        if op:
            f[dn + "/" + t + ".gp.stdout"] = (me, "stdout")
            f[dn + "/" + t + ".gp.stderr"] = (me, "stderr")
    return f


# =============================================================================================== truth: packages
def build(kind, steps, raw="driver", gate=False, basis=None, row=None, rd=None, raw_pairs=True, extra_files=()):
    """steps: ("S1", [attempt launches]) a wrapped S-1 call (gb_only if its launches have gb); ("S2", [attempts]) a
    wrapped S-2 call; ("L", launch) an unwrapped launch. Every attempt but the last of a wrapped call is an SSF attempt:
    its three files are renamed '<name>.ssf-attempt<k>' and listed under the event's renamed_files['attempt<k>'].
    Returns the package (truth + records as the r4 layer writes them)."""
    rd = rd or RUNS + "/RUN-X"
    files, launches = {}, []
    events = []
    counters = {"S-1": {"attempts_total": 0, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 0}, "S-2": {"attempts_total": 0, "wrapped_calls": 0}}
    rb1, rl2 = [], []
    for st in steps:
        if st[0] == "L":
            l = st[1]
            launches.append(l)
            files.update(files_of(l))
            continue
        site, atts = ("S-1" if st[0] == "S1" else "S-2"), st[1]
        gb = site == "S-1" and atts[0]["gb"]
        if gb:
            counters["S-1"]["passthrough_calls_gb_only_true"] += 1
            l = atts[0]
            launches.append(l)
            files.update(files_of(l))
            rl2.append({"tag": l["tag"], "lid": l["lid"], "pair": l["pair"] if l["p227"] else None})
            continue
        counters[site]["wrapped_calls"] += 1
        ev = None
        n = len(atts)
        for k, l in enumerate(atts, start=1):
            l["attempt"] = k
            launches.append(l)
            files.update(files_of(l))
            counters[site]["attempts_total"] += 1
            rb1.append({"site": site, "tag": l["tag"], "k": k, "lid": l["lid"], "pair": l["pair"] if l["p227"] else None})
            if k < n:                                           # an SSF attempt followed by another attempt
                if ev is None:
                    ev = {"site": site, "dir": l["dirn"], "tag": l["tag"], "attempts": [], "renamed_files": {}}
                    events.append(ev)
                ren = {}
                for ext in (".ms.out", ".ms.log", ".ms.err"):
                    src = l["dirn"] + "/" + l["tag"] + ext
                    nm = os.path.basename(src) + ".ssf-attempt%d" % k
                    if src in files:
                        files[src + ".ssf-attempt%d" % k] = (files.pop(src)[0], "renamed r3_resolve 234")
                        ren[nm] = {"renamed": True}
                    else:
                        ren[nm] = {"absent": True}
                ev["renamed_files"]["attempt%d" % k] = ren
        if ev is not None:
            ev["attempts"] = [{"attempt": k} for k in range(1, n + 1)]
            ev["accepted_attempt"] = n
    for rel, w in extra_files:
        files[rel] = w
    for i, l in enumerate(launches):
        l["ordinal"] = i
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, rd=rd, rd_check=rd, files=files,
                events=events, counters=counters, rb1=rb1, rl2=rl2, raw_pairs=raw_pairs, designed=True, altered_after_manifest=False,
                dup=[], note=[])


def premise(pkg, drop=(), drop_rb1=(), drop_rl2=(), counter=None, drop_ren_keys=(), dup=(), event_edit=None, altered=False, note=None):
    """Apply a CONSTRUCTED premise: launch records absent (drop), RB-1 / RL-2 records absent, counter deltas, renamed_files
    keys removed, launch records duplicated, event fields edited. Returns a new package (deep copy)."""
    q = json.loads(json.dumps(pkg))
    for l in q["launches"]:
        if l["lid"] in drop:
            l["recorded"] = False
    q["rb1"] = [r for r in q["rb1"] if (r["site"], r["tag"], r["k"]) not in set(drop_rb1)]
    q["rl2"] = [r for r in q["rl2"] if r["tag"] not in set(drop_rl2)]
    for site, kv in (counter or {}).items():
        for k, v in kv.items():
            q["counters"][site][k] += v
    for (site, tag, key) in drop_ren_keys:
        for e in q["events"]:
            if e["site"] == site and e["tag"] == tag:
                e["renamed_files"].pop(key, None)
    q["dup"] = list(dup)
    if event_edit:
        for e in q["events"]:
            event_edit(e)
    if drop or drop_rb1 or drop_rl2 or counter or drop_ren_keys or dup or event_edit:
        q["designed"] = False
    q["altered_after_manifest"] = altered
    if note:
        q["note"] = q["note"] + [note]
    return q


# =============================================================================================== records as written
def child_created_rk(l):                                  # readbackclose RK-1 (a) / (b)
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def child_created_rf(l):                                  # failclosed RF-1 (a)
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):                                          # the pair the launch record carries (RK-1 (a)/(b), (c))
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return tuple(l["pair"]) if l["pair"] else None


def child_end(l, rs):                                     # childend RG-1 (c), with gapattr RH-4
    if rs in ("RH", "RI", "RIw", "RIx") and l["callback"] == "caught":
        return "undetermined"
    cc = child_created_rf(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):                                         # failclosed RF-3 (a) classes, childend RG-1 (d)
    cc = child_created_rk(l) if rs == "RK" else child_created_rf(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


def records(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = paths(l, pkg["rd"])
        r = {"id": l["lid"], "ordinal": l["ordinal"], "argv": argv, "stdout": so, "stderr": se, "kind": l["kind"], "tag": l["tag"],
             "child_end": child_end(l, rs) if rs not in ("RK", "RF") else None}
        out.append(r)
        if l["lid"] in pkg["dup"]:
            out.append(dict(r, id=l["lid"] + "#dup"))
    return out


def specs(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["kind"] == "childjob":
            rel = "child/" + l["tag"] + ".spec.json"
            if rel in pkg["files"]:
                sp[pkg["rd"] + "/" + rel] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"]}
    return sp


# =============================================================================================== layer 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 / 251)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93)"
    return None


def attr_rg4(rd, rel, recs):
    p = rd + "/" + rel
    names = collections.Counter(a for r in recs for a in set(r["argv"]))
    hits = []
    for r in recs:
        if p in (r["stdout"], r["stderr"]):
            hits.append((r["id"], "stdout/stderr"))
        if p in r["argv"]:
            hits.append((r["id"], "argv exact"))
        for a in r["argv"]:
            if p.startswith(a.rstrip("/") + "/") and names[a] == 1 and a.rstrip("/") in {rd + "/" + d for d in FIVE}:
                hits.append((r["id"], "argv directory"))
    return hits


def attr_rh1(rd, rel, recs, sp, events, restrict=None):
    """gapattr RH-1 (i)-(vi). restrict: RI-1 (d) -- {record id: 'last'|'earlier'} for records of an L(dir, tag) with
    N >= 2 and (a) holding: final files of that tag only to 'last' by (i)/(ii); an 'earlier' record attributes nothing by
    (i)/(ii) and, by (vi), only renamed files of its own attempt k (its position in L)."""
    p = rd + "/" + rel
    names = collections.Counter(a for r in recs for a in set(r["argv"]))
    hits = []
    for r in recs:
        role = (restrict or {}).get(r["id"])
        final_of = None
        if role:
            final_of = role[1]
        allow_i_ii = True
        if role and role[0] == "earlier":
            allow_i_ii = False
        if p in (r["stdout"], r["stderr"]) and allow_i_ii:
            hits.append((r["id"], "(i)"))
        if p in r["argv"] and allow_i_ii:
            hits.append((r["id"], "(ii)"))
        for a in r["argv"]:
            if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                hits.append((r["id"], "(iii)"))
            if a.rstrip("/") in {rd + "/" + d for d in FIVE} and p.startswith(a.rstrip("/") + "/") and names[a] == 1:
                hits.append((r["id"], "(iv)"))
        if r["child_end"] == "exec" and r["argv"]:
            m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
            if m:
                s = sp.get(r["argv"][-1])
                o = rd + "/child/" + m.group("tag")
                if isinstance(s, dict) and s.get("out") == o and p in (o + ".npz", o + ".meta.json"):
                    hits.append((r["id"], "(v)"))
    d, _, name = rel.partition("/")
    m = REN.fullmatch(name)
    if m and d in ("solver", "health"):
        tag, k = m.group("tag"), int(m.group("k"))
        ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
        same = sorted((r for r in recs if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["ordinal"])
        if ev and len(same) >= k:
            R = same[k - 1]
            role = (restrict or {}).get(R["id"])
            hits.append((R["id"], "(vi) k=%d" % k))
    if restrict:                                           # RI-1 (d): the final files of a restricted tag go only to its last record
        fin = None
        for rid, role in restrict.items():
            if role[0] == "last":
                t = role[1]
                if rel in ("%s.ms" % t, "%s.ms.out" % t, "%s.ms.log" % t, "%s.ms.err" % t):
                    fin = rid
        if fin is not None:
            hits = [h for h in hits if not (h[1] in ("(i)", "(ii)") and restrict.get(h[0], ("", ""))[0] != "last"
                                            and h[0] in restrict)]
    return hits


# =============================================================================================== RI-1 (a)-(d)
def ri1(pkg, recs, mode):
    """mode: 'worded' | 'weak' (a) := N >= 1 | 'off' ((a) and (d) disabled). Returns (named_gaps, gap_files, restrict)."""
    rd = pkg["rd_check"]
    named, gapfiles, restrict = [], set(), {}
    L_ = collections.defaultdict(list)
    for r in recs:
        for d in ("solver", "health"):
            m = re.fullmatch(re.escape(rd + "/" + d + "/") + r"(?P<tag>.+)\.ms\.log", r["stdout"])
            if m:
                L_[(d, m.group("tag"))].append(r)
    for k in L_:
        L_[k].sort(key=lambda r: r["ordinal"])
    rb1c = collections.Counter((SITE_OF_DIR_R[r["site"]], r["tag"]) for r in pkg["rb1"])
    rl2c = collections.Counter(("solver", r["tag"]) for r in pkg["rl2"])
    evs = collections.defaultdict(list)
    for e in pkg["events"]:
        evs[(e["dir"], e["tag"])].append(e)
    keys = set(L_) | set(rb1c) | set(rl2c) | set(evs)
    holds = {}
    for (d, t) in sorted(keys):
        N = len(L_.get((d, t), []))
        if mode == "off":
            holds[(d, t)] = None
            continue
        if mode == "weak":
            holds[(d, t)] = N >= 1
            if N < 1:
                named.append("COUNT GAP (%s/%s, N=0; weakened (a): N >= 1 fails)" % (d, t))
            continue
        reasons = []
        want = rb1c.get((d, t), 0) + (rl2c.get((d, t), 0) if d == "solver" else 0)
        if N != want:
            reasons.append("(i) N=%d != RB-1 %d + RL-2 %d" % (N, rb1c.get((d, t), 0), rl2c.get((d, t), 0) if d == "solver" else 0))
        es = evs.get((d, t), [])
        if es:
            if len(es) != 1:
                reasons.append("(ii) %d events" % len(es))
            else:
                e = es[0]
                na, acc, nr = len(e.get("attempts") or []), e.get("accepted_attempt"), 1 + len(e.get("renamed_files") or {})
                nums = [a.get("attempt") for a in (e.get("attempts") or [])]
                if not (N == na == acc == nr):
                    reasons.append("(ii) N=%d attempts=%d accepted=%s 1+renamed=%d" % (N, na, acc, nr))
                if nums != list(range(1, na + 1)):
                    reasons.append("(ii) attempt numbers %s" % nums)
        holds[(d, t)] = not reasons
        if reasons:
            named.append("COUNT GAP (%s/%s, N=%d): %s" % (d, t, N, "; ".join(reasons)))
            for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                if d + "/" + t + ext in pkg["files"]:
                    gapfiles.add(d + "/" + t + ext)
            for f in pkg["files"]:
                mm = REN.fullmatch(f.partition("/")[2])
                if f.startswith(d + "/") and mm and mm.group("tag") == t:
                    gapfiles.add(f)
    if mode == "worded":
        for d, site in (("solver", "S-1"), ("health", "S-2")):
            n = sum(len(v) for (dd, _t), v in L_.items() if dd == d)
            c = pkg["counters"][site]
            want = c["attempts_total"] + (c.get("passthrough_calls_gb_only_true", 0) if site == "S-1" else 0)
            if n != want:
                named.append("SITE COUNT GAP (%s): %d launch records vs counters %s" % (site, n, json.dumps(c, sort_keys=True)))
    # (b) one launch per other output path
    other = collections.defaultdict(list)
    for r in recs:
        if not any(re.fullmatch(re.escape(rd + "/" + d + "/") + r".+\.ms\.log", r["stdout"]) for d in ("solver", "health")):
            other[r["stdout"]].append(r)
    dup_ids = set()
    for so, rs_ in other.items():
        if len(rs_) > 1:
            named.append("DUPLICATE-PATH GAP (%s): ordinals %s" % (so.replace(rd + "/", ""), [r["ordinal"] for r in rs_]))
            dup_ids |= {r["id"] for r in rs_}
    # (d)
    if mode in ("worded", "weak"):
        for (d, t), rs_ in L_.items():
            if len(rs_) >= 2 and holds.get((d, t)):
                for i, r in enumerate(rs_):
                    restrict[r["id"]] = ("last" if i == len(rs_) - 1 else "earlier", d + "/" + t, i + 1)
    return named, gapfiles, restrict, dup_ids


SITE_OF_DIR_R = {"S-1": "solver", "S-2": "health"}


def gaps(pkg, rs):
    rd = pkg["rd_check"]
    rels = sorted(pkg["files"])
    if rs == "RK":
        return [], [], {}
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            if glob and w[0] != "driver" and w[0] not in recorded:
                g.append(rel)
        return sorted(g), [], {}
    recs = records(pkg, rs)
    if rs == "RG":
        att = {rel: attr_rg4(rd, rel, recs) or ([("-", nonlaunch(rel))] if nonlaunch(rel) else []) for rel in rels}
        return sorted(r for r, h in att.items() if not h), [], att
    sp = specs(pkg)
    named, gapfiles, restrict, dup_ids = ([], set(), {}, set())
    if rs in ("RI", "RIw", "RIx"):
        named, gapfiles, restrict, dup_ids = ri1(pkg, recs, {"RI": "worded", "RIw": "weak", "RIx": "off"}[rs])
    att = {}
    for rel in rels:
        h = attr_rh1(rd, rel, recs, sp, pkg["events"], restrict if restrict else None)
        if not h and nonlaunch(rel):
            h = [("-", nonlaunch(rel))]
        if dup_ids:
            h = [x for x in h if x[0] not in dup_ids]
        if rel in gapfiles:
            h = []
        att[rel] = h
    return sorted(r for r, h in att.items() if not h), named, att


# =============================================================================================== layer 2: verdicts
def collected_pairs(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(("launch record (RL-3 d)", rec_pair(l)))
        if l["kind"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"] and l["p227"]:
            ps.append(("meta (RB-2 b)", tuple(l["pair"])))
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(("raw (RB-2 a)", tuple(l["pair"])))
    for r in pkg["rb1"]:
        if r["pair"]:
            ps.append(("RB-1 attempt record (RB-2 c)", tuple(r["pair"])))
    for r in pkg["rl2"]:
        if r["pair"]:
            ps.append(("RL-2 pass-through (RL-3 e)", tuple(r["pair"])))
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = [p for _s, p in collected_pairs(pkg)]
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    childfile = any((r.startswith("child/") and r.endswith(".meta.json")) or (r.startswith("solver/") and r.endswith(".ms.log"))
                    or r.split("/")[0] in ("health", "comparator", "pari") for r in pkg["files"])
    v7 = not pkg["altered_after_manifest"]
    image = pkg["gate"]
    g, named, _att = gaps(pkg, rs)
    if rs == "RK":
        if not items and v7:
            return "PASS"
        if not image and not recs and not childfile and items == ["66-67"] and v7:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(child_created_rf(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs not in ("RF",):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    if (not items and v7 and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign and not g
            and not named and not undet):
        return "PASS"
    if (not image and not recs and not childfile and items == ["66-67"] and v7 and rw == "driver" and pkg["kind"] in ("cells_m5", "fixture4")
            and not foreign and not g and not named):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (child_created_rk(l) if rs == "RK" else child_created_rf(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and tuple(l["pair"] or ()) == CP and (
                any(r["lid"] == l["lid"] and r["pair"] for r in pkg["rb1"]) or any(r["lid"] == l["lid"] and r["pair"] for r in pkg["rl2"])
                or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["kind"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            det = (rs != "RK" and l["foreign_write"] == "ok") or (rs not in ("RK", "RF") and rec and child_end(l, rs) == "undetermined")
            if not det:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs not in ("RK", "RF") and infra_stop(pkg):
        return False
    if rs in ("RH", "RI", "RIw", "RIx") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (premise: absent)"
    cc = child_created_rk(l) if rs == "RK" else child_created_rf(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs not in ("RK", "RF"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii): a created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs not in ("RK", "RF") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant record in another process; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def with_k(pkg, k):
    if not k:
        return pkg
    q = json.loads(json.dumps(pkg))
    base = len(q["launches"])
    for j in range(k):
        l = L("otherB%d" % j, "msolve", "otherB_t%d" % j)
        l["ordinal"] = base + j
        l["attempt"] = 1
        q["launches"].insert(0, l)
        q["files"].update(files_of(l))
        q["counters"]["S-1"]["attempts_total"] += 1
        q["counters"]["S-1"]["wrapped_calls"] += 1
        q["rb1"].append({"site": "S-1", "tag": l["tag"], "k": 1, "lid": l["lid"], "pair": CP})
    for i, l in enumerate(q["launches"]):
        l["ordinal"] = i
    return q


def evaluate(key, label, pkg, rule_sets, ks=(0,), variants=("Mr", "Mc")):
    P("\n### %s: %s" % (key, label))
    for n in pkg.get("note") or []:
        P("  note: " + n)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-26s] %-3s %s" % (l["lid"][:26], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = with_k(pkg, k)
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g, named, _att = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row %s" % q["row"])))
            if rs not in ("RK", "RF") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RI", "RIw", "RIx") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if not q["altered_after_manifest"] is False:
                tags.append("V-7 fails (solver-events.json altered after the manifest)")
            if named:
                tags.append("NAMED %s" % named)
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-16s defs %-30s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var), "definitions": dfs,
                         "fail_open": fo, "planned_basis_refusal": pb, "gaps": g, "named": named})
    OUT[key] = {"label": label, "rows": rows}
    return rows


# ----------------------------------------------------------------------------------------------- helpers
def ms(lid, tag, **kw):
    return L(lid, "msolve", tag, **kw)


def hs(lid, tag, **kw):
    kw.setdefault("in_raw", False)
    return L(lid, "health", tag, **kw)


def cj(lid, tag, job="build", **kw):
    return L(lid, "childjob", tag, job=job, **kw)


def cg(lid, tag, **kw):
    return L(lid, "callgrind", tag, **kw)


def S1(*atts):
    return ("S1", list(atts))


def S2(*atts):
    return ("S2", list(atts))


def X(l):
    return ("L", l)


def ssf_call(tag, n, site="S1", pre="", kind="cells_m5", in_raw_last=True):
    mk = ms if site == "S1" else hs
    return [mk("%s%s attempt %d" % (pre, tag, k), tag, outcome=("ssf" if k < n else "ok"), in_raw=(k == n and in_raw_last and site == "S1"))
            for k in range(1, n + 1)]


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates"
BASIS_M4 = "X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003)"
ALL = ("RK", "RF", "RG", "RH", "RI", "RIw", "RIx")


def cell5_resolved(n=2, drop_k=(), site="S1", counter=None, drop_rb1_k=(), drop_ren=(), note=None, kind=None):
    if site == "S1":
        atts = ssf_call("S5_t1", n)
        pkg = build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*atts)], basis=BASIS_M5, row=485)
        tag, dirn, st = "S5_t1", "solver", "S-1"
    else:
        atts = ssf_call("health_p1073741831_d222", n, site="S2")
        pkg = build("controls_a1", [X(L("gp", "gp", "controls_a1_pari", in_raw=True)), S2(*atts),
                                    S2(hs("health d444", "health_p1073741831_d444")),
                                    X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")), S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
                    gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])
        tag, dirn, st = "health_p1073741831_d222", "health", "S-2"
    drop = {a["lid"] for a in atts if a["attempt"] in set(drop_k)}
    return premise(pkg, drop=drop, drop_rb1=[(st, tag, k) for k in drop_rb1_k], counter=counter,
                   drop_ren_keys=[(st, tag, key) for key in drop_ren], note=note)


# =============================================================================================== BJ-0
P("=" * 118)
P("BJ-0 KNOWN-ANSWER CONTROL (CRI-4 (a)-(f)); method unchanged across objects")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK); RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, pair=None, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False, retained=False)
ka1 = build("cells_m5", [("L", p16)], raw="wrapper", basis=BASIS_M5)
ka1["designed"] = False
ka1["counters"]["S-1"]["attempts_total"] = 0
evaluate("KA-a1", "P-16 (os.fork at v2_solver.py 181 created the child; raise before STORE_FAST pid; wrapper writes raw)", ka1, ("RK", "RF"), ks=(0, 1))
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, pair=None, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False, retained=False)
ka2 = build("cells_m5", [("L", pf2)], raw="wrapper", basis=BASIS_M5)
ka2["designed"] = False
evaluate("KA-a2", "P-F2 after P-14a (raise at 214, then lk.release raises in run_child's finally; final traceback lacks _run_child_locked)", ka2, ("RK", "RF"), ks=(0, 1))
ka3 = build("cells_m5", [], raw="wrapper", basis=BASIS_M5)
ka3["designed"] = False
evaluate("KA-a3", "W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper.py 491-505)", ka3, ("RK", "RF"))

P("\n--- (b) failclosed AS WORDED (RF): FO-1 in both variants, foreign-file write failed / interrupted")
for vl, rep, p227, pair in (("C", "", False, None), ("B", "OK", True, CP)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (vl, wr, rc), "S5_t0", report=rep, rc=rc, p227=p227, pair=pair, exec_=False, escaped=True,
                    foreign_write=wr, outcome="refused_to_start" if vl == "C" else "crashed", in_raw=p227)
            q = build("cells_m5", [S1(fo)], basis=BASIS_M5, row=485)
            q["designed"] = False
            evaluate("KA-b-%s-%s-%d" % (vl, wr, rc), "FO-1 variant %s, foreign write %s, escaped exit %d" % (vl, wr, rc), q, ("RF", "RG", "RH", "RI"), ks=(0, 1))

P("\n--- (c) childend AS WORDED (RG): PB-3, a cells package with one SE-3 re-solve (RF, RH, RI for contrast)")
pb3 = build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*ssf_call("S5_t1", 2))], basis=BASIS_M5, row=485)
evaluate("KA-c", "PB-3 cells m = 5, S5_t1 re-solved once at S-1 (r3_resolve 224-238, 310)", pb3, ("RF", "RG", "RH", "RI"))

P("\n--- (d) gapattr AS WORDED (RH): CX-1 objects LR-1, LR-2, LR-3, LR-5 and LR-4 of review TASK-20260924-94cc33")
P("--- (e) the same objects under attcount with RI-1 (a) WEAKENED to 'N >= 1' (RIw) and AS WORDED (RI)")
LR = {
    "LR-1": ("S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent", dict(n=2, drop_k=(2,))),
    "LR-2": ("S-1 re-solve, 2 attempts, attempt 1's launch record absent", dict(n=2, drop_k=(1,))),
    "LR-3": ("S-1 re-solve, 3 attempts, attempt 2's launch record absent", dict(n=3, drop_k=(2,))),
    "LR-4": ("S-1 re-solve, 3 attempts, attempts 2 and 3 absent", dict(n=3, drop_k=(2, 3))),
    "LR-5": ("S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent", dict(n=2, drop_k=(2,), site="S2")),
}
for key, (lab, kw) in LR.items():
    evaluate(key, lab, cell5_resolved(**kw), ("RH", "RIw", "RI"))
P("\n  every single removal among 2, 3 and 6 attempts at S-1 (RH-6 (i) (19) third case; RI-3 (24)):")
single = []
for n in (2, 3, 6):
    for k in range(1, n + 1):
        q = cell5_resolved(n=n, drop_k=(k,))
        res = {rs: (verdict(q, rs, "Mc"), definitions(q, rs), gaps(q, rs)[1]) for rs in ("RH", "RIw", "RI")}
        single.append({"attempts": n, "removed": k, **{rs: {"verdict": v[0], "defs": v[1], "named": v[2]} for rs, v in res.items()}})
        P("   n=%d removed=%d | RH %s %s | RIw %s %s | RI %s named=%d" % (n, k, res["RH"][0], res["RH"][1], res["RIw"][0], res["RIw"][1],
                                                                        res["RI"][0], len(res["RI"][2])))
OUT["single_removals"] = single


# =============================================================================================== BJ-0 (f): listing check
PK = json.load(open(os.path.join(SCR, "pkgread.json")))
GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
# frozen call-site naming for S-1 calls whose argv raw-result.json does not carry (CRI-9 reconstruction rule):
FROZEN_GB = {"anchor_comparator_system": True}                    # v2_driver.py 711 gb_only=True
FROZEN_NONGB_PREFIX = ("ctl_identity_", "ctl_rawx_", "ctl_planted_")   # v2_driver.py 786, 787, 841 (gb_only default False)


def reconstruct(pk):
    """CRI-9: RECONSTRUCTED launch set and counts of an archived r3 package. Rule: child/<tag>.spec.json -> one child-job
    launch record; solver|health/<tag>.ms.log -> one msolve launch record (one more per <tag>.ms.log.ssf-attempt<k>);
    solver/<tag>.callgrind.stdout -> one callgrind record; comparator/stdout.log -> one comparator record;
    pari/<tag>.gp.stdout -> one gp record. The -g / -P flag and the per-tag RB-1 / RL-2 counts are taken, INDEPENDENTLY of
    the listing, from raw-result.json's solver argv where recorded, else from the frozen call site's gb_only argument.
    Events and site counters are the r3 solver-events.json's. child_end 'exec' where the child's outputs exist."""
    rd = RUNS + "/" + pk
    ents = PK["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    se = PK["packages"][pk]["files"]["solver-events.json"]["json"]
    raw = PK["packages"][pk]["files"]["raw-result.json"]["json"]
    argvs = []

    def walk(o):
        if isinstance(o, dict):
            for k2, v in o.items():
                if k2 == "argv" and isinstance(v, list):
                    argvs.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(raw)
    raw_s1 = {}
    for a in argvs:
        if a and a[0] == MSOLVE and "-f" in a:
            t = os.path.basename(a[a.index("-f") + 1])[:-3]
            raw_s1.setdefault(t, []).append("-g" in a)
    recs, order, rb1, rl2, src = [], 0, [], [], {}
    sp = {}
    for rel, v in PK["packages"][pk]["specs"].items():
        sp[rd + "/" + rel] = {"out": v["json"].get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se_ = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid, kind = "childjob:" + t, "childjob"
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            if t in raw_s1:
                gb = raw_s1[t][0]
                src[t] = "raw-result.json solver argv (%s)" % ("-g 1" if gb else "-P 1")
            elif t in FROZEN_GB:
                gb = FROZEN_GB[t]
                src[t] = "frozen call site v2_driver.py 711 (gb_only=True)"
            elif t.startswith(FROZEN_NONGB_PREFIX):
                gb = False
                src[t] = "frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)"
            else:
                gb = None
                src[t] = "UNKNOWN"
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out"] + (["-g", "1"] if gb else ["-P", "1"])
            so, se_, ce, lid, kind = rd + "/" + rel, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t, "msolve"
            site = SITE_OF_DIR[d]
            if gb:
                rl2.append({"tag": t, "lid": lid, "pair": CP})
            elif gb is False:
                rb1.append({"site": site, "tag": t, "k": 1, "lid": lid, "pair": CP})
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v", "2", "-t", "1",
                    "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se_, ce, lid, kind = rd + "/" + rel, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t, "callgrind"
        elif rel == "comparator/stdout.log":
            argv, so, se_, ce, lid, kind = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se_, ce, lid, kind = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/" + rel, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t, "gp"
        if lid:
            recs.append({"id": lid, "ordinal": order, "argv": argv, "stdout": so, "stderr": se_, "child_end": ce, "kind": kind})
            order += 1
    events = []
    for sname, sec in se["sites"].items():
        for e in sec.get("events") or []:
            events.append({"site": sname, "dir": "solver" if sname == "v2_driver.solve" else "health", "tag": e.get("tag"),
                           "attempts": e.get("attempts"), "accepted_attempt": e.get("accepted_attempt"), "renamed_files": e.get("renamed_files") or {}})
    c1 = se["sites"]["v2_driver.solve"]["counters"]
    c2 = se["sites"]["a1_health.run_system"]["counters"]
    counters = {"S-1": {"attempts_total": c1["attempts_total"], "passthrough_calls_gb_only_true": c1["passthrough_calls_gb_only_true"],
                        "wrapped_calls": c1["wrapped_calls"]},
                "S-2": {"attempts_total": c2["attempts_total"], "wrapped_calls": c2["wrapped_calls"]}}
    s3 = collections.Counter(r.get("tag") for r in se["sites"]["v2_driver.solve/callgrind"].get("records") or [])
    files = {r: ("?", "listed") for r in rels}
    pkg = dict(kind="gate", launches=[], raw="driver", gate=True, basis=None, row=478, rd=rd, rd_check=rd, files=files, events=events,
               counters=counters, rb1=rb1, rl2=rl2, raw_pairs=True, designed=True, altered_after_manifest=False, dup=[], note=[])
    return pkg, recs, sp, src, s3, c1


def listing_check(rule):
    res = {}
    P("\n--- LISTING CHECK under %s (launch sets RECONSTRUCTED, CRI-9)" % rule)
    for pk in GATE:
        pkg, recs, sp, src, s3, c1 = reconstruct(pk)
        rd = pkg["rd"]
        named, gapfiles, restrict, dup_ids = ([], set(), {}, set())
        if rule in ("RI", "RIw"):
            named, gapfiles, restrict, dup_ids = ri1(pkg, recs, "worded" if rule == "RI" else "weak")
        att = {}
        for rel in sorted(pkg["files"]):
            h = attr_rh1(rd, rel, recs, sp, pkg["events"], restrict or None)
            if not h and nonlaunch(rel):
                h = [("-", nonlaunch(rel))]
            if dup_ids:
                h = [x for x in h if x[0] not in dup_ids]
            if rel in gapfiles:
                h = []
            att[rel] = h
        un = sorted(r for r, h in att.items() if not h)
        by = collections.Counter((h[0][1].split(" ")[0] if h else "NONE") for h in att.values())
        kinds = collections.Counter(r["kind"] for r in recs)
        P("  %s: %d files in the five directories; %d reconstructed launch records %s; first clause %s; named gaps %d; unattributed %d"
          % (pk, len(att), len(recs), dict(sorted(kinds.items())), dict(sorted(by.items())), len(named), len(un)))
        for u in un:
            P("    UNATTRIBUTED " + u)
        for n in named:
            P("    NAMED " + n)
        # count table (BJ-2 (2))
        L_ = collections.Counter()
        for r in recs:
            for d in ("solver", "health"):
                m = re.fullmatch(re.escape(rd + "/" + d + "/") + r"(?P<tag>.+)\.ms\.log", r["stdout"])
                if m:
                    L_[(d, m.group("tag"))] += 1
        rb1c = collections.Counter((SITE_OF_DIR_R[r["site"]], r["tag"]) for r in pkg["rb1"])
        rl2c = collections.Counter(("solver", r["tag"]) for r in pkg["rl2"])
        table = []
        for (d, t) in sorted(set(L_) | set(rb1c) | set(rl2c)):
            N = L_[(d, t)]
            ev = [e for e in pkg["events"] if e["dir"] == d and e["tag"] == t]
            row = {"site": SITE_OF_DIR[d], "tag": t, "N_launch_records": N, "RB1_attempt_records": rb1c[(d, t)], "RL2_passthrough_records": rl2c[(d, t)],
                   "event": len(ev), "ii": "no event (not evaluated)" if not ev else "see events", "source_of_RB1_RL2": src.get(t),
                   "i_holds": N == rb1c[(d, t)] + rl2c[(d, t)]}
            table.append(row)
        site_rows = []
        for d, site in (("solver", "S-1"), ("health", "S-2")):
            n = sum(v for (dd, _t), v in L_.items() if dd == d)
            c = pkg["counters"][site]
            want = c["attempts_total"] + (c.get("passthrough_calls_gb_only_true", 0) if site == "S-1" else 0)
            site_rows.append({"site": site, "launch_records_at_dir_ms_log": n, "counters": c, "iii_holds": n == want})
        cg_paths = collections.Counter(r["stdout"] for r in recs if r["kind"] == "callgrind")
        cg_rows = {"callgrind_records_reconstructed": sum(cg_paths.values()), "S3_records_in_r3_solver_events": sum(s3.values()),
                   "per_tag_equal": all(s3.get(r["stdout"].split("/")[-1][:-len(".callgrind.stdout")], 0) == 1 for r in recs if r["kind"] == "callgrind"),
                   "S3_callgrind_children_observed": PK["packages"][pk]["files"]["solver-events.json"]["json"]["sites"]["v2_driver.solve/callgrind"]["counters"]["callgrind_children_observed"]}
        other = collections.Counter(r["stdout"] for r in recs if r["kind"] != "msolve")
        dup_other = {k.replace(rd + "/", ""): v for k, v in other.items() if v > 1}
        mism = [r for r in table if not r["i_holds"]] + [s for s in site_rows if not s["iii_holds"]]
        P("    count table: %d (site, tag) rows; (i) mismatches %d; site rows %s; events %d; callgrind %s; duplicate other stdout paths %s"
          % (len(table), sum(1 for r in table if not r["i_holds"]), [(s["site"], s["launch_records_at_dir_ms_log"], s["counters"], s["iii_holds"]) for s in site_rows],
             len(pkg["events"]), cg_rows, dup_other))
        for r in table:
            P("      %-4s %-40s N=%d RB-1=%d RL-2=%d event=%d (i)=%s  [%s]" % (r["site"], r["tag"], r["N_launch_records"], r["RB1_attempt_records"],
                                                                       r["RL2_passthrough_records"], r["event"], r["i_holds"], r["source_of_RB1_RL2"]))
        res[pk] = {"n_files": len(att), "n_records": len(recs), "record_kinds": dict(kinds), "first_clause": dict(by), "unattributed": un,
                   "named": named, "count_table": table, "site_rows": site_rows, "callgrind": cg_rows, "duplicate_other_stdout": dup_other,
                   "mismatches": mism, "attribution": {r: att[r] for r in att}}
    OUT["listing_" + rule] = res
    return res


P("\n--- (f) LISTING CHECK under attcount (RI) on the four archived r3 gate packages; RH for contrast")
listing_check("RH")
listing_check("RI")

with open(os.path.join(SCR, "rteval_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rteval_v1.json with %d keys" % len(OUT))
````

### `rteval_v2.py`

- sha256: `fb74f767763aa4962896b1742d434e8dc1ef049dd5ad04e45ac2c2a451ecfdfa`
- bytes: 52679; lines: 1024
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 600 python3 -B rteval_v2.py > rteval_v2.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: evaluator version 2 = version 1 with an exec of rteval_v2_objects.py appended before the final write; every rule function unchanged (diff shown in the md, section 2)

````text
#!/usr/bin/env python3
"""TASK-20260924-be2daf rule evaluator, version 2 (scratch; zero runs). = version 1 with objects APPENDED after the BJ-0 section; every rule function unchanged. ONE method, used UNCHANGED for BJ-0..BJ-3.

Imports only json, os, re, sys, itertools, collections. Reads one scratch file (pkgread.json: the O_NOATIME listings
and the archived solver-events.json / raw-result.json / spec files of the four r3 gate packages). Imports nothing from
the repository and no third-party module. Writes rteval_v2.json next to itself; prints its report on stdout.

TRUTH MODEL. A package is built by simulating, in order, the frozen launches of a command (v2_driver.py,
a1_health.py, a1_pari.py, v2_solver.py) and the r3 / r4 resolve layer (r3_resolve.py _bounded 248-319, solve 373-390,
run_system 397-409): files written (by whom), SE-3 / HR-3 events with attempts, accepted_attempt, renamed_files,
the site counters attempts_total (273) and passthrough_calls_gb_only_true (383), RB-1 attempt records (readbackcover
RB-1: one per attempt of every wrapped non-gb_only call at S-1 and every call at S-2), RL-2 pass-through records
(readbackfull RL-2: one per gb_only S-1 call), and RL-1 launch records (one per run_child call). A CONSTRUCTED
premise is applied afterwards (a record absent, a count altered); such a package is not "designed".

RULE SETS (package level):
  RK   readbackclose RK-1 / RK-3 (b) as worded (RL-3 gaps gate nothing: readbackfull RL-3).
  RF   failclosed as worded: RF-0 (b), RF-1 (a), RF-2, RF-3 (a); an RL-3 gap is a file of RL-3's globs (child/*.meta.json,
       solver/*.ms.log, health/, comparator/, pari/) whose writing launch has no launch record (readbackfull RL-3).
  RG   childend: RF with RG-1 (c)/(d) child_end, RG-2 (a)/(b), RG-4 (b) attribution; a gap FAILs.
  RH   gapattr: RG with RH-1 (i)-(vi) in place of RG-4 (b)'s sentence, RH-2 (a)/(b), RH-4.
  RI   attcount: RH with RI-1 (a)-(d) as worded (named COUNT / SITE COUNT / DUPLICATE-PATH gaps; (d) restriction).
  RIw  RI with RI-1 (a) WEAKENED to "N >= 1" (CRI-4 (e)); (b), (c), (d) as worded.
  RIx  RI with RI-1 (a) and (d) DISABLED (RI-3 (25)'s scratch evaluator); (b), (c) as worded.
The frozen checker items evaluated: v2_check_run.py 65-67 (collected read-back list empty) and 68-70 (a collected pair
!= requested cap). Requested cap variants: Mr (r3 base, r3_run_wrapper.py 550: raw envelope cap; None if the wrapper
wrote raw-result.json) and Mc (an r4 wrapper recording the requested cap independently). k = number of added other
class-B S-1 launches. The r4 checks other than the rule under test are taken as passing, except V-7 (valueclose VC-1
(e); r3_check_run.py 153-158) which fails iff solver-events.json was altered after the manifest recorded its sha256.

DEFINITIONS (failclosed 604-621) on TRUTH: FAIL-OPEN iff PASS / PASS_ZL while (i) a pair the parent read is in no
launch record; (ii) a child that may have executed argv (created, and its launch record not class A or C -- an
ABSENT record is not class A or C) has no recorded pair equal to the cap [LR: in a launch record; ANY: in any RB-2 /
RL-3 source]; (iii) a created child recorded child_created false; (iv) a record written in another process goes
undetected (read LITERALLY); (v) the outcome is wrapper-recorded. PLANNED-BASIS REFUSAL iff a driver-logic outcome
(as the rule set reads RF-0 (b)) acted on by a dependant's frozen logic (basis) or enumerated by RFR-2 (row),
designed, receives FAIL.
"""
import collections
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "/usr/local/bin/python3"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}                 # childend RG-1 (c)
REN = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
DIR_OF = {"msolve": "solver", "health": "health", "childjob": "child", "callgrind": "solver", "comparator": "comparator", "gp": "pari"}
SITE_OF_DIR = {"solver": "S-1", "health": "S-2"}
OUT = {}
LINES = []


def P(*a):
    s = " ".join(str(x) for x in a)
    LINES.append(s)
    print(s)


# =============================================================================================== truth: launches
def L(lid, kind, tag, **kw):
    d = dict(lid=lid, kind=kind, tag=tag, dirn=DIR_OF[kind], gb=False, created=True, opened=True, p227=True, pair=CP,
             exec_=True, report="OK", rc=0, raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False,
             foreign_write=None, callback="normal", fired=None, new_pids=None, t_en=None, value=None, outcome="ok",
             job="build", cached=False, partial_npz=False, cg_out_left=False, retained=True, in_raw=True, recorded=True)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if not d["created"]:
        d["opened"] = False
    return d


def paths(l, rd):
    t, dn, k = l["tag"], rd + "/" + l["dirn"], l["kind"]
    if k in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"] +
                (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if k == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2", "-t",
                 "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if k == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if k == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if k == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(k)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch: rel -> (writer, note)."""
    t, dn, k, me = l["tag"], l["dirn"], l["kind"], l["lid"]
    f = {}
    op = l["created"] and l["opened"]                                  # the fork child opened stdout/stderr (v2_solver 188-189)
    if k in ("msolve", "health"):
        if l["retained"] or k == "health":
            f[dn + "/" + t + ".ms"] = ("driver", "v2_driver 161-162 / a1_health 141-143")
        if op:
            f[dn + "/" + t + ".ms.log"] = (me, "stdout")
            f[dn + "/" + t + ".ms.err"] = (me, "stderr")
        if l["exec_"] and l["outcome"] in ("ok", "ssf", "positive_dimensional", "degenerate_parametrisation"):
            f[dn + "/" + t + ".ms.out"] = (me, "-o")
    elif k == "childjob":
        f[dn + "/" + t + ".spec.json"] = ("driver", "v2_driver 98-99")
        if op:
            f[dn + "/" + t + ".stdout"] = (me, "stdout")
            f[dn + "/" + t + ".stderr"] = (me, "stderr")
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f[dn + "/" + t + ".npz"] = (me, "v2_child 38")
                    f[dn + "/" + t + ".meta.json"] = (me, "v2_child 41")
                else:
                    f[dn + "/" + t + ".meta.json"] = (me, "v2_child 104 (.npz removed v2_driver 144)")
            elif l["outcome"] == "refused_meta":
                f[dn + "/" + t + ".meta.json"] = (me, "v2_child 68/80")
            elif l["partial_npz"]:
                f[dn + "/" + t + ".npz"] = (me, "partial")
    elif k == "callgrind":
        if op:
            f[dn + "/" + t + ".callgrind.stdout"] = (me, "stdout")
            f[dn + "/" + t + ".callgrind.stderr"] = (me, "stderr")
        if l["cg_out_left"]:
            f[dn + "/" + t + ".callgrind.out"] = (me, "left by v2_solver 521-524 path")
    elif k == "comparator":
        if op:
            f[dn + "/stdout.log"] = (me, "stdout")
            f[dn + "/stderr.log"] = (me, "stderr")
        if l["exec_"] and l["outcome"] == "ok":
            for x in ("anchor25_random.ms", "anchor25_planted.ms", "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json"):
                f[dn + "/" + x] = (me, "k4a 279-281, 318")
    elif k == "gp":
        f[dn + "/" + t + ".gp"] = ("driver", "a1_pari 91-93")
        if op:
            f[dn + "/" + t + ".gp.stdout"] = (me, "stdout")
            f[dn + "/" + t + ".gp.stderr"] = (me, "stderr")
    return f


# =============================================================================================== truth: packages
def build(kind, steps, raw="driver", gate=False, basis=None, row=None, rd=None, raw_pairs=True, extra_files=()):
    """steps: ("S1", [attempt launches]) a wrapped S-1 call (gb_only if its launches have gb); ("S2", [attempts]) a
    wrapped S-2 call; ("L", launch) an unwrapped launch. Every attempt but the last of a wrapped call is an SSF attempt:
    its three files are renamed '<name>.ssf-attempt<k>' and listed under the event's renamed_files['attempt<k>'].
    Returns the package (truth + records as the r4 layer writes them)."""
    rd = rd or RUNS + "/RUN-X"
    files, launches = {}, []
    events = []
    counters = {"S-1": {"attempts_total": 0, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 0}, "S-2": {"attempts_total": 0, "wrapped_calls": 0}}
    rb1, rl2 = [], []
    for st in steps:
        if st[0] == "L":
            l = st[1]
            launches.append(l)
            files.update(files_of(l))
            continue
        site, atts = ("S-1" if st[0] == "S1" else "S-2"), st[1]
        gb = site == "S-1" and atts[0]["gb"]
        if gb:
            counters["S-1"]["passthrough_calls_gb_only_true"] += 1
            l = atts[0]
            launches.append(l)
            files.update(files_of(l))
            rl2.append({"tag": l["tag"], "lid": l["lid"], "pair": l["pair"] if l["p227"] else None})
            continue
        counters[site]["wrapped_calls"] += 1
        ev = None
        n = len(atts)
        for k, l in enumerate(atts, start=1):
            l["attempt"] = k
            launches.append(l)
            files.update(files_of(l))
            counters[site]["attempts_total"] += 1
            rb1.append({"site": site, "tag": l["tag"], "k": k, "lid": l["lid"], "pair": l["pair"] if l["p227"] else None})
            if k < n:                                           # an SSF attempt followed by another attempt
                if ev is None:
                    ev = {"site": site, "dir": l["dirn"], "tag": l["tag"], "attempts": [], "renamed_files": {}}
                    events.append(ev)
                ren = {}
                for ext in (".ms.out", ".ms.log", ".ms.err"):
                    src = l["dirn"] + "/" + l["tag"] + ext
                    nm = os.path.basename(src) + ".ssf-attempt%d" % k
                    if src in files:
                        files[src + ".ssf-attempt%d" % k] = (files.pop(src)[0], "renamed r3_resolve 234")
                        ren[nm] = {"renamed": True}
                    else:
                        ren[nm] = {"absent": True}
                ev["renamed_files"]["attempt%d" % k] = ren
        if ev is not None:
            ev["attempts"] = [{"attempt": k} for k in range(1, n + 1)]
            ev["accepted_attempt"] = n
    for rel, w in extra_files:
        files[rel] = w
    for i, l in enumerate(launches):
        l["ordinal"] = i
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, rd=rd, rd_check=rd, files=files,
                events=events, counters=counters, rb1=rb1, rl2=rl2, raw_pairs=raw_pairs, designed=True, altered_after_manifest=False,
                dup=[], note=[])


def premise(pkg, drop=(), drop_rb1=(), drop_rl2=(), counter=None, drop_ren_keys=(), dup=(), event_edit=None, altered=False, note=None):
    """Apply a CONSTRUCTED premise: launch records absent (drop), RB-1 / RL-2 records absent, counter deltas, renamed_files
    keys removed, launch records duplicated, event fields edited. Returns a new package (deep copy)."""
    q = json.loads(json.dumps(pkg))
    for l in q["launches"]:
        if l["lid"] in drop:
            l["recorded"] = False
    q["rb1"] = [r for r in q["rb1"] if (r["site"], r["tag"], r["k"]) not in set(drop_rb1)]
    q["rl2"] = [r for r in q["rl2"] if r["tag"] not in set(drop_rl2)]
    for site, kv in (counter or {}).items():
        for k, v in kv.items():
            q["counters"][site][k] += v
    for (site, tag, key) in drop_ren_keys:
        for e in q["events"]:
            if e["site"] == site and e["tag"] == tag:
                e["renamed_files"].pop(key, None)
    q["dup"] = list(dup)
    if event_edit:
        for e in q["events"]:
            event_edit(e)
    if drop or drop_rb1 or drop_rl2 or counter or drop_ren_keys or dup or event_edit:
        q["designed"] = False
    q["altered_after_manifest"] = altered
    if note:
        q["note"] = q["note"] + [note]
    return q


# =============================================================================================== records as written
def child_created_rk(l):                                  # readbackclose RK-1 (a) / (b)
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def child_created_rf(l):                                  # failclosed RF-1 (a)
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):                                          # the pair the launch record carries (RK-1 (a)/(b), (c))
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return tuple(l["pair"]) if l["pair"] else None


def child_end(l, rs):                                     # childend RG-1 (c), with gapattr RH-4
    if rs in ("RH", "RI", "RIw", "RIx") and l["callback"] == "caught":
        return "undetermined"
    cc = child_created_rf(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):                                         # failclosed RF-3 (a) classes, childend RG-1 (d)
    cc = child_created_rk(l) if rs == "RK" else child_created_rf(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


def records(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = paths(l, pkg["rd"])
        r = {"id": l["lid"], "ordinal": l["ordinal"], "argv": argv, "stdout": so, "stderr": se, "kind": l["kind"], "tag": l["tag"],
             "child_end": child_end(l, rs) if rs not in ("RK", "RF") else None}
        out.append(r)
        if l["lid"] in pkg["dup"]:
            out.append(dict(r, id=l["lid"] + "#dup"))
    return out


def specs(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["kind"] == "childjob":
            rel = "child/" + l["tag"] + ".spec.json"
            if rel in pkg["files"]:
                sp[pkg["rd"] + "/" + rel] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"]}
    return sp


# =============================================================================================== layer 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 / 251)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93)"
    return None


def attr_rg4(rd, rel, recs):
    p = rd + "/" + rel
    names = collections.Counter(a for r in recs for a in set(r["argv"]))
    hits = []
    for r in recs:
        if p in (r["stdout"], r["stderr"]):
            hits.append((r["id"], "stdout/stderr"))
        if p in r["argv"]:
            hits.append((r["id"], "argv exact"))
        for a in r["argv"]:
            if p.startswith(a.rstrip("/") + "/") and names[a] == 1 and a.rstrip("/") in {rd + "/" + d for d in FIVE}:
                hits.append((r["id"], "argv directory"))
    return hits


def attr_rh1(rd, rel, recs, sp, events, restrict=None):
    """gapattr RH-1 (i)-(vi). restrict: RI-1 (d) -- {record id: 'last'|'earlier'} for records of an L(dir, tag) with
    N >= 2 and (a) holding: final files of that tag only to 'last' by (i)/(ii); an 'earlier' record attributes nothing by
    (i)/(ii) and, by (vi), only renamed files of its own attempt k (its position in L)."""
    p = rd + "/" + rel
    names = collections.Counter(a for r in recs for a in set(r["argv"]))
    hits = []
    for r in recs:
        role = (restrict or {}).get(r["id"])
        final_of = None
        if role:
            final_of = role[1]
        allow_i_ii = True
        if role and role[0] == "earlier":
            allow_i_ii = False
        if p in (r["stdout"], r["stderr"]) and allow_i_ii:
            hits.append((r["id"], "(i)"))
        if p in r["argv"] and allow_i_ii:
            hits.append((r["id"], "(ii)"))
        for a in r["argv"]:
            if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                hits.append((r["id"], "(iii)"))
            if a.rstrip("/") in {rd + "/" + d for d in FIVE} and p.startswith(a.rstrip("/") + "/") and names[a] == 1:
                hits.append((r["id"], "(iv)"))
        if r["child_end"] == "exec" and r["argv"]:
            m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
            if m:
                s = sp.get(r["argv"][-1])
                o = rd + "/child/" + m.group("tag")
                if isinstance(s, dict) and s.get("out") == o and p in (o + ".npz", o + ".meta.json"):
                    hits.append((r["id"], "(v)"))
    d, _, name = rel.partition("/")
    m = REN.fullmatch(name)
    if m and d in ("solver", "health"):
        tag, k = m.group("tag"), int(m.group("k"))
        ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
        same = sorted((r for r in recs if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["ordinal"])
        if ev and len(same) >= k:
            R = same[k - 1]
            role = (restrict or {}).get(R["id"])
            hits.append((R["id"], "(vi) k=%d" % k))
    if restrict:                                           # RI-1 (d): the final files of a restricted tag go only to its last record
        fin = None
        for rid, role in restrict.items():
            if role[0] == "last":
                t = role[1]
                if rel in ("%s.ms" % t, "%s.ms.out" % t, "%s.ms.log" % t, "%s.ms.err" % t):
                    fin = rid
        if fin is not None:
            hits = [h for h in hits if not (h[1] in ("(i)", "(ii)") and restrict.get(h[0], ("", ""))[0] != "last"
                                            and h[0] in restrict)]
    return hits


# =============================================================================================== RI-1 (a)-(d)
def ri1(pkg, recs, mode):
    """mode: 'worded' | 'weak' (a) := N >= 1 | 'off' ((a) and (d) disabled). Returns (named_gaps, gap_files, restrict)."""
    rd = pkg["rd_check"]
    named, gapfiles, restrict = [], set(), {}
    L_ = collections.defaultdict(list)
    for r in recs:
        for d in ("solver", "health"):
            m = re.fullmatch(re.escape(rd + "/" + d + "/") + r"(?P<tag>.+)\.ms\.log", r["stdout"])
            if m:
                L_[(d, m.group("tag"))].append(r)
    for k in L_:
        L_[k].sort(key=lambda r: r["ordinal"])
    rb1c = collections.Counter((SITE_OF_DIR_R[r["site"]], r["tag"]) for r in pkg["rb1"])
    rl2c = collections.Counter(("solver", r["tag"]) for r in pkg["rl2"])
    evs = collections.defaultdict(list)
    for e in pkg["events"]:
        evs[(e["dir"], e["tag"])].append(e)
    keys = set(L_) | set(rb1c) | set(rl2c) | set(evs)
    holds = {}
    for (d, t) in sorted(keys):
        N = len(L_.get((d, t), []))
        if mode == "off":
            holds[(d, t)] = None
            continue
        if mode == "weak":
            holds[(d, t)] = N >= 1
            if N < 1:
                named.append("COUNT GAP (%s/%s, N=0; weakened (a): N >= 1 fails)" % (d, t))
            continue
        reasons = []
        want = rb1c.get((d, t), 0) + (rl2c.get((d, t), 0) if d == "solver" else 0)
        if N != want:
            reasons.append("(i) N=%d != RB-1 %d + RL-2 %d" % (N, rb1c.get((d, t), 0), rl2c.get((d, t), 0) if d == "solver" else 0))
        es = evs.get((d, t), [])
        if es:
            if len(es) != 1:
                reasons.append("(ii) %d events" % len(es))
            else:
                e = es[0]
                na, acc, nr = len(e.get("attempts") or []), e.get("accepted_attempt"), 1 + len(e.get("renamed_files") or {})
                nums = [a.get("attempt") for a in (e.get("attempts") or [])]
                if not (N == na == acc == nr):
                    reasons.append("(ii) N=%d attempts=%d accepted=%s 1+renamed=%d" % (N, na, acc, nr))
                if nums != list(range(1, na + 1)):
                    reasons.append("(ii) attempt numbers %s" % nums)
        holds[(d, t)] = not reasons
        if reasons:
            named.append("COUNT GAP (%s/%s, N=%d): %s" % (d, t, N, "; ".join(reasons)))
            for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                if d + "/" + t + ext in pkg["files"]:
                    gapfiles.add(d + "/" + t + ext)
            for f in pkg["files"]:
                mm = REN.fullmatch(f.partition("/")[2])
                if f.startswith(d + "/") and mm and mm.group("tag") == t:
                    gapfiles.add(f)
    if mode == "worded":
        for d, site in (("solver", "S-1"), ("health", "S-2")):
            n = sum(len(v) for (dd, _t), v in L_.items() if dd == d)
            c = pkg["counters"][site]
            want = c["attempts_total"] + (c.get("passthrough_calls_gb_only_true", 0) if site == "S-1" else 0)
            if n != want:
                named.append("SITE COUNT GAP (%s): %d launch records vs counters %s" % (site, n, json.dumps(c, sort_keys=True)))
    # (b) one launch per other output path
    other = collections.defaultdict(list)
    for r in recs:
        if not any(re.fullmatch(re.escape(rd + "/" + d + "/") + r".+\.ms\.log", r["stdout"]) for d in ("solver", "health")):
            other[r["stdout"]].append(r)
    dup_ids = set()
    for so, rs_ in other.items():
        if len(rs_) > 1:
            named.append("DUPLICATE-PATH GAP (%s): ordinals %s" % (so.replace(rd + "/", ""), [r["ordinal"] for r in rs_]))
            dup_ids |= {r["id"] for r in rs_}
    # (d)
    if mode in ("worded", "weak"):
        for (d, t), rs_ in L_.items():
            if len(rs_) >= 2 and holds.get((d, t)):
                for i, r in enumerate(rs_):
                    restrict[r["id"]] = ("last" if i == len(rs_) - 1 else "earlier", d + "/" + t, i + 1)
    return named, gapfiles, restrict, dup_ids


SITE_OF_DIR_R = {"S-1": "solver", "S-2": "health"}


def gaps(pkg, rs):
    rd = pkg["rd_check"]
    rels = sorted(pkg["files"])
    if rs == "RK":
        return [], [], {}
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            if glob and w[0] != "driver" and w[0] not in recorded:
                g.append(rel)
        return sorted(g), [], {}
    recs = records(pkg, rs)
    if rs == "RG":
        att = {rel: attr_rg4(rd, rel, recs) or ([("-", nonlaunch(rel))] if nonlaunch(rel) else []) for rel in rels}
        return sorted(r for r, h in att.items() if not h), [], att
    sp = specs(pkg)
    named, gapfiles, restrict, dup_ids = ([], set(), {}, set())
    if rs in ("RI", "RIw", "RIx"):
        named, gapfiles, restrict, dup_ids = ri1(pkg, recs, {"RI": "worded", "RIw": "weak", "RIx": "off"}[rs])
    att = {}
    for rel in rels:
        h = attr_rh1(rd, rel, recs, sp, pkg["events"], restrict if restrict else None)
        if not h and nonlaunch(rel):
            h = [("-", nonlaunch(rel))]
        if dup_ids:
            h = [x for x in h if x[0] not in dup_ids]
        if rel in gapfiles:
            h = []
        att[rel] = h
    return sorted(r for r, h in att.items() if not h), named, att


# =============================================================================================== layer 2: verdicts
def collected_pairs(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(("launch record (RL-3 d)", rec_pair(l)))
        if l["kind"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"] and l["p227"]:
            ps.append(("meta (RB-2 b)", tuple(l["pair"])))
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(("raw (RB-2 a)", tuple(l["pair"])))
    for r in pkg["rb1"]:
        if r["pair"]:
            ps.append(("RB-1 attempt record (RB-2 c)", tuple(r["pair"])))
    for r in pkg["rl2"]:
        if r["pair"]:
            ps.append(("RL-2 pass-through (RL-3 e)", tuple(r["pair"])))
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = [p for _s, p in collected_pairs(pkg)]
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    childfile = any((r.startswith("child/") and r.endswith(".meta.json")) or (r.startswith("solver/") and r.endswith(".ms.log"))
                    or r.split("/")[0] in ("health", "comparator", "pari") for r in pkg["files"])
    v7 = not pkg["altered_after_manifest"]
    image = pkg["gate"]
    g, named, _att = gaps(pkg, rs)
    if rs == "RK":
        if not items and v7:
            return "PASS"
        if not image and not recs and not childfile and items == ["66-67"] and v7:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(child_created_rf(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs not in ("RF",):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    if (not items and v7 and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign and not g
            and not named and not undet):
        return "PASS"
    if (not image and not recs and not childfile and items == ["66-67"] and v7 and rw == "driver" and pkg["kind"] in ("cells_m5", "fixture4")
            and not foreign and not g and not named):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (child_created_rk(l) if rs == "RK" else child_created_rf(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and tuple(l["pair"] or ()) == CP and (
                any(r["lid"] == l["lid"] and r["pair"] for r in pkg["rb1"]) or any(r["lid"] == l["lid"] and r["pair"] for r in pkg["rl2"])
                or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["kind"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            det = (rs != "RK" and l["foreign_write"] == "ok") or (rs not in ("RK", "RF") and rec and child_end(l, rs) == "undetermined")
            if not det:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs not in ("RK", "RF") and infra_stop(pkg):
        return False
    if rs in ("RH", "RI", "RIw", "RIx") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (premise: absent)"
    cc = child_created_rk(l) if rs == "RK" else child_created_rf(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs not in ("RK", "RF"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii): a created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs not in ("RK", "RF") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant record in another process; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def with_k(pkg, k):
    if not k:
        return pkg
    q = json.loads(json.dumps(pkg))
    base = len(q["launches"])
    for j in range(k):
        l = L("otherB%d" % j, "msolve", "otherB_t%d" % j)
        l["ordinal"] = base + j
        l["attempt"] = 1
        q["launches"].insert(0, l)
        q["files"].update(files_of(l))
        q["counters"]["S-1"]["attempts_total"] += 1
        q["counters"]["S-1"]["wrapped_calls"] += 1
        q["rb1"].append({"site": "S-1", "tag": l["tag"], "k": 1, "lid": l["lid"], "pair": CP})
    for i, l in enumerate(q["launches"]):
        l["ordinal"] = i
    return q


def evaluate(key, label, pkg, rule_sets, ks=(0,), variants=("Mr", "Mc")):
    P("\n### %s: %s" % (key, label))
    for n in pkg.get("note") or []:
        P("  note: " + n)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-26s] %-3s %s" % (l["lid"][:26], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = with_k(pkg, k)
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g, named, _att = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row %s" % q["row"])))
            if rs not in ("RK", "RF") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RI", "RIw", "RIx") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if not q["altered_after_manifest"] is False:
                tags.append("V-7 fails (solver-events.json altered after the manifest)")
            if named:
                tags.append("NAMED %s" % named)
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-16s defs %-30s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var), "definitions": dfs,
                         "fail_open": fo, "planned_basis_refusal": pb, "gaps": g, "named": named})
    OUT[key] = {"label": label, "rows": rows}
    return rows


# ----------------------------------------------------------------------------------------------- helpers
def ms(lid, tag, **kw):
    return L(lid, "msolve", tag, **kw)


def hs(lid, tag, **kw):
    kw.setdefault("in_raw", False)
    return L(lid, "health", tag, **kw)


def cj(lid, tag, job="build", **kw):
    return L(lid, "childjob", tag, job=job, **kw)


def cg(lid, tag, **kw):
    return L(lid, "callgrind", tag, **kw)


def S1(*atts):
    return ("S1", list(atts))


def S2(*atts):
    return ("S2", list(atts))


def X(l):
    return ("L", l)


def ssf_call(tag, n, site="S1", pre="", kind="cells_m5", in_raw_last=True):
    mk = ms if site == "S1" else hs
    return [mk("%s%s attempt %d" % (pre, tag, k), tag, outcome=("ssf" if k < n else "ok"), in_raw=(k == n and in_raw_last and site == "S1"))
            for k in range(1, n + 1)]


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates"
BASIS_M4 = "X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003)"
ALL = ("RK", "RF", "RG", "RH", "RI", "RIw", "RIx")


def cell5_resolved(n=2, drop_k=(), site="S1", counter=None, drop_rb1_k=(), drop_ren=(), note=None, kind=None):
    if site == "S1":
        atts = ssf_call("S5_t1", n)
        pkg = build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*atts)], basis=BASIS_M5, row=485)
        tag, dirn, st = "S5_t1", "solver", "S-1"
    else:
        atts = ssf_call("health_p1073741831_d222", n, site="S2")
        pkg = build("controls_a1", [X(L("gp", "gp", "controls_a1_pari", in_raw=True)), S2(*atts),
                                    S2(hs("health d444", "health_p1073741831_d444")),
                                    X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")), S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
                    gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])
        tag, dirn, st = "health_p1073741831_d222", "health", "S-2"
    drop = {a["lid"] for a in atts if a["attempt"] in set(drop_k)}
    return premise(pkg, drop=drop, drop_rb1=[(st, tag, k) for k in drop_rb1_k], counter=counter,
                   drop_ren_keys=[(st, tag, key) for key in drop_ren], note=note)


# =============================================================================================== BJ-0
P("=" * 118)
P("BJ-0 KNOWN-ANSWER CONTROL (CRI-4 (a)-(f)); method unchanged across objects")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK); RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, pair=None, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False, retained=False)
ka1 = build("cells_m5", [("L", p16)], raw="wrapper", basis=BASIS_M5)
ka1["designed"] = False
ka1["counters"]["S-1"]["attempts_total"] = 0
evaluate("KA-a1", "P-16 (os.fork at v2_solver.py 181 created the child; raise before STORE_FAST pid; wrapper writes raw)", ka1, ("RK", "RF"), ks=(0, 1))
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, pair=None, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False, retained=False)
ka2 = build("cells_m5", [("L", pf2)], raw="wrapper", basis=BASIS_M5)
ka2["designed"] = False
evaluate("KA-a2", "P-F2 after P-14a (raise at 214, then lk.release raises in run_child's finally; final traceback lacks _run_child_locked)", ka2, ("RK", "RF"), ks=(0, 1))
ka3 = build("cells_m5", [], raw="wrapper", basis=BASIS_M5)
ka3["designed"] = False
evaluate("KA-a3", "W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper.py 491-505)", ka3, ("RK", "RF"))

P("\n--- (b) failclosed AS WORDED (RF): FO-1 in both variants, foreign-file write failed / interrupted")
for vl, rep, p227, pair in (("C", "", False, None), ("B", "OK", True, CP)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (vl, wr, rc), "S5_t0", report=rep, rc=rc, p227=p227, pair=pair, exec_=False, escaped=True,
                    foreign_write=wr, outcome="refused_to_start" if vl == "C" else "crashed", in_raw=p227)
            q = build("cells_m5", [S1(fo)], basis=BASIS_M5, row=485)
            q["designed"] = False
            evaluate("KA-b-%s-%s-%d" % (vl, wr, rc), "FO-1 variant %s, foreign write %s, escaped exit %d" % (vl, wr, rc), q, ("RF", "RG", "RH", "RI"), ks=(0, 1))

P("\n--- (c) childend AS WORDED (RG): PB-3, a cells package with one SE-3 re-solve (RF, RH, RI for contrast)")
pb3 = build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*ssf_call("S5_t1", 2))], basis=BASIS_M5, row=485)
evaluate("KA-c", "PB-3 cells m = 5, S5_t1 re-solved once at S-1 (r3_resolve 224-238, 310)", pb3, ("RF", "RG", "RH", "RI"))

P("\n--- (d) gapattr AS WORDED (RH): CX-1 objects LR-1, LR-2, LR-3, LR-5 and LR-4 of review TASK-20260924-94cc33")
P("--- (e) the same objects under attcount with RI-1 (a) WEAKENED to 'N >= 1' (RIw) and AS WORDED (RI)")
LR = {
    "LR-1": ("S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent", dict(n=2, drop_k=(2,))),
    "LR-2": ("S-1 re-solve, 2 attempts, attempt 1's launch record absent", dict(n=2, drop_k=(1,))),
    "LR-3": ("S-1 re-solve, 3 attempts, attempt 2's launch record absent", dict(n=3, drop_k=(2,))),
    "LR-4": ("S-1 re-solve, 3 attempts, attempts 2 and 3 absent", dict(n=3, drop_k=(2, 3))),
    "LR-5": ("S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent", dict(n=2, drop_k=(2,), site="S2")),
}
for key, (lab, kw) in LR.items():
    evaluate(key, lab, cell5_resolved(**kw), ("RH", "RIw", "RI"))
P("\n  every single removal among 2, 3 and 6 attempts at S-1 (RH-6 (i) (19) third case; RI-3 (24)):")
single = []
for n in (2, 3, 6):
    for k in range(1, n + 1):
        q = cell5_resolved(n=n, drop_k=(k,))
        res = {rs: (verdict(q, rs, "Mc"), definitions(q, rs), gaps(q, rs)[1]) for rs in ("RH", "RIw", "RI")}
        single.append({"attempts": n, "removed": k, **{rs: {"verdict": v[0], "defs": v[1], "named": v[2]} for rs, v in res.items()}})
        P("   n=%d removed=%d | RH %s %s | RIw %s %s | RI %s named=%d" % (n, k, res["RH"][0], res["RH"][1], res["RIw"][0], res["RIw"][1],
                                                                        res["RI"][0], len(res["RI"][2])))
OUT["single_removals"] = single


# =============================================================================================== BJ-0 (f): listing check
PK = json.load(open(os.path.join(SCR, "pkgread.json")))
GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
# frozen call-site naming for S-1 calls whose argv raw-result.json does not carry (CRI-9 reconstruction rule):
FROZEN_GB = {"anchor_comparator_system": True}                    # v2_driver.py 711 gb_only=True
FROZEN_NONGB_PREFIX = ("ctl_identity_", "ctl_rawx_", "ctl_planted_")   # v2_driver.py 786, 787, 841 (gb_only default False)


def reconstruct(pk):
    """CRI-9: RECONSTRUCTED launch set and counts of an archived r3 package. Rule: child/<tag>.spec.json -> one child-job
    launch record; solver|health/<tag>.ms.log -> one msolve launch record (one more per <tag>.ms.log.ssf-attempt<k>);
    solver/<tag>.callgrind.stdout -> one callgrind record; comparator/stdout.log -> one comparator record;
    pari/<tag>.gp.stdout -> one gp record. The -g / -P flag and the per-tag RB-1 / RL-2 counts are taken, INDEPENDENTLY of
    the listing, from raw-result.json's solver argv where recorded, else from the frozen call site's gb_only argument.
    Events and site counters are the r3 solver-events.json's. child_end 'exec' where the child's outputs exist."""
    rd = RUNS + "/" + pk
    ents = PK["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    se = PK["packages"][pk]["files"]["solver-events.json"]["json"]
    raw = PK["packages"][pk]["files"]["raw-result.json"]["json"]
    argvs = []

    def walk(o):
        if isinstance(o, dict):
            for k2, v in o.items():
                if k2 == "argv" and isinstance(v, list):
                    argvs.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(raw)
    raw_s1 = {}
    for a in argvs:
        if a and a[0] == MSOLVE and "-f" in a:
            t = os.path.basename(a[a.index("-f") + 1])[:-3]
            raw_s1.setdefault(t, []).append("-g" in a)
    recs, order, rb1, rl2, src = [], 0, [], [], {}
    sp = {}
    for rel, v in PK["packages"][pk]["specs"].items():
        sp[rd + "/" + rel] = {"out": v["json"].get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se_ = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid, kind = "childjob:" + t, "childjob"
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            if t in raw_s1:
                gb = raw_s1[t][0]
                src[t] = "raw-result.json solver argv (%s)" % ("-g 1" if gb else "-P 1")
            elif t in FROZEN_GB:
                gb = FROZEN_GB[t]
                src[t] = "frozen call site v2_driver.py 711 (gb_only=True)"
            elif t.startswith(FROZEN_NONGB_PREFIX):
                gb = False
                src[t] = "frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)"
            else:
                gb = None
                src[t] = "UNKNOWN"
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out"] + (["-g", "1"] if gb else ["-P", "1"])
            so, se_, ce, lid, kind = rd + "/" + rel, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t, "msolve"
            site = SITE_OF_DIR[d]
            if gb:
                rl2.append({"tag": t, "lid": lid, "pair": CP})
            elif gb is False:
                rb1.append({"site": site, "tag": t, "k": 1, "lid": lid, "pair": CP})
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v", "2", "-t", "1",
                    "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se_, ce, lid, kind = rd + "/" + rel, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t, "callgrind"
        elif rel == "comparator/stdout.log":
            argv, so, se_, ce, lid, kind = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se_, ce, lid, kind = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/" + rel, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t, "gp"
        if lid:
            recs.append({"id": lid, "ordinal": order, "argv": argv, "stdout": so, "stderr": se_, "child_end": ce, "kind": kind})
            order += 1
    events = []
    for sname, sec in se["sites"].items():
        for e in sec.get("events") or []:
            events.append({"site": sname, "dir": "solver" if sname == "v2_driver.solve" else "health", "tag": e.get("tag"),
                           "attempts": e.get("attempts"), "accepted_attempt": e.get("accepted_attempt"), "renamed_files": e.get("renamed_files") or {}})
    c1 = se["sites"]["v2_driver.solve"]["counters"]
    c2 = se["sites"]["a1_health.run_system"]["counters"]
    counters = {"S-1": {"attempts_total": c1["attempts_total"], "passthrough_calls_gb_only_true": c1["passthrough_calls_gb_only_true"],
                        "wrapped_calls": c1["wrapped_calls"]},
                "S-2": {"attempts_total": c2["attempts_total"], "wrapped_calls": c2["wrapped_calls"]}}
    s3 = collections.Counter(r.get("tag") for r in se["sites"]["v2_driver.solve/callgrind"].get("records") or [])
    files = {r: ("?", "listed") for r in rels}
    pkg = dict(kind="gate", launches=[], raw="driver", gate=True, basis=None, row=478, rd=rd, rd_check=rd, files=files, events=events,
               counters=counters, rb1=rb1, rl2=rl2, raw_pairs=True, designed=True, altered_after_manifest=False, dup=[], note=[])
    return pkg, recs, sp, src, s3, c1


def listing_check(rule):
    res = {}
    P("\n--- LISTING CHECK under %s (launch sets RECONSTRUCTED, CRI-9)" % rule)
    for pk in GATE:
        pkg, recs, sp, src, s3, c1 = reconstruct(pk)
        rd = pkg["rd"]
        named, gapfiles, restrict, dup_ids = ([], set(), {}, set())
        if rule in ("RI", "RIw"):
            named, gapfiles, restrict, dup_ids = ri1(pkg, recs, "worded" if rule == "RI" else "weak")
        att = {}
        for rel in sorted(pkg["files"]):
            h = attr_rh1(rd, rel, recs, sp, pkg["events"], restrict or None)
            if not h and nonlaunch(rel):
                h = [("-", nonlaunch(rel))]
            if dup_ids:
                h = [x for x in h if x[0] not in dup_ids]
            if rel in gapfiles:
                h = []
            att[rel] = h
        un = sorted(r for r, h in att.items() if not h)
        by = collections.Counter((h[0][1].split(" ")[0] if h else "NONE") for h in att.values())
        kinds = collections.Counter(r["kind"] for r in recs)
        P("  %s: %d files in the five directories; %d reconstructed launch records %s; first clause %s; named gaps %d; unattributed %d"
          % (pk, len(att), len(recs), dict(sorted(kinds.items())), dict(sorted(by.items())), len(named), len(un)))
        for u in un:
            P("    UNATTRIBUTED " + u)
        for n in named:
            P("    NAMED " + n)
        # count table (BJ-2 (2))
        L_ = collections.Counter()
        for r in recs:
            for d in ("solver", "health"):
                m = re.fullmatch(re.escape(rd + "/" + d + "/") + r"(?P<tag>.+)\.ms\.log", r["stdout"])
                if m:
                    L_[(d, m.group("tag"))] += 1
        rb1c = collections.Counter((SITE_OF_DIR_R[r["site"]], r["tag"]) for r in pkg["rb1"])
        rl2c = collections.Counter(("solver", r["tag"]) for r in pkg["rl2"])
        table = []
        for (d, t) in sorted(set(L_) | set(rb1c) | set(rl2c)):
            N = L_[(d, t)]
            ev = [e for e in pkg["events"] if e["dir"] == d and e["tag"] == t]
            row = {"site": SITE_OF_DIR[d], "tag": t, "N_launch_records": N, "RB1_attempt_records": rb1c[(d, t)], "RL2_passthrough_records": rl2c[(d, t)],
                   "event": len(ev), "ii": "no event (not evaluated)" if not ev else "see events", "source_of_RB1_RL2": src.get(t),
                   "i_holds": N == rb1c[(d, t)] + rl2c[(d, t)]}
            table.append(row)
        site_rows = []
        for d, site in (("solver", "S-1"), ("health", "S-2")):
            n = sum(v for (dd, _t), v in L_.items() if dd == d)
            c = pkg["counters"][site]
            want = c["attempts_total"] + (c.get("passthrough_calls_gb_only_true", 0) if site == "S-1" else 0)
            site_rows.append({"site": site, "launch_records_at_dir_ms_log": n, "counters": c, "iii_holds": n == want})
        cg_paths = collections.Counter(r["stdout"] for r in recs if r["kind"] == "callgrind")
        cg_rows = {"callgrind_records_reconstructed": sum(cg_paths.values()), "S3_records_in_r3_solver_events": sum(s3.values()),
                   "per_tag_equal": all(s3.get(r["stdout"].split("/")[-1][:-len(".callgrind.stdout")], 0) == 1 for r in recs if r["kind"] == "callgrind"),
                   "S3_callgrind_children_observed": PK["packages"][pk]["files"]["solver-events.json"]["json"]["sites"]["v2_driver.solve/callgrind"]["counters"]["callgrind_children_observed"]}
        other = collections.Counter(r["stdout"] for r in recs if r["kind"] != "msolve")
        dup_other = {k.replace(rd + "/", ""): v for k, v in other.items() if v > 1}
        mism = [r for r in table if not r["i_holds"]] + [s for s in site_rows if not s["iii_holds"]]
        P("    count table: %d (site, tag) rows; (i) mismatches %d; site rows %s; events %d; callgrind %s; duplicate other stdout paths %s"
          % (len(table), sum(1 for r in table if not r["i_holds"]), [(s["site"], s["launch_records_at_dir_ms_log"], s["counters"], s["iii_holds"]) for s in site_rows],
             len(pkg["events"]), cg_rows, dup_other))
        for r in table:
            P("      %-4s %-40s N=%d RB-1=%d RL-2=%d event=%d (i)=%s  [%s]" % (r["site"], r["tag"], r["N_launch_records"], r["RB1_attempt_records"],
                                                                       r["RL2_passthrough_records"], r["event"], r["i_holds"], r["source_of_RB1_RL2"]))
        res[pk] = {"n_files": len(att), "n_records": len(recs), "record_kinds": dict(kinds), "first_clause": dict(by), "unattributed": un,
                   "named": named, "count_table": table, "site_rows": site_rows, "callgrind": cg_rows, "duplicate_other_stdout": dup_other,
                   "mismatches": mism, "attribution": {r: att[r] for r in att}}
    OUT["listing_" + rule] = res
    return res


P("\n--- (f) LISTING CHECK under attcount (RI) on the four archived r3 gate packages; RH for contrast")
listing_check("RH")
listing_check("RI")

exec(compile(open(os.path.join(SCR, 'rteval_v2_objects.py')).read(), 'rteval_v2_objects.py', 'exec'))
with open(os.path.join(SCR, "rteval_v2.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rteval_v2.json with %d keys" % len(OUT))
````

### `rteval_v2_objects.py`

- sha256: `ce59195533c0ff85ca25c88e6f4d22d55bb91e8a6504bf629ad1469de0067151`
- bytes: 20677; lines: 222
- argv: `(executed inside rteval_v2.py by exec(compile(...)))`
- role: the BJ-1..BJ-4 objects; defines no rule function

````text
# TASK-20260924-be2daf scratch: the objects of BJ-1..BJ-4, executed INSIDE rteval_v2.py after its BJ-0 section, with the
# SAME rule functions (layer 1 attribution, RI-1, verdicts, definitions) that BJ-0 used. No rule function is defined or
# changed here; this file only builds packages (truth + premises) and calls evaluate() / gaps() / verdict().

P("\n" + "=" * 118)
P("BJ-1 FAIL-OPEN SEARCH UNDER attcount (RI); RH for contrast; same method as BJ-0")
BJ1 = ("RH", "RI")

P("\n--- (1) a launch record absent, per count RI-1 (a) reads")
base_ne = lambda: build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(ms("S5_t1", "S5_t1"))], basis=BASIS_M5, row=485)
evaluate("LN-1", "non-event S-1 tag S5_t1: its launch record absent (RB-1 attempt record and counters present)",
         premise(base_ne(), drop={"S5_t1"}), BJ1)
evaluate("LN-2", "non-event S-1 tag: launch record AND its RB-1 attempt record absent",
         premise(base_ne(), drop={"S5_t1"}, drop_rb1=[("S-1", "S5_t1", 1)]), BJ1)
evaluate("LN-3", "non-event S-1 tag: launch record, RB-1 attempt record and one attempts_total increment all absent (RGL-9 consistent loss)",
         premise(base_ne(), drop={"S5_t1"}, drop_rb1=[("S-1", "S5_t1", 1)], counter={"S-1": {"attempts_total": -1}}), BJ1)
gbpk = lambda: build("anchor", [X(L("comparator", "comparator", "comparator")), X(cj("anchor_S4", "anchor_S4")),
                                S1(ms("anchor_v2_t0", "anchor_v2_t0", gb=True)), S1(ms("anchor_comparator_system", "anchor_comparator_system", gb=True))],
                     gate=True, row=478)
evaluate("LN-4", "gb_only pass-through anchor_comparator_system: its launch record absent (RL-2 record present)",
         premise(gbpk(), drop={"anchor_comparator_system"}), BJ1)
evaluate("LN-4b", "gb_only pass-through: launch record, RL-2 record and one passthrough increment absent (consistent)",
         premise(gbpk(), drop={"anchor_comparator_system"}, drop_rl2=["anchor_comparator_system"],
                 counter={"S-1": {"passthrough_calls_gb_only_true": -1}}), BJ1)
a1pk = lambda: build("controls_a1", [X(L("gp", "gp", "controls_a1_pari")), S2(hs("health d222", "health_p1073741831_d222")),
                                     S2(hs("health d444", "health_p1073741831_d444")), X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")),
                                     S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
                     gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])
evaluate("LN-5", "S-2 non-event health tag d222: its launch record absent (RB-1 present)", premise(a1pk(), drop={"health d222"}), BJ1)

P("\n--- (1) a launch record absent together with one other counted entry, at an event tag (2 attempts at S-1)")
evaluate("LE-1", "event tag S5_t1: attempt 2's launch record AND its RB-1 attempt record absent",
         cell5_resolved(n=2, drop_k=(2,), drop_rb1_k=(2,)), BJ1)
evaluate("LE-2", "event tag S5_t1: attempt 1's launch record AND renamed_files['attempt1'] absent",
         cell5_resolved(n=2, drop_k=(1,), drop_ren=("attempt1",)), BJ1)


def _trim(e):
    if e["tag"] == "S5_t1":
        e["attempts"] = e["attempts"][:1]
        e["accepted_attempt"] = 1
        e["renamed_files"] = {}


evaluate("LE-3", "event tag: the FINAL attempt lost CONSISTENTLY (launch record, RB-1 k=2, attempts entry, accepted_attempt -> 1, renamed key, attempts_total -1)",
         premise(build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*ssf_call("S5_t1", 2))], basis=BASIS_M5, row=485),
                 drop={"S5_t1 attempt 2"}, drop_rb1=[("S-1", "S5_t1", 2)], counter={"S-1": {"attempts_total": -1}}, event_edit=_trim), BJ1)

P("\n--- (2) launch kinds outside the S-1 / S-2 counts: a record absent")
m4 = lambda cgkw: build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0", "raw_t0")),
                                     X(cg("callgrind raw_t0", "raw_t0", **cgkw))], basis=BASIS_M4, row=488)
evaluate("LC-1", "cells m = 4: callgrind child of raw_t0 exec'd normally; its launch record absent", premise(m4({}), drop={"callgrind raw_t0"}), BJ1)
P7 = dict(opened=False, report="", rc=99, p227=False, pair=None, exec_=False, outcome="refused_to_start", t_en=0, value=0)
evaluate("CX-A-control", "cells m = 4: callgrind child of raw_t0 created, os.open(stdout_path) fails in the child (v2_solver 188 -> 206 -> 208: exit 99, empty report); its record PRESENT",
         m4(P7), ALL[:5] + ("RI",))
evaluate("CX-A", "the same package with the callgrind child's launch record ABSENT (lost-record premise)",
         premise(m4(P7), drop={"callgrind raw_t0"}, note="the child left no file in the five directories; RI-1 counts S-1 / S-2 msolve launches only"),
         ("RF", "RG", "RH", "RI"))
fxpk = lambda: build("fixture", [X(cj("fixture_S3", "fixture_S3")), X(cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid")),
                                 S1(ms("fx_reg0_raw_x", "fx_reg0_raw_x")), X(cg("cg fx_reg0_raw_x", "fx_reg0_raw_x", **P7)),
                                 S1(ms("fx_reg0_S3", "fx_reg0_S3")), X(cg("cg fx_reg0_S3", "fx_reg0_S3"))], gate=True, row=478)
evaluate("CX-A-G2", "fixture (G2 shape): one callgrind child P-7 (no file), its launch record ABSENT", premise(fxpk(), drop={"cg fx_reg0_raw_x"}), ("RH", "RI"))
gpP7 = lambda: build("controls_a1", [X(L("gp", "gp", "controls_a1_pari", **P7)), S2(hs("health d222", "health_p1073741831_d222")),
                                     S2(hs("health d444", "health_p1073741831_d444")), X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")),
                                     S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
                     gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])
evaluate("CX-A-gp", "controls_a1: the gp child P-7 (no gp.stdout / gp.stderr; the .gp script is on the non-launch list), its record ABSENT (the package's own run_status is 'failed': check (b) fails)",
         premise(gpP7(), drop={"gp"}), ("RH", "RI"))
cmpP7 = build("anchor", [X(L("comparator", "comparator", "comparator", **P7))], gate=True, row=478)
evaluate("CX-A-cmp", "anchor-identity: the comparator child P-7 (the driver returns at v2_driver 656-659 before any other launch), its record ABSENT",
         premise(cmpP7, drop={"comparator"}), ("RH", "RI"))
cjP7 = build("controls", [X(cj("ctl_S3", "ctl_S3", **P7)), S1(ms("ctl_planted_S3", "ctl_planted_S3"))], gate=True, row=478)
evaluate("LCJ-1", "controls: a build child job P-7 (no .stdout / .stderr), its record ABSENT: the driver-written spec file remains",
         premise(cjP7, drop={"ctl_S3"}), ("RH", "RI"))
evaluate("LN-6", "non-event S-1 launch refused before fork (class A, input not retained): record, RB-1 and attempts_total consistently absent",
         premise(build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(ms("S5_t1", "S5_t1", created=False, p227=False, pair=None, exec_=False, report=None,
                                                                    rc=None, outcome="refused_to_start", retained=False))], basis=BASIS_M5, row=485),
                 drop={"S5_t1"}, drop_rb1=[("S-1", "S5_t1", 1)], counter={"S-1": {"attempts_total": -1}}), BJ1)
msP7 = lambda: build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(ms("S5_t1", "S5_t1", retained=False, **P7))], basis=BASIS_M5, row=485)
evaluate("LN-7a", "non-event S-1 msolve child P-7 (no file; input not retained): its launch record absent", premise(msP7(), drop={"S5_t1"}), BJ1)
evaluate("LN-7b", "the same with record, RB-1 and attempts_total consistently absent (RGL-9's premise)",
         premise(msP7(), drop={"S5_t1"}, drop_rb1=[("S-1", "S5_t1", 1)], counter={"S-1": {"attempts_total": -1}}), BJ1)

P("\n--- (2) residual premise: a tag solved TWICE in one package (no frozen path found; BJ-2 (1))")
tw = lambda: build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0 call1", "raw_t0")), X(cg("cg raw_t0 call1", "raw_t0")),
                                S1(ms("raw_t0 call2", "raw_t0")), X(cg("cg raw_t0 call2", "raw_t0"))], basis=BASIS_M4, row=488)
evaluate("TW-1", "raw_t0 solved twice with callgrind both times, every record present (HYPOTHETICAL code)", tw(), BJ1)
evaluate("TW-2", "the same, the FIRST callgrind launch record absent", premise(tw(), drop={"cg raw_t0 call1"}), BJ1)
evaluate("TW-3", "the same, the first msolve launch record absent", premise(tw(), drop={"raw_t0 call1"}), BJ1)

P("\n" + "=" * 118)
P("BJ-2 NO PLANNED-BASIS REFUSAL UNDER attcount (RI): normal outcomes of every launch kind; RH for contrast")
BJ2 = ("RH", "RI")
N = [
    ("N-1", "cells m = 5 measured (S5_t0 retained, S5_t1 not retained)", build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(ms("S5_t1", "S5_t1", retained=False))], basis=BASIS_M5, row=485)),
    ("N-2", "cells m = 5 not_measured (timeout, memory_exhausted after exec; no .ms.out)",
     build("cells_m5", [S1(ms("S5_t0", "S5_t0", rc=-9, outcome="timeout")), S1(ms("S5_t1", "S5_t1", rc=-11, outcome="memory_exhausted"))], basis=BASIS_M5, row=485)),
    ("N-3", "cells m = 4 raw_grid measured, callgrind ok (.callgrind.out removed at v2_solver 549)",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0", "raw_t0")), X(cg("cg raw_t0", "raw_t0"))], basis=BASIS_M4, row=488)),
    ("N-4", "cells m = 4 raw_grid child crashed after exec (partial .npz)",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="crashed", rc=1, partial_npz=True)), X(cj("grid_raw_t1", "grid_raw_t1", job="grid")),
                        S1(ms("raw_t1", "raw_t1"))], basis=BASIS_M4, row=488)),
    ("N-5", "SE-3 re-solve at S-1, 2 attempts", build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*ssf_call("S5_t1", 2))], basis=BASIS_M5, row=485)),
    ("N-5b", "SE-3 re-solve at S-1, 6 attempts (K + 1; still SSF after the last attempt)",
     build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*[ms("S5_t1 attempt %d" % k, "S5_t1", outcome="ssf", in_raw=(k == 6)) for k in range(1, 7)])], basis=BASIS_M5, row=485)),
    ("N-5c", "SE-3 re-solve at S-1 on the callgrind target of an m = 4 cell: 3 attempts, final ok, one callgrind child",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(*ssf_call("raw_t0", 3)), X(cg("cg raw_t0", "raw_t0"))], basis=BASIS_M4, row=488)),
    ("N-6", "controls_a1: HR-3 re-solve at S-2 (2 attempts), gp child, health d444, build, S-1 solve",
     build("controls_a1", [X(L("gp", "gp", "controls_a1_pari")), S2(*ssf_call("health_p1073741831_d222", 2, site="S2")), S2(hs("health d444", "health_p1073741831_d444")),
                           X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")), S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
           gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])),
    ("N-6b", "controls_a1: health pattern d222 fails its checks, retried under tag d222_seed2 (a1_health 238-242)",
     build("controls_a1", [X(L("gp", "gp", "controls_a1_pari")), S2(hs("health d222", "health_p1073741831_d222")), S2(hs("health d222 seed2", "health_p1073741831_d222_seed2")),
                           S2(hs("health d444", "health_p1073741831_d444")), X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")),
                           S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
           gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])),
    ("N-7", "failing callgrind child (valgrind exits nonzero after writing its out file)",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0", "raw_t0")), X(cg("cg raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True))], basis=BASIS_M4, row=488)),
    ("N-8", "timed-out callgrind child (SIGKILL, no out file)",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0", "raw_t0")), X(cg("cg raw_t0", "raw_t0", rc=-9, outcome="timeout"))], basis=BASIS_M4, row=488)),
    ("N-9", "build package: cached builds (out under the cache directory)",
     build("build", [X(cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True)), X(cj("build S4", "build_4111_ecgfp5_shaped_S4_m4", cached=True))], basis=BASIS_BUILD, row=483)),
    ("N-10", "fixture4: uncached builds and solves", build("fixture4", [X(cj("f4_S4", "f4_S4")), S1(ms("f4_t0_S4", "f4_t0_S4"))], row=481)),
    ("N-11", "child jobs on refusal paths: refused meta, refused before fork (class A), ERR setrlimit (class C)",
     build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="refused_meta")),
                        X(cj("grid_raw_t1", "grid_raw_t1", job="grid", created=False, p227=False, pair=None, exec_=False, report=None, rc=None, outcome="refused_to_start")),
                        X(cj("grid_raw_t2", "grid_raw_t2", job="grid", report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start", t_en=0, value=0)),
                        S1(ms("raw_t3", "raw_t3"))], basis=BASIS_M4, row=488)),
    ("N-11b", "an S-1 attempt refused before fork (class A: another solver process, EC-10) in a measured cell",
     build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(ms("S5_t1", "S5_t1", created=False, p227=False, pair=None, exec_=False, report=None, rc=None, outcome="refused_to_start"))],
           basis=BASIS_M5, row=485)),
    ("N-12", "anchor-identity: comparator, uncached build, gb_only solves", gbpk()),
    ("N-13", "Z-C5 (no launch)", build("cells_m5", [], basis=BASIS_M5, row=486)),
]
for key, lab, pkg in N:
    evaluate(key, lab, pkg, BJ2, variants=("Mr",))

P("\n--- RKR-4 (b) rows (readbackclose-census.md 476-492) that are PASS or PASS_ZL there, under RI")
ROWS = [
    ("row-478", "G1..G4 completed_valid (fixture shape: builds, raw grids, solves, callgrind)",
     build("fixture", [X(cj("fixture_S3", "fixture_S3")), X(cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid")), S1(ms("fx_reg0_raw_x", "fx_reg0_raw_x")),
                       X(cg("cg fx_reg0_raw_x", "fx_reg0_raw_x")), S1(ms("fx_reg0_S3", "fx_reg0_S3")), X(cg("cg fx_reg0_S3", "fx_reg0_S3"))], gate=True, row=478)),
    ("row-480", "controls_a1 image", a1pk()),
    ("row-481", "fixture4 launched", build("fixture4", [X(cj("f4_S4", "f4_S4")), S1(ms("f4_t0_S4", "f4_t0_S4"))], row=481)),
    ("row-482", "Z-F4 (zero call)", build("fixture4", [], row=482)),
    ("row-483", "build (cached)", build("build", [X(cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True))], basis=BASIS_BUILD, row=483)),
    ("row-485", "cells m = 5 measured", build("cells_m5", [S1(ms("S5_t0", "S5_t0"))], basis=BASIS_M5, row=485)),
    ("row-485b", "cells m = 5 measured, one SE-3 re-solve", build("cells_m5", [S1(ms("S5_t0", "S5_t0")), S1(*ssf_call("S5_t1", 2))], basis=BASIS_M5, row=485)),
    ("row-486", "Z-C5", build("cells_m5", [], basis=BASIS_M5, row=486)),
    ("row-488", "cells m = 4", build("cells_m4", [X(cj("grid_raw_t0", "grid_raw_t0", job="grid")), S1(ms("raw_t0", "raw_t0")), X(cg("cg raw_t0", "raw_t0"))], basis=BASIS_M4, row=488)),
    ("row-489", "aggregate v2", build("aggregate", [], basis="X-10", row=489)),
]
for key, lab, pkg in ROWS:
    evaluate(key, lab, pkg, ("RF", "RH", "RI"), variants=("Mr",))

P("\n" + "=" * 118)
P("BJ-3 CAP-MISMATCH OUTCOMES (RH-2 with RI-5 (a)) under RI; RF / RH for contrast")
p8 = dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start", t_en=0, value=0)
p9 = dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed", t_en=0, value=0)
for kind, basis in (("cells_m5", BASIS_M5), ("cells_m4", BASIS_M4)):
    evaluate("CM-%s-P8" % kind, "%s: every launch P-8" % kind, build(kind, [S1(ms("a", "t0", **p8)), S1(ms("b", "t1", **p8))], basis=basis), ("RF", "RH", "RI"), variants=("Mr",))
    evaluate("CM-%s-P9" % kind, "%s: every launch P-9" % kind, build(kind, [S1(ms("a", "t0", **p9)), S1(ms("b", "t1", **p9))], basis=basis), ("RF", "RH", "RI"), variants=("Mr",))
    evaluate("CM-%s-mix" % kind, "%s: one P-9 launch mixed with one measured launch" % kind, build(kind, [S1(ms("a", "t0", **p9)), S1(ms("b", "t1"))], basis=basis),
             ("RF", "RH", "RI"), variants=("Mr",))
evaluate("CM-build-mix", "build: one P-9 build child mixed with one built child", build("build", [X(cj("b1", "b1", cached=True, **p9)), X(cj("b2", "b2", cached=True))], basis=BASIS_BUILD),
         ("RF", "RH", "RI"), variants=("Mr",))
evaluate("CM-controls", "controls (gate): one P-9 build child", build("controls", [X(cj("ctl_S3", "ctl_S3", **p9)), S1(ms("ok", "ctl_planted_S3"))], gate=True, row=478),
         ("RF", "RH", "RI"), variants=("Mr",))

P("\n" + "=" * 118)
P("BJ-4 RI-3 (19)-(27) DERIVED on development objects altered IN PLACE (V-7 evaluated: altered after the manifest)")


def dev(pkg, **kw):
    q = premise(pkg, altered=True, **kw)
    return q


def dual(key, label, pkg, rule_sets):
    """Report the gap-level result (scratch evaluator: RL-3 list incl. named gaps) and the verdict with and without V-7."""
    P("\n### %s: %s" % (key, label))
    rows = []
    for rs in rule_sets:
        g, named, _a = gaps(pkg, rs)
        v7 = verdict(pkg, rs, "Mr")
        q = dict(pkg)
        q["altered_after_manifest"] = False
        nov7 = verdict(q, rs, "Mr")
        P("  %-3s gaps %-60s named %-3d verdict(with V-7) %-7s verdict(scratch, no V-7) %s" % (rs, str(g)[:60], len(named), v7, nov7))
        for n in named:
            P("        NAMED " + n)
        rows.append({"rule_set": rs, "gaps": g, "named": named, "verdict_with_V7": v7, "verdict_without_V7": nov7})
    OUT[key] = {"label": label, "rows": rows}


e19 = lambda: build("controls", [X(cj("ctl_S3", "ctl_S3")), S1(ms("ctl_planted_S3", "ctl_planted_S3")), S1(*ssf_call("ctl_identity_random", 2))], gate=True, row=478)
dual("RI3-19a", "(19) unaltered dev package with an SE-3 re-solve at S-1 (stand-in SSF once): renamed attempt-1 files attributed", premise(e19()), ("RH", "RI"))
dual("RI3-19b", "(19) the same with renamed_files['attempt1'] removed in place", dev(e19(), drop_ren_keys=[("S-1", "ctl_identity_random", "attempt1")]), ("RH", "RI"))
dual("RI3-19c", "(19) the same with one launch record of the tag removed in place (attempt 2)", dev(e19(), drop={"ctl_identity_random attempt 2"}), ("RH", "RI"))
e20 = lambda: build("controls_a1", [X(L("gp", "gp", "controls_a1_pari")), S2(*ssf_call("health_p1073741831_d222", 2, site="S2")), S2(hs("health d444", "health_p1073741831_d444")),
                                    X(cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")), S1(ms("ctl_a1_planted_S3_rescaled", "ctl_a1_planted_S3_rescaled"))],
                    gate=True, row=480, extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])
dual("RI3-20a", "(20) unaltered dev package with an HR-3 re-solve at S-2", premise(e20()), ("RH", "RI"))
dual("RI3-20c", "(20) one launch record of the S-2 tag removed in place", dev(e20(), drop={"health_p1073741831_d222 attempt 2"}), ("RH", "RI"))
e22 = lambda: build("controls", [X(cj("ctl_S3", "ctl_S3")), X(cj("ctl_raw_random", "ctl_raw_random", job="grid")), S1(ms("ctl_planted_S3", "ctl_planted_S3"))], gate=True, row=478)
dual("RI3-22a", "(22) uncached build child job ctl_S3: its launch record removed in place", dev(e22(), drop={"ctl_S3"}), ("RH", "RI"))
dual("RI3-22b", "(22) raw_grid child job ctl_raw_random: its launch record removed in place", dev(e22(), drop={"ctl_raw_random"}), ("RH", "RI"))
for key, (lab, kw) in LR.items():
    q = cell5_resolved(**kw)
    q["altered_after_manifest"] = True
    dual("RI3-24-" + key, "(24)/(25) %s, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)" % lab, q, ("RI", "RIx"))
dual("RI3-26", "(26) unaltered dev packages (positive control): N-5 shape and N-6 shape", premise(N[4][2]), ("RI",))
dual("RI3-26b", "(26) unaltered N-6 shape", premise(N[7][2]), ("RI",))
dual("RI3-27a", "(27) non-event S-1 tag: its RB-1 attempt record removed in place", dev(base_ne(), drop_rb1=[("S-1", "S5_t1", 1)]), ("RI",))
dual("RI3-27b", "(27) a launch record duplicated in place (S-1 tag S5_t1)", dev(base_ne(), dup=["S5_t1"]), ("RI",))
dual("RI3-27c", "(27) a site counter decremented in place (S-1 attempts_total - 1)", dev(base_ne(), counter={"S-1": {"attempts_total": -1}}), ("RI",))
dual("RI3-27d", "(27) a child-job launch record duplicated in place", dev(e22(), dup=["ctl_S3"]), ("RI",))

P("\n--- callgrind: reconstructed callgrind launch records vs the r3 S-3 (CG-3) records per package (an independent count RI-1 does not read)")
for pk in GATE:
    r = OUT["listing_RI"][pk]["callgrind"]
    P("  %s: %s" % (pk, r))
````

### `rteval_v2.out`

- sha256: `cd9880535dd04e0abb2e42f5579cc805bc67e7f0d12316cf321aeef28887f724`
- bytes: 144055; lines: 1350
- argv: `(stdout of rteval_v2.py)`
- role: FINAL evaluator output; lines 1-544 are byte-identical to rteval_v1.out lines 1-544 (the BJ-0 section)

````text
======================================================================================================================
BJ-0 KNOWN-ANSWER CONTROL (CRI-4 (a)-(f)); method unchanged across objects

--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK); RF for contrast

### KA-a1: P-16 (os.fork at v2_solver.py 181 created the child; raise before STORE_FAST pid; wrapper writes raw)
  record[P-16 raise at 181         ] RK  child_created=False class=None | (iii): a created child recorded child_created false
  record[P-16 raise at 181         ] RF  child_created=undetermined class=None
  package RK  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] FAIL-OPEN ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)', '(v)'] 

### KA-a2: P-F2 after P-14a (raise at 214, then lk.release raises in run_child's finally; final traceback lacks _run_child_locked)
  record[P-F2 after P-14a          ] RK  child_created=False class=None | (iii): a created child recorded child_created false
  record[P-F2 after P-14a          ] RF  child_created=True class=None
  package RK  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] FAIL-OPEN ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)', '(v)'] 

### KA-a3: W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper.py 491-505)
  package RK  k=0 Mr verdict PASS_ZL items ['66-67']        defs ['(v)']                        FAIL-OPEN ['(v)']
  package RK  k=0 Mc verdict PASS_ZL items ['66-67']        defs ['(v)']                        FAIL-OPEN ['(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(v)']                        
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(v)']                        

--- (b) failclosed AS WORDED (RF): FO-1 in both variants, foreign-file write failed / interrupted

### KA-b-C-failed-1: FO-1 variant C, foreign write failed, escaped exit 1
  record[FO-1 C failed rc1         ] RF  child_created=True class=C | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 C failed rc1         ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C failed rc1         ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C failed rc1         ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RG  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        

### KA-b-C-failed--2: FO-1 variant C, foreign write failed, escaped exit -2
  record[FO-1 C failed rc-2        ] RF  child_created=True class=C | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 C failed rc-2        ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C failed rc-2        ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C failed rc-2        ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RG  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        

### KA-b-C-interrupted-1: FO-1 variant C, foreign write interrupted, escaped exit 1
  record[FO-1 C interrupted rc1    ] RF  child_created=True class=C | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 C interrupted rc1    ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C interrupted rc1    ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C interrupted rc1    ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RG  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        

### KA-b-C-interrupted--2: FO-1 variant C, foreign write interrupted, escaped exit -2
  record[FO-1 C interrupted rc-2   ] RF  child_created=True class=C | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 C interrupted rc-2   ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C interrupted rc-2   ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 C interrupted rc-2   ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=0 Mc verdict FAIL    items ['66-67']        defs ['(iv)']                       
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RG  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        infrastructure-stop (RG-2)
  package RI  k=1 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=1 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        

### KA-b-B-failed-1: FO-1 variant B, foreign write failed, escaped exit 1
  record[FO-1 B failed rc1         ] RF  child_created=True class=B | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 B failed rc1         ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B failed rc1         ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B failed rc1         ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []               defs []                             
  package RG  k=0 Mc verdict FAIL    items []               defs []                             
  package RG  k=1 Mr verdict FAIL    items []               defs []                             
  package RG  k=1 Mc verdict FAIL    items []               defs []                             
  package RH  k=0 Mr verdict FAIL    items []               defs []                             
  package RH  k=0 Mc verdict FAIL    items []               defs []                             
  package RH  k=1 Mr verdict FAIL    items []               defs []                             
  package RH  k=1 Mc verdict FAIL    items []               defs []                             
  package RI  k=0 Mr verdict FAIL    items []               defs []                             
  package RI  k=0 Mc verdict FAIL    items []               defs []                             
  package RI  k=1 Mr verdict FAIL    items []               defs []                             
  package RI  k=1 Mc verdict FAIL    items []               defs []                             

### KA-b-B-failed--2: FO-1 variant B, foreign write failed, escaped exit -2
  record[FO-1 B failed rc-2        ] RF  child_created=True class=B | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 B failed rc-2        ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B failed rc-2        ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B failed rc-2        ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []               defs []                             
  package RG  k=0 Mc verdict FAIL    items []               defs []                             
  package RG  k=1 Mr verdict FAIL    items []               defs []                             
  package RG  k=1 Mc verdict FAIL    items []               defs []                             
  package RH  k=0 Mr verdict FAIL    items []               defs []                             
  package RH  k=0 Mc verdict FAIL    items []               defs []                             
  package RH  k=1 Mr verdict FAIL    items []               defs []                             
  package RH  k=1 Mc verdict FAIL    items []               defs []                             
  package RI  k=0 Mr verdict FAIL    items []               defs []                             
  package RI  k=0 Mc verdict FAIL    items []               defs []                             
  package RI  k=1 Mr verdict FAIL    items []               defs []                             
  package RI  k=1 Mc verdict FAIL    items []               defs []                             

### KA-b-B-interrupted-1: FO-1 variant B, foreign write interrupted, escaped exit 1
  record[FO-1 B interrupted rc1    ] RF  child_created=True class=B | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 B interrupted rc1    ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B interrupted rc1    ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B interrupted rc1    ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []               defs []                             
  package RG  k=0 Mc verdict FAIL    items []               defs []                             
  package RG  k=1 Mr verdict FAIL    items []               defs []                             
  package RG  k=1 Mc verdict FAIL    items []               defs []                             
  package RH  k=0 Mr verdict FAIL    items []               defs []                             
  package RH  k=0 Mc verdict FAIL    items []               defs []                             
  package RH  k=1 Mr verdict FAIL    items []               defs []                             
  package RH  k=1 Mc verdict FAIL    items []               defs []                             
  package RI  k=0 Mr verdict FAIL    items []               defs []                             
  package RI  k=0 Mc verdict FAIL    items []               defs []                             
  package RI  k=1 Mr verdict FAIL    items []               defs []                             
  package RI  k=1 Mc verdict FAIL    items []               defs []                             

### KA-b-B-interrupted--2: FO-1 variant B, foreign write interrupted, escaped exit -2
  record[FO-1 B interrupted rc-2   ] RF  child_created=True class=B | (iv)-relevant record in another process; detected by: NOTHING
  record[FO-1 B interrupted rc-2   ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B interrupted rc-2   ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  record[FO-1 B interrupted rc-2   ] RI  child_created=True class=None child_end=undetermined | (iv)-relevant record in another process; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []               defs ['(iv)']                       FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []               defs []                             
  package RG  k=0 Mc verdict FAIL    items []               defs []                             
  package RG  k=1 Mr verdict FAIL    items []               defs []                             
  package RG  k=1 Mc verdict FAIL    items []               defs []                             
  package RH  k=0 Mr verdict FAIL    items []               defs []                             
  package RH  k=0 Mc verdict FAIL    items []               defs []                             
  package RH  k=1 Mr verdict FAIL    items []               defs []                             
  package RH  k=1 Mc verdict FAIL    items []               defs []                             
  package RI  k=0 Mr verdict FAIL    items []               defs []                             
  package RI  k=0 Mc verdict FAIL    items []               defs []                             
  package RI  k=1 Mr verdict FAIL    items []               defs []                             
  package RI  k=1 Mc verdict FAIL    items []               defs []                             

--- (c) childend AS WORDED (RG): PB-3, a cells package with one SE-3 re-solve (RF, RH, RI for contrast)

### KA-c: PB-3 cells m = 5, S5_t1 re-solved once at S-1 (r3_resolve 224-238, 310)
  record[S5_t0                     ] RF  child_created=True class=B
  record[S5_t0                     ] RG  child_created=True class=B child_end=exec
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RF  child_created=True class=B
  record[S5_t1 attempt 1           ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RF  child_created=True class=B
  record[S5_t1 attempt 2           ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RF  k=0 Mc verdict PASS    items []               defs []                             
  package RG  k=0 Mr verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mc verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mc verdict PASS    items []               defs []                             

--- (d) gapattr AS WORDED (RH): CX-1 objects LR-1, LR-2, LR-3, LR-5 and LR-4 of review TASK-20260924-94cc33
--- (e) the same objects under attcount with RI-1 (a) WEAKENED to 'N >= 1' (RIw) and AS WORDED (RI)

### LR-1: S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RIw child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RIw child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RIw NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']

### LR-2: S-1 re-solve, 2 attempts, attempt 1's launch record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RIw child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 1           ] RIw NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 1           ] RI  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RIw child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']

### LR-3: S-1 re-solve, 3 attempts, attempt 2's launch record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RIw child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RIw child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RIw NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RI  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 3           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 3           ] RIw child_created=True class=B child_end=exec
  record[S5_t1 attempt 3           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=2): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=2): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']

### LR-4: S-1 re-solve, 3 attempts, attempts 2 and 3 absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RIw child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RIw child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RIw NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RI  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 3           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 3           ] RIw NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 3           ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RIw k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RIw k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']

### LR-5: S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent
  record[gp                        ] RH  child_created=True class=B child_end=exec
  record[gp                        ] RIw child_created=True class=B child_end=exec
  record[gp                        ] RI  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RH  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RIw child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RI  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RH  NO LAUNCH RECORD (premise: absent)
  record[health_p1073741831_d222 at] RIw NO LAUNCH RECORD (premise: absent)
  record[health_p1073741831_d222 at] RI  NO LAUNCH RECORD (premise: absent)
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RIw child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RIw child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RIw child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RIw k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (health/health_p1073741831_d222, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters {"attempts_total": 3, "wrapped_calls": 2}']; gaps ['health/health_p1073741831_d222.ms', 'health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (health/health_p1073741831_d222, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters {"attempts_total": 3, "wrapped_calls": 2}']; gaps ['health/health_p1073741831_d222.ms', 'health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']

  every single removal among 2, 3 and 6 attempts at S-1 (RH-6 (i) (19) third case; RI-3 (24)):
   n=2 removed=1 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=2 removed=2 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=3 removed=1 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=3 removed=2 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=3 removed=3 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=1 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=2 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=3 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=4 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=5 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2
   n=6 removed=6 | RH PASS ['(i)', '(ii-LR)'] | RIw PASS ['(i)', '(ii-LR)'] | RI FAIL named=2

--- (f) LISTING CHECK under attcount (RI) on the four archived r3 gate packages; RH for contrast

--- LISTING CHECK under RH (launch sets RECONSTRUCTED, CRI-9)
  RUN-GFPN-f6a21a: 284 files in the five directories; 88 reconstructed launch records {'callgrind': 36, 'childjob': 16, 'msolve': 36}; first clause {'(i)': 176, '(ii)': 88, '(v)': 20}; named gaps 0; unattributed 0
    count table: 36 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 36, {'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 36}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}; duplicate other stdout paths {}
      S-1  fx_fresh1_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
  RUN-GFPN-902222: 284 files in the five directories; 88 reconstructed launch records {'callgrind': 36, 'childjob': 16, 'msolve': 36}; first clause {'(i)': 176, '(ii)': 88, '(v)': 20}; named gaps 0; unattributed 0
    count table: 36 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 36, {'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 36}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}; duplicate other stdout paths {}
      S-1  fx_fresh1_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
  RUN-GFPN-f5412a: 32 files in the five directories; 7 reconstructed launch records {'childjob': 1, 'comparator': 1, 'msolve': 5}; first clause {'(i)': 14, '(ii)': 11, '(iv)': 5, '(v)': 2}; named gaps 0; unattributed 0
    count table: 5 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 5, {'attempts_total': 0, 'passthrough_calls_gb_only_true': 5, 'wrapped_calls': 0}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}; duplicate other stdout paths {}
      S-1  anchor_comparator_random                 N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_comparator_system                 N=1 RB-1=0 RL-2=1 event=0 (i)=True  [frozen call site v2_driver.py 711 (gb_only=True)]
      S-1  anchor_v2_t0                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_v2_t1                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_v2_t2                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
  RUN-GFPN-bfe956: 83 files in the five directories; 19 reconstructed launch records {'childjob': 11, 'msolve': 8}; first clause {'(i)': 38, '(ii)': 27, '(v)': 18}; named gaps 0; unattributed 0
    count table: 8 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 8, {'attempts_total': 8, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 8}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}; duplicate other stdout paths {}
      S-1  ctl_identity_planted                     N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_identity_random                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_rawx_planted                         N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_rawx_random                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]

--- LISTING CHECK under RI (launch sets RECONSTRUCTED, CRI-9)
  RUN-GFPN-f6a21a: 284 files in the five directories; 88 reconstructed launch records {'callgrind': 36, 'childjob': 16, 'msolve': 36}; first clause {'(i)': 176, '(ii)': 88, '(v)': 20}; named gaps 0; unattributed 0
    count table: 36 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 36, {'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 36}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}; duplicate other stdout paths {}
      S-1  fx_fresh1_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
  RUN-GFPN-902222: 284 files in the five directories; 88 reconstructed launch records {'callgrind': 36, 'childjob': 16, 'msolve': 36}; first clause {'(i)': 176, '(ii)': 88, '(v)': 20}; named gaps 0; unattributed 0
    count table: 36 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 36, {'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 36}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}; duplicate other stdout paths {}
      S-1  fx_fresh1_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh1_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3                             N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_S3_rescaled                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_u                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_raw_x                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_norm                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_fresh2_torsion_S3_rq                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted0_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_u                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_raw_x                        N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_planted1_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg0_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3                               N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_S3_rescaled                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_u                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_raw_x                            N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_norm                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
      S-1  fx_reg1_torsion_S3_rq                    N=1 RB-1=1 RL-2=0 event=0 (i)=True  [raw-result.json solver argv (-P 1)]
  RUN-GFPN-f5412a: 32 files in the five directories; 7 reconstructed launch records {'childjob': 1, 'comparator': 1, 'msolve': 5}; first clause {'(i)': 14, '(ii)': 11, '(iv)': 5, '(v)': 2}; named gaps 0; unattributed 0
    count table: 5 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 5, {'attempts_total': 0, 'passthrough_calls_gb_only_true': 5, 'wrapped_calls': 0}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}; duplicate other stdout paths {}
      S-1  anchor_comparator_random                 N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_comparator_system                 N=1 RB-1=0 RL-2=1 event=0 (i)=True  [frozen call site v2_driver.py 711 (gb_only=True)]
      S-1  anchor_v2_t0                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_v2_t1                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
      S-1  anchor_v2_t2                             N=1 RB-1=0 RL-2=1 event=0 (i)=True  [raw-result.json solver argv (-g 1)]
  RUN-GFPN-bfe956: 83 files in the five directories; 19 reconstructed launch records {'childjob': 11, 'msolve': 8}; first clause {'(i)': 38, '(ii)': 27, '(v)': 18}; named gaps 0; unattributed 0
    count table: 8 (site, tag) rows; (i) mismatches 0; site rows [('S-1', 8, {'attempts_total': 8, 'passthrough_calls_gb_only_true': 0, 'wrapped_calls': 8}, True), ('S-2', 0, {'attempts_total': 0, 'wrapped_calls': 0}, True)]; events 0; callgrind {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}; duplicate other stdout paths {}
      S-1  ctl_identity_planted                     N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_identity_random                      N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_S3                           N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_S3_rescaled                  N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_torsion_S3_norm              N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_planted_torsion_S3_rq                N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_rawx_planted                         N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]
      S-1  ctl_rawx_random                          N=1 RB-1=1 RL-2=0 event=0 (i)=True  [frozen call site v2_driver.py 786 / 787 / 841 (gb_only default False)]

======================================================================================================================
BJ-1 FAIL-OPEN SEARCH UNDER attcount (RI); RH for contrast; same method as BJ-0

--- (1) a launch record absent, per count RI-1 (a) reads

### LN-1: non-event S-1 tag S5_t1: its launch record absent (RB-1 attempt record and counters present)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']

### LN-2: non-event S-1 tag: launch record AND its RB-1 attempt record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']

### LN-3: non-event S-1 tag: launch record, RB-1 attempt record and one attempts_total increment all absent (RGL-9 consistent loss)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']

### LN-4: gb_only pass-through anchor_comparator_system: its launch record absent (RL-2 record present)
  record[comparator                ] RH  child_created=True class=B child_end=exec
  record[comparator                ] RI  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RH  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RI  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RH  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RI  child_created=True class=B child_end=exec
  record[anchor_comparator_system  ] RH  NO LAUNCH RECORD (premise: absent)
  record[anchor_comparator_system  ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/anchor_comparator_system, N=0): (i) N=0 != RB-1 0 + RL-2 1', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 0, "passthrough_calls_gb_only_true": 2, "wrapped_calls": 0}']; gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/anchor_comparator_system, N=0): (i) N=0 != RB-1 0 + RL-2 1', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 0, "passthrough_calls_gb_only_true": 2, "wrapped_calls": 0}']; gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']

### LN-4b: gb_only pass-through: launch record, RL-2 record and one passthrough increment absent (consistent)
  record[comparator                ] RH  child_created=True class=B child_end=exec
  record[comparator                ] RI  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RH  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RI  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RH  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RI  child_created=True class=B child_end=exec
  record[anchor_comparator_system  ] RH  NO LAUNCH RECORD (premise: absent)
  record[anchor_comparator_system  ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/anchor_comparator_system.ms', 'solver/anchor_comparator_system.ms.err', 'solver/anchor_comparator_system.ms.log', 'solver/anchor_comparator_system.ms.out']

### LN-5: S-2 non-event health tag d222: its launch record absent (RB-1 present)
  record[gp                        ] RH  child_created=True class=B child_end=exec
  record[gp                        ] RI  child_created=True class=B child_end=exec
  record[health d222               ] RH  NO LAUNCH RECORD (premise: absent)
  record[health d222               ] RI  NO LAUNCH RECORD (premise: absent)
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.out']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.out']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (health/health_p1073741831_d222, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 1 launch records vs counters {"attempts_total": 2, "wrapped_calls": 2}']; gaps ['health/health_p1073741831_d222.ms', 'health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (health/health_p1073741831_d222, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 1 launch records vs counters {"attempts_total": 2, "wrapped_calls": 2}']; gaps ['health/health_p1073741831_d222.ms', 'health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.out']

--- (1) a launch record absent together with one other counted entry, at an event tag (2 attempts at S-1)

### LE-1: event tag S5_t1: attempt 2's launch record AND its RB-1 attempt record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']

### LE-2: event tag S5_t1: attempt 1's launch record AND renamed_files['attempt1'] absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 1           ] RI  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=1', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=1', 'SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']; gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']

### LE-3: event tag: the FINAL attempt lost CONSISTENTLY (launch record, RB-1 k=2, attempts entry, accepted_attempt -> 1, renamed key, attempts_total -1)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1 attempt 2           ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']

--- (2) launch kinds outside the S-1 / S-2 counts: a record absent

### LC-1: cells m = 4: callgrind child of raw_t0 exec'd normally; its launch record absent
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[callgrind raw_t0          ] RH  NO LAUNCH RECORD (premise: absent)
  record[callgrind raw_t0          ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']

### CX-A-control: cells m = 4: callgrind child of raw_t0 created, os.open(stdout_path) fails in the child (v2_solver 188 -> 206 -> 208: exit 99, empty report); its record PRESENT
  record[grid_raw_t0               ] RK  child_created=True class=B
  record[grid_raw_t0               ] RF  child_created=True class=B
  record[grid_raw_t0               ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RK  child_created=True class=B
  record[raw_t0                    ] RF  child_created=True class=B
  record[raw_t0                    ] RG  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[callgrind raw_t0          ] RK  child_created=True class=C
  record[callgrind raw_t0          ] RF  child_created=True class=C
  record[callgrind raw_t0          ] RG  child_created=True class=C child_end=frozen_pre_exec_exit
  record[callgrind raw_t0          ] RH  child_created=True class=C child_end=frozen_pre_exec_exit
  record[callgrind raw_t0          ] RI  child_created=True class=C child_end=frozen_pre_exec_exit
  record[callgrind raw_t0          ] RI  child_created=True class=C child_end=frozen_pre_exec_exit
  package RK  k=0 Mr verdict PASS    items []               defs []                             
  package RK  k=0 Mc verdict PASS    items []               defs []                             
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RF  k=0 Mc verdict PASS    items []               defs []                             
  package RG  k=0 Mr verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RG  k=0 Mc verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mc verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mc verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mc verdict PASS    items []               defs []                             

### CX-A: the same package with the callgrind child's launch record ABSENT (lost-record premise)
  note: the child left no file in the five directories; RI-1 counts S-1 / S-2 msolve launches only
  record[grid_raw_t0               ] RF  child_created=True class=B
  record[grid_raw_t0               ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RF  child_created=True class=B
  record[raw_t0                    ] RG  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[callgrind raw_t0          ] RF  NO LAUNCH RECORD (premise: absent)
  record[callgrind raw_t0          ] RG  NO LAUNCH RECORD (premise: absent)
  record[callgrind raw_t0          ] RH  NO LAUNCH RECORD (premise: absent)
  record[callgrind raw_t0          ] RI  NO LAUNCH RECORD (premise: absent)
  package RF  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RF  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RG  k=0 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/grid_raw_t0.meta.json']
  package RG  k=0 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']

### CX-A-G2: fixture (G2 shape): one callgrind child P-7 (no file), its launch record ABSENT
  record[fixture_S3                ] RH  child_created=True class=B child_end=exec
  record[fixture_S3                ] RI  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RI  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RI  child_created=True class=B child_end=exec
  record[cg fx_reg0_raw_x          ] RH  NO LAUNCH RECORD (premise: absent)
  record[cg fx_reg0_raw_x          ] RI  NO LAUNCH RECORD (premise: absent)
  record[fx_reg0_S3                ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_S3                ] RI  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3             ] RH  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3             ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']

### CX-A-gp: controls_a1: the gp child P-7 (no gp.stdout / gp.stderr; the .gp script is on the non-launch list), its record ABSENT (the package's own run_status is 'failed': check (b) fails)
  record[gp                        ] RH  NO LAUNCH RECORD (premise: absent)
  record[gp                        ] RI  NO LAUNCH RECORD (premise: absent)
  record[health d222               ] RH  child_created=True class=B child_end=exec
  record[health d222               ] RI  child_created=True class=B child_end=exec
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']

### CX-A-cmp: anchor-identity: the comparator child P-7 (the driver returns at v2_driver 656-659 before any other launch), its record ABSENT
  record[comparator                ] RH  NO LAUNCH RECORD (premise: absent)
  record[comparator                ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        
  package RH  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mr verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        
  package RI  k=0 Mc verdict FAIL    items ['66-67']        defs ['(ii-ANY)', '(ii-LR)']        

### LCJ-1: controls: a build child job P-7 (no .stdout / .stderr), its record ABSENT: the driver-written spec file remains
  record[ctl_S3                    ] RH  NO LAUNCH RECORD (premise: absent)
  record[ctl_S3                    ] RI  NO LAUNCH RECORD (premise: absent)
  record[ctl_planted_S3            ] RH  child_created=True class=B child_end=exec
  record[ctl_planted_S3            ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/ctl_S3.spec.json']
  package RH  k=0 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/ctl_S3.spec.json']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/ctl_S3.spec.json']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        gaps ['child/ctl_S3.spec.json']

### LN-6: non-event S-1 launch refused before fork (class A, input not retained): record, RB-1 and attempts_total consistently absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mc verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mc verdict PASS    items []               defs []                             

### LN-7a: non-event S-1 msolve child P-7 (no file; input not retained): its launch record absent
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        NAMED ['COUNT GAP (solver/S5_t1, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(ii-ANY)', '(ii-LR)']        NAMED ['COUNT GAP (solver/S5_t1, N=0): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}']

### LN-7b: the same with record, RB-1 and attempts_total consistently absent (RGL-9's premise)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  NO LAUNCH RECORD (premise: absent)
  record[S5_t1                     ] RI  NO LAUNCH RECORD (premise: absent)
  package RH  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mr verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']
  package RI  k=0 Mc verdict PASS    items []               defs ['(ii-ANY)', '(ii-LR)']        FAIL-OPEN ['(ii-ANY)', '(ii-LR)']

--- (2) residual premise: a tag solved TWICE in one package (no frozen path found; BJ-2 (1))

### TW-1: raw_t0 solved twice with callgrind both times, every record present (HYPOTHETICAL code)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0 call1              ] RH  child_created=True class=B child_end=exec
  record[raw_t0 call1              ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0 call1           ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0 call1           ] RI  child_created=True class=B child_end=exec
  record[raw_t0 call2              ] RH  child_created=True class=B child_end=exec
  record[raw_t0 call2              ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mc verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); NAMED ['DUPLICATE-PATH GAP (solver/raw_t0.callgrind.stdout): ordinals [2, 4]']; gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']
  package RI  k=0 Mc verdict FAIL    items []               defs []                             PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); NAMED ['DUPLICATE-PATH GAP (solver/raw_t0.callgrind.stdout): ordinals [2, 4]']; gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout']

### TW-2: the same, the FIRST callgrind launch record absent
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0 call1              ] RH  child_created=True class=B child_end=exec
  record[raw_t0 call1              ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0 call1           ] RH  NO LAUNCH RECORD (premise: absent)
  record[cg raw_t0 call1           ] RI  NO LAUNCH RECORD (premise: absent)
  record[raw_t0 call2              ] RH  child_created=True class=B child_end=exec
  record[raw_t0 call2              ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']

### TW-3: the same, the first msolve launch record absent
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0 call1              ] RH  NO LAUNCH RECORD (premise: absent)
  record[raw_t0 call1              ] RI  NO LAUNCH RECORD (premise: absent)
  record[cg raw_t0 call1           ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0 call1           ] RI  child_created=True class=B child_end=exec
  record[raw_t0 call2              ] RH  child_created=True class=B child_end=exec
  record[raw_t0 call2              ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0 call2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []               defs ['(i)', '(ii-LR)']             FAIL-OPEN ['(i)', '(ii-LR)']
  package RI  k=0 Mr verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/raw_t0, N=1): (i) N=1 != RB-1 2 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}', 'DUPLICATE-PATH GAP (solver/raw_t0.callgrind.stdout): ordinals [2, 4]']; gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout', 'solver/raw_t0.ms', 'solver/raw_t0.ms.err', 'solver/raw_t0.ms.log', 'solver/raw_t0.ms.out']
  package RI  k=0 Mc verdict FAIL    items []               defs ['(i)', '(ii-LR)']             NAMED ['COUNT GAP (solver/raw_t0, N=1): (i) N=1 != RB-1 2 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}', 'DUPLICATE-PATH GAP (solver/raw_t0.callgrind.stdout): ordinals [2, 4]']; gaps ['solver/raw_t0.callgrind.stderr', 'solver/raw_t0.callgrind.stdout', 'solver/raw_t0.ms', 'solver/raw_t0.ms.err', 'solver/raw_t0.ms.log', 'solver/raw_t0.ms.out']

======================================================================================================================
BJ-2 NO PLANNED-BASIS REFUSAL UNDER attcount (RI): normal outcomes of every launch kind; RH for contrast

### N-1: cells m = 5 measured (S5_t0 retained, S5_t1 not retained)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  child_created=True class=B child_end=exec
  record[S5_t1                     ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-2: cells m = 5 not_measured (timeout, memory_exhausted after exec; no .ms.out)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  child_created=True class=B child_end=exec
  record[S5_t1                     ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-3: cells m = 4 raw_grid measured, callgrind ok (.callgrind.out removed at v2_solver 549)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-4: cells m = 4 raw_grid child crashed after exec (partial .npz)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[grid_raw_t1               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t1               ] RI  child_created=True class=B child_end=exec
  record[raw_t1                    ] RH  child_created=True class=B child_end=exec
  record[raw_t1                    ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-5: SE-3 re-solve at S-1, 2 attempts
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-5b: SE-3 re-solve at S-1, 6 attempts (K + 1; still SSF after the last attempt)
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 3           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 3           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 4           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 4           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 5           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 5           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 6           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 6           ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-5c: SE-3 re-solve at S-1 on the callgrind target of an m = 4 cell: 3 attempts, final ok, one callgrind child
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0 attempt 1          ] RH  child_created=True class=B child_end=exec
  record[raw_t0 attempt 1          ] RI  child_created=True class=B child_end=exec
  record[raw_t0 attempt 2          ] RH  child_created=True class=B child_end=exec
  record[raw_t0 attempt 2          ] RI  child_created=True class=B child_end=exec
  record[raw_t0 attempt 3          ] RH  child_created=True class=B child_end=exec
  record[raw_t0 attempt 3          ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-6: controls_a1: HR-3 re-solve at S-2 (2 attempts), gp child, health d444, build, S-1 solve
  record[gp                        ] RH  child_created=True class=B child_end=exec
  record[gp                        ] RI  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RH  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RI  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RH  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 at] RI  child_created=True class=B child_end=exec
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-6b: controls_a1: health pattern d222 fails its checks, retried under tag d222_seed2 (a1_health 238-242)
  record[gp                        ] RH  child_created=True class=B child_end=exec
  record[gp                        ] RI  child_created=True class=B child_end=exec
  record[health d222               ] RH  child_created=True class=B child_end=exec
  record[health d222               ] RI  child_created=True class=B child_end=exec
  record[health d222 seed2         ] RH  child_created=True class=B child_end=exec
  record[health d222 seed2         ] RI  child_created=True class=B child_end=exec
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-7: failing callgrind child (valgrind exits nonzero after writing its out file)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-8: timed-out callgrind child (SIGKILL, no out file)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-9: build package: cached builds (out under the cache directory)
  record[build S5                  ] RH  child_created=True class=B child_end=exec
  record[build S5                  ] RI  child_created=True class=B child_end=exec
  record[build S4                  ] RH  child_created=True class=B child_end=exec
  record[build S4                  ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-10: fixture4: uncached builds and solves
  record[f4_S4                     ] RH  child_created=True class=B child_end=exec
  record[f4_S4                     ] RI  child_created=True class=B child_end=exec
  record[f4_t0_S4                  ] RH  child_created=True class=B child_end=exec
  record[f4_t0_S4                  ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-11: child jobs on refusal paths: refused meta, refused before fork (class A), ERR setrlimit (class C)
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[grid_raw_t1               ] RH  child_created=False class=A child_end=no_child
  record[grid_raw_t1               ] RI  child_created=False class=A child_end=no_child
  record[grid_raw_t2               ] RH  child_created=True class=C child_end=frozen_pre_exec_exit
  record[grid_raw_t2               ] RI  child_created=True class=C child_end=frozen_pre_exec_exit
  record[raw_t3                    ] RH  child_created=True class=B child_end=exec
  record[raw_t3                    ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-11b: an S-1 attempt refused before fork (class A: another solver process, EC-10) in a measured cell
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1                     ] RH  child_created=False class=A child_end=no_child
  record[S5_t1                     ] RI  child_created=False class=A child_end=no_child
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-12: anchor-identity: comparator, uncached build, gb_only solves
  record[comparator                ] RH  child_created=True class=B child_end=exec
  record[comparator                ] RI  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RH  child_created=True class=B child_end=exec
  record[anchor_S4                 ] RI  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RH  child_created=True class=B child_end=exec
  record[anchor_v2_t0              ] RI  child_created=True class=B child_end=exec
  record[anchor_comparator_system  ] RH  child_created=True class=B child_end=exec
  record[anchor_comparator_system  ] RI  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### N-13: Z-C5 (no launch)
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             
  package RI  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             

--- RKR-4 (b) rows (readbackclose-census.md 476-492) that are PASS or PASS_ZL there, under RI

### row-478: G1..G4 completed_valid (fixture shape: builds, raw grids, solves, callgrind)
  record[fixture_S3                ] RF  child_created=True class=B
  record[fixture_S3                ] RH  child_created=True class=B child_end=exec
  record[fixture_S3                ] RI  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RF  child_created=True class=B
  record[fx_reg0_raw_x             ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RI  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RF  child_created=True class=B
  record[fx_reg0_raw_x             ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x             ] RI  child_created=True class=B child_end=exec
  record[cg fx_reg0_raw_x          ] RF  child_created=True class=B
  record[cg fx_reg0_raw_x          ] RH  child_created=True class=B child_end=exec
  record[cg fx_reg0_raw_x          ] RI  child_created=True class=B child_end=exec
  record[fx_reg0_S3                ] RF  child_created=True class=B
  record[fx_reg0_S3                ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_S3                ] RI  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3             ] RF  child_created=True class=B
  record[cg fx_reg0_S3             ] RH  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3             ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-480: controls_a1 image
  record[gp                        ] RF  child_created=True class=B
  record[gp                        ] RH  child_created=True class=B child_end=exec
  record[gp                        ] RI  child_created=True class=B child_end=exec
  record[health d222               ] RF  child_created=True class=B
  record[health d222               ] RH  child_created=True class=B child_end=exec
  record[health d222               ] RI  child_created=True class=B child_end=exec
  record[health d444               ] RF  child_created=True class=B
  record[health d444               ] RH  child_created=True class=B child_end=exec
  record[health d444               ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RF  child_created=True class=B
  record[ctl_a1_S3_rescaled        ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled        ] RI  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RF  child_created=True class=B
  record[ctl_a1_planted_S3_rescaled] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_S3_rescaled] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-481: fixture4 launched
  record[f4_S4                     ] RF  child_created=True class=B
  record[f4_S4                     ] RH  child_created=True class=B child_end=exec
  record[f4_S4                     ] RI  child_created=True class=B child_end=exec
  record[f4_t0_S4                  ] RF  child_created=True class=B
  record[f4_t0_S4                  ] RH  child_created=True class=B child_end=exec
  record[f4_t0_S4                  ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-482: Z-F4 (zero call)
  package RF  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             
  package RI  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             

### row-483: build (cached)
  record[build S5                  ] RF  child_created=True class=B
  record[build S5                  ] RH  child_created=True class=B child_end=exec
  record[build S5                  ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-485: cells m = 5 measured
  record[S5_t0                     ] RF  child_created=True class=B
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-485b: cells m = 5 measured, one SE-3 re-solve
  record[S5_t0                     ] RF  child_created=True class=B
  record[S5_t0                     ] RH  child_created=True class=B child_end=exec
  record[S5_t0                     ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RF  child_created=True class=B
  record[S5_t1 attempt 1           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1           ] RI  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RF  child_created=True class=B
  record[S5_t1 attempt 2           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2           ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-486: Z-C5
  package RF  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             
  package RI  k=0 Mr verdict PASS_ZL items ['66-67']        defs []                             

### row-488: cells m = 4
  record[grid_raw_t0               ] RF  child_created=True class=B
  record[grid_raw_t0               ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t0               ] RI  child_created=True class=B child_end=exec
  record[raw_t0                    ] RF  child_created=True class=B
  record[raw_t0                    ] RH  child_created=True class=B child_end=exec
  record[raw_t0                    ] RI  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RF  child_created=True class=B
  record[cg raw_t0                 ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0                 ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

### row-489: aggregate v2
  package RF  k=0 Mr verdict PASS    items []               defs []                             
  package RH  k=0 Mr verdict PASS    items []               defs []                             
  package RI  k=0 Mr verdict PASS    items []               defs []                             

======================================================================================================================
BJ-3 CAP-MISMATCH OUTCOMES (RH-2 with RI-5 (a)) under RI; RF / RH for contrast

### CM-cells_m5-P8: cells_m5: every launch P-8
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates)
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-cells_m5-P9: cells_m5: every launch P-9
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates)
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-cells_m5-mix: cells_m5: one P-9 launch mixed with one measured launch
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=exec
  record[b                         ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09 / X-10 aggregates)
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-cells_m4-P8: cells_m4: every launch P-8
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-cells_m4-P9: cells_m4: every launch P-9
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-cells_m4-mix: cells_m4: one P-9 launch mixed with one measured launch
  record[a                         ] RF  child_created=True class=B
  record[a                         ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[a                         ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b                         ] RF  child_created=True class=B
  record[b                         ] RH  child_created=True class=B child_end=exec
  record[b                         ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-09 / X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-build-mix: build: one P-9 build child mixed with one built child
  record[b1                        ] RF  child_created=True class=B
  record[b1                        ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b1                        ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[b2                        ] RF  child_created=True class=B
  record[b2                        ] RH  child_created=True class=B child_end=exec
  record[b2                        ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003))
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

### CM-controls: controls (gate): one P-9 build child
  record[ctl_S3                    ] RF  child_created=True class=B
  record[ctl_S3                    ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[ctl_S3                    ] RI  child_created=True class=B child_end=frozen_pre_exec_exit
  record[ok                        ] RF  child_created=True class=B
  record[ok                        ] RH  child_created=True class=B child_end=exec
  record[ok                        ] RI  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478)
  package RH  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)
  package RI  k=0 Mr verdict FAIL    items ['68-70']        defs ['(ii-ANY)', '(ii-LR)']        cap-mismatch stop (RH-2)

======================================================================================================================
BJ-4 RI-3 (19)-(27) DERIVED on development objects altered IN PLACE (V-7 evaluated: altered after the manifest)

### RI3-19a: (19) unaltered dev package with an SE-3 re-solve at S-1 (stand-in SSF once): renamed attempt-1 files attributed
  RH  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS
  RI  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS

### RI3-19b: (19) the same with renamed_files['attempt1'] removed in place
  RH  gaps ['solver/ctl_identity_random.ms.err.ssf-attempt1', 'solver/c named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
  RI  gaps ['solver/ctl_identity_random.ms', 'solver/ctl_identity_rando named 1   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/ctl_identity_random, N=2): (ii) N=2 attempts=2 accepted=2 1+renamed=1

### RI3-19c: (19) the same with one launch record of the tag removed in place (attempt 2)
  RH  gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS
  RI  gaps ['solver/ctl_identity_random.ms', 'solver/ctl_identity_rando named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/ctl_identity_random, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2
        NAMED SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}

### RI3-20a: (20) unaltered dev package with an HR-3 re-solve at S-2
  RH  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS
  RI  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS

### RI3-20c: (20) one launch record of the S-2 tag removed in place
  RH  gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS
  RI  gaps ['health/health_p1073741831_d222.ms', 'health/health_p107374 named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (health/health_p1073741831_d222, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2
        NAMED SITE COUNT GAP (S-2): 2 launch records vs counters {"attempts_total": 3, "wrapped_calls": 2}

### RI3-22a: (22) uncached build child job ctl_S3: its launch record removed in place
  RH  gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3 named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
  RI  gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3 named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL

### RI3-22b: (22) raw_grid child job ctl_raw_random: its launch record removed in place
  RH  gaps ['child/ctl_raw_random.meta.json', 'child/ctl_raw_random.spe named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
  RI  gaps ['child/ctl_raw_random.meta.json', 'child/ctl_raw_random.spe named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL

### RI3-24-LR-1: (24)/(25) S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2
        NAMED SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}
  RIx gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS

### RI3-24-LR-2: (24)/(25) S-1 re-solve, 2 attempts, attempt 1's launch record absent, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2
        NAMED SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 3, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}
  RIx gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS

### RI3-24-LR-3: (24)/(25) S-1 re-solve, 3 attempts, attempt 2's launch record absent, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=2): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3
        NAMED SITE COUNT GAP (S-1): 3 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}
  RIx gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS

### RI3-24-LR-4: (24)/(25) S-1 re-solve, 3 attempts, attempts 2 and 3 absent, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3
        NAMED SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 4, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}
  RIx gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ss named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL

### RI3-24-LR-5: (24)/(25) S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent, altered in place: RI as worded (24) and RIx = RI-1 (a), (d) disabled (25)
  RI  gaps ['health/health_p1073741831_d222.ms', 'health/health_p107374 named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (health/health_p1073741831_d222, N=1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2
        NAMED SITE COUNT GAP (S-2): 2 launch records vs counters {"attempts_total": 3, "wrapped_calls": 2}
  RIx gaps []                                                           named 0   verdict(with V-7) FAIL    verdict(scratch, no V-7) PASS

### RI3-26: (26) unaltered dev packages (positive control): N-5 shape and N-6 shape
  RI  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS

### RI3-26b: (26) unaltered N-6 shape
  RI  gaps []                                                           named 0   verdict(with V-7) PASS    verdict(scratch, no V-7) PASS

### RI3-27a: (27) non-event S-1 tag: its RB-1 attempt record removed in place
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 1   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=1): (i) N=1 != RB-1 0 + RL-2 0

### RI3-27b: (27) a launch record duplicated in place (S-1 tag S5_t1)
  RI  gaps ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms. named 2   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED COUNT GAP (solver/S5_t1, N=2): (i) N=2 != RB-1 1 + RL-2 0
        NAMED SITE COUNT GAP (S-1): 3 launch records vs counters {"attempts_total": 2, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}

### RI3-27c: (27) a site counter decremented in place (S-1 attempts_total - 1)
  RI  gaps []                                                           named 1   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED SITE COUNT GAP (S-1): 2 launch records vs counters {"attempts_total": 1, "passthrough_calls_gb_only_true": 0, "wrapped_calls": 2}

### RI3-27d: (27) a child-job launch record duplicated in place
  RI  gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3 named 1   verdict(with V-7) FAIL    verdict(scratch, no V-7) FAIL
        NAMED DUPLICATE-PATH GAP (child/ctl_S3.stdout): ordinals [0, 0]

--- callgrind: reconstructed callgrind launch records vs the r3 S-3 (CG-3) records per package (an independent count RI-1 does not read)
  RUN-GFPN-f6a21a: {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}
  RUN-GFPN-902222: {'callgrind_records_reconstructed': 36, 'S3_records_in_r3_solver_events': 36, 'per_tag_equal': True, 'S3_callgrind_children_observed': 36}
  RUN-GFPN-f5412a: {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}
  RUN-GFPN-bfe956: {'callgrind_records_reconstructed': 0, 'S3_records_in_r3_solver_events': 0, 'per_tag_equal': True, 'S3_callgrind_children_observed': 0}

WROTE rteval_v2.json with 95 keys
````

### `rdscan.py`

- sha256: `fe573d4255457b538279c5e3f56cc1d3887c4e998eb32a536b9644dac8ef3e7c`
- bytes: 4203; lines: 105
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan.py rdscan.json > rdscan.out 2>&1   (cwd <scratch>/rt_be2daf)`
- role: BJ-4 (2): every recorded value carrying the run directory in four archived packages (O_NOATIME, lstat before / after)

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf scratch (zero runs). BJ-4 (2): in the archived r3 packages RUN-GFPN-bfe956 (controls) and
# RUN-GFPN-f5412a (anchor-identity) -- and, for completeness, the two fixture packages -- find EVERY recorded value
# that carries the package's run directory (the absolute path <repo>/experiments/EXP-GFPN-05ff43/runs/<RUN-ID>).
# Reads, with O_NOATIME and read-only, the text/JSON/YAML files of the package (skips *.npz, solver/*.ms* data,
# comparator/*.ms data); lstat of every file read is compared before and after. For JSON / YAML files it reports the
# key path of every string value containing the run directory and whether the run directory is the value's PREFIX
# (strict reading) or only a prefix of a path token INSIDE the value (loose reading); for text files, the line
# numbers. Imports only json, os, re, sys, collections and yaml (PyYAML, to parse manifest.yaml; not read under BJ-1).
import collections
import json
import os
import re
import sys

import yaml

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-bfe956", "RUN-GFPN-f5412a", "RUN-GFPN-f6a21a", "RUN-GFPN-902222"]
FL = os.O_RDONLY | os.O_NOATIME


def st(p):
    s = os.lstat(p)
    return (s.st_size, s.st_atime_ns, s.st_mtime_ns, s.st_ctime_ns)


def read(p, before):
    before[p] = st(p)
    fd = os.open(p, FL)
    try:
        out = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            out.append(b)
    finally:
        os.close(fd)
    return b"".join(out)


def walk(o, path, rd, hits):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k), rd, hits)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[" + str(i) + "]", rd, hits)
    elif isinstance(o, str) and rd in o:
        hits.append((path, "PREFIX" if o.startswith(rd) else "EMBEDDED", o[:160]))


res = {}
before = {}
for pk in PKGS:
    rd = RUNS + "/" + pk
    per = collections.OrderedDict()
    for dp, dn, fn in os.walk(rd):
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, rd)
            if rel.endswith(".npz") or re.match(r"^(solver|comparator)/.*\.ms(\.out|\.out\.ssf-attempt\d+)?$", rel):
                continue
            if os.path.getsize(p) > 4 * 1024 * 1024:
                per[rel] = {"skipped": "larger than 4 MiB"}
                continue
            b = read(p, before)
            t = b.decode(errors="replace")
            if rd not in t:
                continue
            hits = []
            if rel.endswith(".json"):
                try:
                    walk(json.loads(t), "", rd, hits)
                except Exception as e:                       # noqa: BLE001
                    hits.append(("<unparseable>", repr(e), ""))
            elif rel.endswith(".yaml"):
                try:
                    walk(yaml.safe_load(t), "", rd, hits)
                except Exception as e:                       # noqa: BLE001
                    hits.append(("<unparseable>", repr(e), ""))
            else:
                for i, line in enumerate(t.splitlines(), start=1):
                    if rd in line:
                        hits.append(("line %d" % i, "PREFIX" if line.startswith(rd) else "EMBEDDED", line[:160]))
            per[rel] = {"n": len(hits), "hits": hits}
    res[pk] = per
after = {p: st(p) for p in before}
res["_lstat_checked"] = len(before)
res["_lstat_changed"] = [p for p in before if before[p] != after[p]]
with open(sys.argv[1], "w") as fh:
    json.dump(res, fh, indent=1)
print("lstat checked", len(before), "changed", len(res["_lstat_changed"]))
for pk in PKGS:
    print("==", pk)
    for rel, v in res[pk].items():
        if "skipped" in v:
            print("  %-45s %s" % (rel, v["skipped"]))
            continue
        kinds = collections.Counter(re.sub(r"\[\d+\]", "[]", h[0]) + " :: " + h[1] for h in v["hits"])
        print("  %-45s %d value(s) carry the run directory" % (rel, v["n"]))
        for k, n in sorted(kinds.items()):
            print("      %4d  %s" % (n, k))
````

### `rdscan.out`

- sha256: `75479e306c36411088b3f5ff0586731c6a1ddf1b5a279baa47f089e03d4035e7`
- bytes: 16477; lines: 292
- argv: `(stdout of rdscan.py)`
- role: its output

````text
lstat checked 602 changed 0
== RUN-GFPN-bfe956
  command.txt                                   1 value(s) carry the run directory
         1  line 2 :: EMBEDDED
  child/ctl_S3.spec.json                        1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_S3_rescaled.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_identity_n3.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_identity_n5_m3.spec.json            1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_identity_n5_m4.spec.json            1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_raw_n5_m3.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_raw_n5_m4.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_raw_planted.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_raw_random.spec.json                1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_torsion_S3_norm.spec.json           1 value(s) carry the run directory
         1  /out :: PREFIX
  child/ctl_torsion_S3_rq.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
== RUN-GFPN-f5412a
  command.txt                                   1 value(s) carry the run directory
         1  line 2 :: EMBEDDED
  raw-result.json                               11 value(s) carry the run directory
         1  /build/child/argv[] :: PREFIX
         1  /build/npz :: PREFIX
         1  /comparator/child/argv[] :: PREFIX
         8  /targets[]/solver/argv[] :: PREFIX
  child/anchor_S4.spec.json                     1 value(s) carry the run directory
         1  /out :: PREFIX
== RUN-GFPN-f6a21a
  command.txt                                   1 value(s) carry the run directory
         1  line 2 :: EMBEDDED
  raw-result.json                               80 value(s) carry the run directory
         1  /builds/S3/child/argv[] :: PREFIX
         1  /builds/S3/npz :: PREFIX
         1  /builds/S3_rescaled/child/argv[] :: PREFIX
         1  /builds/S3_rescaled/npz :: PREFIX
         1  /builds/torsion_S3_norm/child/argv[] :: PREFIX
         1  /builds/torsion_S3_norm/npz :: PREFIX
         1  /builds/torsion_S3_rq/child/argv[] :: PREFIX
         1  /builds/torsion_S3_rq/npz :: PREFIX
         4  /planted_targets[]/arms/S3/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/S3_rescaled/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/raw_u/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/raw_x/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/torsion_S3_norm/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/torsion_S3_rq/solver/argv[] :: PREFIX
         8  /targets[]/arms/S3/solver/argv[] :: PREFIX
         8  /targets[]/arms/S3_rescaled/solver/argv[] :: PREFIX
         8  /targets[]/arms/raw_u/solver/argv[] :: PREFIX
         8  /targets[]/arms/raw_x/solver/argv[] :: PREFIX
         8  /targets[]/arms/torsion_S3_norm/solver/argv[] :: PREFIX
         8  /targets[]/arms/torsion_S3_rq/solver/argv[] :: PREFIX
  child/fixture_S3.spec.json                    1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_S3_rescaled.spec.json           1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_torsion_S3_norm.spec.json       1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_torsion_S3_rq.spec.json         1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh1_raw_u.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh1_raw_x.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh2_raw_u.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh2_raw_x.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted0_raw_u.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted0_raw_x.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted1_raw_u.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted1_raw_x.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg0_raw_u.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg0_raw_x.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg1_raw_u.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg1_raw_x.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  solver/fx_fresh1_S3.callgrind.stderr          1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_raw_u.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_raw_x.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_S3.callgrind.stderr          1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_raw_u.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_raw_x.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_S3.callgrind.stderr        1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_raw_u.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_raw_x.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_S3.callgrind.stderr        1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_raw_u.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_raw_x.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_S3.callgrind.stderr            1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_S3_rescaled.callgrind.stderr   1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_raw_u.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_raw_x.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_S3.callgrind.stderr            1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_S3_rescaled.callgrind.stderr   1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_raw_u.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_raw_x.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
== RUN-GFPN-902222
  command.txt                                   1 value(s) carry the run directory
         1  line 2 :: EMBEDDED
  raw-result.json                               80 value(s) carry the run directory
         1  /builds/S3/child/argv[] :: PREFIX
         1  /builds/S3/npz :: PREFIX
         1  /builds/S3_rescaled/child/argv[] :: PREFIX
         1  /builds/S3_rescaled/npz :: PREFIX
         1  /builds/torsion_S3_norm/child/argv[] :: PREFIX
         1  /builds/torsion_S3_norm/npz :: PREFIX
         1  /builds/torsion_S3_rq/child/argv[] :: PREFIX
         1  /builds/torsion_S3_rq/npz :: PREFIX
         4  /planted_targets[]/arms/S3/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/S3_rescaled/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/raw_u/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/raw_x/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/torsion_S3_norm/solver/argv[] :: PREFIX
         4  /planted_targets[]/arms/torsion_S3_rq/solver/argv[] :: PREFIX
         8  /targets[]/arms/S3/solver/argv[] :: PREFIX
         8  /targets[]/arms/S3_rescaled/solver/argv[] :: PREFIX
         8  /targets[]/arms/raw_u/solver/argv[] :: PREFIX
         8  /targets[]/arms/raw_x/solver/argv[] :: PREFIX
         8  /targets[]/arms/torsion_S3_norm/solver/argv[] :: PREFIX
         8  /targets[]/arms/torsion_S3_rq/solver/argv[] :: PREFIX
  child/fixture_S3.spec.json                    1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_S3_rescaled.spec.json           1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_torsion_S3_norm.spec.json       1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fixture_torsion_S3_rq.spec.json         1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh1_raw_u.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh1_raw_x.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh2_raw_u.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_fresh2_raw_x.spec.json               1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted0_raw_u.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted0_raw_x.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted1_raw_u.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_planted1_raw_x.spec.json             1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg0_raw_u.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg0_raw_x.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg1_raw_u.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  child/fx_reg1_raw_x.spec.json                 1 value(s) carry the run directory
         1  /out :: PREFIX
  solver/fx_fresh1_S3.callgrind.stderr          1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_raw_u.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_raw_x.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_S3.callgrind.stderr          1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_raw_u.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_raw_x.callgrind.stderr       1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_fresh2_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_S3.callgrind.stderr        1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_raw_u.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_raw_x.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted0_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_S3.callgrind.stderr        1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_S3_rescaled.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_raw_u.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_raw_x.callgrind.stderr     1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_planted1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_S3.callgrind.stderr            1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_S3_rescaled.callgrind.stderr   1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_raw_u.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_raw_x.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg0_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_S3.callgrind.stderr            1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_S3_rescaled.callgrind.stderr   1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_raw_u.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_raw_x.callgrind.stderr         1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_torsion_S3_norm.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
  solver/fx_reg1_torsion_S3_rq.callgrind.stderr 1 value(s) carry the run directory
         1  line 4 :: EMBEDDED
````

### `tables.py`

- sha256: `86e56fffa5def8bb583815542fc187a8dbe7ce94d0e60e012c53342491558c2e`
- bytes: 7984; lines: 106
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables.py   (cwd <scratch>/rt_be2daf)`
- role: writes the listing and count table parts from rteval_v2.json

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf table writer (scratch). Reads rteval_v2.json (the evaluator's recorded listing checks and count
# tables) from this directory and writes two text parts for the deliverables:
#   tables.yaml.part  (top-level YAML keys listing_tables: and bj2_count_table:, every scalar JSON-quoted)
#   tables.md.part    (the same tables as markdown)
# It computes no attribution and no count itself: every value is copied from rteval_v2.json. Imports only json, os.
import json
import os

SCR = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(SCR, "rteval_v2.json")))
GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
q = json.dumps
Y, M = [], []
RULE = ("CRI-9 RECONSTRUCTION (rteval_v2.py reconstruct()): child/<tag>.spec.json -> one child-job launch record "
        "(argv [python, -B, implementation-v2/v2_child.py, <rd>/child/<tag>.spec.json]; stdout/stderr child/<tag>.stdout/.stderr; "
        "v2_driver.py 92-102); solver|health/<tag>.ms.log -> one msolve launch record (argv -f <dir>/<tag>.ms -o <dir>/<tag>.ms.out, "
        "-g 1 or -P 1; stdout/stderr <tag>.ms.log/.ms.err; v2_driver.py 161-166, a1_health.py 141-147); solver/<tag>.callgrind.stdout -> "
        "one callgrind record (v2_solver.py 515-518, v2_driver.py 208-209); comparator/stdout.log -> one comparator record "
        "(v2_driver.py 647-651); pari/<tag>.gp.stdout -> one gp record (a1_pari.py 91-96). child_end exec where the child's outputs "
        "exist. PER-TAG RB-1 / RL-2 counts (the records do not exist in r3) are taken INDEPENDENTLY of the listing: from the "
        "raw-result.json solver argv of the tag where recorded (-P 1: one RB-1 attempt record; -g 1: one RL-2 pass-through record), "
        "else from the frozen call site's gb_only argument (v2_driver.py 711 gb_only=True; 786, 787, 841 gb_only default False). "
        "Events and site counters are the archived r3 solver-events.json's (sites v2_driver.solve and a1_health.run_system). "
        "Paths are compared as absolute paths under each package's recorded GFPN_RUN_DIR, equal to its current path "
        "(command.txt line 2). A listing or count check is a reading of r3 artifacts under r4 rule text: never a result about "
        "any package's verdict and never evidence about D.")
Y.append("listing_tables:")
Y.append("  reconstruction_rule: " + q(RULE))
M.append("## Listing and count tables (BJ-0 (f), BJ-2 (2))\n")
M.append("Reconstruction rule (CRI-9): " + RULE + "\n")
for rule in ("RI", "RH"):
    L = D["listing_" + rule]
    Y.append("  %s:" % ("attcount_RI1_as_worded" if rule == "RI" else "gapattr_RH1_as_worded_contrast"))
    M.append("### Listing check under %s\n" % ("attcount (RH-1 with RI-1 (a)-(d) as worded)" if rule == "RI" else "gapattr RH-1 as worded (contrast)"))
    M.append("| package | files in the five directories | reconstructed launch records | files by first clause | named gaps | unattributed |")
    M.append("|---|---|---|---|---|---|")
    for pk in GATE:
        r = L[pk]
        Y.append("    %s:" % pk)
        Y.append("      files_in_the_five_directories: %d" % r["n_files"])
        Y.append("      reconstructed_launch_records: %d" % r["n_records"])
        Y.append("      record_kinds: " + q(r["record_kinds"]))
        Y.append("      files_by_first_clause: " + q(r["first_clause"]))
        Y.append("      named_gaps: " + q(r["named"]))
        Y.append("      unattributed_count: %d" % len(r["unattributed"]))
        Y.append("      unattributed: " + q(r["unattributed"]))
        M.append("| %s | %d | %d %s | %s | %d | **%d** |" % (pk, r["n_files"], r["n_records"], json.dumps(r["record_kinds"], sort_keys=True),
                                                           json.dumps(r["first_clause"], sort_keys=True), len(r["named"]), len(r["unattributed"])))
    M.append("")
    M.append("Unattributed files under %s, each listed: %s.\n" % (rule, "; ".join("%s: %s" % (pk, (", ".join(L[pk]["unattributed"]) or "none")) for pk in GATE)))
# per-file first clause under RI
Y.append("  attcount_per_file_first_clause:")
M.append("### Per-file attribution under attcount (first applying clause and record; every file of the five directories)\n")
for pk in GATE:
    att = D["listing_RI"][pk]["attribution"]
    Y.append("    %s:" % pk)
    M.append("#### %s (%d files)\n" % (pk, len(att)))
    M.append("| file | first clause, record |")
    M.append("|---|---|")
    for rel in sorted(att):
        h = att[rel]
        s = ("%s %s" % (h[0][1], h[0][0])) if h else "NONE (recorder gap)"
        Y.append("      %s: %s" % (q(rel), q(s)))
        M.append("| `%s` | %s |" % (rel, s))
    M.append("")
# BJ-2 count table
Y.append("bj2_count_table:")
Y.append("  rule: " + q("RI-1 (a) (i) per tag, (ii) per event tag, (iii) per site, and (b) one launch per other stdout path, evaluated on the "
                         "RECONSTRUCTED launch sets (listing_tables.reconstruction_rule) against the archived r3 solver-events.json events and "
                         "site counters; RB-1 / RL-2 per-tag counts reconstructed from raw-result.json argv or the frozen call site"))
M.append("### BJ-2 (2) count table: every (site, tag) and site count RI-1 (a) evaluates (reconstructed)\n")
for pk in GATE:
    r = D["listing_RI"][pk]
    Y.append("  %s:" % pk)
    Y.append("    per_site_tag:")
    M.append("#### %s\n" % pk)
    M.append("| site | tag | N launch records | RB-1 attempt records | RL-2 pass-through records | SE-3/HR-3 event | (i) holds | source of the RB-1 / RL-2 count |")
    M.append("|---|---|---|---|---|---|---|---|")
    for t in r["count_table"]:
        Y.append("      - {site: %s, tag: %s, N: %d, RB1: %d, RL2: %d, event: %d, i_holds: %s, source: %s}" % (
            q(t["site"]), q(t["tag"]), t["N_launch_records"], t["RB1_attempt_records"], t["RL2_passthrough_records"], t["event"],
            "true" if t["i_holds"] else "false", q(t["source_of_RB1_RL2"])))
        M.append("| %s | `%s` | %d | %d | %d | %d | %s | %s |" % (t["site"], t["tag"], t["N_launch_records"], t["RB1_attempt_records"],
                                                            t["RL2_passthrough_records"], t["event"], t["i_holds"], t["source_of_RB1_RL2"]))
    Y.append("    per_site:")
    M.append("")
    M.append("| site | launch records at <dir>/<tag>.ms.log | r3 site counters | (iii) holds |")
    M.append("|---|---|---|---|")
    for s in r["site_rows"]:
        Y.append("      - {site: %s, launch_records: %d, counters: %s, iii_holds: %s}" % (q(s["site"]), s["launch_records_at_dir_ms_log"],
                                                                                        q(s["counters"]), "true" if s["iii_holds"] else "false"))
        M.append("| %s | %d | %s | %s |" % (s["site"], s["launch_records_at_dir_ms_log"], json.dumps(s["counters"], sort_keys=True), s["iii_holds"]))
    Y.append("    events: 0")
    Y.append("    ii_evaluated: " + q("no SE-3 or HR-3 event in the archived solver-events.json: (ii) has no event tag to evaluate"))
    Y.append("    b_other_stdout_paths_with_more_than_one_record: " + q(r["duplicate_other_stdout"]))
    Y.append("    callgrind_S3_independent_count: " + q(r["callgrind"]))
    Y.append("    mismatches: " + q(r["mismatches"]))
    M.append("")
    M.append("Events: 0 (no SE-3 / HR-3 event recorded; (ii) not evaluable). (b): other stdout paths carried by more than one "
             "reconstructed record: %s. Callgrind, an independent count RI-1 does NOT read: %s. Mismatches: %s.\n"
             % (json.dumps(r["duplicate_other_stdout"]) if r["duplicate_other_stdout"] else "none", json.dumps(r["callgrind"], sort_keys=True),
                json.dumps(r["mismatches"]) if r["mismatches"] else "none"))
open(os.path.join(SCR, "tables.yaml.part"), "w").write("\n".join(Y) + "\n")
open(os.path.join(SCR, "tables.md.part"), "w").write("\n".join(M) + "\n")
print("yaml lines", len(Y), "md lines", len(M))
````

### `selfcheck.py`

- sha256: `6e6acce83a95bdb6c2ad03aabb3b5e0c869ae1b61b6f7c569ce13265c5f85101`
- bytes: 1231; lines: 22
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B selfcheck.py <files>   (cwd <scratch>/rt_be2daf)`
- role: CRI-7 self-check; reads its word list at run time; prints hit counts only

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf CRI-7 name self-check (scratch). Reads its word list AT RUN TIME from words.txt next to this
# script (placed by the dispatching session outside write_scope; one word per line) and counts case-insensitive
# occurrences of each listed word in each file named on the command line. Prints ONLY: the sha256 of words.txt, the
# number of words, and per file the number of hits and the line numbers that hold a hit. It never prints a word.
# Imports only hashlib, os, sys.
import hashlib
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
wb = open(os.path.join(here, "words.txt"), "rb").read()
words = [w.strip().lower() for w in wb.decode("utf-8", "replace").splitlines() if w.strip()]
print("words.txt sha256 %s; %d words" % (hashlib.sha256(wb).hexdigest(), len(words)))
total = 0
for p in sys.argv[1:]:
    lines = open(p, encoding="utf-8", errors="replace").read().lower().splitlines()
    hit_lines = [i for i, line in enumerate(lines, start=1) if any(w in line for w in words)]
    n = sum(line.count(w) for line in lines for w in words)
    total += n
    print("%-60s hits %d lines %s" % (os.path.basename(p), n, hit_lines[:40]))
print("TOTAL hits %d" % total)
````

### `appendix.py`

- sha256: `bd8bcc44a70797a2208677ac0287396091b39ecaad2ee080b522ef1f257b6710`
- bytes: 3889; lines: 45
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B appendix.py   (cwd <scratch>/rt_be2daf)`
- role: writes this appendix

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf appendix writer (scratch). Reproduces each computation script of this review VERBATIM, and the
# outputs its statements rest on, each with its sha256, size and the argv it ran under, into appendix.md.part in this
# directory. Reads only files in this directory. Imports only hashlib, os.
import hashlib
import os

SCR = os.path.dirname(os.path.abspath(__file__))
E = "PYTHONDONTWRITEBYTECODE=1 timeout %d python3 -B %s   (cwd <scratch>/rt_be2daf)"
ITEMS = [
    ("pkgread.py", E % (300, "pkgread.py pkgread.json > pkgread.out 2>&1"), "O_NOATIME listing of the four archived r3 gate packages and read-only reads of solver-events.json, raw-result.json, command.txt and the child/*.spec.json files (lstat before / after)"),
    ("pkgread.out", "(stdout of pkgread.py)", "its printed summary; pkgread.json (the data) is kept in scratch, hash in the attestation"),
    ("scan.py", E % (300, "scan.py scan.json > scan.out 2>&1"), "ast scan of the three implementation trees (run_child / solve / run_system definitions, references and call sites; dis of v2_solver.py line 181), under an audit-hook guard"),
    ("scan.out", "(stdout of scan.py)", "its output"),
    ("scan2.py", E % (300, "scan2.py scan2.json /nonexistent-dir-for-B > scan2.out 2>&1"), "ast scan for process-ending, exec, spawn and hook calls (BJ-1 (5)); part B deliberately given no directory"),
    ("scan2.out", "(stdout of scan2.py)", "its output"),
    ("rteval_v1.py", E % (600, "rteval_v1.py > rteval_v1.out 2>&1"), "evaluator version 1: the rule functions and the BJ-0 objects (a)-(f); edited once before its first run (weak-mode COUNT GAP for N = 0); no output existed before that edit"),
    ("rteval_v2.py", E % (600, "rteval_v2.py > rteval_v2.out 2>&1"), "evaluator version 2 = version 1 with an exec of rteval_v2_objects.py appended before the final write; every rule function unchanged (diff shown in the md, section 2)"),
    ("rteval_v2_objects.py", "(executed inside rteval_v2.py by exec(compile(...)))", "the BJ-1..BJ-4 objects; defines no rule function"),
    ("rteval_v2.out", "(stdout of rteval_v2.py)", "FINAL evaluator output; lines 1-544 are byte-identical to rteval_v1.out lines 1-544 (the BJ-0 section)"),
    ("rdscan.py", E % (300, "rdscan.py rdscan.json > rdscan.out 2>&1"), "BJ-4 (2): every recorded value carrying the run directory in four archived packages (O_NOATIME, lstat before / after)"),
    ("rdscan.out", "(stdout of rdscan.py)", "its output"),
    ("tables.py", E % (120, "tables.py"), "writes the listing and count table parts from rteval_v2.json"),
    ("selfcheck.py", E % (60, "selfcheck.py <files>"), "CRI-7 self-check; reads its word list at run time; prints hit counts only"),
    ("appendix.py", E % (60, "appendix.py"), "writes this appendix"),
]
out = ["## Appendix: computation scripts and outputs, verbatim\n",
       "Every script below ran in this review's scratch directory (`<scratch>/rt_be2daf/`, outside the repository). "
       "Each is reproduced verbatim with its sha256, size and argv. rteval_v1.out (sha256 given in the attestation) is not "
       "reproduced: its lines 1-544 equal rteval_v2.out lines 1-544 (checked by a one-line Python comparison, section 13.4 of "
       "this report), and its remaining line is the file-writing message.\n"]
for name, argv, role in ITEMS:
    p = os.path.join(SCR, name)
    b = open(p, "rb").read()
    t = b.decode("utf-8", "replace")
    out.append("### `%s`\n" % name)
    out.append("- sha256: `%s`" % hashlib.sha256(b).hexdigest())
    out.append("- bytes: %d; lines: %d" % (len(b), t.count("\n")))
    out.append("- argv: `%s`" % argv)
    out.append("- role: %s\n" % role)
    out.append("````text")
    out.append(t.rstrip("\n"))
    out.append("````\n")
open(os.path.join(SCR, "appendix.md.part"), "w").write("\n".join(out) + "\n")
print("appendix parts", len(ITEMS))
````

### `assemble.py`

- sha256: `3d7575a2bc381f90f4f939ef308da7110d0621a4e278c738ae7f3f37ff53a229`
- bytes: 4886; lines: 88
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B assemble.py   (cwd <scratch>/rt_be2daf)`
- role: writes the two deliverables from the parts (this file's text is reproduced here by the file itself)

````text
#!/usr/bin/env python3
# TASK-20260924-be2daf report assembler (scratch). Concatenates the report parts written in this directory into the
# two deliverables, writing each deliverable ONCE, whole, directly (no temporary file beside it):
#   review-report.yaml = body.yaml.part (with the command log and the scratch-file list inserted) + tables.yaml.part
#   review-report.md   = body.md.part + attest.md.part + the command log + the scratch-file list + tables.md.part
#                        + appendix.md.part + this script's own text (verbatim, with its sha256)
# It computes nothing a finding rests on: the only values it derives are the sha256 and size of each scratch file at
# assembly time. Reads only files in this directory; writes only the two deliverables. Imports only hashlib, os, json.
import hashlib
import json
import os

SCR = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf"
PURPOSE = {
    "appendix.md.part": "md part: the verbatim appendix written by appendix.py",
    "appendix.py": "appendix writer",
    "assemble.py": "this assembler",
    "attest.md.part": "md part: red_team_report and attestation (readable)",
    "body.md.part": "md part: sections 1-14",
    "body.yaml.part": "yaml part: everything except the tables",
    "cmdlog.txt": "running command log (hash at assembly; later entries are the post-write checks)",
    "pkgread.json": "pkgread.py data (archived-package listings and records)",
    "pkgread.out": "pkgread.py printed summary",
    "pkgread.py": "archived-package reader (O_NOATIME)",
    "rdscan.json": "rdscan.py data",
    "rdscan.out": "rdscan.py printed summary",
    "rdscan.py": "run-directory value scan (O_NOATIME)",
    "rteval_v1.json": "evaluator version 1 data",
    "rteval_v1.out": "evaluator version 1 output (BJ-0)",
    "rteval_v1.py": "evaluator version 1",
    "rteval_v2.json": "evaluator version 2 data (listing and count tables)",
    "rteval_v2.out": "evaluator version 2 output (final)",
    "rteval_v2.py": "evaluator version 2 (= version 1 + exec of the objects file)",
    "rteval_v2_objects.py": "BJ-1..BJ-4 objects executed inside rteval_v2.py",
    "scan.json": "scan.py data",
    "scan.out": "scan.py output",
    "scan.py": "ast / dis scan of the implementation trees",
    "scan2.json": "scan2.py data",
    "scan2.out": "scan2.py output",
    "scan2.py": "process-ending / exec / hook scan",
    "selfcheck.py": "CRI-7 name self-check",
    "tables.md.part": "md part: listing and count tables",
    "tables.py": "table writer",
    "tables.yaml.part": "yaml part: listing and count tables",
    "words.txt": "word list placed by the dispatching session (read only by selfcheck.py; never printed)",
}


def rd(name):
    return open(os.path.join(SCR, name), encoding="utf-8").read()


names = sorted(os.listdir(SCR))
rows = []
for n in names:
    b = open(os.path.join(SCR, n), "rb").read()
    rows.append((n, hashlib.sha256(b).hexdigest(), len(b), PURPOSE.get(n, "unlisted")))
cmdlog = rd("cmdlog.txt").rstrip("\n")

# ---- YAML
y = rd("body.yaml.part")
y = y.replace("  command_log: __CMDLOG__\n", "  command_log: |-\n" + "".join("    " + ln + "\n" for ln in cmdlog.split("\n")))
sf = "  scratch_files:\n" + "".join(
    "    - {file: %s, sha256_at_assembly: %s, bytes: %d, purpose: %s}\n" % (json.dumps("<scratch>/rt_be2daf/" + n), h, s, json.dumps(p))
    for n, h, s, p in rows)
y = y.replace("  scratch_files: __SCRATCH__\n", sf)
assert "__CMDLOG__" not in y and "__SCRATCH__" not in y
y = y.rstrip("\n") + "\n\n" + rd("tables.yaml.part")

# ---- MD
m = [rd("body.md.part").rstrip("\n"), rd("attest.md.part").rstrip("\n"), "", "```text", cmdlog, "```", "",
     "### 16.2 Scratch files (sha256 at assembly)", "", "| file | sha256 | bytes | purpose |", "|---|---|---|---|"]
m += ["| `<scratch>/rt_be2daf/%s` | %s | %d | %s |" % (n, h, s, p) for n, h, s, p in rows]
m += ["", rd("tables.md.part").rstrip("\n"), "", rd("appendix.md.part").rstrip("\n"), ""]
me = open(os.path.abspath(__file__), "rb").read()
m += ["### `assemble.py`", "", "- sha256: `%s`" % hashlib.sha256(me).hexdigest(), "- bytes: %d; lines: %d" % (len(me), me.count(b"\n")),
      "- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B assemble.py   (cwd <scratch>/rt_be2daf)`",
      "- role: writes the two deliverables from the parts (this file's text is reproduced here by the file itself)", "",
      "````text", me.decode("utf-8").rstrip("\n"), "````", ""]
md = "\n".join(m)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "review-report.yaml"), "w", encoding="utf-8") as fh:
    fh.write(y)
with open(os.path.join(OUT, "review-report.md"), "w", encoding="utf-8") as fh:
    fh.write(md)
print("wrote yaml %d bytes, md %d bytes; scratch files listed %d" % (len(y.encode()), len(md.encode()), len(rows)))
````
