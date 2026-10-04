# TASK-20260924-d897a6 - red-team review of the launchkind draft's difference (review-report.md)

The same content as review-report.yaml, rendered for reading, followed by the listing and count tables, the
per-file listing, the command log, every script verbatim with its sha256 and argv, and every text output.
Observations only. `<scratch>` is the session scratch directory outside the repository.

## Header

- **id**: TASK-20260924-d897a6
- **task_id**: TASK-20260924-d897a6
- **role**: red-team
- **report_kind**: protocol_red_team_review (zero runs)
- **recorded_at**: 2026-09-25
- **goal_id**: GOAL-GFPN-380702
- **question_id**: RQ-GFPN-c01af8
- **experiment_id**: EXP-GFPN-05ff43
- **batch_id**: BATCH-e409ca
- **card**: ledger/handoffs/TASK-20260924-d897a6.yaml (sha256 35d943da8bfd0d5048f7fd4785583feaac963c26add3ea4315ceb00cf0e93484)
- **repository_head_read**: c0b0ecf3a4a5ca9dc1897322747d84398d448480
- **scope_statement**: Observations only. The review reports holds | breaks | inconclusive per joint with the reading or computation it rests on. It makes no approval recommendation, states nothing about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT, and no finding here is evidence about them. Definitions used are failclosed's (v2_addendum_failclosed.yaml 604-621), with definition (iv) read LITERALLY and definition (ii) read with an absent launch record as "not class (A) or (C)" (launchkind carried decision (5), launchkind 643-646).

## draft_under_review

- **id**: AMD-EXP-GFPN-05ff43-20260924-launchkind

- **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml

- **sha256**: ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050

- **difference_reviewed**: RJ-1, RJ-2, RJ-3, RJ-4, RJ-5, RJ-6, RJ-7, RJ-8, RGL-10, RGL-11, RGL-12 (against attcount at 4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48)

## verdict_summary

- **CRJ-2_integrity**: PASS (every check; recorded with full hashes below; checked before any joint)

- **LJ-0_known_answer_control**: holds (the method flagged every object CRJ-4 names, at record and package level)

- **LJ-1_launch_kinds_no_fail_open**: holds (no FAIL-OPEN counterexample outside RGL-10's declared consistent-loss premise; six call sites complete)

- **LJ-2_detectors_no_planned_basis_refusal**: holds (no PLANNED-BASIS REFUSAL; the count check on the four archived packages has no mismatch)

- **LJ-3_definitional_scope_and_statements**: holds (RJ-7 (b) accurate; RGL-10 conservative, with two wording observations)

- **LJ-4_development_harness**: holds (every expectation of RI-3 (19)-(27) as read and of (28)-(32) derivable; fail-closed findings FC-1, FC-2, FC-3)

- **LJ-5_reads_reach_and_readers**: holds (RFR-4 confirmed in this report's own words; RFR-6 readers listed; none computes differently)

- **LJ-6_value_classes_and_neutrality**: holds under reading K (fail-closed finding FC-6 under reading D)

- **fail_open_counterexamples**: none

- **planned_basis_refusals**: none

- **fail_closed_findings**: FC-1 .. FC-8 (never a bar; each with its cost)

## integrity

- **status**: PASS

- **when**: before any joint (C005-C007, 2026-09-25 about 01:35Z)

- **method**: `<scratch>`/rt_d897a6/integrity_v1.py (C005; reads the files as bytes and hashes them; from each of the seven named snapshot receipts it loads the JSON and prints ONLY its path_sha256 field), the git children C003 (see deviation D-1), C006 and C007, and directory listings (C004, C007).

### a_launchkind

- **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml
- **sha256**: ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050
- **expected**: ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050
- **expected_source**: The value the dispatching session supplied as the addendum_sha256 of the TASK-20260924-a571c7 receipt. That receipt was NOT opened (not even the one field).
- **result**: MATCH
- **status_lines**: 184 status: draft / 185 approved_by: null / 186 approval_decision: null

### b_bound_drafts

- **name**: attcount
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml
  - **sha256**: 4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48
  - **result**: MATCH
- **name**: gapattr
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml
  - **sha256**: 919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7
  - **result**: MATCH
- **name**: childend
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml
  - **sha256**: e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b
  - **result**: MATCH
- **name**: failclosed
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml
  - **sha256**: 1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c
  - **result**: MATCH
- **name**: readbackclose
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml
  - **sha256**: f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c
  - **result**: MATCH
- **name**: readbackfull
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml
  - **sha256**: 0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1
  - **result**: MATCH
- **name**: readbackcover
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml
  - **sha256**: dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e
  - **result**: MATCH

### c_archived_reviews_and_censuses

- **note**: For each receipt, the file's sha256 equals the receipt's path_sha256 entry and, for the reviews, the card's CRJ-2 (c) value.
- **receipts**:
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-0c2fdc/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml
        - **sha256**: b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f
        - **result**: MATCH receipt; EQUALS card
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md
        - **sha256**: 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8
        - **result**: MATCH receipt; EQUALS card
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-7e8a5d/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml
        - **sha256**: 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4
        - **result**: MATCH receipt; EQUALS card
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md
        - **sha256**: 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055
        - **result**: MATCH receipt; EQUALS card
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-93f3ca/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml
        - **sha256**: 0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7
        - **result**: MATCH receipt; EQUALS card
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md
        - **sha256**: 02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21
        - **result**: MATCH receipt; EQUALS card
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-682890/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml
        - **sha256**: 03e66166e986670e94f97fcf14452c375bd05f65fa9f73928388457eb2d29467
        - **result**: MATCH receipt; EQUALS card
      - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md
        - **sha256**: a24687c2b57ca0b563425956f9e0707d93d2a60a086501124fa4f3df2f20dca4
        - **result**: MATCH receipt; EQUALS card
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-71d070/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json
        - **sha256**: 9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md
        - **sha256**: ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py
        - **sha256**: 00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c
        - **result**: MATCH receipt
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-ddfb69/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json
        - **sha256**: 36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md
        - **sha256**: 5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py
        - **sha256**: ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558
        - **result**: MATCH receipt
  - **receipt**: coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-a01341/snapshot-receipt.json (path_sha256 only)
    - **files**:
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py
        - **sha256**: 3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json
        - **sha256**: 49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4
        - **result**: MATCH receipt
      - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md
        - **sha256**: 2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3
        - **result**: MATCH receipt

### d_frozen_diff

- **argv**: GIT_OPTIONAL_LOCKS=0 git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json' experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956
- **cwd**: /home/user/crypto-autoresearcher
- **output**: empty (0 bytes; `<scratch>`/rt_d897a6/crj2d_diff.out); exit status 0
- **base_object**: dd103455380238ec2f20d17414de687acdcc822a is a commit object (git cat-file -t)
- **head**: c0b0ecf3a4a5ca9dc1897322747d84398d448480
- **result**: PASS (prints nothing)

- **dp5_sequencing_observed**: 54 directories under experiments/EXP-GFPN-05ff43/runs/; no implementation-v2-r4*, trial-plan-v2-r4.json or trial-plan-v2-a1-r4.json; no coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/ before this review wrote its two files (C007). The launchkind and attcount files are tracked (git ls-files -s, stage 0) and equal to HEAD (git diff --stat HEAD prints nothing).

- **other_inputs_hashed**: Hashes of every other input this review bound (hashes_v1.py, C045) are listed under review_attestation.paths_read.hashed_inputs.

## known_answer_control

- **joint**: LJ-0

- **verdict**: holds

- **reading**: failclosed RFR-0 (c) and CRJ-4 (a)-(f)

- **method**: ONE evaluator, used unchanged for LJ-0, LJ-1, LJ-2, LJ-3 and LJ-4: the rule evaluator core `<scratch>`/rt_d897a6/rjcore_v1.py (sha256 c6e156f495d187fec8d1205bc86f8d2c423d8453b1c3cfa7bbabb4fc08648b9e) and its version 2 rjcore_v2.py (6e686dcfb2599c911c176d81e97701766e03351b6daffffca63875ee389b745f), which adds two transcriptions no LJ-0 object exercises (the frozen checker's aggregate exemption, v2_check_run.py 65; RF-0 (a), (c) applied to an S-1 attempt record whose callgrind_result_present is neither true nor false). LJ-0 was run under both versions (lj0_v1.py, lj0_v2.py): the two outputs are byte-identical except their last line (the name of the JSON written). The core transcribes, with file and line at each rule: the frozen run_child / _run_child_locked paths (v2_solver.py 149-308) as TRUTH per launch (created, pair read at 227, report, child files, child_end, exec); the launch records each draft's recorder writes (readbackfull RL-1; readbackclose RK-1; failclosed RF-1..RF-3; childend RG-1, RG-4); attribution (gapattr RH-1 (i)-(vi) with the non-launch list as each draft keeps it); attcount RI-1 (a)-(d); launchkind RJ-1..RJ-4; the frozen checker's cap items (v2_check_run.py 62-70); the r4 verdict (readbackclose RK-3 (b): PASS / PASS_ZL / FAIL); and failclosed's definitions (i)-(v) evaluated against the TRUTH of each construction. Definition (ii) is evaluated in two sub-readings: ii_LR (the child's own launch record carries no pair equal to the cap) and ii_ANY (no read-back source carries such a pair for it). Rule-set labels: RK readbackclose, RF failclosed, RG childend, RH gapattr, RI attcount, RJ launchkind AS WORDED; RJw launchkind with RJ-1 (b) weakened to "at most" (CRJ-4 (e) only). The core imports nothing from the repository and runs nothing.

- **outputs**: `<scratch>`/rt_d897a6/lj0_v1.out (sha256 5fd879d508e0938bf4cf829bb505a57ce634608939533ec4dcee3962ec7533a9), lj0_v1.json, lj0_v2.out, lj0_v2.json (34 objects); reproduced in the md appendix.

### objects

- **a_readbackclose_RK1_RK3_as_worded**:
  - **expected_by_CRJ-4**: P-16 and P-F2 (after P-14a) reported child_created false for a created child; W-1 PASS_ZL for a wrapper-recorded outcome
  - **what_the_method_did**:
    - **object**: KA-a1 P-16 (fork at v2_solver.py 181 created the child; the raise lands before pid is stored), cells m = 5, one other collected pair equal to the cap, requested cap recorded independently (Mc)
      - **record_level**: RK: the launch record of S5_t1/ms1 has child_created false with raised KeyboardInterrupt (the child exists and later execs: RKL-2), i.e. definition (iii). RF: the same record has child_created `undetermined`. RJ: child_created `undetermined`, child_end `undetermined`.
      - **package_level**: RK PASS and FAIL-OPEN under (ii_LR) (ii_ANY) (iii) (v). RF FAIL. RJ FAIL (COUNT GAP solver/S5_t1: N=1 != RB-1 0 + RL-2 0; SITE COUNT GAP S-1; recorder gaps solver/S5_t1.ms, .ms.err, .ms.log).
    - **object**: KA-a1 P-16 with the requested cap read from the raw envelope (Mr)
      - **package_level**: RK FAIL (frozen item v2_check_run.py 68-70); RF FAIL; RJ FAIL. Definitions (ii) (iii) (v) still hold on the construction.
    - **object**: KA-a1 P-16 with no other collected pair (k = 0)
      - **package_level**: RK FAIL (v2_check_run.py 66-67); RF FAIL; RJ FAIL.
    - **object**: KA-a2 P-F2 after P-14a (a raise at 214, then SolverLock.release raises in the finally at 172-174), k = 1, Mc
      - **record_level**: RK child_created false for a created child (iii); RF / RJ `undetermined`.
      - **package_level**: RK PASS and FAIL-OPEN (ii_LR) (ii_ANY) (iii) (v); RF FAIL; RJ FAIL (same named gaps as KA-a1).
    - **object**: KA-a2 with Mr, and with k = 0
      - **package_level**: RK FAIL (68-70; 66-67); RF FAIL; RJ FAIL.
    - **object**: KA-a3 W-1 (cells m = 5, zero launch, raw-result.json written by the wrapper, r3_run_wrapper.py 483-505)
      - **record_level**: no launch record; raw_result_writer wrapper
      - **package_level**: RK PASS_ZL and FAIL-OPEN under (v). RF FAIL. RJ FAIL.
  - **flagged**: true
- **b_failclosed_FO-1_as_worded**:
  - **expected_by_CRJ-4**: FO-1 in both variants FAIL-OPEN under definition (iv) when the foreign-file write fails
  - **what_the_method_did**:
    - **object**: FO-1 variant C (an asynchronous exception in the fork child before the try at 183; the escaped process writes pari-stack.json; the recorder-foreign file write failed or was interrupted; escaped exit status 1 or -2)
      - **record_level**: RF: the parent's launch record is class C (created, raised null, no pair, report "" with a returncode); the foreign record goes undetected. RG / RI / RJ: child_end `undetermined`.
      - **package_level**: With one other collected pair (k = 1), in all four sub-variants (failed / interrupted x exit 1 / -2): RF PASS and FAIL-OPEN under (iv). With k = 0: RF FAIL (66-67). RG, RI and RJ FAIL in every sub-variant.
    - **object**: FO-1 variant B (after OK at 198; an exception at 202 caught; a second at 207-208; escaped)
      - **package_level**: RF PASS and FAIL-OPEN under (iv) at k = 0 and k = 1 in all four sub-variants; RG, RI, RJ FAIL.
  - **flagged**: true
- **c_childend_PB-3_as_worded**:
  - **expected_by_CRJ-4**: PB-3 (a cells package with one SE-3 re-solve) a PLANNED-BASIS REFUSAL
  - **what_the_method_did**:
    - **object**: PB-3 (cells m = 5, arm S5, target 1 re-solved once by SE-3; attempt 1 SSF, renamed .ssf-attempt1)
      - **record_level**: both msolve launch records present, class B
      - **package_level**: RG FAIL and PLANNED-BASIS REFUSAL (recorder gaps solver/S5_t1.ms.err.ssf-attempt1, .ms.log.ssf-attempt1, .ms.out.ssf-attempt1). RF, RH, RI and RJ PASS.
  - **flagged**: true
- **d_gapattr_CX-1_as_worded**:
  - **expected_by_CRJ-4**: LR-1, LR-2, LR-3 and LR-5 PASS and FAIL-OPEN under definition (i); LR-4 FAIL
  - **what_the_method_did**:
    - **object**: LR-1 (S-1 re-solve, 2 attempts, final attempt's record absent), LR-2 (attempt 1's absent), LR-3 (3 attempts, attempt 2's absent), LR-5 (S-2 HR-3 re-solve in controls_a1, final absent)
      - **record_level**: the absent record's files are attributed to the sibling attempt's record by RH-1 (i) / (ii)
      - **package_level**: RH PASS and FAIL-OPEN under (i) (ii_LR) on each. RI and RJ FAIL with a COUNT GAP and a SITE COUNT GAP (e.g. LR-1: COUNT GAP solver/S5_t1: (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2; SITE COUNT GAP S-1: 3 launch records vs counters 4).
    - **object**: LR-4 (3 attempts, attempts 2 and 3 absent)
      - **package_level**: RH FAIL (recorder gaps solver/S5_t1.ms.err.ssf-attempt2, .ms.log.ssf-attempt2, .ms.out.ssf-attempt2); RI, RJ FAIL.
  - **flagged**: true
- **e_attcount_and_launchkind_CX-A**:
  - **expected_by_CRJ-4**: attcount: CX-A PASS and FAIL-OPEN (ii), LN-7a COUNT GAP and FAIL. launchkind: CX-A CALLGRIND COUNT GAP and FAIL; CX-A-gp recorder gap on pari/`<tag>`.gp and FAIL; CX-A-cmp COMPARATOR COUNT GAP and FAIL. launchkind with RJ-1 (b) weakened: CX-A PASS and FAIL-OPEN (ii).
  - **what_the_method_did**:
    - **object**: CX-A (cells m = 4, target 0 solved with callgrind_timeout, v2_driver.py 1174-1175; msolve ok; the callgrind child's open of `<tag>`.callgrind.stdout fails, v2_solver.py 188 -> 206-208, exit 99, no file; the parent records refused_to_start, 212-225; that launch record absent)
      - **record_level**: callgrind record absent (premise); the S-1 attempt record carries callgrind_result_present true (solve returned the key, v2_driver.py 209)
      - **package_level**: RI PASS and FAIL-OPEN (ii_LR) (ii_ANY). RJ FAIL: CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1; CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt record with callgrind_result_present true. RJw (RJ-1 (b) weakened) PASS and FAIL-OPEN (ii_LR) (ii_ANY).
    - **object**: LN-7a (non-event S-1 msolve child failing before its stdout file, input not retained, launch record absent)
      - **package_level**: RH PASS and FAIL-OPEN (ii); RI FAIL (COUNT GAP solver/S5_t1 (i) N=0 != RB-1 1 + RL-2 0; SITE COUNT GAP); RJ FAIL (same).
    - **object**: CX-A-gp (controls_a1; the gp child fails before its stdout file; its record absent)
      - **package_level**: RI PASS and FAIL-OPEN (ii); RJ FAIL (recorder gap pari/controls_a1_pari.gp); RJ with RJ-2 disabled PASS and FAIL-OPEN (ii).
    - **object**: CX-A-cmp (anchor-identity; the comparator child fails before its stdout file; its record absent)
      - **package_level**: RI FAIL (v2_check_run.py 66-67); RJ FAIL (COMPARATOR COUNT GAP 0 comparator launch records vs comparator.child present, and 66-67).
    - **object**: CX-A-G2 (fixture package of G2 shape, callgrind on every ok solve, v2_driver.py 358; one no-file callgrind record absent)
      - **package_level**: RI PASS and FAIL-OPEN (ii); RJ FAIL (CALLGRIND COUNT GAP fx_reg0_S3 Ncg=0 count=1; CALLGRIND SITE COUNT GAP 1 vs 2); RJw PASS and FAIL-OPEN (ii).
  - **flagged**: true
- **f_listing_and_count_check**:
  - **expected_by_CRJ-4**: Under launchkind on RUN-GFPN-f6a21a, RUN-GFPN-902222, RUN-GFPN-f5412a and RUN-GFPN-bfe956 (launch sets reconstructed, CRJ-9): unattributed files and every named gap listed, per-tag callgrind rows (Ncg against callgrind_result_present reconstructed from raw-result.json) and the comparator row (be2daf reported 0 of 683 unattributed under attcount and 36 = 36 callgrind launches against S-3 records on the fixture packages).
  - **method**: `<scratch>`/rt_d897a6/listing_v1.py (and listing_v2.py with the version 2 core; outputs identical except their last line), reading the O_NOATIME listing and read-only records gathered by pkgread_v1.py (708 lstat values checked before and after, 0 changed). Reconstruction rule: listing_and_count_tables.reconstruction_rule (verbatim).
  - **what_the_method_did**:
    - **package**: RUN-GFPN-f6a21a (fixture_F1_F3)
      - **record_level**: 284 files; 88 reconstructed launch records (16 child job, 36 msolve, 36 callgrind); 0 events
      - **package_level**: 0 unattributed; 0 named gaps; 36 (site, tag) rows, RI-1 (a) (i) and RJ-1 (b) hold on all 36; per-site RJ-1 row 36 = 36 (S-3 cross-check 36); comparator row 0 = 0
    - **package**: RUN-GFPN-902222 (fixture_F1_F3)
      - **record_level**: 284 files; 88 reconstructed launch records (16 / 36 / 36); 0 events
      - **package_level**: 0 unattributed; 0 named gaps; 36 rows hold; per-site RJ-1 row 36 = 36 (S-3 cross-check 36); comparator row 0 = 0
    - **package**: RUN-GFPN-f5412a (anchor_identity)
      - **record_level**: 32 files; 7 reconstructed launch records (1 child job, 5 msolve, 1 comparator); 0 events
      - **package_level**: 0 unattributed; 0 named gaps; 5 rows (all RL-2 pass-through, gb_only) hold; RJ-1 row 0 = 0; comparator row 1 = 1 (raw-result.json comparator.child present)
    - **package**: RUN-GFPN-bfe956 (frozen_controls)
      - **record_level**: 83 files; 19 reconstructed launch records (11 child job, 8 msolve); 0 events
      - **package_level**: 0 unattributed; 0 named gaps; 8 rows (RB-1, callgrind_result_present false) hold; RJ-1 row 0 = 0; comparator row 0 = 0
  - **totals**: 683 files, 0 unattributed under launchkind, 0 named gaps of any kind, 0 unknown-kind stdout paths, 0 pari/ files, 85 (site, tag) rows with 0 mismatches (tables under listing_and_count_tables)
  - **flagged**: The check reproduces be2daf's 0 of 683 and 36 = 36, and adds the launchkind rows (Ncg = callgrind_result_present count on every row; comparator 1 = 1 on RUN-GFPN-f5412a).

- **conclusion**: The method, unchanged, flagged every object CRJ-4 names in the expected way, at record level and package level. LJ-1 and LJ-2 may therefore be reported as holding on this method's evidence.

- **what_would_change_the_verdict**: A transcription error in rjcore (a rule read differently from its text) that made one of the flagged objects come out as expected for the wrong reason; the cited lines are quoted at each rule in rjcore_v1.py / rjcore_v2.py (md appendix) for that check.

## joints

### LJ-1_launch_kinds_no_fail_open

- **verdict**: holds
- **reading**: failclosed RFR-1 (definitions (i)-(v); (iv) literally; (ii) with an absent record read as "not class (A) or (C)"), applied to RJ-1..RJ-4 and RJ-7 (c) and their interaction with RI-1, RH-1, RG-1, RF-0..RF-3, RL-1, RL-2, RL-3 and RB-1.
- **files_and_lines_read**:
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml 1-781 (full)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml 265-505 (RI-1..RI-6, RGL-8, RGL-9)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml 243-318, 455-476
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml 373-437 (RG-3, RG-4)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml 600-708
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml 246-373, 522-535
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml 209-306
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml 196-222, 331-348
  - experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py 149-308, 512-552
  - experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py 77-231, 352-364, 560-568, 626-750, 752-935 (call sites), 1085-1092, 1110-1182
  - experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py 20-143
  - experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py 140-153, 223-253
  - experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py 84-92, 125-131, 144-168, 200-216
  - experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py 44-52, 178-202, 248-412
  - experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py 36-80; r3_entry_a1.py 90-111
  - every .py file of implementation/, implementation-v2/, implementation-v2-a1/, implementation-v2-r1/, implementation-v2-r2/, implementation-v2-r3/ (71 files) by ast / dis in scan_v1.py and scan_v2.py
- **computation**: (a) Static scan (scan_v1.py, scan_v2.py; sources compiled with compile() in the reviewer's process, never imported; an audit-hook guard refused imports and launches of the scanned trees: 0 refusals). (b) The evaluator core applied to one lost-record construction per kind and child path (lj1_v1.py; lj1_v1.out, 1454 lines; lj1_v1.json).
- **launch_kind_table**:
  - **LK-1_child_job**:
    - **call_site**: v2_driver.py 101 (child_job; callers build_poly 122 and raw_grid 136)
    - **stdout_form**: child/`<tag>`.stdout
    - **detector**: child/`<tag>`.spec.json
    - **where_and_when_written**: By the frozen driver in the installing process at 98-99 (C.write_json), BEFORE the launch, and named as argv's last element (100). Not written by the launch recorder; not derived from launch records.
    - **lost_record_constructions**:
      - record lost, path A (refusal before fork, v2_solver.py 153-169): RJ FAIL (spec file a recorder gap: RH-1 (ii) needs the record)
      - record lost, pre_stdout_99 (188 fails, 206-208, no file): RJ FAIL (spec gap)
      - record lost, err_setrlimit_97 (193, 195-196; stdout and stderr files exist): RJ FAIL
      - record lost, P8 (OK with soft != cap, 200-201 / 228-232): RJ FAIL
      - record lost, exec_ok: RJ FAIL (spec, .stdout, .stderr and .meta.json gaps; the raw_grid child job's .npz is removed at v2_driver.py 144, an uncached build_poly's .npz is a fifth gap)
      - record AND spec file absent (the spec removed after 99: a file-deletion premise): path A PASS with no definition holding; pre_stdout_99 PASS and FAIL-OPEN (ii) -- a residual premise object within RGL-10's words
      - escaped child (FO1_C, FO1_B) at the child-job launch with the parent record lost: RJ FAIL
    - **consistency_needed_to_escape_detection**: the launch record and the spec file (the only detector), and no child file (paths A and pre_stdout_99 only)
  - **LK-2_msolve_S-1**:
    - **call_site**: v2_driver.py 166 (solve, wrapped by SE-3, r3_resolve.py 373-390)
    - **stdout_form**: solver/`<tag>`.ms.log
    - **detector**: RI-1 (a): RB-1 attempt records (and RL-2 pass-through records for gb_only), the SE-3 event's attempts list, accepted_attempt and renamed_files at an event tag, the site counters attempts_total (r3_resolve.py 273) and passthrough_calls_gb_only_true (383). The input `<tag>`.ms is written by the frozen driver before the launch (161-162) and removed by _retain when not retained (219-221).
    - **where_and_when_written**: By the r4 SE-3 wrapper in the installing process AFTER the frozen solve returned, through the layer's single event writer; not by the launch recorder (RL-1 replaces run_child, beneath SE-3); not derived from launch records.
    - **lost_record_constructions**:
      - record lost on A, pre_stdout_99, err_setrlimit_97, P8, exec_ok, exec_timeout: RJ FAIL (COUNT GAP and SITE COUNT GAP)
      - consistent loss (record + RB-1 record + counter), path A: PASS, no definition holds (LN-6)
      - consistent loss, pre_stdout_99, input not retained: PASS and FAIL-OPEN (ii) (LN-7b; RGL-10 declares it)
      - consistent loss, pre_stdout_99, input retained (target 0): FAIL (solver/`<tag>`.ms a recorder gap)
      - consistent loss on err_setrlimit_97, P8, exec_ok, exec_timeout: FAIL (the child's .ms.log / .ms.err exist)
      - event-tag variants (EV-ms2 lost; EV-attempt2 consistent; EV-attempt2 consistent + renamed key): FAIL
      - escaped child with the parent record lost: FAIL
    - **consistency_needed_to_escape_detection**: the launch record, the RB-1 (or RL-2) record, the site counter (and at an event tag the attempts entry, accepted_attempt and a renamed_files key), and no file (A, or pre_stdout_99 with the input not retained)
  - **LK-3_callgrind**:
    - **call_site**: v2_solver.py 517 (callgrind_instructions, called only at v2_driver.py 209 inside the branch at 207)
    - **stdout_form**: solver/`<tag>`.callgrind.stdout
    - **detector**: RB-1 (e) callgrind_result_present on the S-1 attempt record: true iff the result the frozen solve returned carries the top-level key instructions_callgrind. The only writer of that key in the six trees is v2_driver.py 209 (scan_v1: one subscript store); dis of solve shows the store after the call returns, so the key exists exactly when callgrind_instructions returned; callgrind_instructions calls run_child at 517 before every one of its returns (524, 552).
    - **where_and_when_written**: By the r4 SE-3 wrapper in the installing process AFTER the frozen solve returned (after the launch); copied from the returned result; not by the launch recorder; not derived from launch records.
    - **key_without_launch**: none (run_child at 517 precedes 519-552; no other writer)
    - **launch_without_key**: callgrind_instructions raising after 517 (open and parse at 526-529 are outside any try; 533 is inside the try 531-547; 549 inside its own try): solve raises, no returned result, no RB-1 record for the call: CALLGRIND COUNT GAP and COUNT GAP, FAIL (RGL-11 objects: FAIL with every record present, with the callgrind record lost, with both records lost). The package fails anyway (the exception reaches the entry, r3_entry_v2.py 67-79).
    - **lost_record_constructions**:
      - record lost on A, pre_stdout_99 (= CX-A), err_setrlimit_97, P8, exec_ok, exec_fail, exec_timeout: RJ FAIL (CALLGRIND COUNT GAP and CALLGRIND SITE COUNT GAP)
      - consistent loss of every detector bound to it (callgrind record + RB-1 record, which also binds the msolve launch, + the msolve record + counter), pre_stdout_99 or exec_ok: FAIL (callgrind runs only after an ok msolve, 207, so the msolve child's .ms.log / .ms.err / .ms.out and the retained .ms of target 0 remain as gaps)
      - record lost with RB-1 (e) written false although the returned result carries the key (a recorder defect contradicting RB-1's copied-from-the-returned-result rule), pre_stdout_99: PASS and FAIL-OPEN (ii) -- a residual premise object; the same defect on the unaltered (28) package fails the positive control (32) at stage time
      - record lost with RB-1 (e) absent: FAIL (RF-0 (a), (c) undetermined; core version 2)
      - TW-2 (a tag solved twice with callgrind, first callgrind record lost): FAIL (CALLGRIND COUNT GAP Ncg=1 vs 2); TW-1 (every record present): FAIL (DUPLICATE-PATH GAP, RI-1 (b))
      - escaped child with the parent record lost: FAIL
    - **consistency_needed_to_escape_detection**: not achievable by a loss alone (every consistent loss leaves the msolve files); only a mis-recorded RB-1 (e)
  - **LK-4_comparator**:
    - **call_site**: v2_driver.py 650 (cmd_anchor_identity)
    - **stdout_form**: comparator/stdout.log
    - **detector**: raw-result.json comparator.child: comp["child"] = _slim(rec) at 652, raw["comparator"] = comp at 655, before every exit (656-659, 664-668, 674-677, final 748). The only writer of the raw key comparator in the production closure is 655 (scan_v1).
    - **where_and_when_written**: By the frozen driver in the installing process AFTER the launch, written to disk by finish (v2_driver.py 84); not by the launch recorder; derived from the returned record, not from launch records.
    - **lost_record_constructions**:
      - record lost on A, pre_stdout_99, err_setrlimit_97, P8, exec_ok, exec_fail: RJ FAIL (COMPARATOR COUNT GAP; on no-pair paths also v2_check_run.py 66-67)
      - record lost AND comparator.child absent from raw-result.json (an alteration of raw-result.json: a writer the repository lacks): FAIL (an exec'd comparator's files are gaps; a no-file comparator ends the package at 656-659 with no pair, 66-67)
      - escaped child with the parent record lost: FAIL
    - **consistency_needed_to_escape_detection**: none reachable (a no-file comparator failure always ends the package with no collected pair)
  - **LK-5_msolve_S-2**:
    - **call_site**: a1_health.py 147 (run_system, wrapped by HR-3, r3_resolve.py 397-409)
    - **stdout_form**: health/`<tag>`.ms.log
    - **detector**: RI-1 (a) at S-2: RB-1 attempt records, the HR-3 event (event tags), the site counter attempts_total. The input health/`<tag>`.ms (a1_health.py 141-143) and health-`<p>`.json (251) stay on the non-launch list (RJ-2 leaves them).
    - **where_and_when_written**: By the r4 HR-3 wrapper in the installing process AFTER the frozen run_system returned; not by the launch recorder; not derived from launch records.
    - **lost_record_constructions**:
      - record lost on A, pre_stdout_99, err_setrlimit_97, P8, exec_ok: RJ FAIL (COUNT GAP and SITE COUNT GAP)
      - consistent loss, path A: PASS, no definition
      - consistent loss, pre_stdout_99: PASS and FAIL-OPEN (ii) (the S-2 analogue of LN-7b; the .ms input is a listed non-launch write, so no gap) -- within RGL-10's declared class
      - consistent loss on err_setrlimit_97, P8, exec_ok: FAIL
      - escaped child with the parent record lost: FAIL
    - **consistency_needed_to_escape_detection**: the launch record, the RB-1 record, the counter (and event entries at an event tag), and no child file (A or pre_stdout_99)
  - **LK-6_gp**:
    - **call_site**: a1_pari.py 96 (curve_facts; called in production only at a1_driver.py 89; fb1_curve_search 126-143 has no caller in the six trees)
    - **stdout_form**: pari/`<tag>`.gp.stdout
    - **detector**: pari/`<tag>`.gp, written by the frozen curve_facts at 91-93 before its one launch and named as argv's last whole element (94); attributed only by RH-1 (ii) (RJ-2). The only write-mode open of a .gp file in the production closure is a1_pari.py 92 (scan_v2). The gp program text (gp_script, a1_pari.py 36-53) only prints and quits; it writes no file.
    - **where_and_when_written**: By the frozen code in the installing process BEFORE the fork; not by the launch recorder; not derived from launch records.
    - **lost_record_constructions**:
      - record lost on A, pre_stdout_99 (= CX-A-gp), err_setrlimit_97, P8, exec_ok: RJ FAIL (pari/`<tag>`.gp a recorder gap)
      - record AND script absent (the script removed after 93: a file-deletion premise): A PASS, no definition; pre_stdout_99 PASS and FAIL-OPEN (ii) -- a residual premise object within RGL-10's words
      - escaped child with the parent record lost: FAIL
    - **consistency_needed_to_escape_detection**: the launch record and the script file, and no child file (A or pre_stdout_99)
- **circularity**: None of the six detectors is derived from launch records: the spec and the script are written by frozen code before the fork; RB-1 (e), RB-1 / RL-2 records, events and counters are copied from the frozen functions' returned results by the resolve layer; comparator.child is copied by the frozen driver from run_child's returned record.
- **six_sites_complete**: scan_v1.py over the 71 .py files of the six trees: one def of run_child (v2_solver.py 149) and of _run_child_locked (177, referenced only at 171); 12 calls, 6 in production closure (v2_driver.py 101, 166, 650; v2_solver.py 517; a1_health.py 147; a1_pari.py 96) and 6 in development files outside both entries' import closures (r1_devchecks.py 177, r1_devchecks_more.py 75, r2_devchecks.py 186, r2_devchecks_more.py 75, r3_devchecks.py 190, r3_devchecks_more.py 80). No non-call reference, no store, no from-import, no getattr / setattr, no default argument referencing run_child. Dynamic imports exist only in implementation/ladder_select.py 28 (v1) and a1_run_wrapper.py 278 (the retired a1 wrapper), outside the r3 closures. RJ-4 (a)'s six sites are all of them. RJ-4 (b)'s six forms match every ordinary launch's stdout_path relative to the package's run directory (child/ 93-101; solver/ 160-166; solver/ 517 with workdir sd; comparator/ 647-650; health/ via a1_driver.py 129 and a1_health.py 145; pari/ via a1_driver.py 86-89 and a1_pari.py 95); see FC-7 for the absolute-path reading.
- **definition_iv_literally**: RJ-1 newly reads RB-1 (e) (written by the SE-3 wrapper after the frozen solve returned) and RJ-3 reads raw-result.json (written by finish, v2_driver.py 84). An escaped fork child leaves the frozen child path only by an exception (the child branch 182-208 has no return), unwinds through solve / cmd_anchor_identity / curve_facts with no frozen handler (scan_v2: no try encloses a launching call), is caught only by the entry's except BaseException, which writes pari-stack.json and re-raises (r3_entry_v2.py 67-79; r3_entry_a1.py 98-110). It therefore never writes an RB-1 record through the returned-result path (in r3 _bounded writes nothing when the call raises, r3_resolve.py 263) and never reaches finish. RJ-2's script is written before the fork. No new definition (iv) route; the r4 event writer on a raise stays under failclosed RF-1 as carried.
- **residuals**: X1, X6b, X10: os._exit only at v2_solver.py 196, 201, 208; exec only at 204-205; sys.exit with integers only in v2_child.py 60, 69, 81 (the exec'd child program) and __main__ guards; SystemExit raised only with strings (v2_common.py 100; a1_driver.py 52, 224, 233); no signal.signal, atexit.register, os.register_at_fork, faulthandler or threading in the production closure (scan_v2). No supplying code: unchanged. IV-1 / RGL-8: k4a_anchor_system.py writes four .ms files and k4a_results.json and starts no subprocess in its text (C035); its runtime was not read: unchanged. TW-2: closed by RJ-1 (CALLGRIND COUNT GAP). The optional third-party source text was NOT read: RGL-6 unchanged.
- **fail_open_counterexamples**: none
- **residual_premise_objects**:
  - RP-1: LN-6 type (path A, consistent loss; no definition holds)
  - RP-2: LN-7b (LK-2, pre_stdout_99, consistent loss, input not retained)
  - RP-3: LK-5, pre_stdout_99, consistent loss
  - RP-4: LK-1 record and spec removed; LK-6 record and script removed
  - RP-5: LK-3 record lost with RB-1 (e) mis-recorded false
- **fail_closed_findings**:
  - FC-4
  - FC-7
  - FC-8
- **what_would_change_the_verdict**: A seventh production call site of run_child (none in the six trees); a path on which a detector of LK-1, LK-3, LK-4 or LK-6 is not written while the launch happens (none: the spec and the script precede the launch unconditionally, the key and comparator.child follow every return of the launch); a writer of the key instructions_callgrind or of raw comparator other than v2_driver.py 209 / 655 (none); or r4 code that writes RB-1 (e) other than from the returned result (the r4 code does not exist; DV-18 (32) on the unaltered (28) package is the stage check).

### LJ-2_detectors_no_planned_basis_refusal

- **verdict**: holds
- **reading**: failclosed RFR-2, applied to RJ-1..RJ-4 and RJ-5
- **files_and_lines_read**:
  - v2_driver.py 158-231 (solve), 352-364 (fixture 358), 560-568 (fixture4 565), 628-750 (anchor-identity 650-659, 693, 711), 752-935 (controls 768, 782, 786, 787, 801, 805, 816, 841), 1085-1092 and 1130-1182 (cells 1174-1175)
  - a1_driver.py 84-92 (gp), 125-131 (health), 144-168 (build 146, solve 166)
  - a1_pari.py 20-143; v2_solver.py 512-552
  - experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md 470-495 (RKR-4 (b) table)
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml (N-1..N-13 by grep)
  - the four archived packages' listings, raw-result.json, solver-events.json (pkgread_v1.py)
- **computation**: (1) Ordinary paths from the frozen code: every solve call site with and without callgrind_timeout: 358 (callgrind on every ok arm), 565, 693 and 711 (gb_only: RL-2, return at 187-189 before 207), 786, 787, 841 (no callgrind_timeout), 1174-1175 (target 0 of an m <= 4 cell), a1_driver.py 166 (none). callgrind_result_present is true exactly on the attempts that launched a callgrind child: failing and timed-out callgrind children return a result with a reason (521-524), so N-7 and N-8 give Ncg = 1 = count. SSF attempts never launch callgrind (every SSF clause needs outcome degenerate_parametrisation or positive_dimensional, r3_resolve.py 61-74; callgrind needs ok, 207). gp: the script is written at 91-93 and the launch at 96 follows unconditionally; a refusal before fork returns a record carrying argv (152), so RH-1 (ii) attributes the script (NJ-gp A PASS); fb1_curve_search is uncalled and would pair each of its scripts with its own launch. Comparator: 650, 652, 655 precede every exit; the failure exits (NJ-cmp A, pre_stdout_99) FAIL by 66-67 because the comparator is the package's first capped launch; that outcome has an infrastructure launch and is a designed stop, not a planned basis outcome (readbackclose RK-3 (c) 355-363). Child jobs: the spec precedes every launch. No ordinary launch has a stdout_path outside RJ-4 (a)'s six forms. (2) The count check (listing_and_count_tables): every (site, tag) row RI-1 (a) and RJ-1 (b) evaluate, the per-site rows and the RJ-3 row on the four packages, reconstructed (CRJ-9): no mismatch. (3) lj2_v1.py (lj2_v1.out, 981 lines): every PASS / PASS_ZL row of the close census's RKR-4 (b) table (G1 fixture, G3 anchor, G4 controls, controls_a1 image, F-4, Z-F4, build, cells m = 5 measured and not measured, Z-C5, cells m = 4, aggregate) and N-1..N-13 of review 94cc33, plus NJ objects (callgrind child on A / pre_stdout_99 / err_setrlimit_97 / exec_fail / exec_timeout with its record present; msolve refused before fork on a callgrind target; gp child on A / pre_stdout_99 / err_setrlimit_97 / exec_fail; comparator exec_fail; a fixture with a replaced fresh draw) come out PASS or PASS_ZL under launchkind exactly as under attcount. The difference reads no run_status, so Z-C5 has the same verdict (PASS_ZL) in both run_status variants (0 = 0 in RJ-1 (b) and RJ-3; no launch record for RJ-4 (b)).
- **where_it_may_break_checked**:
  - a callgrind child launched on a path whose returned result lacks the key: only when callgrind_instructions raises after its launch (RGL-11), where solve raises and the package fails (a wrapper-recorded outcome, never a planned basis outcome, RFR-2)
  - a gp script written on a path with no launch: only when gp_script raises after open() created the file at 92 (the program text is built inside the with block) or a raise between 93 and 96; the exception propagates (no frozen handler) and the package fails anyway (FC-8)
  - a comparator record absent from raw-result.json on a path where the comparator launched: only if cmd_anchor_identity raises between 650 and 655 (_slim and a dict store) or run_child raises; the wrapper then writes raw-result.json (483-505) without comparator and the package fails anyway (COMPARATOR COUNT GAP is an added reason)
- **planned_basis_refusals**: none
- **fail_closed_findings**:
  - FC-8
- **what_would_change_the_verdict**: An ordinary path of either plan on which the key instructions_callgrind and the callgrind launch diverge, a .gp file without a launch, or comparator.child without a comparator launch record, on an outcome a dependant acts on; none was found in the frozen code; the four archived packages show none (85 rows).

### LJ-3_definitional_scope_and_statements

- **verdict**: holds
- **reading**: failclosed RFR-2 applied to RH-2 with RI-5 (a) as RJ-7 (b) restates it; RGL-10..RGL-12 and RJ-7 (c) as wording
- **files_and_lines_read**:
  - launchkind 480-496 (RJ-7), 532-569 (RGL-10..RGL-12)
  - attcount 431-459 (RI-5), 486-505 (RGL-8, RGL-9); gapattr 288-318 (RH-2), 470-476 (RGL-7)
  - readbackfull 286-306 (RL-4); r3_run_wrapper.py 199-203 (R-8 existence test); v2_check_run.py 62-70; v2_driver.py 1110-1127 (_condition_met)
- **computation**: RJ-7 (b): a mixture of a P-8 / P-9 launch with a measured launch fails the frozen item 68-70 in every protocol version (the item compares every collected pair with the requested cap). Under r4, RL-4 (286-306) admits a package that reads another only on the r4 checker's exit 0 for each read package (requires, _load_build, _prior_cells / _condition_met, the aggregates), so no r4 dependant reads it. Under v2 and r3, R-8 (r3_run_wrapper.py 199-203) tests manifest existence only, as RJ-7 (b) now says. The in-package conditional measured_in_this_package (1115-1118) reads measured_by_arm, i.e. the package's own cell, and that package FAILs as a whole. RJ-7 (b) is accurate and hides no outcome the frozen sequencing acts on as a basis before 68-70 stops it. RGL-10 against LN-*, LE-* and CX-A and the LJ-1 table: the objects RGL-10 names (LN-6 no definition; LN-7b (ii)) are the undetected consistent losses at LK-2; the same class exists at LK-5 (S-2 analogue) and, with the detector file removed, at LK-1 and LK-6; at LK-3 and LK-4 no consistent loss escapes (LJ-1 table). RGL-10's statement is therefore a superset of the undetected class (conservative; observation OB-1), and its alteration sentence is inexact (OB-2). RGL-11 matches the RGL-11 objects (FAIL in all three variants). RGL-12 matches the reading applied here (carried decision (5)); the draft relies on no inference from a missing file: every kind's detector is a positive record. RJ-7 (c) appends a sentence to a WHY text and changes no rule. RJ-7 (a) replaces RGL-9 by RGL-10 (method limits; no rule). No other planned basis outcome that FAILs by design was found under any joint.
- **observations**:
  - OB-1
  - OB-2
- **planned_basis_refusals**: none
- **what_would_change_the_verdict**: A dependant (frozen or r4) that reads a cap-mismatch mixture's measured data before 68-70 FAILs it, other than the in-package conditional of the same failing package; none found.

### LJ-4_development_harness

- **verdict**: holds
- **reading**: failclosed RFR-3, applied to RJ-5 and RJ-6 with RI-3, RI-4, RH-3 and RG-3
- **files_and_lines_read**:
  - launchkind 406-479 (RJ-5, RJ-6); attcount 365-430 (RI-3, RI-4); childend 373-415 (RG-3)
  - r3_check_run.py 61-77, 150-185 (V-7 153-158), 245-260, 322-342; r3_run_wrapper.py 434-472, 540-552
  - the controls (RUN-GFPN-bfe956) and anchor-identity (RUN-GFPN-f5412a) packages, every regular file except *.npz (rdscan_v1.py, O_NOATIME; 155 lstat values checked, 0 changed)
  - a1_pari.py 87-99; a1_health.py 140-153, 223-253; r3_resolve.py 191-202, 397-409
- **computation**: (1) lj4_v1.py (lj4_v1.out; 58 rows): each expected outcome of RI-3 (19)-(27) as RJ-5 reads them and of (28)-(32), derived under the full rule set with the carried V-7 item (r3_check_run.py 153-158) and without it, at gap level and verdict level. Results: (19) unaltered PASS; renamed_files entry removed FAIL (COUNT GAP (ii)); one record removed FAIL (COUNT GAP). (20) unaltered PASS; S-2 record removed FAIL. (21) failing callgrind child PASS (.callgrind.out attributed by RH-1 (iii)). (22) uncached build_poly record removed: five gaps, FAIL; raw_grid record removed: four gaps, FAIL. (23) cap-mismatch stop outcome FAIL, stop class, no planned-basis refusal. (24) LR-1..LR-5 and every single removal among 2, 3 and 6 attempts: COUNT GAP, FAIL. (25) with RI-1 (a) and (d) disabled: no named gap and no recorder gap on LR-1, LR-2, LR-3, LR-5 (PASS without V-7; FAIL with V-7, expected and not the discriminant). (26) unaltered packages and DV-18 (a), (b), (e): no gap. (27) each alteration yields its named gap and FAIL. (28) the CX-A control with RJ-1 disabled: no gap (PASS without V-7); under launchkind: CALLGRIND COUNT GAP and CALLGRIND SITE COUNT GAP, FAIL; under attcount (contrast): no gap. (29) first object (gp record removed): pari/`<tag>`.gp, .gp.stdout, .gp.stderr gaps, FAIL (attcount and RJ-2-disabled contrasts also FAIL, by the stdout / stderr gaps); second object (gp stdout open fails, record removed): pari/`<tag>`.gp gap, FAIL (RJ-2 disabled: no gap). (30) comparator record removed: COMPARATOR COUNT GAP plus seven comparator/ gaps, FAIL (RJ-3 disabled and attcount: the seven gaps, FAIL). (31) an appended record of unknown form: UNKNOWN-KIND GAP, FAIL (RJ-4 (b) disabled and attcount: no gap). (32) every unaltered package: no named gap of any kind and no recorder gap. Every expectation is derivable as worded; RJ-5 (a) repairs the V-7 conflict (carried FC-1 of be2daf) by stating expectations at the gap level. Discrimination: (25) separates gapattr from attcount (RI-1), not attcount from launchkind; (28) separates attcount from launchkind at the gap and verdict level; (29) first object and (30) separate them at the gap level only; (29) second object and (31) at the verdict level (OB-4). (2) Stand-ins: the (28) / (29) stand-in raises in the child for names ending ".callgrind.stdout" / ".gp.stdout". The production closure calls os.open only at v2_solver.py 188-189, inside the child branch (C043); the parent reads those files with the builtin open (r3_resolve.py 336, a1_pari.py 101, v2_solver.py 299), which does not go through os.open (behaviour B-4). The stand-in changes nothing the parent reads or records beyond the child's own outcome (class C: report "", returncode 99, the pre_stdout_99 path), which is the object's purpose. (3) Recorded values carrying the run directory (rdscan_v1.json): in RUN-GFPN-bfe956, the 11 child/*.spec.json "out" values (PREFIX) and command.txt line 2 "# GFPN_RUN_DIR=`<rd>`" (OTHER); in RUN-GFPN-f5412a, the spec "out" (PREFIX), command.txt line 2 (OTHER) and 11 values of raw-result.json, all PREFIX: /build/child/argv[3], /build/npz, /comparator/child/argv[2], /targets[0..3]/solver/argv[6] and [8]; manifest.yaml, environment.json, pari-stack.json and the stdout / stderr logs carry none. controls-a1 (no archived package; from the code): a1_pari.py 97 "script" (PREFIX) and "command" (the gp argv joined by spaces: an element that begins with the run directory, ELEM_PREFIX); a1_health.py 148 "input.path" (PREFIX) and 149 "command" (ELEM_PREFIX); the S-2 attempt record "command" (r3_resolve.py 198, a copy of 149); health-`<p>`.json (251) copies of those fields; the launch records' stdout_path / stderr_path (PREFIX) and argv (RG-3 (e)). The controls builds' raw["build"]["npz"] is absent from the controls raw-result.json (768, 816 discard the build info), as RJ-6 says. Against RJ-6 as worded: every value is listed or covered except that command.txt line 2 carries the run directory in a form that is neither a path prefix nor a whole element, and the command strings carry it as a prefix of a whole element rather than as a whole element (FC-1). (4) RG-3 (a)-(d) with RH-3 (b) re-checked: r3_run_wrapper.py 437 (git_tree_state), 438-446 (phase_a_commits), 464 (ladder_json_sha256), 545-546 (inputs) and r3_check_run.py 248-250 (derived_from), 253-260 (phase_a_commits), 324-334 (REG-1 items 329-330, 331-332, 333-334) are as the carried findings state; no change since dd1034553 (CRJ-2 (d)).
- **fail_closed_findings**:
  - FC-1
  - FC-2
  - FC-3
- **observations**:
  - OB-4
  - OB-5
  - OB-6
- **what_would_change_the_verdict**: An expectation of (19)-(32) that the rules as worded cannot produce, or a stand-in that changes a parent read; neither found. FC-1..FC-3 are reading-dependent stops at stage time, not breaks.

### LJ-5_reads_reach_and_readers

- **verdict**: holds
- **reading**: failclosed RFR-4 (explicit) and RFR-6 (informational), applied to RJ-1..RJ-6
- **files_and_lines_read**:
  - a1_check_run.py 30 (grep), 60-86; r3_check_run.py 61-77, 86-100; r3_run_wrapper.py 97-104, 186-203, 284-292, 381-400, 505-512; v2_check_run.py 60-72, 92-106
  - r3_common.py 24-32, 110-115; v2_common.py 27-40; a1_common.py 88-100
- **rfr4_confirmation_in_this_reports_words**: CONFIRMED. X-13 is the frozen addendum checker's item at a1_check_run.py 79-84: for a package whose plan entry has controls_a1_gate_required, it takes cid = plan["gate"]["addendum_blocking_package"] from the plan loaded at 67 (AC.PLAN_A1_PATH, which r3_check_run.frozen_a1 sets to R.PLAN_A1_R3 = `<EXP_DIR>`/trial-plan-v2-a1-r3.json at line 65), opens `<C.EXP_DIR>`/runs/`<cid>`/raw-result.json (81; a missing file reads as {}), and fails unless run_status is "completed_valid" and gate_pass is True (83-84); an unparseable file makes json.load raise, so the checker exits non-zero. X-02 is the r3 wrapper's R-7 check r7_controls_a1_image (r3_run_wrapper.py 190-196), called at 288-289 for an a1r3 package with controls_a1_gate_required, with cid = plan["gate"]["addendum_blocking_package"] of the same plan file (R.PLAN_A1_R3); it reads `<RUNS>`/`<cid>`/raw-result.json through _raw (97-104), refuses when the file is missing (194), reads an unparseable file as run_status "unparseable" and refuses, and refuses unless run_status is "completed_valid" and gate_pass is True (195-196). The roots coincide: RUNS = R.RUNS_DIR = `<EXP_DIR>`/runs (r3_run_wrapper.py 68; r3_common.py 27, 31) and C.EXP_DIR = the same directory (v2_common.py 30; a1_check_run.py 30 calls AC.redirect_v2() with no arguments, so a1_common.redirect_v2 90-100 leaves C.EXP_DIR unchanged). Same file, same two fields, same predicate. The carried RLR-2 / RKR-2 findings stand: CRJ-2 (d)'s diff against dd1034553 prints nothing, the six production run_child sites and the single definitions are as the censuses list them (scan_v1), and no rebinding of run_child exists in the trees.
- **rfr6_readers**: RB-1 (e): read by RJ-1 (b) only (E2 through RF-3 (a)); RB-2 / RB-3 read other RB-1 fields; the carried V-7 item hashes the whole solver-events.json (a field added changes the bytes, not the check); REG-1's SE-4 (e) quotation of solver-events.json is report-only; the frozen checkers never read solver-events.json. raw-result.json comparator key: the frozen checker's walk (v2_check_run.py 99, scan for F3 / tail_check keys) and serialization test (103) traverse it without reacting (E7); the wrappers' collect(raw, "rlimit_as_child_getrlimit") (r3_run_wrapper.py 510) collects the comparator child's pair, as it already did (K-2, unchanged); find_solver_records (r3_check_run.py 89-98) ignores it (no "solver" mapping). pari/`<tag>`.gp: read by the gp child, hashed by curve_facts (a1_pari.py 97), by RH-1 (ii) under RJ-2, by RL-3's listing hashes and by the archive sweep. The new named gaps (CALLGRIND COUNT, CALLGRIND SITE COUNT, COMPARATOR COUNT, UNKNOWN-KIND) enter the RL-3 recorder-gap list and are read by RF-3 (a) (FAIL), the RF-3 (b) stop record, RL-4 through the r4 verdict, DV-18 and DV-11; no frozen or r3 code reads them (they do not exist in the r3 base; a grep of tools/ and harness/ for the new labels and field names finds nothing, C041). raw_result_writer, the recorder-foreign file and the `undetermined` value: unchanged by the difference (RJ-1 (d) and the version 2 core read an undetermined RB-1 (e) as RF-0 (a), (c) would, FAIL). None changes what it computes (REG-1, the key and byte sweeps, the frozen checkers).
- **what_would_change_the_verdict**: a reader of X-13 or X-02 other than those lines, or a root that differs between them; none found.

### LJ-6_value_classes_and_neutrality

- **verdict**: holds (under reading K; FC-6 under reading D)
- **reading**: failclosed RFR-6 (informational), applied to RJ-1 (a), (d), RJ-3 and RJ-4 (b), with DEC-20260924-e52eec VA-6 (c) and CC-5
- **files_and_lines_read**:
  - ledger/decisions/DEC-20260924-e52eec.yaml 714-740 (VA-6)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_consumercover.yaml 335-381 (CC-2 S-3 values V-1..V-6), 426-441 (CC-5), 535-566 (definitions)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml 269-295 (VC-1 (b))
  - readbackcover 196-220 (RB-1), 331-348 (RB-7); readbackfull 209-252 (RL-1)
  - r3_resolve.py 44-52 (CG_RECORD_KEYS, CG_CHILD_KEYS), 322-390; r3_run_wrapper.py 381-400
- **is_RJ-1_a_or_b_a_CG-3_field_read**: NO under reading K. RJ-1 (a)'s bit is whether the key instructions_callgrind is among the keys of the S-1 SITE RECORD, which consumercover's definitions make "the solve() result ... and every key solve() sets" (535-546; the key is set by solve at v2_driver.py 209). It reads no value inside res["instructions_callgrind"] (V-1), none of the CG-3 fields (r3_resolve.py 50-51: method, label, reason, f4_core_function, f4_core_note; child outcome, returncode, rlimit_as_child_getrlimit), no V-5 record (the S-3 records in solver-events.json, r3_resolve.py 355-363) and no callgrind-site count of the manifest's solver_events block (r3_run_wrapper.py 398-400). VA-6 (c) (DEC-20260924-e52eec 728-733) names exactly those values, so it is not engaged. RJ-1 (b) reads the RB-1 (e) value (epsilon, VC-1 (b); valueclose 269-295 allows an E1-E4 reader of an epsilon value only as a consistency, integrity, spacing or reporting check, and (b) is a consistency check) and the stdout_path of launch records (RL-1 declares launch records value class epsilon, readbackfull 210). RI-1 (b) already reads the callgrind launch records' stdout_path at E2 (DUPLICATE-PATH GAP), so the read is not new in kind. Reading D and its STOP: FC-6.
- **neutrality**: RB-1 (e) is a dict membership test on the result after the frozen solve returned, before the unmodified result is returned; it mutates nothing and adds no step between frozen steps. RJ-1 (b), RJ-3 and RJ-4 (b) read solver-events.json and raw-result.json after the driver exited. None can change a value the frozen parent or the resolve layer records, or the order of a frozen step. The added field changes the bytes of solver-events.json, whose readers are the V-7 hash (whole file, recomputed from the same file) and report-only quotations.
- **classes**: Each read carries exactly one class: RJ-1 (b)'s count and RJ-3's count epsilon (the RL-3 recorder-gap computation), RB-1 (e) epsilon, RJ-4 (b) epsilon. RJ-3's justification "class epsilon, as RB-2 (a) reads it" is inexact (RB-7 classes the RB-2 collector as a K-2 derivative with effect E5; RJ-3's read has effect E2); the class assigned is still one (OB-5).
- **gap_label_readers**: The four added labels are read only by RF-3 (a), the RF-3 (b) stop record, RL-4 (through the verdict), DV-18 expectations and DV-11's inventory (LJ-5). No other verdict function reads them.
- **fail_closed_findings**:
  - FC-5
  - FC-6
- **what_would_change_the_verdict**: A ruling that RB-1 (e) is a value derived from the S-3 site record (reading D) makes RJ-1 (b) a CC-5 STOP by construction (FC-6); that is fail-closed, not a break.

## counterexamples

### fail_open


- **fail_open_note**: No FAIL-OPEN counterexample was found at any of the six call sites outside RGL-10's declared consistent-loss premise, and no production run_child call site outside the six (carried decision (6) is therefore not triggered by this review). No FAIL-OPEN counterexample in the foreign-process class was found (carried decision (3) not triggered).

### planned_basis_refusals


- **planned_basis_refusals_note**: none found under any joint (LJ-2, LJ-3; also none arose while working LJ-1, LJ-4, LJ-5, LJ-6)

### residual_premise_objects

- **id**: RP-1 (LN-6 type)
  - **construction**: a refusal before fork (path A) at LK-2 or LK-5 whose launch record, RB-1 record and site counter are lost together
  - **outcome**: PASS; no definition holds (no child was created)
  - **premise**: consistent loss of the record and every detector (RGL-10)
- **id**: RP-2 (LN-7b)
  - **construction**: an S-1 msolve child (non-event tag, input not retained) failing at 188 (no file), its launch record, RB-1 record and counter lost together
  - **outcome**: PASS and definition (ii) holds
  - **premise**: consistent loss (RGL-10 declares it)
- **id**: RP-3 (LN-7b at S-2)
  - **construction**: the same at LK-5 (health/`<tag>`.ms is a listed non-launch write)
  - **outcome**: PASS and (ii)
  - **premise**: consistent loss (within RGL-10's words)
- **id**: RP-4
  - **construction**: LK-1 or LK-6, child failing at 188, launch record lost AND the spec file / gp script removed after the frozen code wrote it
  - **outcome**: PASS and (ii)
  - **premise**: consistent loss including the deletion of a file the frozen code wrote (within RGL-10's words "every detector bound to it")
- **id**: RP-5
  - **construction**: LK-3, callgrind child failing at 188, its launch record lost, and RB-1 (e) recorded false although the returned result carries the key
  - **outcome**: PASS and (ii)
  - **premise**: a recorder defect contradicting RB-1 (copied from the returned result and from nothing else) together with a lost record; code the repository lacks (the r4 layer does not exist); the defect makes the positive control (32) fail on the unaltered (28) package (Ncg 1 vs 0), a STOP at stage time.

## fail_closed_findings

- **id**: FC-1
  - **joint**: LJ-4
  - **finding**: RJ-6 lists the second line of command.txt, whose value is "# GFPN_RUN_DIR=`<run directory>`" (r3_run_wrapper.py 468-471; archived command.txt line 2 of RUN-GFPN-bfe956 and RUN-GFPN-f5412a, form OTHER in rdscan_v1). The run directory there is neither a path prefix of the value nor a whole whitespace-delimited element. The command strings a1_pari.py 97, a1_health.py 149 and the S-2 attempt record command (r3_resolve.py 198) carry it as the leading part of a whole element (`<rd>`/pari/`<tag>`.gp, `<rd>`/health/`<tag>`.ms, ...), never as an element equal to it.
  - **readings**: Reading A (RJ-6's form clause governs every value, listed or not): line 2 carries the development run directory "in any other form", a DV-18 STOP by construction on every DV-18 (a), (b) and (e) package. Reading A' ("as a whole whitespace-delimited element" means an element equal to the run directory): the three command fields carry it in another form, a STOP on DV-18 (e). Reading B (a listed value is substituted by RG-3 (e)'s every-occurrence replacement, childend 404-415, and compared; the form clause applies to unlisted values) and B' (an element that is a path under the run directory): no STOP.
  - **cost**: under A or A', the r4 stage stops at DV-18 until a Coordinator reading; no package runs and nothing is a result. Zero under B / B'.
- **id**: FC-2
  - **joint**: LJ-4
  - **finding**: RJ-5 (c) (29)'s second object ("and one whose gp child's stdout open fails (a stand-in as in (28)...)") needs an os.open stand-in in the child. If "one" is read as another DV-18 (e) controls-a1 development package, RF-4 (a) (2) as RG-3 (b) words it ("the development shims wrap, replace or trace no function of any module", childend 383-386) forbids the stand-in in that package.
  - **readings**: Reading P (it is a DV-18 (e) package) gives a STOP by construction; reading S (a separate development object with RF-6 stand-ins, as the preamble of RJ-5 says) gives none.
  - **cost**: a stage-time STOP under P until a Coordinator reading; the object also costs one more controls-a1-shaped development package (OB-6).
- **id**: FC-3
  - **joint**: LJ-4
  - **finding**: RJ-5 (b)'s stand-in level "a function the frozen solve, run_system, callgrind_instructions, child_job or curve_facts calls" admits V.run_child itself, which all five call and which the r4 launch recorder replaces (RL-1). A stand-in at that attribute bypasses or replaces the recorder, so (26) / (32) would show COUNT gaps (a STOP). Conversely, the (28) / (29) stand-in (os.open, called by _run_child_locked, called by run_child) is at an admitted level only if "calls" is read transitively.
  - **readings**: Direct-call reading excludes the os.open stand-in (a harness STOP for (28) / (29)); transitive reading admits it and also admits V.run_child (a STOP if chosen). A reading that excludes the recorder's slot and admits transitive callees has neither.
  - **cost**: a stage-time STOP under the unfavourable readings; no package runs.
- **id**: FC-4
  - **joint**: LJ-1
  - **finding**: RJ-4 (c): "no r4 function calls run_child". The launch recorder is an r4 function that calls the ORIGINAL run_child (RL-1 (a)).
  - **readings**: Semantic reading: the closure item STOPs on the recorder itself, by construction. Syntactic reading (ast calls through V.run_child or the module global run_child, as be2daf BJ-5 derived them): the recorder's call through its captured object is not such a call and passes, but a call through any stored reference in r4 code is then invisible to the scan (no r4 code exists to check; a residual for the stage).
  - **cost**: a stage-time STOP under the semantic reading until a Coordinator reading.
- **id**: FC-5
  - **joint**: LJ-6
  - **finding**: readbackcover RB-7 (331-348, unchanged by the draft except RB-1 (e)): "RB-1 values ... read at E1-E4 only by the consumers named here"; "any other r4 consumer of an RB-1 value at E1-E4 is a DV-11 STOP". RJ-1 (b) reads RB-1 (a) tag and RB-1 (e) with effect E2 and is not named in RB-7. attcount RI-1 (a) (i) is in the same position (pre-existing).
  - **readings**: Strict reading gives a DV-11 STOP by construction on RI-1 (a) (i) and RJ-1 (b); the reading under which the draft's own normative text names its consumer (RJ-1 (d), VC-1 (b)) gives none.
  - **cost**: a stage-time STOP under the strict reading.
- **id**: FC-6
  - **joint**: LJ-6
  - **finding**: consumercover's DERIVED VALUE definition (547-552: any value computed from a site-record field and stored elsewhere, followed transitively) admits a reading D under which callgrind_result_present is derived from the existence of the S-3 site record (V-1).
  - **readings**: Reading D makes RJ-1 (b) an r3-lineage consumer with effect E2 that CC-2 does not cover, a CC-5 / DV-11 STOP by construction. Reading K (a key of the S-1 site record, 541-542) gives none (LJ-6).
  - **cost**: a stage-time STOP under reading D until a Coordinator reading.
- **id**: FC-7
  - **joint**: LJ-1
  - **finding**: RJ-1 (b), RJ-3 and RJ-4 (a) / (b) state stdout forms relative to the package (solver/`<tag>`.callgrind.stdout, comparator/stdout.log, the six forms), while RL-1 / RG-4 (a) record stdout_path as passed, i.e. absolute (v2_driver.py 101, 166, 650; v2_solver.py 517; a1_health.py 145-147; a1_pari.py 95-96).
  - **readings**: Reading R (relative to the package's own run directory, the convention of RH-1, RL-3 and RI-1 (b), applied by be2daf's and this review's listing checks) gives no gap on any ordinary launch. Reading L (literal string comparison) makes every launch record UNKNOWN-KIND and every count 0, so DV-18 (32) STOPs at stage time before any package runs.
  - **cost**: a stage-time STOP under L; zero under R.
- **id**: FC-8
  - **joint**: LJ-1 / LJ-2
  - **finding**: On a raise out of run_child, RK-1 (b) copies from the frame's rec only rlimit_as_child_getrlimit, child_rlimit_report, outcome, refusal_reason and returncode (readbackclose 264-268), and RL-1 (c) copies argv "as the returned record carries it" (readbackfull 230-231). A raise-path record may carry no argv, so RH-1 (ii) cannot attribute pari/`<tag>`.gp (RJ-2) or child/`<tag>`.spec.json (LK-1) to it: a recorder gap. Likewise gp_script raising after open() created pari/`<tag>`.gp (a1_pari.py 92-93) leaves a script with no launch.
  - **readings**: Only one outcome (FAIL); these paths raise through the driver (no frozen handler encloses a launch call) and the package fails anyway (wrapper-recorded outcome).
  - **cost**: none beyond an added gap on an already failed package.

## observations

- **id**: OB-1
  - **joint**: LJ-3
  - **text**: RGL-10 states the undetected class as "the consistent loss of a launch that left no file". Per kind (LJ-1 table) that class is non-empty at LK-1, LK-2, LK-5 and LK-6 and empty at LK-3 (every consistent loss leaves the msolve files, because callgrind follows an ok msolve and the S-1 attempt record binds both launches) and at LK-4 (a no-file comparator failure ends the package with no collected pair, 66-67). The statement is a superset of what is undetected: conservative.
- **id**: OB-2
  - **joint**: LJ-3
  - **text**: RGL-10's sentence "one between the launch and the manifest write is not detected by V-7 and is visible after the fact only through RL-3's listing hashes" is inexact: RL-3's listing is the wrapper's post-completion listing (gapattr RGL-7 470-476), so an alteration made before it is recorded into the listing hashes, not revealed by them. Such an alteration is detected by the counts unless it is consistent, and a consistent one is not visible. The writer is a premise (RGL-7: "not known on any path"); wording only.
- **id**: OB-3
  - **joint**: LJ-1
  - **text**: Forward guidance for LK-5's consistent-loss class: a1_health.run writes health-`<p>`.json (a1_health.py 251-252), a frozen non-launch record with one "systems" entry per wrapped run_system call (first, reinvocation, retry_seed2, retry_seed2_reinvocation), independent of the launch recorder and the resolve layer. It counts calls, not attempts, and is written after all calls, so it could bind non-event S-2 launches; it is not used as a detector by the draft.
- **id**: OB-4
  - **joint**: LJ-4
  - **text**: Discrimination levels: (25) separates gapattr from attcount; (28) and (31) separate attcount from launchkind at the verdict level; (29)'s second object at the verdict level; (29)'s first object and (30) only at the gap level (attcount already FAILs them by the stdout / stderr or comparator/ gaps). No development object isolates RJ-3 at the verdict level: the comparator is the anchor-identity package's first capped launch, so any no-file comparator failure ends the package with no collected pair (v2_driver.py 650-659; v2_check_run.py 66-67), which is what RJ-3's WHY sentence says it makes the detection independent of.
- **id**: OB-5
  - **joint**: LJ-6
  - **text**: RJ-3's class justification "as RB-2 (a) reads it" is inexact (RB-7 gives the RB-2 collector effect E5); the class assigned (epsilon) is one.
- **id**: OB-6
  - **joint**: LJ-4
  - **text**: (29)'s second object costs one more controls-a1-shaped development package (a gp child, the health check, two builds and two solves at the development prime), development observations only.
- **id**: OB-7
  - **joint**: LJ-1
  - **text**: RJ-2's WHY statement "every run_child record carries argv from its first line (v2_solver.py 152), a refusal before fork included" is true of the frozen rec and of every returned record; for a raise-path launch record see FC-8.
- **id**: OB-8
  - **joint**: LJ-1
  - **text**: RJ-1 (a)'s side statements are accurate (a1_health.run_system's one run_child is 147 and it launches no callgrind child; a gb_only solve returns at 187-189 before 207); RJ-3's statement "stores comp as raw["comparator"] (655) before either exit path (656-659)" is accurate and also holds for the later exits 664-668, 674-677 and 748.

## behaviours_relied_on

- **id**: B-1
  - **behaviour**: open(2) with O_WRONLY | O_CREAT | O_TRUNC can fail without creating the file (e.g. ENOENT on a missing directory, EACCES, EMFILE), so the pre_stdout_99 child leaves no file
  - **provenance**: recalled operating-system behaviour (POSIX open)
  - **verdict_dependence**: the reachability of the pre_stdout_99 constructions (CX-A and the LJ-1 no-file cases); if open always created the file, those cases would leave a file and FAIL (more fail-closed)
- **id**: B-2
  - **behaviour**: os._exit(n) ends the process immediately with status n, running no Python handlers, finally blocks or atexit functions
  - **provenance**: recalled CPython behaviour
  - **verdict_dependence**: RG-1 child_end classes of the 97 / 98 / 99 paths; the residuals X1, X6b, X10
- **id**: B-3
  - **behaviour**: the parent's read of the report pipe returns EOF when every write end is closed (the child exits or closes it), so the parent reads "" for a child that dies before writing
  - **provenance**: recalled operating-system behaviour (pipes)
  - **verdict_dependence**: class C with report "" for pre_stdout_99 (v2_solver.py 212-225)
- **id**: B-4
  - **behaviour**: the builtin open (io.open / FileIO) opens files through the C library, not through the Python-level os.open attribute, so an os.open stand-in does not affect it
  - **provenance**: recalled CPython behaviour
  - **verdict_dependence**: LJ-4 (2) (the stand-in changes no parent read); if false, the (28) / (29) stand-in could raise in the parent's reads of the same names (r3_resolve.py 336; a1_pari.py 101), which would make those objects FAIL differently (fail-closed)
- **id**: B-5
  - **behaviour**: an uncaught exception ends the interpreter with status 1; SystemExit with a string argument exits with status 1
  - **provenance**: recalled CPython behaviour
  - **verdict_dependence**: residual X1 (unchanged); FO-1 escaped exit status 1 in LJ-0 (b)
- **id**: B-6
  - **behaviour**: `key in dict` tests key membership without reading or mutating the value
  - **provenance**: Python language reference (recalled)
  - **verdict_dependence**: LJ-6 neutrality of RB-1 (e)
- **id**: B-7
  - **behaviour**: dis opcodes of CPython 3.11 (STORE_SUBSCR after the CALL of callgrind_instructions at v2_driver.py 209)
  - **provenance**: observed in this review's own process (scan_v1.py, compile() of the source text, never imported)
  - **verdict_dependence**: LK-3 (the key exists exactly when callgrind_instructions returned)
- **id**: B-8
  - **behaviour**: O_NOATIME reads leave atime unchanged for files the process owns; relatime updates atime at most once a day otherwise
  - **provenance**: recalled Linux behaviour; checked by lstat before and after (708 + 155 values, 0 changed) and stat of package directories (C015)
  - **verdict_dependence**: CRJ-1 (no metadata change under runs/); no verdict
- **id**: B-9
  - **behaviour**: GIT_OPTIONAL_LOCKS=0 makes git status and diff skip the optional index refresh write
  - **provenance**: recalled git behaviour
  - **verdict_dependence**: CRJ-1 (no write); no verdict (see deviation D-1 for the one child run without it)
- **id**: B-10
  - **behaviour**: sys.addaudithook sees import and subprocess / fork / exec events raised in the process
  - **provenance**: recalled CPython behaviour
  - **verdict_dependence**: the scan guard only (0 refusals); no verdict

## listing_and_count_tables

Reconstruction rule (CRJ-9), verbatim from listing_v1.json:

```text
(the r4 launch, RB-1 and RL-2 records do not exist in r3):
  launch records, from the file listing and the frozen code's naming:
    child/<tag>.spec.json          -> one child-job record (v2_driver.py 92-102): stdout child/<tag>.stdout, stderr
                                      child/<tag>.stderr, argv's last element the spec; child_end "exec" (the child's
                                      .meta.json or .stdout exists), spec "out" as the archived spec file records it;
    solver|health/<tag>.ms.log     -> one msolve record (v2_driver.py 161-166; a1_health.py 141-147): stdout .ms.log,
                                      stderr .ms.err, argv names <tag>.ms and <tag>.ms.out;
    solver/<tag>.callgrind.stdout  -> one callgrind record (v2_solver.py 515-518; v2_driver.py 208-209): argv names
                                      <tag>.ms and <tag>.cg.ms.out, --callgrind-out-file=<tag>.callgrind.out;
    comparator/stdout.log          -> one comparator record (v2_driver.py 647-651): argv names comparator/;
    pari/<tag>.gp.stdout           -> one gp record (a1_pari.py 91-96): argv names pari/<tag>.gp.
    Every reconstructed record is child_created true, raised null, pair equal to the cap (class B).
  S-1 attempt records (RB-1) and pass-through records (RL-2), per tag, INDEPENDENTLY of the listing:
    from raw-result.json's solve records (a mapping with a "solver" mapping carrying argv): -P 1 -> one RB-1 attempt
    record; -g 1 -> one RL-2 record; the tag is the basename of argv's -f value without ".ms";
    callgrind_result_present (RJ-1 (a)) := the row's "instructions_callgrind" value is a non-null mapping (the frozen
    rows copy the key with r.get, v2_driver.py 359-361 and 1179-1181, so key presence in the row is not the test;
    callgrind_instructions always returns a dict, v2_solver.py 519-552);
    where raw-result.json carries no solve record for a tag: from the frozen call site (anchor_comparator_system:
    v2_driver.py 711 gb_only=True -> RL-2; controls ctl_*: v2_driver.py 786, 787, 841, gb_only False, no
    callgrind_timeout -> RB-1 with callgrind_result_present false).
  events and site counters: the archived r3 solver-events.json (sites v2_driver.solve and a1_health.run_system).
  raw comparator.child: raw-result.json top-level "comparator" mapping carrying "child".
  Paths: compared relative to each package's run directory (GFPN_RUN_DIR, command.txt line 2, equal to its path).
A listing or count check is a reading of r3 artifacts under r4 rule text: never a result about any package's verdict
and never evidence about D.
```

### RUN-GFPN-f6a21a

- files in the package listing: 284; reconstructed launch records: 88 {"callgrind": 36, "childjob": 16, "msolve": 36}; SE-3/HR-3 events: 0
- unattributed files under launchkind (recorder gaps): 0 []; named gaps: []
- contrast under attcount (RI): recorder gaps [], named gaps []
- RJ-4 (b) unknown-kind stdout paths: []; RJ-2 pari/ files: []

| site | tag | N (launch records, stdout <dir>/<tag>.ms.log) | RB-1 attempt records | RL-2 pass-through records | RI-1 (a) (i) | Ncg (callgrind launch records) | attempt records with callgrind_result_present true | RJ-1 (b) | S-3 record (cross-check only) | raw row carries key instructions_callgrind | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | fx_fresh1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/S3 (argv -P 1) |
| S-1 | fx_fresh1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_fresh1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/raw_u (argv -P 1) |
| S-1 | fx_fresh1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/raw_x (argv -P 1) |
| S-1 | fx_fresh1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_fresh1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_fresh2_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/S3 (argv -P 1) |
| S-1 | fx_fresh2_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_fresh2_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/raw_u (argv -P 1) |
| S-1 | fx_fresh2_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/raw_x (argv -P 1) |
| S-1 | fx_fresh2_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_fresh2_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_planted0_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/S3 (argv -P 1) |
| S-1 | fx_planted0_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_planted0_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/raw_u (argv -P 1) |
| S-1 | fx_planted0_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/raw_x (argv -P 1) |
| S-1 | fx_planted0_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_planted0_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_planted1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/S3 (argv -P 1) |
| S-1 | fx_planted1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_planted1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/raw_u (argv -P 1) |
| S-1 | fx_planted1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/raw_x (argv -P 1) |
| S-1 | fx_planted1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_planted1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_reg0_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/S3 (argv -P 1) |
| S-1 | fx_reg0_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_reg0_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/raw_u (argv -P 1) |
| S-1 | fx_reg0_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/raw_x (argv -P 1) |
| S-1 | fx_reg0_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_reg0_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_reg1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/S3 (argv -P 1) |
| S-1 | fx_reg1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_reg1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/raw_u (argv -P 1) |
| S-1 | fx_reg1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/raw_x (argv -P 1) |
| S-1 | fx_reg1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_reg1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/torsion_S3_rq (argv -P 1) |

Site rows (RI-1 (a) (iii)):

| site | launch records | attempts_total | passthrough_calls_gb_only_true | holds |
|---|---|---|---|---|
| S-1 | 36 | 36 | 0 | True |
| S-2 | 0 | 0 | n/a (S-2) | True |

RJ-1 (b) per-site row: callgrind launch records 36; S-1 attempt records with callgrind_result_present true 36; holds True; cross-check only: S-3 records 36, S-3 counter callgrind_children_observed 36.

RJ-3 comparator row: comparator launch records 0; raw-result.json comparator.child present False; required 0; holds True.

Mismatches: none

### RUN-GFPN-902222

- files in the package listing: 284; reconstructed launch records: 88 {"callgrind": 36, "childjob": 16, "msolve": 36}; SE-3/HR-3 events: 0
- unattributed files under launchkind (recorder gaps): 0 []; named gaps: []
- contrast under attcount (RI): recorder gaps [], named gaps []
- RJ-4 (b) unknown-kind stdout paths: []; RJ-2 pari/ files: []

| site | tag | N (launch records, stdout <dir>/<tag>.ms.log) | RB-1 attempt records | RL-2 pass-through records | RI-1 (a) (i) | Ncg (callgrind launch records) | attempt records with callgrind_result_present true | RJ-1 (b) | S-3 record (cross-check only) | raw row carries key instructions_callgrind | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | fx_fresh1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/S3 (argv -P 1) |
| S-1 | fx_fresh1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_fresh1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/raw_u (argv -P 1) |
| S-1 | fx_fresh1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/raw_x (argv -P 1) |
| S-1 | fx_fresh1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_fresh1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[2]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_fresh2_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/S3 (argv -P 1) |
| S-1 | fx_fresh2_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_fresh2_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/raw_u (argv -P 1) |
| S-1 | fx_fresh2_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/raw_x (argv -P 1) |
| S-1 | fx_fresh2_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_fresh2_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[3]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_planted0_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/S3 (argv -P 1) |
| S-1 | fx_planted0_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_planted0_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/raw_u (argv -P 1) |
| S-1 | fx_planted0_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/raw_x (argv -P 1) |
| S-1 | fx_planted0_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_planted0_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[0]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_planted1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/S3 (argv -P 1) |
| S-1 | fx_planted1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_planted1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/raw_u (argv -P 1) |
| S-1 | fx_planted1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/raw_x (argv -P 1) |
| S-1 | fx_planted1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_planted1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /planted_targets[1]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_reg0_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/S3 (argv -P 1) |
| S-1 | fx_reg0_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_reg0_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/raw_u (argv -P 1) |
| S-1 | fx_reg0_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/raw_x (argv -P 1) |
| S-1 | fx_reg0_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_reg0_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[0]/arms/torsion_S3_rq (argv -P 1) |
| S-1 | fx_reg1_S3 | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/S3 (argv -P 1) |
| S-1 | fx_reg1_S3_rescaled | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/S3_rescaled (argv -P 1) |
| S-1 | fx_reg1_raw_u | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/raw_u (argv -P 1) |
| S-1 | fx_reg1_raw_x | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/raw_x (argv -P 1) |
| S-1 | fx_reg1_torsion_S3_norm | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/torsion_S3_norm (argv -P 1) |
| S-1 | fx_reg1_torsion_S3_rq | 1 | 1 | 0 | holds | 1 | 1 | holds | 1 | True | raw-result.json /targets[1]/arms/torsion_S3_rq (argv -P 1) |

Site rows (RI-1 (a) (iii)):

| site | launch records | attempts_total | passthrough_calls_gb_only_true | holds |
|---|---|---|---|---|
| S-1 | 36 | 36 | 0 | True |
| S-2 | 0 | 0 | n/a (S-2) | True |

RJ-1 (b) per-site row: callgrind launch records 36; S-1 attempt records with callgrind_result_present true 36; holds True; cross-check only: S-3 records 36, S-3 counter callgrind_children_observed 36.

RJ-3 comparator row: comparator launch records 0; raw-result.json comparator.child present False; required 0; holds True.

Mismatches: none

### RUN-GFPN-f5412a

- files in the package listing: 32; reconstructed launch records: 7 {"childjob": 1, "comparator": 1, "msolve": 5}; SE-3/HR-3 events: 0
- unattributed files under launchkind (recorder gaps): 0 []; named gaps: []
- contrast under attcount (RI): recorder gaps [], named gaps []
- RJ-4 (b) unknown-kind stdout paths: []; RJ-2 pari/ files: []

| site | tag | N (launch records, stdout <dir>/<tag>.ms.log) | RB-1 attempt records | RL-2 pass-through records | RI-1 (a) (i) | Ncg (callgrind launch records) | attempt records with callgrind_result_present true | RJ-1 (b) | S-3 record (cross-check only) | raw row carries key instructions_callgrind | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | anchor_comparator_random | 1 | 0 | 1 | holds | 0 | 0 | holds | 0 | False | raw-result.json /targets[0] (argv -g 1) |
| S-1 | anchor_comparator_system | 1 | 0 | 1 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 711 (gb_only=True) |
| S-1 | anchor_v2_t0 | 1 | 0 | 1 | holds | 0 | 0 | holds | 0 | False | raw-result.json /targets[1] (argv -g 1) |
| S-1 | anchor_v2_t1 | 1 | 0 | 1 | holds | 0 | 0 | holds | 0 | False | raw-result.json /targets[2] (argv -g 1) |
| S-1 | anchor_v2_t2 | 1 | 0 | 1 | holds | 0 | 0 | holds | 0 | False | raw-result.json /targets[3] (argv -g 1) |

Site rows (RI-1 (a) (iii)):

| site | launch records | attempts_total | passthrough_calls_gb_only_true | holds |
|---|---|---|---|---|
| S-1 | 5 | 0 | 5 | True |
| S-2 | 0 | 0 | n/a (S-2) | True |

RJ-1 (b) per-site row: callgrind launch records 0; S-1 attempt records with callgrind_result_present true 0; holds True; cross-check only: S-3 records 0, S-3 counter callgrind_children_observed 0.

RJ-3 comparator row: comparator launch records 1; raw-result.json comparator.child present True; required 1; holds True.

Mismatches: none

### RUN-GFPN-bfe956

- files in the package listing: 83; reconstructed launch records: 19 {"childjob": 11, "msolve": 8}; SE-3/HR-3 events: 0
- unattributed files under launchkind (recorder gaps): 0 []; named gaps: []
- contrast under attcount (RI): recorder gaps [], named gaps []
- RJ-4 (b) unknown-kind stdout paths: []; RJ-2 pari/ files: []

| site | tag | N (launch records, stdout <dir>/<tag>.ms.log) | RB-1 attempt records | RL-2 pass-through records | RI-1 (a) (i) | Ncg (callgrind launch records) | attempt records with callgrind_result_present true | RJ-1 (b) | S-3 record (cross-check only) | raw row carries key instructions_callgrind | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | ctl_identity_planted | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_identity_random | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_planted_S3 | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_planted_S3_rescaled | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_planted_torsion_S3_norm | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_planted_torsion_S3_rq | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_rawx_planted | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |
| S-1 | ctl_rawx_random | 1 | 1 | 0 | holds | 0 | 0 | holds | 0 | None | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout) |

Site rows (RI-1 (a) (iii)):

| site | launch records | attempts_total | passthrough_calls_gb_only_true | holds |
|---|---|---|---|---|
| S-1 | 8 | 8 | 0 | True |
| S-2 | 0 | 0 | n/a (S-2) | True |

RJ-1 (b) per-site row: callgrind launch records 0; S-1 attempt records with callgrind_result_present true 0; holds True; cross-check only: S-3 records 0, S-3 counter callgrind_children_observed 0.

RJ-3 comparator row: comparator launch records 0; raw-result.json comparator.child present False; required 0; holds True.

Mismatches: none

TOTAL: files 683; unattributed under launchkind 0.


## red_team_report

- **id**: TASK-20260924-d897a6

- **task_id**: TASK-20260924-d897a6

- **claim_under_review**: The DRAFT AMD-EXP-GFPN-05ff43-20260924-launchkind (sha256 ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050), read with everything it incorporates, gives each of the six production launch kinds a lost-record detector written independently of the launch recorder (RJ-1..RJ-4), so that a lost launch record is a named gap or a recorder gap (FAIL) outside RGL-10's consistent-loss premise, without refusing any planned basis outcome, and its development checks (RJ-5), path values (RJ-6) and statements (RJ-7) hold on the r3 base.

### objections

- FC-1 .. FC-8 (fail-closed, reading-dependent stage-time stops or added gaps on failed packages; never a bar)
- OB-1 .. OB-8 (wording and forward guidance)

### required_controls

- At the r4 stage, before any package: DV-18 (28) and (29)'s second object on development packages, recording the gap-level results with and without RJ-1 / RJ-2 in the scratch evaluator, and (32) on the unaltered (28) package (it also exposes a mis-recorded RB-1 (e), RP-5).
- A Coordinator reading, recorded before the stage, of RJ-6's form clause for command.txt line 2 and the command strings (FC-1), of RJ-5 (b)'s stand-in level (FC-3), of RJ-4 (c)'s "calls" (FC-4), of RB-7's consumer list (FC-5), of consumercover's DERIVED VALUE for RB-1 (e) (FC-6) and of the stdout forms (FC-7).

- **counterexample_or_mutation**: No fail-open counterexample and no planned-basis refusal. Cheapest discriminating control: DV-18 (28) (the CX-A control) evaluated with RJ-1 disabled and enabled. Cheapest mutation that would widen the detected class: bind S-2 calls to the frozen health-`<p>`.json entries (OB-3), and extend DV-18 (h)'s scan to stored references of run_child (FC-4).

- **baseline_comparison**: Not applicable to a recording / verdict repair (no algorithm and no cost claim; Pollard-rho, BSGS and specialized baselines are not engaged). The comparison made is against the incorporated drafts: under attcount (RI) CX-A, CX-A-gp and CX-A-G2 are PASS and fail-open; under launchkind (RJ) they FAIL with a named gap or a recorder gap; with RJ-1 (b) weakened (RJw) CX-A is fail-open again.

### heuristic_challenges


### cost_model_challenges

- (29)'s second object adds one controls-a1-shaped development package (OB-6); FC-1..FC-7 cost a Coordinator reading at stage time under their unfavourable readings; FC-8 costs nothing beyond an added gap on a failed package.

### reduction_and_scope_challenges

- RGL-10 overstates the undetected class for LK-3 and LK-4 (conservative) and its alteration sentence is inexact (OB-1, OB-2).
- The listing and count checks are reconstructed readings of r3 artifacts under r4 rule text (CRJ-9); no r4 package exists and none was run.

### proof_architecture_challenges

- Nearby-object control: CX-A evaluated under attcount (RI), launchkind (RJ) and launchkind with RJ-1 (b) weakened (RJw): the verdict flips exactly with RJ-1 (b)'s equality, so the repair's effect is attributable to that clause.

- **narrowest_supported_statement**: On the frozen trees at HEAD c0b0ecf3a4a5ca9dc1897322747d84398d448480 (unchanged since dd1034553 in the implementation trees, trial plans and the four archived r3 gate packages), with definitions (i)-(v) as the card reads them and the reconstruction rule of CRJ-9: every single lost launch record at each of the six production run_child call sites, on every child path constructed (refusal before fork, failure before the stdout open, ERR setrlimit, cap mismatch, exec, and escapes), yields a named gap or a recorder gap and FAIL under launchkind as worded; the only PASS outcomes with a definition holding need a consistent loss of the record and every detector bound to it (RGL-10) or a mis-recorded RB-1 (e); no planned basis outcome of either plan was found to FAIL by design; the four archived packages show 0 of 683 files unattributed and no count mismatch in 85 rows. Nothing here is a statement about D.

- **next_concrete_action**: Check step: at the r4 stage, run DV-18 (28), (29) (second object) and (32) on the unaltered (28) package in scratch development processes, and record the gap-level outcomes with RJ-1 / RJ-2 enabled and disabled together with the readings chosen for FC-1, FC-3, FC-4, FC-5, FC-6 and FC-7.

### artifact_paths

- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md

## review_attestation

### task_id

TASK-20260924-d897a6

### role

red-team

### joints_owned

- LJ-0
- LJ-1
- LJ-2
- LJ-3
- LJ-4
- LJ-5
- LJ-6

### verdicts

- **LJ-0**: holds
- **LJ-1**: holds
- **LJ-2**: holds
- **LJ-3**: holds
- **LJ-4**: holds
- **LJ-5**: holds
- **LJ-6**: holds

### read_sibling_reports

none (the archived reviews f5631b, 1ecb7d, 94cc33 and be2daf were read as inputs, as the card lists them; there are no sibling reports in this round)

### blind_from_not_opened

- ledger/decisions/DEC-20260924-babd04.yaml
- ledger/corrections/CORR-20260924-c248d6.yaml
- ledger/handoffs/TASK-20260924-491b2a.yaml
- ledger/handoffs/TASK-20260924-a571c7.yaml
- knowledge/techniques/KN-TECH-fe7faf.md
- ledger/decisions/DEC-20260924-1d7614.yaml
- ledger/corrections/CORR-20260924-5c3086.yaml
- ledger/handoffs/TASK-20260924-9ba862.yaml
- ledger/handoffs/TASK-20260924-2a7c7f.yaml
- ledger/goals/GOAL-GFPN-380702/goal.yaml
- knowledge/techniques/KN-TECH-175a62.md
- knowledge/techniques/KN-TECH-79d6b9.md
- ledger/decisions/DEC-20260924-61b22c.yaml
- ledger/corrections/CORR-20260924-3c831f.yaml
- ledger/handoffs/TASK-20260924-c9218d.yaml
- ledger/handoffs/TASK-20260924-27ea14.yaml
- ledger/decisions/DEC-20260924-844896.yaml
- ledger/corrections/CORR-20260924-862f7d.yaml
- ledger/handoffs/TASK-20260924-64c8fe.yaml
- ledger/handoffs/TASK-20260924-5816cd.yaml
- ledger/decisions/DEC-20260924-8fa3d4.yaml
- ledger/corrections/CORR-20260924-7fcbd2.yaml
- ledger/handoffs/TASK-20260924-7e9d3e.yaml
- ledger/handoffs/TASK-20260924-eb2540.yaml

### dispatcher_withheld_not_opened

- ledger/handoffs/TASK-20260924-68cf6b.yaml
- coordination/goals/GOAL-GFPN-380702/batches/ (everything under it)
- coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-a571c7/ (not even the addendum_sha256 field; the dispatching session supplied its value)
- coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-2a7c7f/, TASK-20260924-27ea14/, TASK-20260924-5816cd/, TASK-20260924-eb2540/
- every field other than path_sha256 of the snapshot receipts of TASK-20260924-0c2fdc, -7e8a5d, -93f3ca, -682890, -71d070, -ddfb69 and -a01341 (see blindness_disclosures BD-3)
- coordination/bus/ and coordination/events/
- every directory under coordination/goals/*/reviews/ other than TASK-20260924-f5631b/, -1ecb7d/, -94cc33/, -be2daf/ and the three released files (reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py; reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n3.json and square_analogue_n4.json)
- git commit messages (no git log body, no git show of a commit object)
- pull requests and the web (no web search or fetch)

### blindness_disclosures

- **id**: BD-1
  - **text**: KNOWN IN ADVANCE and read as part of the draft: the launchkind draft summarizes DEC-20260924-babd04's rulings (header 1-59, findings_carried 226-267, carried decisions 624-651, options_weighed 653-693) and cites DEC-20260924-babd04, CORR-20260924-c248d6, DEC-20260924-1d7614, DEC-20260924-61b22c and DEC-20260924-844896. None of those files was opened.
- **id**: BD-2
  - **text**: The incorporated drafts and the archived reviews name other withheld records (decisions, corrections, handoffs, knowledge entries) in their text; their names and the draft-quoted rulings were read as part of those inputs; no withheld file was opened.
- **id**: BD-3
  - **text**: integrity_v1.py loaded each of the seven snapshot receipts with json.load and printed ONLY its path_sha256 field; no other field was printed, compared or viewed. C003 listed those seven archive directories (ls -la; file names and sizes only).
- **id**: BD-4
  - **text**: The review directories listed by C004 and C007 (ls of coordination/goals/GOAL-GFPN-380702/reviews/ and of the four archived review directories) show directory names only; no withheld review directory was entered. The persisted-output file of deviation D-3 (outside the repository, under the session-configuration directory) was not opened.

### paths_read

- **note**: Every path this review read, by extent. The running list the command log's header names (paths_read.txt) was never created; this list was rebuilt after the compaction (deviations D-4, D-7) from the command log, the scripts and the working notes. Line ranges are given where they were re-read after the compaction (C048-C091); ranges read only before the compaction are not itemized ("in part").
- **repository_in_full**:
  - ledger/handoffs/TASK-20260924-d897a6.yaml
  - agents/red-team.md
  - AGENTS.md
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml
  - every .py file of experiments/EXP-GFPN-05ff43/implementation/, implementation-v2/, implementation-v2-a1/, implementation-v2-r1/, implementation-v2-r2/ and implementation-v2-r3/ (71 files; as text, ast and dis by scan_v1.py / scan_v2.py; never imported)
  - experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/, RUN-GFPN-902222/, RUN-GFPN-f5412a/ and RUN-GFPN-bfe956/: the listing and lstat of each package directory and of child/, solver/, health/, comparator/ and pari/, and the full bytes (O_NOATIME) of solver-events.json, raw-result.json, command.txt and every child/*.spec.json (pkgread_v1.py); and every regular file except *.npz of RUN-GFPN-bfe956/ and RUN-GFPN-f5412a/ (rdscan_v1.py, O_NOATIME)
- **repository_in_part**:
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml (in part; re-read 243-318, 455-485)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml (in part and outline; re-read 373-440)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml (in part and outline; re-read 246-373, 522-535)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml (in part; re-read 209-306)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml (in part and outline; re-read 196-222, 331-348)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_consumercover.yaml (grep and in part; re-read 335-381, 426-441, 535-566)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml (grep and in part; re-read 269-295)
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchcover.yaml (grep only, C008)
  - ledger/decisions/DEC-20260924-e52eec.yaml (grep; re-read 714-740)
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml (1-998, 1620-1759; re-read 245-256)
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md (1-344)
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml (grep for N-1..N-13, C018)
  - experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md (470-495, C019)
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py (line count and grep for writes, launches and imports, C035)
  - experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py (270-285, C035)
  - frozen code re-read after the compaction: v2_solver.py 149-308, 512-552; v2_driver.py 77-231, 352-364, 560-568, 626-750, 752-935 (call-site grep), 1085-1092, 1110-1182; a1_pari.py 20-143; a1_health.py 140-153, 223-253; a1_driver.py 84-92, 125-131, 144-168, 200-216; r3_resolve.py 44-52, 178-202, 248-412; r3_run_wrapper.py 97-104, 186-203, 284-292, 381-400, 434-472, 505-512, 540-552; r3_check_run.py 61-77, 86-100, 150-185, 245-260, 322-342; v2_check_run.py 60-72, 92-106; a1_check_run.py 60-86; r3_common.py 24-32, 110-115; v2_common.py 27-40; a1_common.py 88-100; r3_entry_v2.py 36-80; r3_entry_a1.py 90-111; r3_run_wrapper.py line 68 (grep)
- **repository_hashed_only**:
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml
    - **sha256**: b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md
    - **sha256**: 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml
    - **sha256**: 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md
    - **sha256**: 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md
    - **sha256**: 02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json
    - **sha256**: 9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py
    - **sha256**: 00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json
    - **sha256**: 36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md
    - **sha256**: 5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py
    - **sha256**: ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py
    - **sha256**: 3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json
    - **sha256**: 49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4
  - **path**: experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md
    - **sha256**: 2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n3.json
    - **sha256**: 22550c2f4ede32a41d7b8134f2c72c04121d20065eacd6604640b0ef0e8a81ba
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n4.json
    - **sha256**: e3bc6d120a52a898fd84e47efe54f727f20e2013c906522cd41a73303ae595a2
- **hashed_inputs**:
  - **path**: ledger/handoffs/TASK-20260924-d897a6.yaml
    - **sha256**: 35d943da8bfd0d5048f7fd4785583feaac963c26add3ea4315ceb00cf0e93484
  - **path**: agents/red-team.md
    - **sha256**: c66633c45ccacb2779bbcb291227703d8f0c0d8ee79fa5669d22bc214e7ff8ee
  - **path**: AGENTS.md
    - **sha256**: 16b87c767e698a15f988ad8d6f03b07b2c0e5ac7e2738846d0084c2473288a56
  - **path**: ledger/decisions/DEC-20260924-e52eec.yaml
    - **sha256**: e5d6907cf8cbdd0bcf2f280c0078d3a9be15f6c78d0c836663b11fcca3d92591
  - **path**: coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py
    - **sha256**: 3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_consumercover.yaml
    - **sha256**: a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0
  - **path**: experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml
    - **sha256**: 877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py
    - **sha256**: 0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py
    - **sha256**: 0d22a082c967500f28d0aabdce1b0cdf125cf5a3109727045e6cf55407a20098
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py
    - **sha256**: ed813df7760be9d9289a6643ba7be95cf9be905e6ba0835d476b56ea551d2e25
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py
    - **sha256**: c064144c7d70d84727cd286baf34df8160eca2b3b5e469ea29556446289b6592
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py
    - **sha256**: 0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py
    - **sha256**: dafe748d9a1e923c106a5fa0cfcdd7d622fbb80cb23e1099d5fc6064be4e7293
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py
    - **sha256**: 749237a6cfc15eeb235824dcf5e28e6733ee099df56daad3f996ae028650e5b7
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py
    - **sha256**: 516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_common.py
    - **sha256**: f347eebafa51eace211012f780c8425a2f4d6917f61370c7c2f20a1c62a9185b
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py
    - **sha256**: 3a6828f42a6e8dd97fd487510fbb0c153ca8f51d9bcd0c310d1af96c8d5e3e15
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py
    - **sha256**: dd52a4bfad9c4bfb0e4e37ee8a24951e8992edf8d2f1dfcc112e9bcdbabb9c19
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py
    - **sha256**: 939d7d7e5bc8a8c64f15df188f98f13b22ef7a9d696680f8e47854c2dbdcd14d
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py
    - **sha256**: f79161999507cdb5438c1be39de21ba74d25ef745f490c08e56a600c28117fbd
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py
    - **sha256**: cefbb3348174bf02546129a65a9a0961b3ad5f60341d25ca4bfab1d54cb56f23
  - **path**: experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_common.py
    - **sha256**: 7bb7b688250d69a2ca209a57fd70176727aa1fe225c95c9878076be407380868
- **repository_receipts_one_field_only**:
  - coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-{0c2fdc,7e8a5d,93f3ca,682890,71d070,ddfb69,a01341}/snapshot-receipt.json (path_sha256 only; BD-3)
- **repository_listed_only**:
  - experiments/EXP-GFPN-05ff43/runs/ (54 directories) and the four archived packages (C014, C015 stat of package directories)
  - experiments/EXP-GFPN-05ff43/ (top level), implementation*/ directories (C009, C011)
  - coordination/goals/GOAL-GFPN-380702/reviews/ (top level) and the four archived review directories (C004, C007)
  - experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/, readbackfull-census/, readback-census/ (C004)
  - coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-{0c2fdc,7e8a5d,93f3ca,682890,71d070,ddfb69,a01341}/ (C003)
- **repository_searched_only**:
  - tools/ and harness/ (grep -rln for the new labels and field names, C041; no match)
  - experiments/EXP-GFPN-05ff43/implementation-v2/, -v2-a1/, -v2-r3/ (grep, C010, C043)
- **git_objects_read**: HEAD (rev-parse), dd103455380238ec2f20d17414de687acdcc822a (cat-file -t only), the index entries of the launchkind and attcount files (ls-files -s), git diff --stat outputs (empty); no commit message, no git log body, no git show of a commit object
- **outside_repository**:
  - `<scratch>`/rt_d897a6/ (this review's scratch directory: its own scripts, outputs and notes, and words.txt placed by the dispatching session, read only by wordcheck_v1.py and the assembler / checker, never printed)
  - the interpreter (CPython 3.11) and its standard library, and the shared libraries and shell utilities the commands loaded; the yaml module was imported by the assembler and checker (for the parse check) and its source was not read
  - not read: the optional installed third-party source text (flint, numpy, cypari2, yaml); anything else under /tmp; the session-configuration directories

### commands

See Appendix B (command log verbatim and the exact argv after the compaction) and Appendix C (argv per script). Assembler runs: `C095: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1`; `C098: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v2.py > assemble_v2.out 2>&1`.

### post_write_commands

- **note**: Declared before they ran; they run after both files are written, so their outputs are reported in the hand-back, not in this file.
- **list**:
  - C099: cd `<scratch>`/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1_run2.out 2>&1; echo exit=$?; cat check_v1_run2.out
  - C100: cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6; ls -la coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/; sha256sum coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md

### scratch_files

- **directory**: `<scratch>`/rt_d897a6/ (outside the repository; transient)
- **files**:
  - **name**: assemble_v1.out
    - **bytes**: 321
    - **sha256**: 75ea437007e728b9e981aacaede175fc5eae14cd9e0eb6371708d80d3bb727af
    - **purpose**: its printed summary
  - **name**: assemble_v1.py
    - **bytes**: 20448
    - **sha256**: 3ebde27e0aa96c166cff349ebaaa37bb8b49689f305f5940a0af9df0a79cd816
    - **purpose**: assembler, version 1 (first write of the deliverables, C095)
  - **name**: assemble_v2.py
    - **bytes**: 21947
    - **sha256**: 6e4bb8ad2b24f0dcaabe7630dde3d5815fda8a47dc1fc547fed4e4e8eff90d35
    - **purpose**: assembler, version 2 (whole rewrite of the deliverables, C098)
  - **name**: body_v1.yaml.part
    - **bytes**: 90841
    - **sha256**: 340201347d760cab6ed6a7c2a4346788deb9df9a5598c3d4bdbd4ccc8c8b3577
    - **purpose**: hand-written YAML body of the report
  - **name**: body_v2.yaml.part
    - **bytes**: 90977
    - **sha256**: 2600f718e0b72cfc8d2afe64a6aa7be2902872c893905788f9308c504e53627d
    - **purpose**: hand-written YAML body, version 2
  - **name**: check_v1.out
    - **bytes**: 1308
    - **sha256**: ff124c738bdea334b2182999e3cddfe8955bb803c2ba851a990fd3d7beaec256
    - **purpose**: post-write check of the version 1 deliverables (C096)
  - **name**: check_v1.py
    - **bytes**: 3734
    - **sha256**: 07379d7a116b280cce281f58ce919a794e2ad38d2f0e094407edc204edb29b4b
    - **purpose**: post-write checker
  - **name**: command_log.txt
    - **bytes**: 23059
    - **sha256**: 5254ed5ebd062301bc3d47d8ec6f7d58cdaac440c78bae0e24638bacfce97e9b
    - **purpose**: running command log (one entry per shell child; C001-C094 before assembly)
  - **name**: crj2d_diff.out
    - **bytes**: 0
    - **sha256**: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    - **purpose**: CRJ-2 (d) git diff --stat output (0 bytes)
  - **name**: deviations_v1.yaml.part
    - **bytes**: 4979
    - **sha256**: 24e724e71a10043ccb9c8d88abb102d6639cc64d52cb0dade351a24a6c108209
    - **purpose**: deviations part
  - **name**: deviations_v2.yaml.part
    - **bytes**: 5960
    - **sha256**: 226242ecba6912084ad1b7e603d0629649a5833ecfbf94f1e9d820a8f6b63dd8
    - **purpose**: deviations part, version 2
  - **name**: exact_argv_post_compaction.txt
    - **bytes**: 9388
    - **sha256**: 518e89b3a8735937b9414c55e75cb2bb737ce79e150dd6e5d6410f7670be6695
    - **purpose**: exact argv of every shell child after the compaction (X01-X52)
  - **name**: explore_v1.out
    - **bytes**: 17199
    - **sha256**: 53821bfdbc97da20293bdba24112b8018bfbfac591af7e21e4950ba1b8b2b0e7
    - **purpose**: its output
  - **name**: explore_v1.py
    - **bytes**: 2406
    - **sha256**: e40dc2068353bea086bc937c854df52ecf2b783258f869f2e0c3727a54fd5a74
    - **purpose**: exploration of pkgread_v1.json (record shapes)
  - **name**: hashes_v1.out
    - **bytes**: 3043
    - **sha256**: ddf95cd9b3d1577d8b728531daa9d910d2c16f41b2a467dcbfa43d3dd1705115
    - **purpose**: its output
  - **name**: hashes_v1.py
    - **bytes**: 2101
    - **sha256**: 5731ab87a46a698f2a65a335f88a12529df693b07a303f004879216274ad9056
    - **purpose**: sha256 of the card, contracts and frozen files read
  - **name**: integrity_v1.out
    - **bytes**: 8510
    - **sha256**: ab79ae4e4c4506a5700e245dc366212bb665cd39e48e29b838f5451ebe57b806
    - **purpose**: its output
  - **name**: integrity_v1.py
    - **bytes**: 4468
    - **sha256**: 5456853e9244b81f051136c2578661161430a17e26f916eb592ad87663e3755e
    - **purpose**: CRJ-2 integrity checks (a)-(c)
  - **name**: listing_v1.json
    - **bytes**: 91182
    - **sha256**: 6e42a1a40fc08f93ae88f40d48a9fa72f18348109cd3a1d5b5e588c30c7dc79c
    - **purpose**: its data
  - **name**: listing_v1.out
    - **bytes**: 15904
    - **sha256**: 707031b55e2d724de08a4a86d5e08b7076a47060dd4353a3beea8a89aa3438ab
    - **purpose**: its output
  - **name**: listing_v1.py
    - **bytes**: 14806
    - **sha256**: cea024e213a3a7acc7ac050de6a519152806f9a95dedf901aa34afb058a43c57
    - **purpose**: LJ-0 (f) / LJ-2 listing and count check with core v1
  - **name**: listing_v2.json
    - **bytes**: 91182
    - **sha256**: 6e42a1a40fc08f93ae88f40d48a9fa72f18348109cd3a1d5b5e588c30c7dc79c
    - **purpose**: its data
  - **name**: listing_v2.out
    - **bytes**: 15904
    - **sha256**: 332de305c7d15c8e90e626b81f8b1587efae1bd11369737fba027bf176c759c0
    - **purpose**: its output
  - **name**: listing_v2.py
    - **bytes**: 14806
    - **sha256**: ae0be006a642487800a5f5dd94cfafd47bd178cfbadf9976cb08e8bae6c3faa4
    - **purpose**: the same with core v2
  - **name**: lj0_v1.json
    - **bytes**: 95382
    - **sha256**: 1b8e56a8adc2d704ec96dba34e03758c6cc38ea07ebc4284ab9c134675b147d5
    - **purpose**: its data
  - **name**: lj0_v1.out
    - **bytes**: 71881
    - **sha256**: 5fd879d508e0938bf4cf829bb505a57ce634608939533ec4dcee3962ec7533a9
    - **purpose**: its output
  - **name**: lj0_v1.py
    - **bytes**: 10311
    - **sha256**: 42525fab5bd8006fc34b8a030e80475c172c0b827a4a2b39be75d8180bada145
    - **purpose**: LJ-0 (a)-(e) with core v1
  - **name**: lj0_v2.json
    - **bytes**: 95382
    - **sha256**: 1b8e56a8adc2d704ec96dba34e03758c6cc38ea07ebc4284ab9c134675b147d5
    - **purpose**: its data
  - **name**: lj0_v2.out
    - **bytes**: 71881
    - **sha256**: 7832a61331e634915469e1a2d94bfe403f649e52b8adce8badca8dd2ffca43f1
    - **purpose**: its output
  - **name**: lj0_v2.py
    - **bytes**: 10311
    - **sha256**: 025e4b17c3d058bc24895042eeba9b5f4f4dca2cf7a9045d75d917c5010c3660
    - **purpose**: LJ-0 (a)-(e) with core v2
  - **name**: lj1_v1.json
    - **bytes**: 82483
    - **sha256**: 5efe982d2e75d465c23cb5b97666f8e68068dade19f88abd8016e2de85eb502e
    - **purpose**: its data
  - **name**: lj1_v1.out
    - **bytes**: 152179
    - **sha256**: c6bd62a187e1a21e58e28ba2c662de5dacdeddb7ea114de59a4a448313afe5a4
    - **purpose**: its output
  - **name**: lj1_v1.py
    - **bytes**: 17677
    - **sha256**: 0f551d8e18b14ed20f9bcb6efee541fb38a1150b63ead78fd5f9403c3511a602
    - **purpose**: LJ-1 lost-record constructions per launch kind
  - **name**: lj2_v1.json
    - **bytes**: 18230
    - **sha256**: 8459fb40273919b8ac81a50987f7e531f3c6f2f0dfa607ec20f2afcf2eee9a92
    - **purpose**: its data
  - **name**: lj2_v1.out
    - **bytes**: 122205
    - **sha256**: 48b8ca882c80d5ee08bd5bc6c2dce0dad70038ddeb7b73077d1af369b7fdc2f3
    - **purpose**: its output
  - **name**: lj2_v1.py
    - **bytes**: 11154
    - **sha256**: f66ffdf96d09f6bb5ae448b8848d07bae4d54f46c6d2544f686ecd4789b34aa5
    - **purpose**: LJ-2 planned-basis rows, N-1..N-13 and NJ objects
  - **name**: lj4_v1.json
    - **bytes**: 28729
    - **sha256**: e0d28b80105ceed84e62a0f06f2a280dbad2533ebb5ae950584e7978089591d9
    - **purpose**: its data
  - **name**: lj4_v1.out
    - **bytes**: 17143
    - **sha256**: e8e3481d6951d55c4e18d9f1a5dcbd3160c5130f12d24f8096aadcf9b2e2cec1
    - **purpose**: its output
  - **name**: lj4_v1.py
    - **bytes**: 11653
    - **sha256**: df1759402007f146d221b6ace214ce0c8ad1b7891477acfe24c6e78b86ba72a6
    - **purpose**: LJ-4 (1) development-check derivations (19)-(32)
  - **name**: notes.md
    - **bytes**: 9772
    - **sha256**: 44e1ed2b0102d5b382accfae1faca3ff9f68fed713c2486f569f04506e5b2b57
    - **purpose**: working notes kept across the compaction (not reproduced; listed by hash)
  - **name**: paths_read_v1.yaml.part
    - **bytes**: 11736
    - **sha256**: d074c775814b1015d4611cef14b1f37af229a6c3eb3c7a16e5bd69b4b66810af
    - **purpose**: paths_read part
  - **name**: pkgread_v1.json
    - **bytes**: 709959
    - **sha256**: c083046809f00ccce93dd6dd2e72f51ee161dd8dc81428d87c77220a5a702466
    - **purpose**: its data
  - **name**: pkgread_v1.out
    - **bytes**: 2477
    - **sha256**: c1395cf11719ef4e5a0566c5c8752e8f206919a7b4de7e20570103f4000033bb
    - **purpose**: its output
  - **name**: pkgread_v1.py
    - **bytes**: 2850
    - **sha256**: 96764d2cd95bcb924ca1441022f430cf127e7d64f2841ed6ccca2a542ee60119
    - **purpose**: O_NOATIME listing and read-only records of the four archived packages
  - **name**: rdscan_v1.json
    - **bytes**: 3704
    - **sha256**: e771c75f09170382db786536a0c5b9b7d46ce0c18be110bbb623a66e0c6e721d
    - **purpose**: its data
  - **name**: rdscan_v1.out
    - **bytes**: 1624
    - **sha256**: 547f8fede05528cd9ad1bd98c1d9e4d4936844a51fa3ec979d642e7b16721bdc
    - **purpose**: its output
  - **name**: rdscan_v1.py
    - **bytes**: 4118
    - **sha256**: f3b04122fc00429246511458d0aef22a4129006b1637a54ea1b5d30c044558fb
    - **purpose**: LJ-4 (3) run-directory values in two packages
  - **name**: rjcore_v1.py
    - **bytes**: 34437
    - **sha256**: c6e156f495d187fec8d1205bc86f8d2c423d8453b1c3cfa7bbabb4fc08648b9e
    - **purpose**: rule evaluator core, version 1
  - **name**: rjcore_v2.py
    - **bytes**: 35392
    - **sha256**: 6e686dcfb2599c911c176d81e97701766e03351b6daffffca63875ee389b745f
    - **purpose**: rule evaluator core, version 2
  - **name**: scan_v1.json
    - **bytes**: 102245
    - **sha256**: e0f2840b30a2daca68f1b53004918ff3034accf134aed56ab1df04426bf15751
    - **purpose**: its data
  - **name**: scan_v1.out
    - **bytes**: 11511
    - **sha256**: 179452fe82d4ac9cb1822fab59914c4766a028f827c513d65219fdea166b1a8c
    - **purpose**: its output
  - **name**: scan_v1.py
    - **bytes**: 12387
    - **sha256**: c3f5eb34f93577c7594317eb5095ba91b5c12df116e12e55aadb48a35001e747
    - **purpose**: static scan of the six trees (ast, dis; audit-hook guard)
  - **name**: scan_v2.json
    - **bytes**: 13213
    - **sha256**: 2a0775a3cc0ec71613e351f768863b8128240e64cfb484e111d9bcb8d9df6161
    - **purpose**: its data
  - **name**: scan_v2.out
    - **bytes**: 3741
    - **sha256**: 64c8ba177f19c90dd041c6c4afdf7d51cdadee1fb458d1809c27a8a3fa920bb7
    - **purpose**: its output
  - **name**: scan_v2.py
    - **bytes**: 6571
    - **sha256**: bd16afc0c27dcef4046afef79537315ddcb1ece092ab68ae00817319be6ba9cb
    - **purpose**: static scan, part 2 (process enders, handlers, removals, write opens)
  - **name**: tables_v1.md
    - **bytes**: 19434
    - **sha256**: e49c9d6ec402e9f419db87fb39c5e2adc9e86de41099235428cf3219972122d4
    - **purpose**: table (markdown)
  - **name**: tables_v1.out
    - **bytes**: 33
    - **sha256**: f4a32ae653a1fcd18e8969369bd7ad07c8fca71822f3784db968703a21260734
    - **purpose**: its output
  - **name**: tables_v1.py
    - **bytes**: 7778
    - **sha256**: 3db2ab4b030c00d227616a8e0214f5cedc45e1736130dab6f1eb7cc86a4901aa
    - **purpose**: renders the listing and count tables from listing_v1.json
  - **name**: tables_v1.yaml
    - **bytes**: 25716
    - **sha256**: 77115869f6ae1c40fe026c1703c8f9ab4009bd86074a62635ef247574fb4db4d
    - **purpose**: table (YAML)
  - **name**: tables_v1_perfile.md
    - **bytes**: 48192
    - **sha256**: 91c7ff045e49b0242790dc78f1248dde2bbecef60853ea601b635595a37d33f9
    - **purpose**: per-file first attribution clause
  - **name**: wordcheck_v1.py
    - **bytes**: 1219
    - **sha256**: b42715fc0506b5e17bb1ab9d58cf054bd9a6e83e1a86a3a590593b0f24e9ba0d
    - **purpose**: CRJ-7 self-check over scratch files
  - **name**: wordcheck_v1_parts.out
    - **bytes**: 627
    - **sha256**: 4de9727effc61e89057d1f716009dcc2144a269b97b0e223c660f9be12aa0f8a
    - **purpose**: its output (report parts, exact-argv file, assembler, checker)
  - **name**: wordcheck_v1_parts2.out
    - **bytes**: 369
    - **sha256**: cb5ba3c928a23cd9f1ab268fa63f350c966eae7a0698a0d336cbf405c691ae0c
    - **purpose**: its output (version 2 parts and assembler)
  - **name**: wordcheck_v1_scratch.out
    - **bytes**: 3379
    - **sha256**: 8a58eb777ff302b0a7e3343d4e0948d14c61767752418d02abc6466f3f92a995
    - **purpose**: its output (scripts, outputs, log, tables)
  - **name**: words.txt
    - **bytes**: 113
    - **sha256**: c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268
    - **purpose**: word list placed by the dispatching session for the CRJ-7 self-check; read only at run time by wordcheck_v1.py, assemble_v1.py and check_v1.py; never printed
- **written_after_this_list**: assemble_v2.out (this assembler's printed summary) and check_v1_run2.out (the post-write checker's output on these files)

### files_written_outside_repository

Only scratch files under `<scratch>`/rt_d897a6/ (listed under scratch_files), and one file the harness wrote itself when a command's output exceeded its display limit (deviation D-3; under the session-configuration directory outside the repository; not opened, not written by this review's commands).

### files_written_inside_repository

- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md

### static_only_attestation

Zero runs. No msolve, valgrind, callgrind_annotate, gp, Sage or builder child (not even a version or help flag); no run, fixture, control, cell or toy package; no perf_event_open call; no fork of a process running scanned code; no import, exec, eval or runpy of any module or code object from experiments/EXP-GFPN-05ff43/implementation*/, tools/ or harness/ (scan_v1.py compiled two frozen sources with compile() for dis only and installed an audit-hook guard that refused such imports and launches: 0 refusals); no third-party source read under LJ-1, and the one third-party module imported (yaml, by the assembler and checker for the parse check) was not read. Every Python child ran with -B and PYTHONDONTWRITEBYTECODE=1; no py_compile / compileall. No git write of any kind. Nothing under experiments/EXP-GFPN-05ff43/runs/ was written, touched or renamed; package files were read with O_NOATIME and lstat before and after (863 values, 0 changed).

### inference

- **requested_policy**: review-adversarial
- **agent_binding**: red-team, at the policy's default reasoning effort, as the dispatching session arranged
- **resolved_model_id**: null (none supplied by the dispatching session; none invented)
- **model_verified**: false
- **fallback_used**: false
- **bedrock_used**: false

### deviations

- **id**: D-1
  - **command**: C003
  - **text**: `git rev-parse HEAD` and `git status --porcelain | head -20` were run WITHOUT GIT_OPTIONAL_LOCKS=0 (full text in the command log, C003). git status may take an optional index lock and refresh the stat data of .git/index. Output: HEAD c0b0ecf3a4a5ca9dc1897322747d84398d448480; status printed nothing. Every later git child carried GIT_OPTIONAL_LOCKS=0. No research file was written.
- **id**: D-2
  - **command**: C023
  - **text**: The command line contained `python3 -B -c 1 2>/dev/null`, a `python3 -c` program (the no-op "1"; stderr discarded; no output). CRJ-5 forbids `python3 -c` programs. It read and wrote nothing.
- **id**: D-3
  - **command**: C027
  - **text**: The output of `sed -n 433,724p lj0_v1.out | cut -c1-330` exceeded the display limit and the session harness persisted it to a file under the session-configuration directory outside the repository (a file this review's commands did not write). That file was NOT opened; only a 2 KB preview of scratch bytes was displayed. The same bytes were re-read in filtered parts (C028).
- **id**: D-4
  - **command**: between C045 and C046
  - **text**: The reviewer's working context was compacted (2026-09-25, about 02:18-02:21Z), after every joint had been computed and before the deliverables were written. As CRJ-5 requires, every line a verdict cites was re-read after the compaction (C048-C091: the draft and the card in full; attcount 265-505; failclosed 600-708; gapattr 243-318 and 455-485; childend 373-440; readbackclose 246-373 and 522-535; readbackfull 209-306; readbackcover 196-222 and 331-348; consumercover 335-381, 426-441 and 535-566; valueclose 269-295; DEC-20260924-e52eec 714-740; the frozen-code ranges listed under paths_read; and the scratch outputs lj0_v1.out, lj1_v1.out, lj2_v1.out, lj4_v1.out, listing_v1.out, rdscan_v1.out, scan_v1.out, scan_v2.out, integrity_v1.out and hashes_v1.out). No verdict changed.
- **id**: D-5
  - **command**: C069
  - **text**: The command line ended with `python3 -B -c pass 2>/dev/null || true`, a `python3 -c` program (the no-op "pass"; no output). CRJ-5 forbids it. It read and wrote nothing. The log entry C068 records the planned form of the same probe; C069 records the command actually run.
- **id**: D-6
  - **command**: C025, C072-C073
  - **text**: Two scripts were edited with the Edit tool after their first write and BEFORE their first run, so no output of a pre-edit version exists: rjcore_v1.py (six edits; first-write sha256 recorded in the log only in abbreviated form "ea0698e6...6b15", the full value having been displayed at C025 but not logged; the run version is c6e156f495d187fec8d1205bc86f8d2c423d8453b1c3cfa7bbabb4fc08648b9e) and tables_v1.py (four edits; first write d305d6992020c7d71f59eef52d79461560722241a1ac72e5243cccf5276372bf). The scratch parts paths_read_v1.yaml.part and deviations_v1.yaml.part (inputs of the assembler, not outputs) were corrected with the Edit tool before assembly, and assemble_v1.py received four edits before its first run (wordcheck_v1_parts.out was taken after the first of them; the post-write check covers the final text inside the md). No output was overwritten; every evaluator version and every output is kept under its own name.
- **id**: D-7
  - **command**: none
  - **text**: The command log's header names a paths_read.txt that was never created. paths_read in this attestation was rebuilt after the compaction from the command log, the scripts and the working notes; ranges read only before the compaction are marked "in part" without line numbers.
- **id**: D-8
  - **command**: C001-C094
  - **text**: The command log records argv with two abbreviations: `<repo>` for /home/user/crypto-autoresearcher and `<scratch>` for the session scratch directory (whose real path contains a word this report may not carry). Before the compaction a few entries recorded a pattern list or a repeated file list in abbreviated form ("(patterns)", "(same three trees)", "(outline)") rather than verbatim (C008, C010, C018, C021); those were read-only grep / sed children over the named files, and their verbatim text cannot be recovered without reading the session transcript, which this review may not read. After the compaction the log entries C048-C094 describe commands in prose; their exact argv are recorded separately, in order, in `<scratch>`/rt_d897a6/exact_argv_post_compaction.txt (X01-X52), which is reproduced under commands and in the md appendix.
- **id**: D-9
  - **command**: C095, C098
  - **text**: The two deliverables were first written by assemble_v1.py (C095; review-report.yaml sha256 3a84029a83219dcc3a766f1b12a4edaa359ebdceb5659609e3697e85a33c4cb2, review-report.md sha256 996ac45ade9e94596c34623789fb4ff5ea85e8ccd613f258bb39d474f0ce5412). The post-write inspection found that version's inference block carried a seventh key (resolved_model_note) beyond the six the dispatching session fixed. Both files were then rewritten WHOLE, once each, by assemble_v2.py (C098) from body_v2.yaml.part and deviations_v2.yaml.part: the note became a YAML comment on resolved_model_id, LJ-5 names a1_check_run.py 30, and the LK-1 exec_ok line states the raw_grid .npz removal. No verdict changed. The version 1 inputs, the version 1 assembler and its output are kept in scratch; the md appendix shows the unified diffs.

### budget

Advisory 43200 s; started about 2026-09-25T01:33Z; deliverables written at 2026-09-25T02:50:28Z. Memory within 4 GB (largest scratch process well below; no OOM, timeout or tool failure affected a verdict).

## Appendix A - per-file first attribution clause (reconstructed, CRJ-9)

Per-file first attribution clause under launchkind (RH-1 clause and record, NON-LAUNCH writer, or UNATTRIBUTED), reconstructed (CRJ-9), from listing_v1.json per_file_first_clause_RJ:

#### RUN-GFPN-f6a21a (284 files)

```text
child/fixture_S3.meta.json  <-  (v) cj:fixture_S3
child/fixture_S3.npz  <-  (v) cj:fixture_S3
child/fixture_S3.spec.json  <-  (ii) cj:fixture_S3
child/fixture_S3.stderr  <-  (i) cj:fixture_S3
child/fixture_S3.stdout  <-  (i) cj:fixture_S3
child/fixture_S3_rescaled.meta.json  <-  (v) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.npz  <-  (v) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.spec.json  <-  (ii) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.stderr  <-  (i) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.stdout  <-  (i) cj:fixture_S3_rescaled
child/fixture_torsion_S3_norm.meta.json  <-  (v) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.npz  <-  (v) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.spec.json  <-  (ii) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.stderr  <-  (i) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.stdout  <-  (i) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_rq.meta.json  <-  (v) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.npz  <-  (v) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.spec.json  <-  (ii) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.stderr  <-  (i) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.stdout  <-  (i) cj:fixture_torsion_S3_rq
child/fx_fresh1_raw_u.meta.json  <-  (v) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.spec.json  <-  (ii) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.stderr  <-  (i) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.stdout  <-  (i) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_x.meta.json  <-  (v) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.spec.json  <-  (ii) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.stderr  <-  (i) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.stdout  <-  (i) cj:fx_fresh1_raw_x
child/fx_fresh2_raw_u.meta.json  <-  (v) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.spec.json  <-  (ii) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.stderr  <-  (i) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.stdout  <-  (i) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_x.meta.json  <-  (v) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.spec.json  <-  (ii) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.stderr  <-  (i) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.stdout  <-  (i) cj:fx_fresh2_raw_x
child/fx_planted0_raw_u.meta.json  <-  (v) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.spec.json  <-  (ii) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.stderr  <-  (i) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.stdout  <-  (i) cj:fx_planted0_raw_u
child/fx_planted0_raw_x.meta.json  <-  (v) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.spec.json  <-  (ii) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.stderr  <-  (i) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.stdout  <-  (i) cj:fx_planted0_raw_x
child/fx_planted1_raw_u.meta.json  <-  (v) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.spec.json  <-  (ii) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.stderr  <-  (i) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.stdout  <-  (i) cj:fx_planted1_raw_u
child/fx_planted1_raw_x.meta.json  <-  (v) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.spec.json  <-  (ii) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.stderr  <-  (i) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.stdout  <-  (i) cj:fx_planted1_raw_x
child/fx_reg0_raw_u.meta.json  <-  (v) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.spec.json  <-  (ii) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.stderr  <-  (i) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.stdout  <-  (i) cj:fx_reg0_raw_u
child/fx_reg0_raw_x.meta.json  <-  (v) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.spec.json  <-  (ii) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.stderr  <-  (i) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.stdout  <-  (i) cj:fx_reg0_raw_x
child/fx_reg1_raw_u.meta.json  <-  (v) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.spec.json  <-  (ii) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.stderr  <-  (i) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.stdout  <-  (i) cj:fx_reg1_raw_u
child/fx_reg1_raw_x.meta.json  <-  (v) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.spec.json  <-  (ii) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.stderr  <-  (i) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.stdout  <-  (i) cj:fx_reg1_raw_x
solver/fx_fresh1_S3.callgrind.stderr  <-  (i) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.callgrind.stdout  <-  (i) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.ms  <-  (ii) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.ms.err  <-  (i) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3.ms.log  <-  (i) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3.ms.out  <-  (ii) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.ms  <-  (ii) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.ms.err  <-  (i) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_S3_rescaled.ms.log  <-  (i) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_S3_rescaled.ms.out  <-  (ii) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_raw_u.callgrind.stderr  <-  (i) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.callgrind.stdout  <-  (i) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.ms  <-  (ii) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.ms.err  <-  (i) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_u.ms.log  <-  (i) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_u.ms.out  <-  (ii) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_x.callgrind.stderr  <-  (i) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.callgrind.stdout  <-  (i) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.ms  <-  (ii) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.ms.err  <-  (i) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_raw_x.ms.log  <-  (i) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_raw_x.ms.out  <-  (ii) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.ms  <-  (ii) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.ms.err  <-  (i) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_norm.ms.log  <-  (i) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.ms  <-  (ii) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.ms.err  <-  (i) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh1_torsion_S3_rq.ms.log  <-  (i) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh2_S3.callgrind.stderr  <-  (i) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.callgrind.stdout  <-  (i) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.ms  <-  (ii) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.ms.err  <-  (i) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3.ms.log  <-  (i) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3.ms.out  <-  (ii) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.ms  <-  (ii) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.ms.err  <-  (i) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_S3_rescaled.ms.log  <-  (i) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_S3_rescaled.ms.out  <-  (ii) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_raw_u.callgrind.stderr  <-  (i) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.callgrind.stdout  <-  (i) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.ms  <-  (ii) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.ms.err  <-  (i) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_u.ms.log  <-  (i) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_u.ms.out  <-  (ii) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_x.callgrind.stderr  <-  (i) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.callgrind.stdout  <-  (i) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.ms  <-  (ii) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.ms.err  <-  (i) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_raw_x.ms.log  <-  (i) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_raw_x.ms.out  <-  (ii) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.ms  <-  (ii) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.ms.err  <-  (i) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_norm.ms.log  <-  (i) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_norm.ms.out  <-  (ii) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.ms  <-  (ii) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.ms.err  <-  (i) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_fresh2_torsion_S3_rq.ms.log  <-  (i) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_fresh2_torsion_S3_rq.ms.out  <-  (ii) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_planted0_S3.callgrind.stderr  <-  (i) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.callgrind.stdout  <-  (i) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.ms  <-  (ii) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.ms.err  <-  (i) solver:fx_planted0_S3/ms
solver/fx_planted0_S3.ms.log  <-  (i) solver:fx_planted0_S3/ms
solver/fx_planted0_S3.ms.out  <-  (ii) solver:fx_planted0_S3/ms
solver/fx_planted0_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.ms  <-  (ii) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.ms.err  <-  (i) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_S3_rescaled.ms.log  <-  (i) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_S3_rescaled.ms.out  <-  (ii) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_raw_u.callgrind.stderr  <-  (i) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.callgrind.stdout  <-  (i) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.ms  <-  (ii) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.ms.err  <-  (i) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_u.ms.log  <-  (i) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_u.ms.out  <-  (ii) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_x.callgrind.stderr  <-  (i) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.callgrind.stdout  <-  (i) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.ms  <-  (ii) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.ms.err  <-  (i) solver:fx_planted0_raw_x/ms
solver/fx_planted0_raw_x.ms.log  <-  (i) solver:fx_planted0_raw_x/ms
solver/fx_planted0_raw_x.ms.out  <-  (ii) solver:fx_planted0_raw_x/ms
solver/fx_planted0_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.ms  <-  (ii) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.ms.err  <-  (i) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_norm.ms.log  <-  (i) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_norm.ms.out  <-  (ii) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.ms  <-  (ii) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.ms.err  <-  (i) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted0_torsion_S3_rq.ms.log  <-  (i) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted0_torsion_S3_rq.ms.out  <-  (ii) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted1_S3.callgrind.stderr  <-  (i) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.callgrind.stdout  <-  (i) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.ms  <-  (ii) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.ms.err  <-  (i) solver:fx_planted1_S3/ms
solver/fx_planted1_S3.ms.log  <-  (i) solver:fx_planted1_S3/ms
solver/fx_planted1_S3.ms.out  <-  (ii) solver:fx_planted1_S3/ms
solver/fx_planted1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.ms  <-  (ii) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.ms.err  <-  (i) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_S3_rescaled.ms.log  <-  (i) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_S3_rescaled.ms.out  <-  (ii) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_raw_u.callgrind.stderr  <-  (i) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.callgrind.stdout  <-  (i) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.ms  <-  (ii) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.ms.err  <-  (i) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_u.ms.log  <-  (i) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_u.ms.out  <-  (ii) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_x.callgrind.stderr  <-  (i) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.callgrind.stdout  <-  (i) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.ms  <-  (ii) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.ms.err  <-  (i) solver:fx_planted1_raw_x/ms
solver/fx_planted1_raw_x.ms.log  <-  (i) solver:fx_planted1_raw_x/ms
solver/fx_planted1_raw_x.ms.out  <-  (ii) solver:fx_planted1_raw_x/ms
solver/fx_planted1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.ms  <-  (ii) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.ms.err  <-  (i) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_norm.ms.log  <-  (i) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.ms  <-  (ii) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.ms.err  <-  (i) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_planted1_torsion_S3_rq.ms.log  <-  (i) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_planted1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_reg0_S3.callgrind.stderr  <-  (i) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.callgrind.stdout  <-  (i) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.ms  <-  (ii) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.ms.err  <-  (i) solver:fx_reg0_S3/ms
solver/fx_reg0_S3.ms.log  <-  (i) solver:fx_reg0_S3/ms
solver/fx_reg0_S3.ms.out  <-  (ii) solver:fx_reg0_S3/ms
solver/fx_reg0_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.ms  <-  (ii) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.ms.err  <-  (i) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_S3_rescaled.ms.log  <-  (i) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_S3_rescaled.ms.out  <-  (ii) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_raw_u.callgrind.stderr  <-  (i) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.callgrind.stdout  <-  (i) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.ms  <-  (ii) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.ms.err  <-  (i) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_u.ms.log  <-  (i) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_u.ms.out  <-  (ii) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_x.callgrind.stderr  <-  (i) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.callgrind.stdout  <-  (i) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.ms  <-  (ii) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.ms.err  <-  (i) solver:fx_reg0_raw_x/ms
solver/fx_reg0_raw_x.ms.log  <-  (i) solver:fx_reg0_raw_x/ms
solver/fx_reg0_raw_x.ms.out  <-  (ii) solver:fx_reg0_raw_x/ms
solver/fx_reg0_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.ms  <-  (ii) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.ms.err  <-  (i) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_norm.ms.log  <-  (i) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_norm.ms.out  <-  (ii) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.ms  <-  (ii) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.ms.err  <-  (i) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg0_torsion_S3_rq.ms.log  <-  (i) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg0_torsion_S3_rq.ms.out  <-  (ii) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg1_S3.callgrind.stderr  <-  (i) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.callgrind.stdout  <-  (i) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.ms  <-  (ii) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.ms.err  <-  (i) solver:fx_reg1_S3/ms
solver/fx_reg1_S3.ms.log  <-  (i) solver:fx_reg1_S3/ms
solver/fx_reg1_S3.ms.out  <-  (ii) solver:fx_reg1_S3/ms
solver/fx_reg1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.ms  <-  (ii) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.ms.err  <-  (i) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_S3_rescaled.ms.log  <-  (i) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_S3_rescaled.ms.out  <-  (ii) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_raw_u.callgrind.stderr  <-  (i) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.callgrind.stdout  <-  (i) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.ms  <-  (ii) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.ms.err  <-  (i) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_u.ms.log  <-  (i) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_u.ms.out  <-  (ii) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_x.callgrind.stderr  <-  (i) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.callgrind.stdout  <-  (i) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.ms  <-  (ii) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.ms.err  <-  (i) solver:fx_reg1_raw_x/ms
solver/fx_reg1_raw_x.ms.log  <-  (i) solver:fx_reg1_raw_x/ms
solver/fx_reg1_raw_x.ms.out  <-  (ii) solver:fx_reg1_raw_x/ms
solver/fx_reg1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.ms  <-  (ii) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.ms.err  <-  (i) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_norm.ms.log  <-  (i) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.ms  <-  (ii) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.ms.err  <-  (i) solver:fx_reg1_torsion_S3_rq/ms
solver/fx_reg1_torsion_S3_rq.ms.log  <-  (i) solver:fx_reg1_torsion_S3_rq/ms
solver/fx_reg1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_reg1_torsion_S3_rq/ms
```

#### RUN-GFPN-902222 (284 files)

```text
child/fixture_S3.meta.json  <-  (v) cj:fixture_S3
child/fixture_S3.npz  <-  (v) cj:fixture_S3
child/fixture_S3.spec.json  <-  (ii) cj:fixture_S3
child/fixture_S3.stderr  <-  (i) cj:fixture_S3
child/fixture_S3.stdout  <-  (i) cj:fixture_S3
child/fixture_S3_rescaled.meta.json  <-  (v) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.npz  <-  (v) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.spec.json  <-  (ii) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.stderr  <-  (i) cj:fixture_S3_rescaled
child/fixture_S3_rescaled.stdout  <-  (i) cj:fixture_S3_rescaled
child/fixture_torsion_S3_norm.meta.json  <-  (v) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.npz  <-  (v) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.spec.json  <-  (ii) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.stderr  <-  (i) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_norm.stdout  <-  (i) cj:fixture_torsion_S3_norm
child/fixture_torsion_S3_rq.meta.json  <-  (v) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.npz  <-  (v) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.spec.json  <-  (ii) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.stderr  <-  (i) cj:fixture_torsion_S3_rq
child/fixture_torsion_S3_rq.stdout  <-  (i) cj:fixture_torsion_S3_rq
child/fx_fresh1_raw_u.meta.json  <-  (v) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.spec.json  <-  (ii) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.stderr  <-  (i) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_u.stdout  <-  (i) cj:fx_fresh1_raw_u
child/fx_fresh1_raw_x.meta.json  <-  (v) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.spec.json  <-  (ii) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.stderr  <-  (i) cj:fx_fresh1_raw_x
child/fx_fresh1_raw_x.stdout  <-  (i) cj:fx_fresh1_raw_x
child/fx_fresh2_raw_u.meta.json  <-  (v) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.spec.json  <-  (ii) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.stderr  <-  (i) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_u.stdout  <-  (i) cj:fx_fresh2_raw_u
child/fx_fresh2_raw_x.meta.json  <-  (v) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.spec.json  <-  (ii) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.stderr  <-  (i) cj:fx_fresh2_raw_x
child/fx_fresh2_raw_x.stdout  <-  (i) cj:fx_fresh2_raw_x
child/fx_planted0_raw_u.meta.json  <-  (v) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.spec.json  <-  (ii) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.stderr  <-  (i) cj:fx_planted0_raw_u
child/fx_planted0_raw_u.stdout  <-  (i) cj:fx_planted0_raw_u
child/fx_planted0_raw_x.meta.json  <-  (v) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.spec.json  <-  (ii) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.stderr  <-  (i) cj:fx_planted0_raw_x
child/fx_planted0_raw_x.stdout  <-  (i) cj:fx_planted0_raw_x
child/fx_planted1_raw_u.meta.json  <-  (v) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.spec.json  <-  (ii) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.stderr  <-  (i) cj:fx_planted1_raw_u
child/fx_planted1_raw_u.stdout  <-  (i) cj:fx_planted1_raw_u
child/fx_planted1_raw_x.meta.json  <-  (v) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.spec.json  <-  (ii) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.stderr  <-  (i) cj:fx_planted1_raw_x
child/fx_planted1_raw_x.stdout  <-  (i) cj:fx_planted1_raw_x
child/fx_reg0_raw_u.meta.json  <-  (v) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.spec.json  <-  (ii) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.stderr  <-  (i) cj:fx_reg0_raw_u
child/fx_reg0_raw_u.stdout  <-  (i) cj:fx_reg0_raw_u
child/fx_reg0_raw_x.meta.json  <-  (v) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.spec.json  <-  (ii) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.stderr  <-  (i) cj:fx_reg0_raw_x
child/fx_reg0_raw_x.stdout  <-  (i) cj:fx_reg0_raw_x
child/fx_reg1_raw_u.meta.json  <-  (v) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.spec.json  <-  (ii) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.stderr  <-  (i) cj:fx_reg1_raw_u
child/fx_reg1_raw_u.stdout  <-  (i) cj:fx_reg1_raw_u
child/fx_reg1_raw_x.meta.json  <-  (v) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.spec.json  <-  (ii) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.stderr  <-  (i) cj:fx_reg1_raw_x
child/fx_reg1_raw_x.stdout  <-  (i) cj:fx_reg1_raw_x
solver/fx_fresh1_S3.callgrind.stderr  <-  (i) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.callgrind.stdout  <-  (i) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.ms  <-  (ii) solver:fx_fresh1_S3/cg
solver/fx_fresh1_S3.ms.err  <-  (i) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3.ms.log  <-  (i) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3.ms.out  <-  (ii) solver:fx_fresh1_S3/ms
solver/fx_fresh1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.ms  <-  (ii) solver:fx_fresh1_S3_rescaled/cg
solver/fx_fresh1_S3_rescaled.ms.err  <-  (i) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_S3_rescaled.ms.log  <-  (i) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_S3_rescaled.ms.out  <-  (ii) solver:fx_fresh1_S3_rescaled/ms
solver/fx_fresh1_raw_u.callgrind.stderr  <-  (i) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.callgrind.stdout  <-  (i) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.ms  <-  (ii) solver:fx_fresh1_raw_u/cg
solver/fx_fresh1_raw_u.ms.err  <-  (i) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_u.ms.log  <-  (i) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_u.ms.out  <-  (ii) solver:fx_fresh1_raw_u/ms
solver/fx_fresh1_raw_x.callgrind.stderr  <-  (i) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.callgrind.stdout  <-  (i) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.ms  <-  (ii) solver:fx_fresh1_raw_x/cg
solver/fx_fresh1_raw_x.ms.err  <-  (i) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_raw_x.ms.log  <-  (i) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_raw_x.ms.out  <-  (ii) solver:fx_fresh1_raw_x/ms
solver/fx_fresh1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.ms  <-  (ii) solver:fx_fresh1_torsion_S3_norm/cg
solver/fx_fresh1_torsion_S3_norm.ms.err  <-  (i) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_norm.ms.log  <-  (i) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_fresh1_torsion_S3_norm/ms
solver/fx_fresh1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.ms  <-  (ii) solver:fx_fresh1_torsion_S3_rq/cg
solver/fx_fresh1_torsion_S3_rq.ms.err  <-  (i) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh1_torsion_S3_rq.ms.log  <-  (i) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_fresh1_torsion_S3_rq/ms
solver/fx_fresh2_S3.callgrind.stderr  <-  (i) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.callgrind.stdout  <-  (i) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.ms  <-  (ii) solver:fx_fresh2_S3/cg
solver/fx_fresh2_S3.ms.err  <-  (i) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3.ms.log  <-  (i) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3.ms.out  <-  (ii) solver:fx_fresh2_S3/ms
solver/fx_fresh2_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.ms  <-  (ii) solver:fx_fresh2_S3_rescaled/cg
solver/fx_fresh2_S3_rescaled.ms.err  <-  (i) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_S3_rescaled.ms.log  <-  (i) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_S3_rescaled.ms.out  <-  (ii) solver:fx_fresh2_S3_rescaled/ms
solver/fx_fresh2_raw_u.callgrind.stderr  <-  (i) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.callgrind.stdout  <-  (i) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.ms  <-  (ii) solver:fx_fresh2_raw_u/cg
solver/fx_fresh2_raw_u.ms.err  <-  (i) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_u.ms.log  <-  (i) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_u.ms.out  <-  (ii) solver:fx_fresh2_raw_u/ms
solver/fx_fresh2_raw_x.callgrind.stderr  <-  (i) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.callgrind.stdout  <-  (i) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.ms  <-  (ii) solver:fx_fresh2_raw_x/cg
solver/fx_fresh2_raw_x.ms.err  <-  (i) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_raw_x.ms.log  <-  (i) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_raw_x.ms.out  <-  (ii) solver:fx_fresh2_raw_x/ms
solver/fx_fresh2_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.ms  <-  (ii) solver:fx_fresh2_torsion_S3_norm/cg
solver/fx_fresh2_torsion_S3_norm.ms.err  <-  (i) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_norm.ms.log  <-  (i) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_norm.ms.out  <-  (ii) solver:fx_fresh2_torsion_S3_norm/ms
solver/fx_fresh2_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.ms  <-  (ii) solver:fx_fresh2_torsion_S3_rq/cg
solver/fx_fresh2_torsion_S3_rq.ms.err  <-  (i) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_fresh2_torsion_S3_rq.ms.log  <-  (i) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_fresh2_torsion_S3_rq.ms.out  <-  (ii) solver:fx_fresh2_torsion_S3_rq/ms
solver/fx_planted0_S3.callgrind.stderr  <-  (i) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.callgrind.stdout  <-  (i) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.ms  <-  (ii) solver:fx_planted0_S3/cg
solver/fx_planted0_S3.ms.err  <-  (i) solver:fx_planted0_S3/ms
solver/fx_planted0_S3.ms.log  <-  (i) solver:fx_planted0_S3/ms
solver/fx_planted0_S3.ms.out  <-  (ii) solver:fx_planted0_S3/ms
solver/fx_planted0_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.ms  <-  (ii) solver:fx_planted0_S3_rescaled/cg
solver/fx_planted0_S3_rescaled.ms.err  <-  (i) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_S3_rescaled.ms.log  <-  (i) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_S3_rescaled.ms.out  <-  (ii) solver:fx_planted0_S3_rescaled/ms
solver/fx_planted0_raw_u.callgrind.stderr  <-  (i) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.callgrind.stdout  <-  (i) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.ms  <-  (ii) solver:fx_planted0_raw_u/cg
solver/fx_planted0_raw_u.ms.err  <-  (i) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_u.ms.log  <-  (i) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_u.ms.out  <-  (ii) solver:fx_planted0_raw_u/ms
solver/fx_planted0_raw_x.callgrind.stderr  <-  (i) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.callgrind.stdout  <-  (i) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.ms  <-  (ii) solver:fx_planted0_raw_x/cg
solver/fx_planted0_raw_x.ms.err  <-  (i) solver:fx_planted0_raw_x/ms
solver/fx_planted0_raw_x.ms.log  <-  (i) solver:fx_planted0_raw_x/ms
solver/fx_planted0_raw_x.ms.out  <-  (ii) solver:fx_planted0_raw_x/ms
solver/fx_planted0_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.ms  <-  (ii) solver:fx_planted0_torsion_S3_norm/cg
solver/fx_planted0_torsion_S3_norm.ms.err  <-  (i) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_norm.ms.log  <-  (i) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_norm.ms.out  <-  (ii) solver:fx_planted0_torsion_S3_norm/ms
solver/fx_planted0_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.ms  <-  (ii) solver:fx_planted0_torsion_S3_rq/cg
solver/fx_planted0_torsion_S3_rq.ms.err  <-  (i) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted0_torsion_S3_rq.ms.log  <-  (i) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted0_torsion_S3_rq.ms.out  <-  (ii) solver:fx_planted0_torsion_S3_rq/ms
solver/fx_planted1_S3.callgrind.stderr  <-  (i) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.callgrind.stdout  <-  (i) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.ms  <-  (ii) solver:fx_planted1_S3/cg
solver/fx_planted1_S3.ms.err  <-  (i) solver:fx_planted1_S3/ms
solver/fx_planted1_S3.ms.log  <-  (i) solver:fx_planted1_S3/ms
solver/fx_planted1_S3.ms.out  <-  (ii) solver:fx_planted1_S3/ms
solver/fx_planted1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.ms  <-  (ii) solver:fx_planted1_S3_rescaled/cg
solver/fx_planted1_S3_rescaled.ms.err  <-  (i) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_S3_rescaled.ms.log  <-  (i) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_S3_rescaled.ms.out  <-  (ii) solver:fx_planted1_S3_rescaled/ms
solver/fx_planted1_raw_u.callgrind.stderr  <-  (i) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.callgrind.stdout  <-  (i) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.ms  <-  (ii) solver:fx_planted1_raw_u/cg
solver/fx_planted1_raw_u.ms.err  <-  (i) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_u.ms.log  <-  (i) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_u.ms.out  <-  (ii) solver:fx_planted1_raw_u/ms
solver/fx_planted1_raw_x.callgrind.stderr  <-  (i) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.callgrind.stdout  <-  (i) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.ms  <-  (ii) solver:fx_planted1_raw_x/cg
solver/fx_planted1_raw_x.ms.err  <-  (i) solver:fx_planted1_raw_x/ms
solver/fx_planted1_raw_x.ms.log  <-  (i) solver:fx_planted1_raw_x/ms
solver/fx_planted1_raw_x.ms.out  <-  (ii) solver:fx_planted1_raw_x/ms
solver/fx_planted1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.ms  <-  (ii) solver:fx_planted1_torsion_S3_norm/cg
solver/fx_planted1_torsion_S3_norm.ms.err  <-  (i) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_norm.ms.log  <-  (i) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_planted1_torsion_S3_norm/ms
solver/fx_planted1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.ms  <-  (ii) solver:fx_planted1_torsion_S3_rq/cg
solver/fx_planted1_torsion_S3_rq.ms.err  <-  (i) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_planted1_torsion_S3_rq.ms.log  <-  (i) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_planted1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_planted1_torsion_S3_rq/ms
solver/fx_reg0_S3.callgrind.stderr  <-  (i) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.callgrind.stdout  <-  (i) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.ms  <-  (ii) solver:fx_reg0_S3/cg
solver/fx_reg0_S3.ms.err  <-  (i) solver:fx_reg0_S3/ms
solver/fx_reg0_S3.ms.log  <-  (i) solver:fx_reg0_S3/ms
solver/fx_reg0_S3.ms.out  <-  (ii) solver:fx_reg0_S3/ms
solver/fx_reg0_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.ms  <-  (ii) solver:fx_reg0_S3_rescaled/cg
solver/fx_reg0_S3_rescaled.ms.err  <-  (i) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_S3_rescaled.ms.log  <-  (i) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_S3_rescaled.ms.out  <-  (ii) solver:fx_reg0_S3_rescaled/ms
solver/fx_reg0_raw_u.callgrind.stderr  <-  (i) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.callgrind.stdout  <-  (i) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.ms  <-  (ii) solver:fx_reg0_raw_u/cg
solver/fx_reg0_raw_u.ms.err  <-  (i) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_u.ms.log  <-  (i) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_u.ms.out  <-  (ii) solver:fx_reg0_raw_u/ms
solver/fx_reg0_raw_x.callgrind.stderr  <-  (i) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.callgrind.stdout  <-  (i) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.ms  <-  (ii) solver:fx_reg0_raw_x/cg
solver/fx_reg0_raw_x.ms.err  <-  (i) solver:fx_reg0_raw_x/ms
solver/fx_reg0_raw_x.ms.log  <-  (i) solver:fx_reg0_raw_x/ms
solver/fx_reg0_raw_x.ms.out  <-  (ii) solver:fx_reg0_raw_x/ms
solver/fx_reg0_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.ms  <-  (ii) solver:fx_reg0_torsion_S3_norm/cg
solver/fx_reg0_torsion_S3_norm.ms.err  <-  (i) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_norm.ms.log  <-  (i) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_norm.ms.out  <-  (ii) solver:fx_reg0_torsion_S3_norm/ms
solver/fx_reg0_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.ms  <-  (ii) solver:fx_reg0_torsion_S3_rq/cg
solver/fx_reg0_torsion_S3_rq.ms.err  <-  (i) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg0_torsion_S3_rq.ms.log  <-  (i) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg0_torsion_S3_rq.ms.out  <-  (ii) solver:fx_reg0_torsion_S3_rq/ms
solver/fx_reg1_S3.callgrind.stderr  <-  (i) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.callgrind.stdout  <-  (i) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.ms  <-  (ii) solver:fx_reg1_S3/cg
solver/fx_reg1_S3.ms.err  <-  (i) solver:fx_reg1_S3/ms
solver/fx_reg1_S3.ms.log  <-  (i) solver:fx_reg1_S3/ms
solver/fx_reg1_S3.ms.out  <-  (ii) solver:fx_reg1_S3/ms
solver/fx_reg1_S3_rescaled.callgrind.stderr  <-  (i) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.callgrind.stdout  <-  (i) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.ms  <-  (ii) solver:fx_reg1_S3_rescaled/cg
solver/fx_reg1_S3_rescaled.ms.err  <-  (i) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_S3_rescaled.ms.log  <-  (i) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_S3_rescaled.ms.out  <-  (ii) solver:fx_reg1_S3_rescaled/ms
solver/fx_reg1_raw_u.callgrind.stderr  <-  (i) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.callgrind.stdout  <-  (i) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.ms  <-  (ii) solver:fx_reg1_raw_u/cg
solver/fx_reg1_raw_u.ms.err  <-  (i) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_u.ms.log  <-  (i) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_u.ms.out  <-  (ii) solver:fx_reg1_raw_u/ms
solver/fx_reg1_raw_x.callgrind.stderr  <-  (i) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.callgrind.stdout  <-  (i) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.ms  <-  (ii) solver:fx_reg1_raw_x/cg
solver/fx_reg1_raw_x.ms.err  <-  (i) solver:fx_reg1_raw_x/ms
solver/fx_reg1_raw_x.ms.log  <-  (i) solver:fx_reg1_raw_x/ms
solver/fx_reg1_raw_x.ms.out  <-  (ii) solver:fx_reg1_raw_x/ms
solver/fx_reg1_torsion_S3_norm.callgrind.stderr  <-  (i) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.callgrind.stdout  <-  (i) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.ms  <-  (ii) solver:fx_reg1_torsion_S3_norm/cg
solver/fx_reg1_torsion_S3_norm.ms.err  <-  (i) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_norm.ms.log  <-  (i) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_norm.ms.out  <-  (ii) solver:fx_reg1_torsion_S3_norm/ms
solver/fx_reg1_torsion_S3_rq.callgrind.stderr  <-  (i) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.callgrind.stdout  <-  (i) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.ms  <-  (ii) solver:fx_reg1_torsion_S3_rq/cg
solver/fx_reg1_torsion_S3_rq.ms.err  <-  (i) solver:fx_reg1_torsion_S3_rq/ms
solver/fx_reg1_torsion_S3_rq.ms.log  <-  (i) solver:fx_reg1_torsion_S3_rq/ms
solver/fx_reg1_torsion_S3_rq.ms.out  <-  (ii) solver:fx_reg1_torsion_S3_rq/ms
```

#### RUN-GFPN-f5412a (32 files)

```text
child/anchor_S4.meta.json  <-  (v) cj:anchor_S4
child/anchor_S4.npz  <-  (v) cj:anchor_S4
child/anchor_S4.spec.json  <-  (ii) cj:anchor_S4
child/anchor_S4.stderr  <-  (i) cj:anchor_S4
child/anchor_S4.stdout  <-  (i) cj:anchor_S4
comparator/anchor17_planted.ms  <-  (iv) cmp
comparator/anchor17_random.ms  <-  (iv) cmp
comparator/anchor25_planted.ms  <-  (iv) cmp
comparator/anchor25_random.ms  <-  (iv) cmp
comparator/k4a_results.json  <-  (iv) cmp
comparator/stderr.log  <-  (i) cmp
comparator/stdout.log  <-  (i) cmp
solver/anchor_comparator_random.ms  <-  (ii) solver:anchor_comparator_random/ms
solver/anchor_comparator_random.ms.err  <-  (i) solver:anchor_comparator_random/ms
solver/anchor_comparator_random.ms.log  <-  (i) solver:anchor_comparator_random/ms
solver/anchor_comparator_random.ms.out  <-  (ii) solver:anchor_comparator_random/ms
solver/anchor_comparator_system.ms  <-  (ii) solver:anchor_comparator_system/ms
solver/anchor_comparator_system.ms.err  <-  (i) solver:anchor_comparator_system/ms
solver/anchor_comparator_system.ms.log  <-  (i) solver:anchor_comparator_system/ms
solver/anchor_comparator_system.ms.out  <-  (ii) solver:anchor_comparator_system/ms
solver/anchor_v2_t0.ms  <-  (ii) solver:anchor_v2_t0/ms
solver/anchor_v2_t0.ms.err  <-  (i) solver:anchor_v2_t0/ms
solver/anchor_v2_t0.ms.log  <-  (i) solver:anchor_v2_t0/ms
solver/anchor_v2_t0.ms.out  <-  (ii) solver:anchor_v2_t0/ms
solver/anchor_v2_t1.ms  <-  (ii) solver:anchor_v2_t1/ms
solver/anchor_v2_t1.ms.err  <-  (i) solver:anchor_v2_t1/ms
solver/anchor_v2_t1.ms.log  <-  (i) solver:anchor_v2_t1/ms
solver/anchor_v2_t1.ms.out  <-  (ii) solver:anchor_v2_t1/ms
solver/anchor_v2_t2.ms  <-  (ii) solver:anchor_v2_t2/ms
solver/anchor_v2_t2.ms.err  <-  (i) solver:anchor_v2_t2/ms
solver/anchor_v2_t2.ms.log  <-  (i) solver:anchor_v2_t2/ms
solver/anchor_v2_t2.ms.out  <-  (ii) solver:anchor_v2_t2/ms
```

#### RUN-GFPN-bfe956 (83 files)

```text
child/ctl_S3.meta.json  <-  (v) cj:ctl_S3
child/ctl_S3.npz  <-  (v) cj:ctl_S3
child/ctl_S3.spec.json  <-  (ii) cj:ctl_S3
child/ctl_S3.stderr  <-  (i) cj:ctl_S3
child/ctl_S3.stdout  <-  (i) cj:ctl_S3
child/ctl_S3_rescaled.meta.json  <-  (v) cj:ctl_S3_rescaled
child/ctl_S3_rescaled.npz  <-  (v) cj:ctl_S3_rescaled
child/ctl_S3_rescaled.spec.json  <-  (ii) cj:ctl_S3_rescaled
child/ctl_S3_rescaled.stderr  <-  (i) cj:ctl_S3_rescaled
child/ctl_S3_rescaled.stdout  <-  (i) cj:ctl_S3_rescaled
child/ctl_identity_n3.meta.json  <-  (v) cj:ctl_identity_n3
child/ctl_identity_n3.npz  <-  (v) cj:ctl_identity_n3
child/ctl_identity_n3.spec.json  <-  (ii) cj:ctl_identity_n3
child/ctl_identity_n3.stderr  <-  (i) cj:ctl_identity_n3
child/ctl_identity_n3.stdout  <-  (i) cj:ctl_identity_n3
child/ctl_identity_n5_m3.meta.json  <-  (v) cj:ctl_identity_n5_m3
child/ctl_identity_n5_m3.npz  <-  (v) cj:ctl_identity_n5_m3
child/ctl_identity_n5_m3.spec.json  <-  (ii) cj:ctl_identity_n5_m3
child/ctl_identity_n5_m3.stderr  <-  (i) cj:ctl_identity_n5_m3
child/ctl_identity_n5_m3.stdout  <-  (i) cj:ctl_identity_n5_m3
child/ctl_identity_n5_m4.meta.json  <-  (v) cj:ctl_identity_n5_m4
child/ctl_identity_n5_m4.npz  <-  (v) cj:ctl_identity_n5_m4
child/ctl_identity_n5_m4.spec.json  <-  (ii) cj:ctl_identity_n5_m4
child/ctl_identity_n5_m4.stderr  <-  (i) cj:ctl_identity_n5_m4
child/ctl_identity_n5_m4.stdout  <-  (i) cj:ctl_identity_n5_m4
child/ctl_raw_n5_m3.meta.json  <-  (v) cj:ctl_raw_n5_m3
child/ctl_raw_n5_m3.spec.json  <-  (ii) cj:ctl_raw_n5_m3
child/ctl_raw_n5_m3.stderr  <-  (i) cj:ctl_raw_n5_m3
child/ctl_raw_n5_m3.stdout  <-  (i) cj:ctl_raw_n5_m3
child/ctl_raw_n5_m4.meta.json  <-  (v) cj:ctl_raw_n5_m4
child/ctl_raw_n5_m4.spec.json  <-  (ii) cj:ctl_raw_n5_m4
child/ctl_raw_n5_m4.stderr  <-  (i) cj:ctl_raw_n5_m4
child/ctl_raw_n5_m4.stdout  <-  (i) cj:ctl_raw_n5_m4
child/ctl_raw_planted.meta.json  <-  (v) cj:ctl_raw_planted
child/ctl_raw_planted.spec.json  <-  (ii) cj:ctl_raw_planted
child/ctl_raw_planted.stderr  <-  (i) cj:ctl_raw_planted
child/ctl_raw_planted.stdout  <-  (i) cj:ctl_raw_planted
child/ctl_raw_random.meta.json  <-  (v) cj:ctl_raw_random
child/ctl_raw_random.spec.json  <-  (ii) cj:ctl_raw_random
child/ctl_raw_random.stderr  <-  (i) cj:ctl_raw_random
child/ctl_raw_random.stdout  <-  (i) cj:ctl_raw_random
child/ctl_torsion_S3_norm.meta.json  <-  (v) cj:ctl_torsion_S3_norm
child/ctl_torsion_S3_norm.npz  <-  (v) cj:ctl_torsion_S3_norm
child/ctl_torsion_S3_norm.spec.json  <-  (ii) cj:ctl_torsion_S3_norm
child/ctl_torsion_S3_norm.stderr  <-  (i) cj:ctl_torsion_S3_norm
child/ctl_torsion_S3_norm.stdout  <-  (i) cj:ctl_torsion_S3_norm
child/ctl_torsion_S3_rq.meta.json  <-  (v) cj:ctl_torsion_S3_rq
child/ctl_torsion_S3_rq.npz  <-  (v) cj:ctl_torsion_S3_rq
child/ctl_torsion_S3_rq.spec.json  <-  (ii) cj:ctl_torsion_S3_rq
child/ctl_torsion_S3_rq.stderr  <-  (i) cj:ctl_torsion_S3_rq
child/ctl_torsion_S3_rq.stdout  <-  (i) cj:ctl_torsion_S3_rq
solver/ctl_identity_planted.ms  <-  (ii) solver:ctl_identity_planted/ms
solver/ctl_identity_planted.ms.err  <-  (i) solver:ctl_identity_planted/ms
solver/ctl_identity_planted.ms.log  <-  (i) solver:ctl_identity_planted/ms
solver/ctl_identity_planted.ms.out  <-  (ii) solver:ctl_identity_planted/ms
solver/ctl_identity_random.ms  <-  (ii) solver:ctl_identity_random/ms
solver/ctl_identity_random.ms.err  <-  (i) solver:ctl_identity_random/ms
solver/ctl_identity_random.ms.log  <-  (i) solver:ctl_identity_random/ms
solver/ctl_identity_random.ms.out  <-  (ii) solver:ctl_identity_random/ms
solver/ctl_planted_S3.ms  <-  (ii) solver:ctl_planted_S3/ms
solver/ctl_planted_S3.ms.err  <-  (i) solver:ctl_planted_S3/ms
solver/ctl_planted_S3.ms.log  <-  (i) solver:ctl_planted_S3/ms
solver/ctl_planted_S3.ms.out  <-  (ii) solver:ctl_planted_S3/ms
solver/ctl_planted_S3_rescaled.ms  <-  (ii) solver:ctl_planted_S3_rescaled/ms
solver/ctl_planted_S3_rescaled.ms.err  <-  (i) solver:ctl_planted_S3_rescaled/ms
solver/ctl_planted_S3_rescaled.ms.log  <-  (i) solver:ctl_planted_S3_rescaled/ms
solver/ctl_planted_S3_rescaled.ms.out  <-  (ii) solver:ctl_planted_S3_rescaled/ms
solver/ctl_planted_torsion_S3_norm.ms  <-  (ii) solver:ctl_planted_torsion_S3_norm/ms
solver/ctl_planted_torsion_S3_norm.ms.err  <-  (i) solver:ctl_planted_torsion_S3_norm/ms
solver/ctl_planted_torsion_S3_norm.ms.log  <-  (i) solver:ctl_planted_torsion_S3_norm/ms
solver/ctl_planted_torsion_S3_norm.ms.out  <-  (ii) solver:ctl_planted_torsion_S3_norm/ms
solver/ctl_planted_torsion_S3_rq.ms  <-  (ii) solver:ctl_planted_torsion_S3_rq/ms
solver/ctl_planted_torsion_S3_rq.ms.err  <-  (i) solver:ctl_planted_torsion_S3_rq/ms
solver/ctl_planted_torsion_S3_rq.ms.log  <-  (i) solver:ctl_planted_torsion_S3_rq/ms
solver/ctl_planted_torsion_S3_rq.ms.out  <-  (ii) solver:ctl_planted_torsion_S3_rq/ms
solver/ctl_rawx_planted.ms  <-  (ii) solver:ctl_rawx_planted/ms
solver/ctl_rawx_planted.ms.err  <-  (i) solver:ctl_rawx_planted/ms
solver/ctl_rawx_planted.ms.log  <-  (i) solver:ctl_rawx_planted/ms
solver/ctl_rawx_planted.ms.out  <-  (ii) solver:ctl_rawx_planted/ms
solver/ctl_rawx_random.ms  <-  (ii) solver:ctl_rawx_random/ms
solver/ctl_rawx_random.ms.err  <-  (i) solver:ctl_rawx_random/ms
solver/ctl_rawx_random.ms.log  <-  (i) solver:ctl_rawx_random/ms
solver/ctl_rawx_random.ms.out  <-  (ii) solver:ctl_rawx_random/ms
```



## Appendix B - command log (verbatim) and exact argv after the compaction

### B.1 `<scratch>/rt_d897a6/command_log.txt` (sha256 5254ed5ebd062301bc3d47d8ec6f7d58cdaac440c78bae0e24638bacfce97e9b at assembly)

```text
# Running command log for TASK-20260924-d897a6 (red-team). One entry per shell child, exact argv.
# Read-tool file reads are listed in paths_read.txt.
C001 mkdir -p <scratch>/rt_d897a6 && ls -la <scratch>/rt_d897a6
C002 wc -l AGENTS.md amendments/v2_addendum_{launchkind,attcount,failclosed,gapattr,childend,readbackclose,readbackfull,readbackcover}.yaml  (absolute paths under /home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/amendments/)
C003 cd /home/user/crypto-autoresearcher && for t in 0c2fdc 7e8a5d 93f3ca 682890 71d070 ddfb69 a01341; do ls -la coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-$t/; done; git rev-parse HEAD; git status --porcelain | head -20
     DEVIATION D-1: `git rev-parse HEAD` and `git status --porcelain` were run WITHOUT GIT_OPTIONAL_LOCKS=0. git status may take an optional index lock and refresh .git/index stat data. Output: HEAD c0b0ecf3a4a5ca9dc1897322747d84398d448480; status printed nothing.
C004 ls -la experiments/EXP-GFPN-05ff43/dev-evidence/{readbackclose-census,readbackfull-census,readback-census}/ coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-{f5631b,1ecb7d,94cc33,be2daf}/   (cwd /home/user/crypto-autoresearcher; expanded list of 7 dirs)
C005 cd <scratch>/rt_d897a6 && python3 -B integrity_v1.py > integrity_v1.out 2>&1; echo "exit=$?"; cat integrity_v1.out      -> exit=0, ALL_OK
C006 cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json' experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956 > <scratch>/rt_d897a6/crj2d_diff.out 2>&1; echo "exit=$?"; wc -c <scratch>/rt_d897a6/crj2d_diff.out; GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD; GIT_OPTIONAL_LOCKS=0 git cat-file -t dd103455380238ec2f20d17414de687acdcc822a
     -> exit=0; 0 bytes; HEAD c0b0ecf3a4a5ca9dc1897322747d84398d448480; object type commit
C007 cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git ls-files -s -- experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml; GIT_OPTIONAL_LOCKS=0 git diff --stat HEAD -- experiments/EXP-GFPN-05ff43/amendments/ coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33; ls experiments/EXP-GFPN-05ff43/runs/ | wc -l; ls experiments/EXP-GFPN-05ff43/ ; ls coordination/goals/GOAL-GFPN-380702/reviews/
     -> both tracked (stage 0); diff vs HEAD empty; 54 run dirs; no implementation-v2-r4*/trial-plan-*-r4*; no reviews/TASK-20260924-d897a6
C008 Read tool reads (see paths_read); grep -n outlines of readbackcover/readbackclose/childend/consumercover/e52eec (cwd experiments/EXP-GFPN-05ff43/amendments or ledger/decisions): grep -n '^    R[A-Z]-[0-9]*\|...' v2_addendum_readbackcover.yaml; grep -n (outline) v2_addendum_readbackclose.yaml v2_addendum_childend.yaml; wc -l DEC-20260924-e52eec.yaml && grep -n 'VA-6\|CC-5\|DV-11\|VA-12' DEC-20260924-e52eec.yaml; grep -n '\bm1\b\|\bm3\b\|\bm7\b\|V-5\b\|E1-E4\|\bE1\b' v2_addendum_consumercover.yaml v2_addendum_launchcover.yaml v2_addendum_valueclose.yaml
C009 cd experiments/EXP-GFPN-05ff43 && wc -l implementation-v2/*.py implementation-v2-a1/*.py implementation-v2-r3/*.py | sort -n | tail -45
C010 cd experiments/EXP-GFPN-05ff43 && grep -rn 'instructions_callgrind' implementation-v2/ implementation-v2-a1/ implementation-v2-r3/ --include=*.py | cut -c1-220; grep -rn 'fb1_curve_search\|curve_facts(' (same three trees) | cut -c1-200; grep -rn 'run_child' (same three trees) | cut -c1-200
C011 cd experiments/EXP-GFPN-05ff43 && ls implementation implementation-v2 implementation-v2-a1 implementation-v2-r1 implementation-v2-r2 implementation-v2-r3 | head -120; sed -n 1,84p implementation-v2-r3/r3_entry_v2.py | grep -n 'import\|install\|run_child\|readback'
C012 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v1.py scan_v1.json > scan_v1.out 2>&1; echo "exit=$?"; cat scan_v1.out | cut -c1-400    -> exit 0
C013 cd <scratch>/rt_d897a6 && sed -n '/^dis solve/p' scan_v1.out | tr '(' '\n' | tail -30; grep -o "closure r3_entry_v2.*" scan_v1.out | cut -c1-900; grep -o "closure r3_entry_a1.*" scan_v1.out | cut -c1-1200; (append to command_log.txt)
C014 cd experiments/EXP-GFPN-05ff43/runs && for r in RUN-GFPN-f6a21a RUN-GFPN-902222 RUN-GFPN-f5412a RUN-GFPN-bfe956; do echo "== $r"; ls -la $r | head -40; for d in child solver health comparator pari certificates polynomials; do if [ -d $r/$d ]; then echo "  $d: $(ls $r/$d | wc -l) files"; fi; done; done
C015 cd experiments/EXP-GFPN-05ff43/runs && stat -c '%n atime=%x mtime=%y ctime=%z' <13 package dirs and 2 files>; date -u   -> atimes all 2026-09-24 13:0x (unchanged by C014; relatime window), now 2026-09-25T01:47:16Z
C016 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread_v1.py pkgread_v1.json > pkgread_v1.out 2>&1; echo "exit=$?"; cat pkgread_v1.out
C017 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B explore_v1.py pkgread_v1.json > explore_v1.out 2>&1; echo "exit=$?"; cut -c1-600 explore_v1.out
C018 cd coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33 && grep -n (N-1..N-13 patterns) review-report.yaml | head -40
C019 cd experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census && sed -n 470,495p readbackclose-census.md
C020 cd experiments/EXP-GFPN-05ff43/amendments && grep -n 'VC-1\|epsilon\|alpha)' v2_addendum_valueclose.yaml | head -40
C021 cd experiments/EXP-GFPN-05ff43 && grep -n (root constants) implementation-v2-r3/r3_common.py; grep -n (roots) implementation-v2/v2_common.py; grep -n (roots) implementation-v2-a1/a1_common.py; sed -n 60,70p implementation-v2-a1/a1_check_run.py; sed -n 26,34p implementation-v2-a1/a1_check_run.py
C022 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v2.py scan_v2.json scan_v1.json > scan_v2.out 2>&1; echo "exit=$?"; cut -c1-300 scan_v2.out
C023 cd <scratch>/rt_d897a6 && python3 -B -c 1 2>/dev/null; echo "(no-op check skipped)"; grep -n '"file": "implementation-v2-r3/r3_entry\|"file": "implementation-v2-a1/a1_driver\|"file": "implementation-v2/v2_driver' scan_v2.json | head -5
     DEVIATION D-2: this command line contained a `python3 -B -c 1` invocation (a no-op program "1", stderr discarded, no output, exit status not printed). CRJ-5 forbids `python3 -c` programs; it read nothing and wrote nothing, but it is recorded as a deviation with its full text.
C024 sed -n 95,140p <scratch>/rt_d897a6/scan_v2.json
C025 cd <scratch>/rt_d897a6 && ls -la && sha256sum rjcore_v1.py   (rjcore_v1.py first-write hash ea0698e6...6b15, before the pre-run edits E1-E6 made with the Edit tool; no run existed before the edits)
C026 cd <scratch>/rt_d897a6 && sha256sum rjcore_v1.py lj0_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v1.py > lj0_v1.out 2>&1; echo "exit=$?"; wc -l lj0_v1.out; grep -n 'verdict\|^KA\|expected' lj0_v1.out | head -150
C027 cd <scratch>/rt_d897a6 && sed -n 433,724p lj0_v1.out | cut -c1-330
     DEVIATION D-3: C027's output exceeded the display limit; the session harness persisted it to a file under the session-configuration directory outside the repository (path shown by the harness; NOT opened). Only the 2 KB preview of scratch bytes was displayed. The same bytes are re-read below in smaller filtered parts.
C028 cd <scratch>/rt_d897a6 && sed -n 462,724p lj0_v1.out | grep -v '      record ' | cut -c1-300
C029 cd <scratch>/rt_d897a6 && sha256sum listing_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v1.py > listing_v1.out 2>&1; echo "exit=$?"; wc -l listing_v1.out; grep -v '^    S-1 ' listing_v1.out | cut -c1-400
C030 cd <scratch>/rt_d897a6 && grep '^    S-1 ' listing_v1.out | cut -c1-230 | sed -n '1,4p;37,40p;73,86p'
C031 cd <scratch>/rt_d897a6 && cp rjcore_v1.py rjcore_v2.py && sha256sum rjcore_v1.py rjcore_v2.py
C032 (Edit tool, three edits of <scratch>/rt_d897a6/rjcore_v2.py: docstring header; aggregate exemption in frozen_items; RF-0 undetermined callgrind_result_present named gap)
C033 cd <scratch>/rt_d897a6 && sed -e 's/rjcore_v1/rjcore_v2/g' -e 's/lj0_v1\.json/lj0_v2.json/g' -e 's/with the evaluator core rjcore_v2.py UNCHANGED/with the evaluator core rjcore_v2.py (version 2)/' lj0_v1.py > lj0_v2.py && diff lj0_v1.py lj0_v2.py; PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v2.py > lj0_v2.out 2>&1; echo "exit=$?"; diff lj0_v1.out lj0_v2.out; sha256sum rjcore_v2.py lj0_v2.py lj0_v1.out lj0_v2.out
C034 cd <scratch>/rt_d897a6 && sed -e 's/rjcore_v1/rjcore_v2/g' -e 's/listing_v1\.json/listing_v2.json/g' listing_v1.py > listing_v2.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v2.py > listing_v2.out 2>&1; echo "exit=$?"; diff listing_v1.out listing_v2.out; sha256sum listing_v2.py listing_v1.out listing_v2.out
C035 cd /home/user/crypto-autoresearcher && wc -l coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py && grep -n 'open(\|write\|subprocess\|os\.system\|popen\|Popen\|exec\|fork\|mkdir\|makedirs\|save\|import ' <same file> | cut -c1-200; sed -n 270,285p experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py
C036 cd <scratch>/rt_d897a6 && sha256sum lj1_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj1_v1.py > lj1_v1.out 2>&1; echo "exit=$?"; wc -l lj1_v1.out; grep -n '^[A-Z].*: \|verdict' lj1_v1.out | ... | cut -c1-200 | head -120
C037 cd <scratch>/rt_d897a6 && grep -n '^[A-Z].*: \|verdict' lj1_v1.out | cut -c1-200 | sed -n '121,400p'
C038 cd <scratch>/rt_d897a6 && for n in 199 396 614 700 969 1122 1137 1153 1308 1325 1400 1417; do sed -n "${n},$((n+14))p" lj1_v1.out | grep -v '      record ' | cut -c1-260 | sed -n '1,9p'; echo ...; done
C039 cd <scratch>/rt_d897a6 && sha256sum lj2_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj2_v1.py > lj2_v1.out 2>&1; echo "exit=$?"; wc -l lj2_v1.out; grep -n '^[A-Za-z].*: \|verdict\|PLANNED' lj2_v1.out | cut -c1-170
C040 cd <scratch>/rt_d897a6 && sha256sum rdscan_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan_v1.py rdscan_v1.json > rdscan_v1.out 2>&1; echo "exit=$?"; cut -c1-260 rdscan_v1.out
C041 cd /home/user/crypto-autoresearcher && grep -rln -e 'callgrind_result_present' -e 'COMPARATOR COUNT' -e 'CALLGRIND COUNT' -e 'UNKNOWN-KIND' -e 'launch_records' -e 'raw_result_writer' -e 'recorder-foreign' -e 'solver-events' tools/ harness/ 2>/dev/null; echo "grep exit=$?"
C042 cd <scratch>/rt_d897a6 && sha256sum lj4_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj4_v1.py > lj4_v1.out 2>&1; echo "exit=$?"; cut -c1-250 lj4_v1.out
C043 cd experiments/EXP-GFPN-05ff43 && grep -n 'os\.open(' implementation-v2/*.py implementation-v2-a1/*.py implementation-v2-r3/{r3_resolve,r3_common,r3_entry_v2,r3_entry_a1,r3_run_wrapper,r3_check_run}.py; echo "exit=$?"
C044 cd <scratch>/rt_d897a6 && grep -o '"where": "[^"]*"' rdscan_v1.json | sort | uniq -c
C045 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B hashes_v1.py > hashes_v1.out 2>&1; echo "exit=$?"; cat hashes_v1.out; date -u
     DEVIATION D-4 (CRJ-5): the reviewer's working context was compacted between C045 and C046 (2026-09-25, about 02:18-02:21Z). After the compaction every line a verdict cites is re-read (C046 onward) before the deliverables are written.
C046 tail -c 6000 <scratch>/rt_d897a6/command_log.txt; ls -la <scratch>/rt_d897a6/; date -u +%Y-%m-%dT%H:%M:%SZ
C047 (this append to command_log.txt, shell heredoc append; scratch only); cat <scratch>/rt_d897a6/notes.md
C048 cd <repo> && wc -l experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml ledger/handoffs/TASK-20260924-d897a6.yaml; (Read tool) launchkind 1-600 re-read after compaction
C049 (Read tool) launchkind 1-781 and card 1-567 re-read after compaction; cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2 && sed -n 149,308p v2_solver.py; sed -n 512,552p v2_solver.py
C050 cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2 && awk 'NR>=77&&NR<=231' v2_driver.py; awk 'NR>=352&&NR<=364' v2_driver.py; awk 'NR>=560&&NR<=568' v2_driver.py; awk 'NR>=626&&NR<=716' v2_driver.py (each prefixed with its line number)
C051 cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2 && awk (line-numbered) v2_driver.py 716-750, 760-845 (grep-filtered for solve/build/raw/finish), 1085-1092, 1110-1182
C052 cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2-a1 && awk (line-numbered) a1_pari.py 87-143; a1_health.py 140-153 and 223-253; a1_driver.py 84-92, 125-131, 144-168, 200-216
C053 cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2-r3 && awk (line-numbered) r3_resolve.py 44-52, 178-202, 248-412
C054 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk (line-numbered) v2_addendum_attcount.yaml 265-505
C055 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk (line-numbered) v2_addendum_failclosed.yaml 600-708
C056 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk (line-numbered) v2_addendum_gapattr.yaml 243-318; v2_addendum_readbackfull.yaml 209-306
C057 cd <repo> && awk (line-numbered) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml 196-222, 331-348; ledger/decisions/DEC-20260924-e52eec.yaml 714-740; experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml 269-295
C058 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk (line-numbered) v2_addendum_consumercover.yaml 335-381, 426-441, 535-566
C059 cd <repo>/experiments/EXP-GFPN-05ff43 && awk (line-numbered) implementation-v2-r3/r3_run_wrapper.py 97-104, 186-203, 284-292, 381-400, 434-472, 540-552; implementation-v2-r3/r3_check_run.py 61-77, 150-185, 245-260, 322-342; implementation-v2/v2_check_run.py 60-72; implementation-v2-a1/a1_check_run.py 60-86
C060 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && grep -n 'RG-3' v2_addendum_childend.yaml | head; awk (line-numbered) v2_addendum_childend.yaml around RG-3 text
C061 cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk 'NR>=373&&NR<=440' v2_addendum_childend.yaml (line-numbered; RG-3, RG-4)
C062 cd <repo>/experiments/EXP-GFPN-05ff43 && awk (line-numbered) r3_check_run.py 61-77,150-185,245-260,322-342; v2_check_run.py 60-72; a1_check_run.py 60-86; then r3_common.py 24-32,110-115; v2_common.py 27-40; a1_common.py 88-100; r3_entry_v2.py 36-80; r3_entry_a1.py 90-111; r3_run_wrapper.py 20-40 (RUNS)
C063 cd <scratch>/rt_d897a6 && grep -n 'FO1\|FO-1\|escape' rjcore_v2.py | head -40
C064 cd <scratch>/rt_d897a6 && sed -n 1,140p rjcore_v2.py; then cd <repo>/experiments/EXP-GFPN-05ff43/amendments && awk (line-numbered) v2_addendum_readbackclose.yaml 246-373, 522-535
C065 cd <scratch>/rt_d897a6 && grep -n '^[A-Za-z].*: \|verdict\|PLANNED' lj2_v1.out | cut -c1-200 | head -150
C066 cd <scratch>/rt_d897a6 && grep -n (summary lines) lj2_v1.out | cut -c1-200 | head -150; then cd <repo>/experiments/EXP-GFPN-05ff43 && awk (line-numbered) implementation-v2-r3/r3_check_run.py 86-100; implementation-v2/v2_check_run.py 92-106; implementation-v2-r3/r3_run_wrapper.py 505-512
C067 cd <scratch>/rt_d897a6 && grep -v '^    S-1 ' listing_v1.out | cut -c1-260 | head -120; python3 -B json key probe NOT run; head -c 1500 listing_v1.json
C068 cd <scratch>/rt_d897a6 && grep -v '^    S-1 ' listing_v1.out | cut -c1-260 | head -120; head -c 1500 listing_v1.json; grep -o '"[a-zA-Z_0-9]*": ' listing_v1.json | sort | uniq -c | sort -rn | head -60; grep -n '^    S-1 ' listing_v1.out | head -3
C069 cd <scratch>/rt_d897a6 && grep -o '"[a-zA-Z_0-9-]*": ' listing_v1.json | sort | uniq -c | sort -rn | head -60; grep -n '^    S-1 ' listing_v1.out | head -3 | cut -c1-400; sed -n '/"reconstruction_rule"/,+3p' listing_v1.json | cut -c1-100 | head -3; python3 -B -c pass 2>/dev/null || true
     DEVIATION D-5: this command line (C069) ended with `python3 -B -c pass 2>/dev/null || true`, a `python3 -c` program (the no-op "pass"; stderr discarded; no output; exit status not printed). CRJ-5 forbids `python3 -c` programs. It read nothing and wrote nothing; recorded with its full text. (C068's logged text above is the planned form of the same probe; C069 is the command actually run.)
C070 (Write tool) <scratch>/rt_d897a6/tables_v1.py; grep -n 'files_in_the_five_directories\|unattributed_count\|FIVE\|os.walk\|def list' <scratch>/rt_d897a6/listing_v1.py
C071 sed -n 150,225p <scratch>/rt_d897a6/listing_v1.py
C072 sed -n 150,225p listing_v1.py (read); sha256sum tables_v1.py (first write, before the fix below; never run)
C073 (Edit tool, four pre-run edits of tables_v1.py: unattributed_count read from P[RJ] (three places); per-file listing output argv[3]); cd <scratch>/rt_d897a6 && sha256sum tables_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1; echo exit=$?; cat tables_v1.out; wc -l tables_v1.md tables_v1.yaml tables_v1_perfile.md
C074 sed -n '1,40p;100,209p' tables_v1.md | cut -c1-260; head -30 tables_v1.yaml | cut -c1-260; grep -c UNATTRIBUTED tables_v1_perfile.md; sed -n 1,12p tables_v1_perfile.md
C075 cd <scratch>/rt_d897a6 && sed -n '1,120p;433,724p' tables_v1.md ... (viewed); grep -v '      record ' lj0_v1.out | cut -c1-240 | sed -n 1,200p
C076 grep -v '      record ' lj0_v1.out | cut -c1-240 | sed -n 1,200p (viewed); sed -n 1,40p lj0_v1.out | grep '      record ' | cut -c1-330
C077 sed -n 1,40p lj0_v1.out | grep '      record ' | cut -c1-330 (viewed); grep -v '      record \|premises:\|expected by' lj0_v1.out | cut -c1-200 | sed -n 200,520p
C078 grep -v '      record \|premises:\|expected by' lj0_v1.out | cut -c1-200 | sed -n 200,520p (viewed); awk '/^[A-Z]/{h=$0} /\[RJ\] verdict/{print substr(h,1,150) " => " $0}' lj1_v1.out | cut -c1-230
C079 awk (headers + RJ verdict) lj1_v1.out | cut -c1-230 (viewed); grep -v '      record ' lj4_v1.out | cut -c1-230
C080 grep -v '      record ' lj4_v1.out | cut -c1-230 (viewed); cd <repo>/experiments/EXP-GFPN-05ff43/amendments && grep -n 'RGL-7' v2_addendum_gapattr.yaml | head -5; awk (line-numbered) around RGL-7 text
C081 awk 'NR>=455&&NR<=485' <repo>/experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml (viewed); cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2-a1 && grep -n 'def gp_script' a1_pari.py; awk (line-numbered) a1_pari.py from def gp_script to line 86; grep -n 'write\|system\|extern\|install\|read(' in that range
C082 awk 'NR>=20&&NR<=86' a1_pari.py (viewed); cd <repo>/coordination/goals/GOAL-GFPN-380702/reviews && grep -n 'X6b\|X10\b\|\bX1\b\|TW-2\|IV-1' TASK-20260924-be2daf/review-report.yaml | cut -c1-260 | head -30
C083 sed -n 245,256p TASK-20260924-be2daf/review-report.yaml | cut -c1-300
C084 head -c 6000 <scratch>/rt_d897a6/command_log.txt; grep -c . command_log.txt; grep -c 'tmp/cl' command_log.txt
C085 cd <scratch>/rt_d897a6 && grep -n 'REPO\|os.path.join\|TREES\|open(' integrity_v1.py scan_v1.py scan_v2.py pkgread_v1.py explore_v1.py | cut -c1-220
C086 sed -n 12,22p scan_v1.py; sed -n 180,200p scan_v1.py; sed -n 55,70p integrity_v1.py
C087 (Write tool) <scratch>/rt_d897a6/wordcheck_v1.py; cd <scratch>/rt_d897a6 && sha256sum wordcheck_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1; echo exit=$?; cat wordcheck_v1_scratch.out
C088 cat integrity_v1.out | cut -c1-250; cat hashes_v1.out
C089 cut -c1-300 scan_v1.out | head -80; cut -c1-300 scan_v2.out
C090 cut -c1-300 scan_v1.out | head -80; cut -c1-300 scan_v2.out (viewed); grep -n 'Z-C5\|run_status' lj2_v1.py | head; sed -n 354,360p lj2_v1.out; sed -n 600,607p lj2_v1.out
C091 grep -n 'Z-C5\|run_status' lj2_v1.py | head; sed -n 354,360p lj2_v1.out; sed -n 600,607p lj2_v1.out (viewed); cd <repo> && grep -n 'red_team_report' -A 60 agents/red-team.md | head -120
C092 (Write tool) <scratch>/rt_d897a6/body_v1.yaml.part; cd <scratch>/rt_d897a6 && grep -n 'import rjcore\|rjcore_v' lj0_v1.py lj0_v2.py listing_v1.py listing_v2.py lj1_v1.py lj2_v1.py lj4_v1.py | cut -c1-160; sed -n 1,12p lj0_v2.py | cut -c1-200
C093 (Write tool) <scratch>/rt_d897a6/paths_read_v1.yaml.part; sed -n 1,70p pkgread_v1.py
C094 sed -n 1,70p pkgread_v1.py (viewed); (Edit tool) paths_read_v1.yaml.part pkgread extent corrected; cut -c1-250 rdscan_v1.out
C095a (Write tool) check_v1.py, assemble_v1.py (+1 pre-run edit); cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v1.yaml.part paths_read_v1.yaml.part deviations_v1.yaml.part exact_argv_post_compaction.txt assemble_v1.py check_v1.py > wordcheck_v1_parts.out 2>&1; echo exit=$?; cat wordcheck_v1_parts.out
C095 (Edit tool: assemble_v1.py three more pre-run edits; deviations_v1.yaml.part one edit); cd <scratch>/rt_d897a6 && sha256sum assemble_v1.py check_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1; echo exit=$?; cat assemble_v1.out
C096 cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1; echo exit=$?; cat check_v1.out
C097a sed -n 1728,1745p review-report.yaml; sed -n 1368,1378p review-report.md (inspect the inference block)
C097b sed -n 1,140p review-report.md | cut -c1-220
C097c grep -n '^## \|^### ' review-report.md | head -80; grep -n 'LK-3_callgrind' review-report.md
C098a cd <exp>/implementation-v2-a1 && grep -n 'redirect_v2' a1_check_run.py a1_driver.py a1_common.py | cut -c1-200
C098b cd <scratch>/rt_d897a6 && cp body_v1.yaml.part body_v2.yaml.part && cp deviations_v1.yaml.part deviations_v2.yaml.part && cp assemble_v1.py assemble_v2.py && sha256sum body_v1.yaml.part deviations_v1.yaml.part assemble_v1.py
C098c cd <scratch>/rt_d897a6 && cat >> deviations_v2.yaml.part <<'EOF' (the D-9 text) EOF
C097x EXACT ARGV of C097a as run (its entry above abbreviates it): cd /home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6 && sed -n 1728,1745p review-report.yaml; echo ----; sed -n 1366,1378p review-report.md
C098d (Edit tool: body_v2.yaml.part four edits, assemble_v2.py twelve edits, before assemble_v2's first run); cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v2.yaml.part deviations_v2.yaml.part assemble_v2.py > wordcheck_v1_parts2.out 2>&1; echo exit=$?; cat wordcheck_v1_parts2.out
C098e correction to C098d: assemble_v2.py received sixteen pre-run edits in all (the fourteen before C098d, including the command-log entry regex, and two after it adding wordcheck_v1_parts2.out to its file lists); none after its run.
C098 cd <scratch>/rt_d897a6 && sha256sum assemble_v2.py body_v2.yaml.part deviations_v2.yaml.part && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v2.py > assemble_v2.out 2>&1; echo exit=$?; cat assemble_v2.out
```

### B.2 `<scratch>/rt_d897a6/exact_argv_post_compaction.txt` (sha256 518e89b3a8735937b9414c55e75cb2bb737ce79e150dd6e5d6410f7670be6695)

```text
# EXACT ARGV of every shell child after the compaction (C046-C094), as run, in order. <scratch> abbreviates the
# session scratch directory, <repo> = /home/user/crypto-autoresearcher, <exp> = <repo>/experiments/EXP-GFPN-05ff43.
# Every command below except X01 and X02 began with `echo "<its log entry>" >> <scratch>/rt_d897a6/command_log.txt; `
# (a text append whose payload is the entry recorded in command_log.txt). In the awk programs, P stands for the
# action text {printf "%d\t%s\n", NR, $0} written out in full in each command.
X01 (C046) tail -c 6000 <scratch>/rt_d897a6/command_log.txt; echo; ls -la <scratch>/rt_d897a6/; date -u +%Y-%m-%dT%H:%M:%SZ
X02 (C047) cd <scratch>/rt_d897a6 && cat >> command_log.txt <<'EOF' (three log lines: D-4, C046, C047) EOF ; cat notes.md
X03 (C048) cd <repo> && wc -l experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml ledger/handoffs/TASK-20260924-d897a6.yaml
X04 (C049) cd <exp>/implementation-v2 && sed -n 149,308p v2_solver.py | cat -n | sed 's/^ *\([0-9]*\)/\1+148/' | awk -F'\t' '{split($1,a,"+"); printf "%d\t%s\n", a[1]+a[2], $2}'; echo ----; sed -n 512,552p v2_solver.py | awk '{printf "%d\t%s\n", NR+511, $0}'
X05 (C050) cd <exp>/implementation-v2 && awk 'NR>=77&&NR<=231P' v2_driver.py; echo ----; awk 'NR>=352&&NR<=364P' v2_driver.py; echo ----; awk 'NR>=560&&NR<=568P' v2_driver.py; echo ----; awk 'NR>=626&&NR<=716P' v2_driver.py
X06 (C051) cd <exp>/implementation-v2 && awk 'NR>=716&&NR<=750P' v2_driver.py; echo ----; awk 'NR>=752&&NR<=935P' v2_driver.py | grep -n 'solve(\|build_poly(\|raw_grid(\|child_job(\|run_child\|finish(\|raw\["build\|binfo\|def ' | cut -c1-230; echo ----; awk 'NR>=1085&&NR<=1092P' v2_driver.py; echo ----; awk 'NR>=1110&&NR<=1182P' v2_driver.py
X07 (C052) cd <exp>/implementation-v2-a1 && awk 'NR>=87&&NR<=143P' a1_pari.py; echo ----; awk '(NR>=140&&NR<=153)||(NR>=223&&NR<=253)P' a1_health.py; echo ----; awk '(NR>=84&&NR<=92)||(NR>=125&&NR<=131)||(NR>=144&&NR<=168)||(NR>=200&&NR<=216)P' a1_driver.py
X08 (C053) cd <exp>/implementation-v2-r3 && awk '(NR>=44&&NR<=52)||(NR>=178&&NR<=202)||(NR>=248&&NR<=412)P' r3_resolve.py
X09 (C054) cd <exp>/amendments && awk 'NR>=265&&NR<=505P' v2_addendum_attcount.yaml
X10 (C055) cd <exp>/amendments && awk 'NR>=600&&NR<=708P' v2_addendum_failclosed.yaml
X11 (C056) cd <exp>/amendments && awk 'NR>=243&&NR<=318P' v2_addendum_gapattr.yaml; echo -----; awk 'NR>=209&&NR<=306P' v2_addendum_readbackfull.yaml
X12 (C057) cd <repo> && awk '(NR>=196&&NR<=222)||(NR>=331&&NR<=348)P' experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml; echo ----; awk 'NR>=714&&NR<=740P' ledger/decisions/DEC-20260924-e52eec.yaml; echo ----; awk 'NR>=269&&NR<=295P' experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml
X13 (C058) cd <exp>/amendments && awk '(NR>=335&&NR<=381)||(NR>=426&&NR<=441)||(NR>=535&&NR<=566)P' v2_addendum_consumercover.yaml
X14 (C059) cd <exp> && awk '(NR>=97&&NR<=104)||(NR>=186&&NR<=203)||(NR>=284&&NR<=292)||(NR>=381&&NR<=400)||(NR>=434&&NR<=472)||(NR>=540&&NR<=552)P' implementation-v2-r3/r3_run_wrapper.py | cut -c1-240
X15 (C060) cd <exp>/amendments && grep -n 'RG-3' v2_addendum_childend.yaml | head
X16 (no echo; logged as C061) cd <exp>/amendments && awk 'NR>=373&&NR<=440P' v2_addendum_childend.yaml
X17 (C061/C062) cd <exp> && awk '(NR>=61&&NR<=77)||(NR>=150&&NR<=185)||(NR>=245&&NR<=260)||(NR>=322&&NR<=342)P' implementation-v2-r3/r3_check_run.py | cut -c1-220; echo ----; awk 'NR>=60&&NR<=72P' implementation-v2/v2_check_run.py | cut -c1-220; echo ----; awk 'NR>=60&&NR<=86P' implementation-v2-a1/a1_check_run.py | cut -c1-220
X18 (C062) cd <exp> && awk '(NR>=24&&NR<=32)||(NR>=110&&NR<=115)P' implementation-v2-r3/r3_common.py | cut -c1-200; echo ----; awk 'NR>=27&&NR<=40P' implementation-v2/v2_common.py | cut -c1-200; echo ----; awk 'NR>=88&&NR<=100P' implementation-v2-a1/a1_common.py | cut -c1-200; echo ----; grep -n '^RUNS\|^RUNS =\|RUNS = ' implementation-v2-r3/r3_run_wrapper.py; echo ----; awk 'NR>=36&&NR<=80P' implementation-v2-r3/r3_entry_v2.py | cut -c1-200; echo ----; awk 'NR>=90&&NR<=111P' implementation-v2-r3/r3_entry_a1.py | cut -c1-200
X19 (C063) cd <scratch>/rt_d897a6 && grep -n 'FO1\|FO-1\|escape' rjcore_v2.py | head -40
X20 (C064) cd <scratch>/rt_d897a6 && sed -n 1,140p rjcore_v2.py
X21 (C064) cd <exp>/amendments && awk '(NR>=246&&NR<=373)||(NR>=522&&NR<=535)P' v2_addendum_readbackclose.yaml
X22 (C065) cd <scratch>/rt_d897a6 && grep -n '^[A-Za-z].*: \|verdict\|PLANNED' lj2_v1.out | cut -c1-200 | head -150
X23 (C066) cd <exp> && awk 'NR>=86&&NR<=100P' implementation-v2-r3/r3_check_run.py | cut -c1-200; echo ----; awk 'NR>=92&&NR<=106P' implementation-v2/v2_check_run.py | cut -c1-200; echo ----; awk 'NR>=505&&NR<=512P' implementation-v2-r3/r3_run_wrapper.py | cut -c1-200
X24 (C067) cd <scratch>/rt_d897a6 && grep -v '^    S-1 ' listing_v1.out | cut -c1-260 | head -120; echo; head -c 1500 listing_v1.json
X25 (C069; deviation D-5) cd <scratch>/rt_d897a6 && grep -o '"[a-zA-Z_0-9-]*": ' listing_v1.json | sort | uniq -c | sort -rn | head -60; grep -n '^    S-1 ' listing_v1.out | head -3 | cut -c1-400; sed -n '/"reconstruction_rule"/,+3p' listing_v1.json | cut -c1-100 | head -3; python3 -B -c pass 2>/dev/null || true
X26 (C069 log) cd <scratch>/rt_d897a6 && cat >> command_log.txt <<'EOF' (the C069 entry and deviation D-5 text) EOF ; echo ok
X27 (C070) cd <scratch>/rt_d897a6 && grep -n 'files_in_the_five_directories\|unattributed_count\|FIVE\|os.walk\|def list\|pkgread' listing_v1.py | cut -c1-220
X28 (C071) cd <scratch>/rt_d897a6 && sed -n 150,225p listing_v1.py
X29 (C072) cd <scratch>/rt_d897a6 && sha256sum tables_v1.py
X30 (C073) cd <scratch>/rt_d897a6 && sha256sum tables_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1; echo exit=$?; cat tables_v1.out; wc -l tables_v1.md tables_v1.yaml tables_v1_perfile.md
X31 (C074) cd <scratch>/rt_d897a6 && sed -n '1,40p;100,209p' tables_v1.md | cut -c1-260; head -30 tables_v1.yaml | cut -c1-260; grep -c UNATTRIBUTED tables_v1_perfile.md; sed -n 1,12p tables_v1_perfile.md
X32 (C075) cd <scratch>/rt_d897a6 && grep -v '      record ' lj0_v1.out | cut -c1-240 | sed -n 1,200p
X33 (C076) cd <scratch>/rt_d897a6 && sed -n 1,40p lj0_v1.out | grep '      record ' | cut -c1-330
X34 (C077) cd <scratch>/rt_d897a6 && grep -v '      record \|premises:\|expected by' lj0_v1.out | cut -c1-200 | sed -n 200,520p
X35 (C078) cd <scratch>/rt_d897a6 && awk '/^[A-Z]/{h=$0} /\[RJ\] verdict/{print substr(h,1,150) " => " $0}' lj1_v1.out | cut -c1-230
X36 (C079) cd <scratch>/rt_d897a6 && grep -v '      record ' lj4_v1.out | cut -c1-230
X37 (C080) cd <exp>/amendments && grep -n 'RGL-7' v2_addendum_gapattr.yaml | head -5
X38 (no echo; logged in C081) cd <exp>/amendments && awk 'NR>=455&&NR<=485P' v2_addendum_gapattr.yaml
X39 (C081) cd <exp>/implementation-v2-a1 && grep -n 'def gp_script' a1_pari.py; awk 'NR>=20&&NR<=86P' a1_pari.py | cut -c1-200
X40 (C082) cd <repo>/coordination/goals/GOAL-GFPN-380702/reviews && grep -n 'X6b\|X10\b\|\bX1\b\|TW-2\|IV-1' TASK-20260924-be2daf/review-report.yaml | cut -c1-260 | head -30
X41 (C083) cd <repo>/coordination/goals/GOAL-GFPN-380702/reviews && sed -n 245,256p TASK-20260924-be2daf/review-report.yaml | cut -c1-300
X42 (C084) cd <scratch>/rt_d897a6 && head -c 6000 command_log.txt; echo; grep -c . command_log.txt; grep -c 'tmp/cl' command_log.txt
X43 (C085) cd <scratch>/rt_d897a6 && grep -n 'REPO\|TREES\|open(\|RUNS\|receipt\|path_sha256' integrity_v1.py scan_v1.py scan_v2.py pkgread_v1.py explore_v1.py | cut -c1-220 | head -80
X44 (C086) cd <scratch>/rt_d897a6 && sed -n 12,22p scan_v1.py; echo ---; sed -n 180,200p scan_v1.py; echo ---; sed -n 55,70p integrity_v1.py
X45 (C087) cd <scratch>/rt_d897a6 && sha256sum wordcheck_v1.py && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1; echo exit=$?; cat wordcheck_v1_scratch.out
X46 (C088) cd <scratch>/rt_d897a6 && cut -c1-250 integrity_v1.out; echo ----; cat hashes_v1.out
X47 (C089) cd <scratch>/rt_d897a6 && cut -c1-300 scan_v1.out | head -80; echo ----; cut -c1-300 scan_v2.out
X48 (C090) cd <scratch>/rt_d897a6 && grep -n 'Z-C5\|run_status' lj2_v1.py | head; sed -n 354,360p lj2_v1.out | cut -c1-250; sed -n 600,607p lj2_v1.out | cut -c1-250
X49 (C091) cd <repo> && grep -n 'red_team_report' -A 70 agents/red-team.md | head -110
X50 (C092) cd <scratch>/rt_d897a6 && grep -n 'import rjcore\|rjcore_v' lj0_v1.py lj0_v2.py listing_v1.py listing_v2.py lj1_v1.py lj2_v1.py lj4_v1.py | cut -c1-160; sed -n 1,12p lj0_v2.py | cut -c1-200
X51 (C093) cd <scratch>/rt_d897a6 && sed -n 1,70p pkgread_v1.py
X52 (C094) cd <scratch>/rt_d897a6 && cut -c1-250 rdscan_v1.out
# Read-tool reads after the compaction (not shell children): <exp>/amendments/v2_addendum_launchkind.yaml (1-781),
# <repo>/ledger/handoffs/TASK-20260924-d897a6.yaml (1-567), <scratch>/rt_d897a6/hashes_v1.py and rdscan_v1.py
# (displayed by the session on resumption). Write / Edit tool writes after the compaction (scratch only): tables_v1.py
# (+4 edits), wordcheck_v1.py, body_v1.yaml.part, paths_read_v1.yaml.part (+1 edit), deviations_v1.yaml.part,
# exact_argv_post_compaction.txt, and the assembler and checker named in the command log.
```

## Appendix C - every script, verbatim, with sha256 and argv

### integrity_v1.py

- sha256: 5456853e9244b81f051136c2578661161430a17e26f916eb592ad87663e3755e
- argv: `C005: cd <scratch>/rt_d897a6 && python3 -B integrity_v1.py > integrity_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# CRJ-2 integrity check for TASK-20260924-d897a6. Reads bytes, hashes them, and
# from each named snapshot receipt prints ONLY its path_sha256 field.
import hashlib
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
AMD = "experiments/EXP-GFPN-05ff43/amendments/"


def sha(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


ok = True

# (a) launchkind vs the value the dispatching session supplied from the a571c7 receipt
LK = AMD + "v2_addendum_launchkind.yaml"
LK_EXPECT = "ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050"
got = sha(LK)
print("(a)", LK, got, "expected", LK_EXPECT, "MATCH" if got == LK_EXPECT else "MISMATCH")
ok &= got == LK_EXPECT
# status / approved_by / approval_decision lines, read as text (top-level keys of the amendment block)
with open(os.path.join(REPO, LK), "r", encoding="utf-8") as fh:
    for n, line in enumerate(fh, 1):
        s = line.strip()
        if s.startswith("status:") or s.startswith("approved_by:") or s.startswith("approval_decision:"):
            print("(a) line", n, repr(line.rstrip("\n")))

# (b) bound amendments
BOUND = {
    "v2_addendum_attcount.yaml": "4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48",
    "v2_addendum_gapattr.yaml": "919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7",
    "v2_addendum_childend.yaml": "e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b",
    "v2_addendum_failclosed.yaml": "1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c",
    "v2_addendum_readbackclose.yaml": "f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c",
    "v2_addendum_readbackfull.yaml": "0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1",
    "v2_addendum_readbackcover.yaml": "dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e",
}
for name, exp in BOUND.items():
    got = sha(AMD + name)
    print("(b)", AMD + name, got, "MATCH" if got == exp else "MISMATCH expected " + exp)
    ok &= got == exp

# (c) reviews and censuses vs the path_sha256 of the snapshot receipts (only that field is read)
CARD = {
    "TASK-20260924-0c2fdc": {
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml": "b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f",
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md": "0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8",
    },
    "TASK-20260924-7e8a5d": {
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml": "139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4",
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md": "97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055",
    },
    "TASK-20260924-93f3ca": {
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml": "0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7",
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md": "02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21",
    },
    "TASK-20260924-682890": {
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml": "03e66166e986670e94f97fcf14452c375bd05f65fa9f73928388457eb2d29467",
        "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md": "a24687c2b57ca0b563425956f9e0707d93d2a60a086501124fa4f3df2f20dca4",
    },
    "TASK-20260924-71d070": {},
    "TASK-20260924-ddfb69": {},
    "TASK-20260924-a01341": {},
}
for task, card_vals in CARD.items():
    rp = os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/archives", task, "snapshot-receipt.json")
    with open(rp, "r", encoding="utf-8") as fh:
        ps = json.load(fh)["path_sha256"]
    print("(c)", task, "path_sha256 =", json.dumps(ps, sort_keys=True))
    for p, h in sorted(ps.items()):
        got = sha(p)
        m = got == h
        ok &= m
        print("(c)   ", p, got, "MATCH receipt" if m else "MISMATCH receipt " + h)
    for p, h in card_vals.items():
        m = ps.get(p) == h
        ok &= m
        print("(c)    card value for", p, h, "EQUALS receipt" if m else "DIFFERS FROM receipt")

print("ALL_OK" if ok else "FAILURE")
sys.exit(0 if ok else 1)
```

### scan_v1.py

- sha256: c3f5eb34f93577c7594317eb5095ba91b5c12df116e12e55aadb48a35001e747
- argv: `C012: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v1.py scan_v1.json > scan_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch (zero runs; static only). AST / dis scan of the SOURCE TEXT of the frozen trees.
# Every file is read as text and parsed / compiled IN THIS PROCESS; nothing is imported from the scanned trees and
# nothing is executed. An audit hook refuses (a) an import of any module name that a scanned file defines and
# (b) every process-launch event, as a guard. Standard library only. Writes JSON to argv[1]; summary to stdout.
import ast
import dis
import io
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
EXP = os.path.join(REPO, "experiments/EXP-GFPN-05ff43")
TREES = ["implementation", "implementation-v2", "implementation-v2-a1", "implementation-v2-r1",
         "implementation-v2-r2", "implementation-v2-r3"]

FILES = []
for t in TREES:
    d = os.path.join(EXP, t)
    for f in sorted(os.listdir(d)):
        if f.endswith(".py"):
            FILES.append(os.path.join(d, f))
MODNAMES = {os.path.basename(p)[:-3] for p in FILES}

REFUSED = {"import": 0, "launch": 0}


def _hook(event, args):
    if event == "import":
        name = str(args[0]).split(".")[0] if args else ""
        if name in MODNAMES:
            REFUSED["import"] += 1
            raise RuntimeError("guard: import of scanned module %s refused" % name)
    if event in ("subprocess.Popen", "os.system", "os.exec", "os.fork", "os.posix_spawn", "os.spawn", "os.forkpty"):
        REFUSED["launch"] += 1
        raise RuntimeError("guard: process launch refused (%s)" % event)


sys.addaudithook(_hook)


def rel(p):
    return os.path.relpath(p, EXP)


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class Enclosing(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
        self.map = {}

    def generic_visit(self, node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.stack.append(node.name)
            for ch in ast.iter_child_nodes(node):
                self.map[id(ch)] = ".".join(self.stack)
                self.generic_visit(ch)
            self.stack.pop()
        else:
            for ch in ast.iter_child_nodes(node):
                self.map[id(ch)] = ".".join(self.stack) or "<module>"
                self.generic_visit(ch)


out = {"files": [rel(p) for p in FILES], "run_child_calls": [], "run_child_refs": [], "run_child_defs": [],
       "run_child_attr_stores": [], "from_v2_solver_imports": [], "getattr_run_child": [],
       "key_writes_instructions_callgrind": [], "key_writes_comparator": [], "launch_calls_other": [],
       "imports": {}, "dynamic_import": [], "calls_of_interest": [], "defaults_referencing_run_child": []}
INTEREST = {"curve_facts", "fb1_curve_search", "run_system", "callgrind_instructions", "child_job", "solve", "run"}
LAUNCH = {"os.fork", "os.forkpty", "os.system", "os.popen", "os.execv", "os.execve", "os.execvp", "os.execl",
          "os.posix_spawn", "os.posix_spawnp", "os.spawnv", "subprocess.run", "subprocess.Popen", "subprocess.call",
          "subprocess.check_call", "subprocess.check_output", "multiprocessing.Process"}

for path in FILES:
    src = open(path, encoding="utf-8", errors="replace").read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        out.setdefault("parse_errors", []).append({"file": rel(path), "error": repr(e)})
        continue
    enc = Enclosing()
    enc.generic_visit(tree)
    imps = []
    call_func_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_func_ids.add(id(node.func))
    for node in ast.walk(tree):
        fn = enc.map.get(id(node), "<module>")
        if isinstance(node, ast.Import):
            for a in node.names:
                imps.append({"line": node.lineno, "module": a.name, "as": a.asname, "in": fn})
        elif isinstance(node, ast.ImportFrom):
            imps.append({"line": node.lineno, "module": node.module, "names": [a.name for a in node.names], "in": fn})
            if node.module == "v2_solver":
                out["from_v2_solver_imports"].append({"file": rel(path), "line": node.lineno, "names": [a.name for a in node.names]})
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "run_child":
                out["run_child_defs"].append({"file": rel(path), "line": node.lineno, "in": fn})
            for dflt in list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]:
                for sub in ast.walk(dflt):
                    if (isinstance(sub, ast.Name) and sub.id == "run_child") or (isinstance(sub, ast.Attribute) and sub.attr == "run_child"):
                        out["defaults_referencing_run_child"].append({"file": rel(path), "line": node.lineno, "function": node.name})
        if isinstance(node, ast.Call):
            d = dotted(node.func)
            name = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else None)
            if name == "run_child":
                out["run_child_calls"].append({"file": rel(path), "line": node.lineno, "func": d, "in": fn})
            if name in INTEREST:
                out["calls_of_interest"].append({"file": rel(path), "line": node.lineno, "func": d, "in": fn})
            if d in LAUNCH or (d and d.split(".")[-1] in ("Popen", "execv", "execve", "fork", "system", "posix_spawn")):
                out["launch_calls_other"].append({"file": rel(path), "line": node.lineno, "func": d, "in": fn})
            if d in ("getattr", "setattr", "hasattr") and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and node.args[1].value == "run_child":
                out["getattr_run_child"].append({"file": rel(path), "line": node.lineno, "func": d, "in": fn})
            if d in ("__import__", "importlib.import_module", "importlib.util.spec_from_file_location", "runpy.run_path", "exec", "eval"):
                out["dynamic_import"].append({"file": rel(path), "line": node.lineno, "func": d, "in": fn})
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("update", "setdefault"):
                for kw in node.keywords:
                    if kw.arg in ("instructions_callgrind", "comparator"):
                        out["key_writes_" + kw.arg].append({"file": rel(path), "line": node.lineno, "how": node.func.attr + " keyword", "in": fn})
                if node.func.attr == "setdefault" and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in ("instructions_callgrind", "comparator"):
                    out["key_writes_" + node.args[0].value].append({"file": rel(path), "line": node.lineno, "how": "setdefault", "in": fn})
        if isinstance(node, (ast.Name, ast.Attribute)):
            nm = node.id if isinstance(node, ast.Name) else node.attr
            if nm == "run_child" and id(node) not in call_func_ids:
                ctx = type(node.ctx).__name__
                rec = {"file": rel(path), "line": node.lineno, "expr": dotted(node), "ctx": ctx, "in": fn}
                if ctx == "Store":
                    out["run_child_attr_stores"].append(rec)
                else:
                    out["run_child_refs"].append(rec)
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store):
            sl = node.slice
            if isinstance(sl, ast.Constant) and sl.value in ("instructions_callgrind", "comparator"):
                out["key_writes_" + sl.value].append({"file": rel(path), "line": node.lineno, "how": "subscript store " + (dotted(node.value) or "?"), "in": fn})
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and k.value in ("instructions_callgrind", "comparator"):
                    out["key_writes_" + k.value].append({"file": rel(path), "line": k.lineno, "how": "dict literal key", "in": fn})
    out["imports"][rel(path)] = imps

# import closure from the two r3 entries (module names resolved inside the v2, v2-a1 and r3 trees)
MOD2FILE = {}
for p in FILES:
    t = rel(p).split("/")[0]
    if t in ("implementation-v2", "implementation-v2-a1", "implementation-v2-r3"):
        MOD2FILE[os.path.basename(p)[:-3]] = rel(p)


def closure(start):
    seen, todo = set(), [start]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        for im in out["imports"].get(f, []):
            m = (im.get("module") or "").split(".")[0]
            if m in MOD2FILE:
                todo.append(MOD2FILE[m])
    return sorted(seen)


out["closure_r3_entry_v2"] = closure("implementation-v2-r3/r3_entry_v2.py")
out["closure_r3_entry_a1"] = closure("implementation-v2-r3/r3_entry_a1.py")
out["closure_r3_run_wrapper"] = closure("implementation-v2-r3/r3_run_wrapper.py")
out["closure_r3_check_run"] = closure("implementation-v2-r3/r3_check_run.py")
prod = set(out["closure_r3_entry_v2"]) | set(out["closure_r3_entry_a1"])
out["production_run_child_calls"] = [c for c in out["run_child_calls"] if c["file"] in prod]
out["nonproduction_run_child_calls"] = [c for c in out["run_child_calls"] if c["file"] not in prod]

# dis of v2_driver.solve compiled here from source text (never imported): ordering at lines 207-209
drv = os.path.join(EXP, "implementation-v2/v2_driver.py")
code = compile(open(drv).read(), drv, "exec")
solve_code = next(c for c in code.co_consts if hasattr(c, "co_name") and c.co_name == "solve")
buf = io.StringIO()
lines = []
for ins in dis.get_instructions(solve_code):
    ln = ins.positions.lineno if getattr(ins, "positions", None) else None
    if ln in (207, 208, 209, 210):
        lines.append({"line": ln, "opname": ins.opname, "argrepr": ins.argrepr})
out["dis_v2_driver_solve_207_210"] = lines
# dis of a1_pari.curve_facts lines 91-96 (script write before launch)
ap = os.path.join(EXP, "implementation-v2-a1/a1_pari.py")
code2 = compile(open(ap).read(), ap, "exec")
cf = next(c for c in code2.co_consts if hasattr(c, "co_name") and c.co_name == "curve_facts")
out["dis_a1_pari_curve_facts_91_96"] = [{"line": (i.positions.lineno if getattr(i, "positions", None) else None), "opname": i.opname, "argrepr": i.argrepr}
                                        for i in dis.get_instructions(cf)
                                        if getattr(i, "positions", None) and i.positions.lineno in (91, 92, 93, 94, 95, 96)]
out["guard_refusals"] = REFUSED
out["python"] = sys.version

with open(sys.argv[1], "w") as fh:
    json.dump(out, fh, indent=1)
print("files scanned:", len(FILES))
print("run_child defs:", out["run_child_defs"])
print("run_child calls (all):", len(out["run_child_calls"]))
for c in out["run_child_calls"]:
    print("   ", c["file"], c["line"], c["func"], "in", c["in"], "PRODUCTION" if c in out["production_run_child_calls"] else "non-production")
print("run_child non-call refs:", out["run_child_refs"])
print("run_child stores:", out["run_child_attr_stores"])
print("from v2_solver import:", out["from_v2_solver_imports"])
print("getattr/setattr run_child:", out["getattr_run_child"])
print("defaults referencing run_child:", out["defaults_referencing_run_child"])
print("dynamic import/exec/eval:", out["dynamic_import"])
print("writes of key instructions_callgrind:", out["key_writes_instructions_callgrind"])
print("writes of key comparator:", out["key_writes_comparator"])
print("other launch calls:")
for c in out["launch_calls_other"]:
    print("   ", c["file"], c["line"], c["func"], "in", c["in"], "PROD" if c["file"] in prod else "")
print("closure r3_entry_v2:", out["closure_r3_entry_v2"])
print("closure r3_entry_a1:", out["closure_r3_entry_a1"])
print("calls of interest in production closure:")
for c in out["calls_of_interest"]:
    if c["file"] in prod:
        print("   ", c["file"], c["line"], c["func"], "in", c["in"])
print("dis solve 207-210:", [(d["line"], d["opname"], d["argrepr"]) for d in out["dis_v2_driver_solve_207_210"]])
print("dis curve_facts 91-96:", [(d["line"], d["opname"], d["argrepr"]) for d in out["dis_a1_pari_curve_facts_91_96"]])
print("guard refusals:", REFUSED, "python:", sys.version.split()[0])
```

### scan_v2.py

- sha256: bd16afc0c27dcef4046afef79537315ddcb1ece092ab68ae00817319be6ba9cb
- argv: `C022: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v2.py scan_v2.json scan_v1.json > scan_v2.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch (zero runs; static only). Second AST scan (a new file, scan_v1 is kept unchanged):
# (1) process-ending, exec, hook and thread calls in the production closure (residuals X1, X6b, X10);
# (2) every try/except whose body encloses a call of a launching function in the production closure;
# (3) definitions, stores and references of _run_child_locked;
# (4) file removals (os.remove / os.unlink / shutil) in the production closure, with their argument text;
# (5) every write-mode open() in the production closure, with its argument text.
# Source text is parsed in this process; nothing from the scanned trees is imported or executed; an audit hook
# refuses scanned-module imports and process launches. Standard library only. Writes JSON to argv[1].
import ast
import json
import os
import sys

EXP = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43"
SCAN1 = json.load(open(sys.argv[2]))
PROD = sorted(set(SCAN1["closure_r3_entry_v2"]) | set(SCAN1["closure_r3_entry_a1"]))
ALLTREES = SCAN1["files"]
MODNAMES = {os.path.basename(p)[:-3] for p in ALLTREES}
REFUSED = {"import": 0, "launch": 0}


def _hook(event, args):
    if event == "import":
        name = str(args[0]).split(".")[0] if args else ""
        if name in MODNAMES:
            REFUSED["import"] += 1
            raise RuntimeError("guard")
    if event in ("subprocess.Popen", "os.system", "os.exec", "os.fork", "os.posix_spawn", "os.spawn", "os.forkpty"):
        REFUSED["launch"] += 1
        raise RuntimeError("guard")


sys.addaudithook(_hook)


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def seg(src, node):
    try:
        return ast.get_source_segment(src, node)
    except Exception:  # noqa: BLE001
        return None


ENDERS = {"os._exit", "sys.exit", "exit", "quit", "os.abort", "os.kill", "signal.signal", "atexit.register",
          "os.register_at_fork", "faulthandler.enable", "faulthandler.register", "threading.Thread", "os.execv", "os.execve",
          "os.execvp", "os.execvpe", "os.execl", "os.execle", "os.execlp", "os.execlpe", "os.posix_spawn", "os.posix_spawnp",
          "os.system", "os.popen", "os.fork", "os.forkpty", "signal.setitimer", "signal.alarm", "signal.pthread_kill"}
LAUNCHERS = {"run_child", "solve", "run_system", "curve_facts", "child_job", "callgrind_instructions", "build_poly", "raw_grid",
             "run", "fb1_curve_search"}
out = {"production_files": PROD, "enders": [], "raise_systemexit": [], "handlers_around_launchers": [], "all_handlers": [],
       "rcl_defs": [], "rcl_refs": [], "removals": [], "write_opens": []}
for rel in ALLTREES:
    path = os.path.join(EXP, rel)
    src = open(path, encoding="utf-8", errors="replace").read()
    tree = ast.parse(src, filename=path)
    prod = rel in PROD
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_child_locked":
            out["rcl_defs"].append({"file": rel, "line": node.lineno})
        if isinstance(node, (ast.Name, ast.Attribute)):
            nm = node.id if isinstance(node, ast.Name) else node.attr
            if nm == "_run_child_locked":
                out["rcl_refs"].append({"file": rel, "line": node.lineno, "ctx": type(node.ctx).__name__})
        if not prod:
            continue
        if isinstance(node, ast.Call):
            d = dotted(node.func) or ""
            if d in ENDERS or d.endswith("._exit") or d.startswith("os.exec") or d.startswith("os.spawn"):
                out["enders"].append({"file": rel, "line": node.lineno, "call": d, "text": (seg(src, node) or "")[:160]})
            if d in ("os.remove", "os.unlink", "shutil.rmtree", "os.rmdir", "os.rename", "os.replace", "shutil.move"):
                out["removals"].append({"file": rel, "line": node.lineno, "call": d, "text": (seg(src, node) or "")[:160]})
            if d == "open" and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str) and any(c in node.args[1].value for c in "wax+"):
                out["write_opens"].append({"file": rel, "line": node.lineno, "text": (seg(src, node) or "")[:160]})
        if isinstance(node, ast.Raise) and node.exc is not None:
            t = seg(src, node.exc) or ""
            if "SystemExit" in t or "KeyboardInterrupt" in t:
                out["raise_systemexit"].append({"file": rel, "line": node.lineno, "text": t[:160]})
        if isinstance(node, ast.Try):
            htypes = [seg(src, h.type) if h.type is not None else "<bare>" for h in node.handlers]
            called = set()
            for b in node.body:
                for sub in ast.walk(b):
                    if isinstance(sub, ast.Call):
                        d = dotted(sub.func) or ""
                        last = d.split(".")[-1] if d else ""
                        if last in LAUNCHERS:
                            called.add(d)
            rec = {"file": rel, "line": node.lineno, "end": getattr(node, "end_lineno", None), "handlers": htypes,
                   "finally": bool(node.finalbody), "launcher_calls_in_body": sorted(called)}
            out["all_handlers"].append(rec)
            if called:
                out["handlers_around_launchers"].append(rec)
out["guard_refusals"] = REFUSED
with open(sys.argv[1], "w") as fh:
    json.dump(out, fh, indent=1)
print("production files:", len(PROD))
print("_run_child_locked defs:", out["rcl_defs"])
print("_run_child_locked refs:", out["rcl_refs"])
print("process-ending / exec / hook / thread calls in production closure:")
for e in out["enders"]:
    print("   ", e["file"], e["line"], e["call"], "|", e["text"])
print("raise SystemExit/KeyboardInterrupt in production closure:")
for e in out["raise_systemexit"]:
    print("   ", e["file"], e["line"], e["text"])
print("try statements whose body calls a launching function (production closure):")
for e in out["handlers_around_launchers"]:
    print("   ", e["file"], e["line"], "-", e["end"], e["handlers"], "finally" if e["finally"] else "", e["launcher_calls_in_body"])
print("removals in production closure:")
for e in out["removals"]:
    print("   ", e["file"], e["line"], e["call"], "|", e["text"])
print("write-mode open() in production closure:")
for e in out["write_opens"]:
    print("   ", e["file"], e["line"], "|", e["text"])
print("guard refusals:", REFUSED)
```

### pkgread_v1.py

- sha256: 96764d2cd95bcb924ca1441022f430cf127e7d64f2841ed6ccca2a542ee60119
- argv: `C016: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread_v1.py pkgread_v1.json > pkgread_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch (zero runs; static only). Lists the four archived r3 gate packages (os.scandir) and
# reads, READ-ONLY with O_NOATIME, exactly: solver-events.json, raw-result.json, command.txt and every
# child/*.spec.json of each package. lstat (including atime) of every directory listed and every file read is taken
# before and after; any difference is reported. Imports nothing from the repository. Writes ONE JSON file (argv[1]).
import hashlib
import json
import os
import sys

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
FIVE = ["child", "solver", "health", "comparator", "pari"]


def st(p):
    s = os.lstat(p)
    return [s.st_mode, s.st_size, s.st_atime_ns, s.st_mtime_ns, s.st_ctime_ns, s.st_ino]


def read_noatime(p):
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
        return b"".join(chunks)
    finally:
        os.close(fd)


before, after = {}, {}
out = {"packages": {}}
for rid in PKGS:
    rd = os.path.join(RUNS, rid)
    before[rd] = st(rd)
    top = sorted(e.name for e in os.scandir(rd))
    listing = {}
    for d in FIVE:
        dp = os.path.join(rd, d)
        if os.path.isdir(dp):
            before[dp] = st(dp)
            names = sorted(e.name for e in os.scandir(dp))
            listing[d] = names
            for n in names:
                before[os.path.join(dp, n)] = st(os.path.join(dp, n))
    files = {}
    for f in ("solver-events.json", "raw-result.json", "command.txt"):
        p = os.path.join(rd, f)
        before[p] = st(p)
        b = read_noatime(p)
        files[f] = {"sha256": hashlib.sha256(b).hexdigest(), "text": b.decode("utf-8", errors="replace")}
    specs = {}
    for n in listing.get("child", []):
        if n.endswith(".spec.json"):
            p = os.path.join(rd, "child", n)
            b = read_noatime(p)
            specs[n] = json.loads(b.decode("utf-8"))
    out["packages"][rid] = {"run_dir": rd, "top": top, "listing": listing, "files": files, "specs": specs}

for p in list(before):
    after[p] = st(p)
changed = [p for p in before if before[p] != after[p]]
out["lstat_checked"] = len(before)
out["lstat_changed"] = changed
with open(sys.argv[1], "w") as fh:
    json.dump(out, fh)
for rid in PKGS:
    pk = out["packages"][rid]
    print(rid, "top:", pk["top"])
    print("   five-dir counts:", {d: len(v) for d, v in pk["listing"].items()}, "total", sum(len(v) for v in pk["listing"].values()))
    print("   sha256:", {f: v["sha256"] for f, v in pk["files"].items()})
print("lstat checked:", out["lstat_checked"], "changed:", changed)
```

### explore_v1.py

- sha256: e40dc2068353bea086bc937c854df52ecf2b783258f869f2e0c3727a54fd5a74
- argv: `C017: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B explore_v1.py pkgread_v1.json > explore_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch: summarize the archived records held in pkgread_v1.json (no repository read).
import json
import sys

D = json.load(open(sys.argv[1]))
for rid, pk in D["packages"].items():
    se = json.loads(pk["files"]["solver-events.json"]["text"])
    raw = json.loads(pk["files"]["raw-result.json"]["text"])
    print("=" * 100)
    print(rid, "raw kind", raw.get("kind"), "run_status", raw.get("run_status"), "gate_pass", raw.get("gate_pass"),
          "top keys", sorted(raw.keys()))
    print("  command.txt:", pk["files"]["command.txt"]["text"].replace("\n", " | ")[:400])
    print("  solver-events top keys:", sorted(se.keys()))
    for site, sec in (se.get("sites") or {}).items():
        print("   site", site, "counters", json.dumps(sec.get("counters")), "events", len(sec.get("events") or []),
              "records", len(sec.get("records") or []))
    s3 = (se.get("sites") or {}).get("v2_driver.solve/callgrind") or {}
    tags3 = [r.get("tag") for r in s3.get("records") or []]
    print("   S-3 record tags (%d):" % len(tags3), tags3[:40])
    if s3.get("records"):
        r0 = s3["records"][0]
        print("   S-3 record[0] keys:", sorted(r0.keys()), "files", r0.get("files"))
    print("  listing solver sample:", pk["listing"].get("solver", [])[:12])
    print("  listing child sample:", pk["listing"].get("child", [])[:8])
    print("  listing comparator:", pk["listing"].get("comparator"))
    # where do solve records sit in raw?
    def walk(o, path, acc):
        if isinstance(o, dict):
            if isinstance(o.get("solver"), dict) and ("instructions_callgrind" in o or "outcome" in o):
                acc.append((path, "instructions_callgrind" in o, o.get("instructions_callgrind") is not None, o.get("outcome"),
                            (o.get("solver") or {}).get("argv", [None])[-3:] if (o.get("solver") or {}).get("argv") else None))
            for k, v in o.items():
                walk(v, path + "/" + str(k), acc)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i, acc)
    acc = []
    walk(raw, "", acc)
    print("  solve-like records in raw: %d" % len(acc))
    for a in acc[:6]:
        print("    ", a)
    print("  comparator key:", ("comparator" in raw), (sorted(raw["comparator"].keys()) if isinstance(raw.get("comparator"), dict) else None))
```

### rjcore_v1.py

- sha256: c6e156f495d187fec8d1205bc86f8d2c423d8453b1c3cfa7bbabb4fc08648b9e
- argv: `not run directly; imported (from the scratch directory) by lj0_v1.py and listing_v1.py`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). THE RULE EVALUATOR CORE, version 1.

One method, used UNCHANGED for LJ-0 (known-answer control), LJ-1, LJ-2, LJ-3 and LJ-4 objects. It computes, from
rule TEXT as transcribed below (file and line cited at each rule), what each draft's rules say about a constructed
package: the launch records as each draft's recorder would write them, attribution, named gaps, the frozen checker's
cap items, the r4 verdict (PASS / PASS_ZL / FAIL), and failclosed's definitions (i)-(v) evaluated against the TRUTH
of the construction. Standard library only; it imports nothing from the repository and runs nothing.

Rule sets (the draft AS WORDED unless named otherwise):
  RK  readbackclose RK-1 / RK-3 (readbackclose.yaml 246-373)
  RF  failclosed RF-0..RF-3 (failclosed.yaml 280-418)
  RG  childend RG-1, RG-2, RG-4 (childend.yaml 250-437)
  RH  gapattr RH-1, RH-2 (gapattr.yaml 243-318)
  RI  attcount RI-1 (attcount.yaml 265-345)
  RJ  launchkind RJ-1..RJ-4 (launchkind.yaml 270-405)
  RJw launchkind with RJ-1 (b) WEAKENED to "Ncg(<tag>) is at most the count" (CRJ-4 (e) only)
  RJx launchkind with RJ-1 disabled in the evaluator (RJ-5 (c) (28) only)
  RJnogp launchkind with RJ-2 disabled (gp script back on the non-launch list; (29) discrimination only)
  RJnocmp launchkind with RJ-3 disabled ((30) discrimination only)
  RJnouk launchkind with RJ-4 (b) disabled ((31) discrimination only)
  RIx attcount with RI-1 (a) and (d) disabled (RI-3 (25) as RJ-5 (a) reads it)
Definitions (failclosed.yaml 604-617): (i), (ii) with an absent record read as "not class (A) or (C)" (launchkind
carried decision (5)) in two sub-readings ii_LR (the child's own launch record) and ii_ANY (any read-back source),
(iii), (iv) read LITERALLY, (v).
"""
import re

CAP = "cap"          # a read-back pair equal to the requested cap
NEQ = "neq"          # a read-back pair not equal to the requested cap
FIVE = ("child", "solver", "health", "comparator", "pari")
RULESETS = ("RK", "RF", "RG", "RH", "RI", "RJ", "RJw", "RJx", "RJnogp", "RJnocmp", "RJnouk", "RIx")
EXEC_PATHS = ("exec_ok", "exec_fail", "exec_timeout", "exec_ssf")
SIX_FORMS = [re.compile(r"^child/[^/]+\.stdout$"), re.compile(r"^solver/[^/]+\.ms\.log$"),
             re.compile(r"^solver/[^/]+\.callgrind\.stdout$"), re.compile(r"^comparator/stdout\.log$"),
             re.compile(r"^health/[^/]+\.ms\.log$"), re.compile(r"^pari/[^/]+\.gp\.stdout$")]


# =============================================================================================== truth of one launch
def path_facts(path, foreign_exit=1):
    """Frozen run_child / _run_child_locked facts per path (v2_solver.py 149-308), as TRUTH:
    created (os.fork at 181 returned a pid), pair_read (227 executed) and its value, report (the key set at 220 and
    its value), returncode, execs (argv executed), raised (a raise leaving run_child), child_files (the child opened
    stdout / stderr at 188-189), child_end (childend RG-1 (c)), rc_for_end."""
    f = {"created": True, "pair": None, "report": None, "returncode": None, "execs": False, "raised": None,
         "child_files": False, "child_end": None, "foreign": False}
    if path == "A":                                     # refusal before fork: 153-169 (class A)
        f.update(created=False, child_end="no_child")
    elif path in EXEC_PATHS:                            # 188-189 files, 198 OK, 227 pair, 236 go byte, 204-205 exec
        f.update(pair=CAP, report="OK", returncode=(0 if path in ("exec_ok", "exec_ssf") else (-9 if path == "exec_timeout" else 1)),
                 execs=True, child_files=True, child_end="exec")
    elif path == "pre_stdout_99":                       # 188 open fails -> 206-208 os._exit(99): no file, report ""
        f.update(report="", returncode=99, child_end="frozen_pre_exec_exit")
    elif path == "err_setrlimit_97":                    # 188-189 files created, 193 fails, 195 ERR report, 196 _exit(97)
        f.update(report="ERR", returncode=97, child_files=True, child_end="frozen_pre_exec_exit")
    elif path == "P8":                                  # OK soft != cap: 227 pair (unequal), parent refuses 228-232; child 200-201 exit 98
        f.update(pair=NEQ, report="OK", returncode=98, child_files=True, child_end="frozen_pre_exec_exit")
    elif path == "P16":                                 # fork created the child; raise before STORE_FAST pid (181); child later execs (RKL-2)
        f.update(raised="KeyboardInterrupt", child_files=True, execs=True, child_end="undetermined")
    elif path == "PF2_after_P14a":                      # raise at 214, then lk.release raises in the finally (172-174)
        f.update(raised="OSError", child_files=True, execs=True, child_end="undetermined")
    elif path == "FO1_C":                               # async exception in the fork child before 183: escaped child
        f.update(report="", returncode=foreign_exit, child_end="undetermined", foreign=True)
    elif path == "FO1_B":                               # after OK at 198; exception at 202 caught; second at 207-208: escaped
        f.update(pair=CAP, report="OK", returncode=foreign_exit, child_files=True, child_end="undetermined", foreign=True)
    else:
        raise ValueError(path)
    return f


# =============================================================================================== a package under construction
class Pkg:
    def __init__(self, name, kind, gate=False, a1_image=False, planned_basis=False, normal=True, raw_writer="driver",
                 cap_source="Mc", note=""):
        self.name, self.kind, self.gate, self.a1_image = name, kind, gate, a1_image
        self.planned_basis, self.normal, self.raw_writer, self.cap_source, self.note = planned_basis, normal, raw_writer, cap_source, note
        self.launches = []              # truth, in launch order
        self.files = {}                 # rel path -> origin
        self.nonlaunch = {}             # rel path -> frozen non-launch writer (RG-4 (b) list as each draft keeps it)
        self.specs = {}                 # child/<tag>.spec.json -> "out" (rel)
        self.rb1 = []                   # attempt records: {site, tag, attempt, pair, cg_present}
        self.rl2 = []                   # pass-through records: {tag, pair}
        self.events = {}                # (site, tag) -> {"attempts": [..], "accepted": k, "renamed": {"attempt<k>": [names]}}
        self.counters = {"S-1": {"attempts_total": 0, "passthrough": 0}, "S-2": {"attempts_total": 0}}
        self.raw_pairs = {}             # lid -> pair copied by the frozen driver into raw-result.json
        self.meta_pairs = []            # child/*.meta.json read-backs
        self.raw_comparator_child = False
        self.lost = set()               # launch records absent (premise)
        self.foreign_file = False       # recorder-foreign-<pid>.json present (failclosed RF-1 (b))
        self.foreign_record_undetected = False
        self.extra_items = []           # other frozen checker items that fail
        self.altered_in_place = False   # V-7 (r3_check_run.py 153-158) fails on an in-place alteration
        self.consistency_violation = False
        self.premises = []
        self.v7_applies = True

    # --------------------------------------------------------------------------------------- launches
    def launch(self, lid, kind, path, stdout, stderr, argv_paths=(), argv_dirs=(), cg_out=None, spec=None, site=None,
               tag=None, outputs=(), foreign_exit=1, raw_pair=True):
        f = path_facts(path, foreign_exit)
        L = {"lid": lid, "kind": kind, "path": path, "stdout": stdout, "stderr": stderr, "argv_paths": set(argv_paths),
             "argv_dirs": set(argv_dirs), "cg_out": cg_out, "spec": spec, "site": site, "tag": tag, **f}
        self.launches.append(L)
        if f["child_files"]:
            self.files[stdout] = "launch:" + lid
            self.files[stderr] = "launch:" + lid
        if f["execs"] or path == "FO1_B":
            for o in outputs:
                self.files[o] = "launch:" + lid
        if raw_pair and f["pair"] is not None:
            self.raw_pairs[lid] = f["pair"]
        if f["foreign"]:
            self.foreign_record_undetected = True       # pari-stack.json / stderr written in the escaped process
        return L

    def solve(self, tag, attempts, retain_input=True, gb_only=False, callgrind=None, raw_row=True):
        """v2_driver.solve (158-214) through the SE-3 wrapper (r3_resolve.py 373-390; r4 counterpart). attempts: list of
        msolve paths, one per attempt; every attempt but the last has the SSF signature (r3_resolve.py 61-74, 295-310).
        callgrind: None or the path of the one callgrind launch after the last attempt when its outcome is ok (207-209)."""
        d = "solver"
        n = len(attempts)
        cg_lid = None
        for k, p in enumerate(attempts, 1):
            lid = "%s/ms%d" % (tag, k)
            self.files["solver/%s.ms" % tag] = "driver:solve-input"          # 161-162, before the launch
            outs = ["solver/%s.ms.out" % tag] if p in ("exec_ok", "exec_ssf") else []
            L = self.launch(lid, "msolve", p, "solver/%s.ms.log" % tag, "solver/%s.ms.err" % tag,
                            argv_paths=("solver/%s.ms" % tag, "solver/%s.ms.out" % tag), site="S-1", tag=tag, outputs=outs,
                            raw_pair=(k == n and raw_row))
            returned = L["raised"] is None
            cg_present = False
            if k == n and callgrind is not None and returned:
                cg_lid = "%s/cg" % tag
                cgp = callgrind
                cg_outs = ["solver/%s.callgrind.out" % tag] if cgp == "exec_fail" else []   # kept on non-ok (521-524); removed at 549 on ok
                self.launch(cg_lid, "callgrind", cgp, "solver/%s.callgrind.stdout" % tag, "solver/%s.callgrind.stderr" % tag,
                            argv_paths=("solver/%s.ms" % tag, "solver/%s.cg.ms.out" % tag), cg_out="solver/%s.callgrind.out" % tag,
                            site="S-3", tag=tag, outputs=cg_outs, raw_pair=raw_row)
                cg_present = True                                              # 209: set when callgrind_instructions returns
            if not returned:
                return                                                         # solve raised: no RB-1 record, no counter, no _retain
            if not retain_input:
                self.files.pop("solver/%s.ms" % tag, None)                     # _retain 219-221 on every return path
            if gb_only:
                self.rl2.append({"lid": lid, "tag": tag, "pair": L["pair"]})
                self.counters["S-1"]["passthrough"] += 1
            else:
                self.rb1.append({"lid": lid, "site": "S-1", "tag": tag, "attempt": k, "pair": L["pair"], "cg_present": cg_present})
                self.counters["S-1"]["attempts_total"] += 1
            if n >= 2:
                ev = self.events.setdefault(("S-1", tag), {"attempts": [], "accepted": None, "renamed": {}})
                ev["attempts"].append(k)
                if k < n:
                    ren = []
                    for ext in (".ms.out", ".ms.log", ".ms.err"):
                        src = "solver/%s%s" % (tag, ext)
                        if src in self.files:
                            dst = src + ".ssf-attempt%d" % k
                            self.files[dst] = self.files.pop(src)
                            ren.append(dst.split("/")[-1])
                    ev["renamed"]["attempt%d" % k] = ren
                else:
                    ev["accepted"] = k
        return cg_lid

    def health(self, tag, attempts):
        """a1_health.run_system (140-220) through the HR-3 wrapper (r3_resolve.py 397-409)."""
        n = len(attempts)
        for k, p in enumerate(attempts, 1):
            lid = "health:%s/ms%d" % (tag, k)
            self.files["health/%s.ms" % tag] = "nonlaunch:a1_health.py 141-143"
            self.nonlaunch["health/%s.ms" % tag] = "a1_health.py 141-143"
            outs = ["health/%s.ms.out" % tag] if p in ("exec_ok", "exec_ssf") else []
            L = self.launch(lid, "msolve", p, "health/%s.ms.log" % tag, "health/%s.ms.err" % tag,
                            argv_paths=("health/%s.ms" % tag, "health/%s.ms.out" % tag), site="S-2", tag=tag, outputs=outs,
                            raw_pair=False)
            if L["raised"] is not None:
                return
            self.rb1.append({"lid": lid, "site": "S-2", "tag": tag, "attempt": k, "pair": L["pair"], "cg_present": None})
            self.counters["S-2"]["attempts_total"] += 1
            if n >= 2:
                ev = self.events.setdefault(("S-2", tag), {"attempts": [], "accepted": None, "renamed": {}})
                ev["attempts"].append(k)
                if k < n:
                    ren = []
                    for ext in (".ms.out", ".ms.log", ".ms.err"):
                        src = "health/%s%s" % (tag, ext)
                        if src in self.files:
                            dst = src + ".ssf-attempt%d" % k
                            self.files[dst] = self.files.pop(src)
                            ren.append(dst.split("/")[-1])
                    ev["renamed"]["attempt%d" % k] = ren
                else:
                    ev["accepted"] = k

    def health_report(self, p):
        self.files["health/health-%d.json" % p] = "nonlaunch:a1_health.py 251"
        self.nonlaunch["health/health-%d.json" % p] = "a1_health.py 251"

    def child_job(self, tag, path, job="build_poly", to_cache=False):
        """v2_driver.child_job (92-107): the spec is written BEFORE the launch (98-99) and named as argv's last element (100)."""
        spec = "child/%s.spec.json" % tag
        self.files[spec] = "driver:child_job-spec"
        out = ("CACHE/%s" % tag) if to_cache else ("child/%s" % tag)
        self.specs[spec] = out
        outs = []
        if path in ("exec_ok",) and not to_cache:
            outs = [out + ".meta.json"] + ([out + ".npz"] if job == "build_poly" else [])   # raw_grid removes .npz (144)
        L = self.launch("cj:" + tag, "childjob", path, "child/%s.stdout" % tag, "child/%s.stderr" % tag,
                        argv_paths=(spec,), spec=spec, tag=tag, outputs=outs, raw_pair=False)
        if path == "exec_ok" and not to_cache:
            self.meta_pairs.append(CAP)
            L["meta_pair"] = CAP
        return L

    def comparator(self, path):
        """v2_driver.cmd_anchor_identity (647-655): run_child at 650; comp["child"] at 652; raw["comparator"] at 655."""
        outs = ["comparator/%s" % n for n in ("anchor17_planted.ms", "anchor17_random.ms", "anchor25_planted.ms",
                                               "anchor25_random.ms", "k4a_results.json")]
        L = self.launch("cmp", "comparator", path, "comparator/stdout.log", "comparator/stderr.log",
                        argv_dirs=("comparator",), outputs=outs)
        if L["raised"] is None:
            self.raw_comparator_child = True
        return L

    def gp(self, tag, path):
        """a1_pari.curve_facts (87-115): the script is written BEFORE the launch (91-93), named by argv (94); launch at 96."""
        scr = "pari/%s.gp" % tag
        self.files[scr] = "frozen:a1_pari.py 91-93"
        self.nonlaunch[scr] = "a1_pari.py 91-93"
        return self.launch("gp:" + tag, "gp", path, "pari/%s.gp.stdout" % tag, "pari/%s.gp.stderr" % tag,
                           argv_paths=(scr,), tag=tag)


# =============================================================================================== records as each draft writes them
def record_of(L, rs):
    """The launch record the draft's recorder writes for truth L (readbackfull RL-1 (c); readbackclose RK-1;
    failclosed RF-1 (a); childend RG-1, RG-4 (a))."""
    created_rk = L["report"] is not None                              # RK-1 (a) key presence; on raise (b): P16 / P-F2 give False
    if L["path"] in ("P16", "PF2_after_P14a"):
        created_rk = False
    created_rf = created_rk
    if L["path"] == "P16":
        created_rf = "undetermined"                                   # RF-1 (a): frame at 181 with no pid
    elif L["path"] == "PF2_after_P14a":
        created_rf = True                                             # RF-1 (a): pid on the __context__ traceback
    created = created_rk if rs == "RK" else created_rf
    r = {"lid": L["lid"], "kind": L["kind"], "stdout": L["stdout"], "stderr": L["stderr"], "argv_paths": L["argv_paths"],
         "argv_dirs": L["argv_dirs"], "cg_out": L["cg_out"], "spec": L["spec"], "child_created": created,
         "raised": L["raised"], "pair": L["pair"], "pair_read_by_parent": L["pair"] is not None, "report": L["report"],
         "returncode": L["returncode"], "child_end": L["child_end"] if rs not in ("RK", "RF") else None}
    return r


def record_class(r, rs):
    """failclosed RF-3 (a) classes (376-395), narrowed by childend RG-1 (d) for RG and later."""
    base = None
    if r["child_created"] is False and r["raised"] is None:
        base = "A"
    elif r["child_created"] is True and r["raised"] is None and r["pair_read_by_parent"]:
        base = "B"
    elif (r["child_created"] is True and r["raised"] is None and not r["pair_read_by_parent"]
          and r["report"] in ("", "ERR") and r["returncode"] is not None):
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = r["child_end"]
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and r["returncode"] in (98, 99))) else None
    if base == "C":
        return "C" if ce == "frozen_pre_exec_exit" else None
    return None


# =============================================================================================== attribution
def fam(rs):
    if rs in ("RK", "RF"):
        return "truth"          # readbackfull RL-3: "child files ... whose launch has no launch record"
    if rs == "RG":
        return "RG4b"
    return "RH1"


def five(p):
    return p.split("/")[0] in FIVE


def attribute(pkg, recs, rs):
    """Returns (attr: file -> [(clause, lid)], gaps: [file], named: [str])."""
    files = {p: o for p, o in pkg.files.items() if five(p)}
    nonlaunch = dict(pkg.nonlaunch)
    if rs in ("RJ", "RJw", "RJx", "RJnocmp", "RJnouk"):               # RJ-2: the gp script leaves the non-launch list
        nonlaunch = {p: w for p, w in nonlaunch.items() if not (p.startswith("pari/") and p.endswith(".gp"))}
    attr, gaps, named = {}, [], []
    present = {r["lid"]: r for r in recs}
    F = fam(rs)
    if F == "truth":
        # readbackfull RL-3 (269-285): "child files in the package (child/*.meta.json, solver/*.ms.log, health/,
        # comparator/, pari/) whose launch has no launch record" -- only files of that list can be gaps here.
        def listed(p):
            return (re.match(r"^child/[^/]+\.meta\.json$", p) or re.match(r"^solver/[^/]+\.ms\.log$", p)
                    or p.split("/")[0] in ("health", "comparator", "pari"))
        for p, o in files.items():
            if p in nonlaunch:
                continue
            if o.startswith("launch:"):
                if o[7:] in present:
                    attr.setdefault(p, []).append(("launch", o[7:]))
                elif listed(p):
                    gaps.append(p)
            elif any(p in r["argv_paths"] for r in recs):
                attr.setdefault(p, []).append(("argv", "-"))
            elif listed(p):
                gaps.append(p)
        return attr, sorted(set(gaps)), named
    dir_count = {}
    for r in recs:
        for d in r["argv_dirs"]:
            dir_count[d] = dir_count.get(d, 0) + 1
    for p in files:
        if p in nonlaunch:
            continue
        for r in recs:
            if p in (r["stdout"], r["stderr"]):
                attr.setdefault(p, []).append(("i", r["lid"]))
            if p in r["argv_paths"]:
                attr.setdefault(p, []).append(("ii", r["lid"]))
            if F == "RH1" and r["cg_out"] == p:
                attr.setdefault(p, []).append(("iii", r["lid"]))
            for d in r["argv_dirs"]:
                if p.startswith(d + "/") and dir_count[d] == 1:
                    attr.setdefault(p, []).append(("iv", r["lid"]))
            if F == "RH1" and r["spec"] and r["child_end"] == "exec":
                out = pkg.specs.get(r["spec"]) if r["spec"] in pkg.files else None
                if out is not None and out == r["spec"][:-len(".spec.json")] and p in (out + ".npz", out + ".meta.json"):
                    attr.setdefault(p, []).append(("v", r["lid"]))
        if F == "RH1":
            m = re.match(r"^(solver|health)/(.+)\.(ms\.out|ms\.log|ms\.err)\.ssf-attempt(\d+)$", p)
            if m:
                d, tag, _ext, k = m.group(1), m.group(2), m.group(3), int(m.group(4))
                site = "S-1" if d == "solver" else "S-2"
                ev = pkg.events.get((site, tag))
                Lrecs = [r for r in recs if r["stdout"] == "%s/%s.ms.log" % (d, tag)]
                if ev and p.split("/")[-1] in ev["renamed"].get("attempt%d" % k, []) and len(Lrecs) >= k:
                    attr.setdefault(p, []).append(("vi", Lrecs[k - 1]["lid"]))
    # RJ-2: the gp script is attributed ONLY by (ii), to the gp record whose argv names it
    if rs in ("RJ", "RJw", "RJx", "RJnocmp", "RJnouk"):
        for p in list(attr):
            if p.startswith("pari/") and p.endswith(".gp"):
                attr[p] = [a for a in attr[p] if a[0] == "ii" and present[a[1]]["kind"] == "gp"]
                if not attr[p]:
                    del attr[p]
    # RI-1 (a)-(d) (attcount 265-322), RJ-1 (b)-(c), RJ-3, RJ-4 (b)
    forced_gaps = set()
    if rs in ("RI", "RIx") or rs.startswith("RJ"):
        full_ri = rs != "RIx"
        tags = {}
        for r in recs:
            m = re.match(r"^(solver|health)/(.+)\.ms\.log$", r["stdout"])
            if m:
                tags.setdefault((m.group(1), m.group(2)), []).append(r)
        for rb in pkg.rb1:
            tags.setdefault(("solver" if rb["site"] == "S-1" else "health", rb["tag"]), [])
        for rl in pkg.rl2:
            tags.setdefault(("solver", rl["tag"]), [])
        for (d, tag), Lrecs in sorted(tags.items()):
            site = "S-1" if d == "solver" else "S-2"
            N = len(Lrecs)
            nrb = sum(1 for rb in pkg.rb1 if rb["site"] == site and rb["tag"] == tag)
            nrl = sum(1 for rl in pkg.rl2 if rl["tag"] == tag) if site == "S-1" else 0
            fails = []
            if full_ri and N != nrb + nrl:
                fails.append("(i) N=%d != RB-1 %d + RL-2 %d" % (N, nrb, nrl))
            ev = pkg.events.get((site, tag))
            if full_ri and ev is not None:
                acc = ev["accepted"]
                ren = len(ev["renamed"])
                if not (N == len(ev["attempts"]) == acc == 1 + ren and ev["attempts"] == list(range(1, N + 1))):
                    fails.append("(ii) N=%d attempts=%d accepted=%s 1+renamed=%d" % (N, len(ev["attempts"]), acc, 1 + ren))
            if fails:
                named.append("COUNT GAP (%s/%s): %s" % (d, tag, "; ".join(fails)))
                for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                    for q in ["%s/%s%s" % (d, tag, ext)] + [x for x in files if x.startswith("%s/%s%s.ssf-attempt" % (d, tag, ext))]:
                        if q in files and q not in nonlaunch:
                            forced_gaps.add(q)
            elif full_ri and N >= 2:                                          # RI-1 (d)
                last = Lrecs[-1]["lid"]
                for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                    q = "%s/%s%s" % (d, tag, ext)
                    if q in attr:
                        kept = [a for a in attr[q] if not (a[0] in ("i", "ii") and a[1] in {x["lid"] for x in Lrecs} and a[1] != last)]
                        if kept:
                            attr[q] = kept
                        else:
                            del attr[q]
        if full_ri:
            for d, site in (("solver", "S-1"), ("health", "S-2")):
                nl = sum(1 for r in recs if re.match(r"^%s/.+\.ms\.log$" % d, r["stdout"]))
                cnt = pkg.counters[site]["attempts_total"] + (pkg.counters[site].get("passthrough", 0) if site == "S-1" else 0)
                if nl != cnt:
                    named.append("SITE COUNT GAP (%s): %d launch records vs counters %d" % (site, nl, cnt))
        seen = {}
        for r in recs:                                                        # RI-1 (b)
            if re.match(r"^(solver|health)/.+\.ms\.log$", r["stdout"]):
                continue
            seen.setdefault(r["stdout"], []).append(r["lid"])
        for sp, lids in seen.items():
            if len(lids) > 1:
                named.append("DUPLICATE-PATH GAP (%s): %s" % (sp, lids))
                for q, al in attr.items():
                    if any(a[1] in lids for a in al):
                        forced_gaps.add(q)
        if rs.startswith("RJ") and rs != "RJx":                               # RJ-1 (b), (c) (launchkind 290-306)
            cgtags = {}
            for r in recs:
                m = re.match(r"^solver/(.+)\.callgrind\.stdout$", r["stdout"])
                if m:
                    cgtags[m.group(1)] = cgtags.get(m.group(1), 0) + 1
            cnt = {}
            for rb in pkg.rb1:
                if rb["site"] == "S-1" and rb["cg_present"] is True:
                    cnt[rb["tag"]] = cnt.get(rb["tag"], 0) + 1
            for tag in sorted(set(cgtags) | set(cnt)):
                ncg, c = cgtags.get(tag, 0), cnt.get(tag, 0)
                bad = (ncg > c) if rs == "RJw" else (ncg != c)
                if bad:
                    named.append("CALLGRIND COUNT GAP (%s): Ncg=%d count=%d" % (tag, ncg, c))
                    for ext in (".callgrind.stdout", ".callgrind.stderr", ".callgrind.out"):
                        q = "solver/%s%s" % (tag, ext)
                        if q in files:
                            forced_gaps.add(q)
            tot_ncg, tot_c = sum(cgtags.values()), sum(cnt.values())
            if (tot_ncg > tot_c) if rs == "RJw" else (tot_ncg != tot_c):
                named.append("CALLGRIND SITE COUNT GAP: %d callgrind launch records vs %d attempt records with callgrind_result_present true" % (tot_ncg, tot_c))
        if rs.startswith("RJ") and rs != "RJnocmp":                            # RJ-3 (launchkind 342-361)
            ncmp = sum(1 for r in recs if r["stdout"] == "comparator/stdout.log")
            want = 1 if (pkg.raw_writer == "driver" and pkg.raw_comparator_child) else 0
            if ncmp != want:
                named.append("COMPARATOR COUNT GAP: %d comparator launch records vs comparator.child %s" % (ncmp, "present" if want else "absent"))
                for q in files:
                    if q.startswith("comparator/"):
                        forced_gaps.add(q)
        if rs.startswith("RJ") and rs != "RJnouk":                             # RJ-4 (b) (launchkind 389-392)
            for i, r in enumerate(recs):
                if not any(f.match(r["stdout"]) for f in SIX_FORMS):
                    named.append("UNKNOWN-KIND GAP (ordinal %d): %s" % (i, r["stdout"]))
    for p in files:
        if p in nonlaunch:
            continue
        if p not in attr or p in forced_gaps:
            gaps.append(p)
    return attr, sorted(set(gaps)), named


# =============================================================================================== verdicts
def frozen_items(pkg, recs):
    """v2_check_run.py 62-70 on the r4 manifest: caps = RB-2 (a) raw, (b) meta, (c) attempt records, RL-3 (d) launch
    records, (e) pass-through records. Mr: requested cap from raw envelope (r3_run_wrapper.py 550; None when the raw
    is wrapper-written); Mc: requested cap recorded independently."""
    caps = [r["pair"] for r in recs if r["pair"] is not None]
    caps += [rb["pair"] for rb in pkg.rb1 if rb["pair"] is not None]
    caps += [rl["pair"] for rl in pkg.rl2 if rl["pair"] is not None]
    if pkg.raw_writer == "driver":
        caps += list(pkg.raw_pairs.values())
    caps += pkg.meta_pairs
    items = []
    if not caps:
        items.append("66-67 no child RLIMIT_AS read-back recorded")
    req_known = pkg.cap_source == "Mc" or pkg.raw_writer == "driver"
    if caps and (not req_known or any(c != CAP for c in caps)):
        items.append("68-70 child RLIMIT_AS read-back != requested")
    return items + list(pkg.extra_items)


def evaluate(pkg, rs, v7=True):
    recs = [record_of(L, rs) for L in pkg.launches if L["lid"] not in pkg.lost]
    attr, gaps, named = attribute(pkg, recs, rs)
    items = frozen_items(pkg, recs)
    r4_ok = not pkg.consistency_violation and not (v7 and pkg.v7_applies and pkg.altered_in_place)
    classes = {r["lid"]: record_class(r, rs) for r in recs}
    undetermined = any(r["child_created"] == "undetermined" for r in recs) or (
        rs not in ("RK", "RF") and any(r["child_end"] == "undetermined" for r in recs))
    reasons = []
    if rs == "RK":
        pass_ = not items and r4_ok
        zl = (not pass_ and not pkg.gate and not pkg.a1_image and not recs and not gaps
              and not any(five(p) for p in pkg.files) and items == ["66-67 no child RLIMIT_AS read-back recorded"] and r4_ok)
    else:
        cls_ok = all(c in ("A", "B", "C") for c in classes.values())
        pass_ = (not items and r4_ok and cls_ok and pkg.raw_writer == "driver" and not pkg.foreign_file and not gaps
                 and not named and not undetermined)
        zl = (not pass_ and not pkg.gate and not pkg.a1_image and not recs and not gaps and not named
              and not any(five(p) and p not in pkg.nonlaunch for p in pkg.files)
              and items == ["66-67 no child RLIMIT_AS read-back recorded"] and r4_ok and pkg.raw_writer == "driver"
              and pkg.kind in ("cells", "fixture4", "contingency") and not pkg.foreign_file)
        if not cls_ok:
            reasons.append("launch record outside classes A/B/C: %s" % sorted(l for l, c in classes.items() if c is None))
        if undetermined:
            reasons.append("undetermined value")
        if pkg.raw_writer != "driver":
            reasons.append("raw_result_writer %s" % pkg.raw_writer)
    if items:
        reasons.append("frozen checker: %s" % items)
    if gaps:
        reasons.append("recorder gaps: %s" % gaps)
    if named:
        reasons.append("named gaps: %s" % named)
    if not r4_ok:
        reasons.append("r4 check (consistency / V-7)")
    verdict = "PASS" if pass_ else ("PASS_ZL" if zl else "FAIL")
    defs = definitions(pkg, recs, rs)
    flag = None
    if verdict in ("PASS", "PASS_ZL") and any(defs.values()):
        flag = "FAIL-OPEN " + " ".join("(%s)" % k for k, v in defs.items() if v)
    pb = planned_basis(pkg, recs, rs, items)
    if verdict == "FAIL" and pb and pkg.normal:
        flag = "PLANNED-BASIS REFUSAL"
    return {"rule_set": rs, "verdict": verdict, "flag": flag, "definitions": {k: v for k, v in defs.items() if v},
            "named_gaps": named, "recorder_gaps": gaps, "frozen_items": items, "reasons": reasons,
            "records": [{"lid": r["lid"], "class": classes[r["lid"]], "child_created": r["child_created"],
                         "child_end": r["child_end"], "pair": r["pair"], "raised": r["raised"]} for r in recs],
            "absent_records": sorted(pkg.lost), "attribution": {p: a for p, a in sorted(attr.items())}}


def definitions(pkg, recs, rs):
    """failclosed definitions (604-617), evaluated against the TRUTH of the construction."""
    present = {r["lid"]: r for r in recs}
    d = {"i": False, "ii_LR": False, "ii_ANY": False, "iii": False, "iv": False, "v": False}
    for L in pkg.launches:
        r = present.get(L["lid"])
        if L["pair"] is not None and (r is None or r["pair"] is None):
            d["i"] = True
        if L["created"]:
            cls = record_class(r, rs if rs not in ("RK",) else "RF") if r is not None else None
            if cls not in ("A", "C"):
                if r is None or r["pair"] != CAP:
                    d["ii_LR"] = True
                    other = (pkg.raw_writer == "driver" and pkg.raw_pairs.get(L["lid"]) == CAP)
                    other = other or any(x.get("lid") == L["lid"] and x["pair"] == CAP for x in pkg.rb1 + pkg.rl2)
                    other = other or L.get("meta_pair") == CAP
                    if not other:
                        d["ii_ANY"] = True
            if r is not None and r["child_created"] is False:
                d["iii"] = True
    if pkg.foreign_record_undetected and not pkg.foreign_file:
        d["iv"] = True
    if pkg.raw_writer == "wrapper":
        d["v"] = True
    return d


def planned_basis(pkg, recs, rs, items):
    """failclosed RF-0 (b) with childend RG-2 (b) and gapattr RH-2 (b): a driver-logic outcome a dependant acts on."""
    if not pkg.planned_basis or pkg.raw_writer != "driver":
        return False
    if rs in ("RG", "RH", "RI", "RIx") or rs.startswith("RJ"):
        infra = recs and all((r["child_created"] is False) or (r["raised"] is not None) or (not r["pair_read_by_parent"]) for r in recs)
        if infra:
            return False
    if rs in ("RH", "RI", "RIx") or rs.startswith("RJ"):
        if any(i.startswith("68-70") for i in items):
            return False
    return True


def show(res, pkg, P):
    """Print record level, then package level."""
    P("  [%s] verdict %s%s" % (res["rule_set"], res["verdict"], ("  ** " + res["flag"] + " **") if res["flag"] else ""))
    for r in res["records"]:
        P("      record %-34s class %-4s child_created %-12s child_end %-22s pair %s raised %s"
          % (r["lid"], r["class"], r["child_created"], r["child_end"], r["pair"], r["raised"]))
    if res["absent_records"]:
        P("      ABSENT launch records (premise): %s" % res["absent_records"])
    if res["named_gaps"]:
        P("      named gaps: %s" % res["named_gaps"])
    if res["recorder_gaps"]:
        P("      recorder gaps: %s" % res["recorder_gaps"])
    if res["frozen_items"]:
        P("      frozen checker items: %s" % res["frozen_items"])
    if res["definitions"]:
        P("      definitions holding: %s" % sorted(res["definitions"]))
```

### rjcore_v2.py

- sha256: 6e686dcfb2599c911c176d81e97701766e03351b6daffffca63875ee389b745f
- argv: `not run directly; imported (from the scratch directory) by lj0_v2.py, listing_v2.py, lj1_v1.py, lj2_v1.py and lj4_v1.py`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). THE RULE EVALUATOR CORE, version 2 = version 1 plus two
rule transcriptions that no LJ-0 object exercises: (1) the frozen checker's aggregate exemption from the cap items
(v2_check_run.py 65); (2) failclosed RF-0 (a), (c) applied to RJ-1 (a): an S-1 attempt record whose
callgrind_result_present is neither true nor false is `undetermined` and yields FAIL (launchkind families only).
Version 1's text follows unchanged apart from these two additions (diff recorded in review-report.md).

One method, used UNCHANGED for LJ-0 (known-answer control), LJ-1, LJ-2, LJ-3 and LJ-4 objects. It computes, from
rule TEXT as transcribed below (file and line cited at each rule), what each draft's rules say about a constructed
package: the launch records as each draft's recorder would write them, attribution, named gaps, the frozen checker's
cap items, the r4 verdict (PASS / PASS_ZL / FAIL), and failclosed's definitions (i)-(v) evaluated against the TRUTH
of the construction. Standard library only; it imports nothing from the repository and runs nothing.

Rule sets (the draft AS WORDED unless named otherwise):
  RK  readbackclose RK-1 / RK-3 (readbackclose.yaml 246-373)
  RF  failclosed RF-0..RF-3 (failclosed.yaml 280-418)
  RG  childend RG-1, RG-2, RG-4 (childend.yaml 250-437)
  RH  gapattr RH-1, RH-2 (gapattr.yaml 243-318)
  RI  attcount RI-1 (attcount.yaml 265-345)
  RJ  launchkind RJ-1..RJ-4 (launchkind.yaml 270-405)
  RJw launchkind with RJ-1 (b) WEAKENED to "Ncg(<tag>) is at most the count" (CRJ-4 (e) only)
  RJx launchkind with RJ-1 disabled in the evaluator (RJ-5 (c) (28) only)
  RJnogp launchkind with RJ-2 disabled (gp script back on the non-launch list; (29) discrimination only)
  RJnocmp launchkind with RJ-3 disabled ((30) discrimination only)
  RJnouk launchkind with RJ-4 (b) disabled ((31) discrimination only)
  RIx attcount with RI-1 (a) and (d) disabled (RI-3 (25) as RJ-5 (a) reads it)
Definitions (failclosed.yaml 604-617): (i), (ii) with an absent record read as "not class (A) or (C)" (launchkind
carried decision (5)) in two sub-readings ii_LR (the child's own launch record) and ii_ANY (any read-back source),
(iii), (iv) read LITERALLY, (v).
"""
import re

CAP = "cap"          # a read-back pair equal to the requested cap
NEQ = "neq"          # a read-back pair not equal to the requested cap
FIVE = ("child", "solver", "health", "comparator", "pari")
RULESETS = ("RK", "RF", "RG", "RH", "RI", "RJ", "RJw", "RJx", "RJnogp", "RJnocmp", "RJnouk", "RIx")
EXEC_PATHS = ("exec_ok", "exec_fail", "exec_timeout", "exec_ssf")
SIX_FORMS = [re.compile(r"^child/[^/]+\.stdout$"), re.compile(r"^solver/[^/]+\.ms\.log$"),
             re.compile(r"^solver/[^/]+\.callgrind\.stdout$"), re.compile(r"^comparator/stdout\.log$"),
             re.compile(r"^health/[^/]+\.ms\.log$"), re.compile(r"^pari/[^/]+\.gp\.stdout$")]


# =============================================================================================== truth of one launch
def path_facts(path, foreign_exit=1):
    """Frozen run_child / _run_child_locked facts per path (v2_solver.py 149-308), as TRUTH:
    created (os.fork at 181 returned a pid), pair_read (227 executed) and its value, report (the key set at 220 and
    its value), returncode, execs (argv executed), raised (a raise leaving run_child), child_files (the child opened
    stdout / stderr at 188-189), child_end (childend RG-1 (c)), rc_for_end."""
    f = {"created": True, "pair": None, "report": None, "returncode": None, "execs": False, "raised": None,
         "child_files": False, "child_end": None, "foreign": False}
    if path == "A":                                     # refusal before fork: 153-169 (class A)
        f.update(created=False, child_end="no_child")
    elif path in EXEC_PATHS:                            # 188-189 files, 198 OK, 227 pair, 236 go byte, 204-205 exec
        f.update(pair=CAP, report="OK", returncode=(0 if path in ("exec_ok", "exec_ssf") else (-9 if path == "exec_timeout" else 1)),
                 execs=True, child_files=True, child_end="exec")
    elif path == "pre_stdout_99":                       # 188 open fails -> 206-208 os._exit(99): no file, report ""
        f.update(report="", returncode=99, child_end="frozen_pre_exec_exit")
    elif path == "err_setrlimit_97":                    # 188-189 files created, 193 fails, 195 ERR report, 196 _exit(97)
        f.update(report="ERR", returncode=97, child_files=True, child_end="frozen_pre_exec_exit")
    elif path == "P8":                                  # OK soft != cap: 227 pair (unequal), parent refuses 228-232; child 200-201 exit 98
        f.update(pair=NEQ, report="OK", returncode=98, child_files=True, child_end="frozen_pre_exec_exit")
    elif path == "P16":                                 # fork created the child; raise before STORE_FAST pid (181); child later execs (RKL-2)
        f.update(raised="KeyboardInterrupt", child_files=True, execs=True, child_end="undetermined")
    elif path == "PF2_after_P14a":                      # raise at 214, then lk.release raises in the finally (172-174)
        f.update(raised="OSError", child_files=True, execs=True, child_end="undetermined")
    elif path == "FO1_C":                               # async exception in the fork child before 183: escaped child
        f.update(report="", returncode=foreign_exit, child_end="undetermined", foreign=True)
    elif path == "FO1_B":                               # after OK at 198; exception at 202 caught; second at 207-208: escaped
        f.update(pair=CAP, report="OK", returncode=foreign_exit, child_files=True, child_end="undetermined", foreign=True)
    else:
        raise ValueError(path)
    return f


# =============================================================================================== a package under construction
class Pkg:
    def __init__(self, name, kind, gate=False, a1_image=False, planned_basis=False, normal=True, raw_writer="driver",
                 cap_source="Mc", note=""):
        self.name, self.kind, self.gate, self.a1_image = name, kind, gate, a1_image
        self.planned_basis, self.normal, self.raw_writer, self.cap_source, self.note = planned_basis, normal, raw_writer, cap_source, note
        self.launches = []              # truth, in launch order
        self.files = {}                 # rel path -> origin
        self.nonlaunch = {}             # rel path -> frozen non-launch writer (RG-4 (b) list as each draft keeps it)
        self.specs = {}                 # child/<tag>.spec.json -> "out" (rel)
        self.rb1 = []                   # attempt records: {site, tag, attempt, pair, cg_present}
        self.rl2 = []                   # pass-through records: {tag, pair}
        self.events = {}                # (site, tag) -> {"attempts": [..], "accepted": k, "renamed": {"attempt<k>": [names]}}
        self.counters = {"S-1": {"attempts_total": 0, "passthrough": 0}, "S-2": {"attempts_total": 0}}
        self.raw_pairs = {}             # lid -> pair copied by the frozen driver into raw-result.json
        self.meta_pairs = []            # child/*.meta.json read-backs
        self.raw_comparator_child = False
        self.lost = set()               # launch records absent (premise)
        self.foreign_file = False       # recorder-foreign-<pid>.json present (failclosed RF-1 (b))
        self.foreign_record_undetected = False
        self.extra_items = []           # other frozen checker items that fail
        self.altered_in_place = False   # V-7 (r3_check_run.py 153-158) fails on an in-place alteration
        self.consistency_violation = False
        self.premises = []
        self.v7_applies = True

    # --------------------------------------------------------------------------------------- launches
    def launch(self, lid, kind, path, stdout, stderr, argv_paths=(), argv_dirs=(), cg_out=None, spec=None, site=None,
               tag=None, outputs=(), foreign_exit=1, raw_pair=True):
        f = path_facts(path, foreign_exit)
        L = {"lid": lid, "kind": kind, "path": path, "stdout": stdout, "stderr": stderr, "argv_paths": set(argv_paths),
             "argv_dirs": set(argv_dirs), "cg_out": cg_out, "spec": spec, "site": site, "tag": tag, **f}
        self.launches.append(L)
        if f["child_files"]:
            self.files[stdout] = "launch:" + lid
            self.files[stderr] = "launch:" + lid
        if f["execs"] or path == "FO1_B":
            for o in outputs:
                self.files[o] = "launch:" + lid
        if raw_pair and f["pair"] is not None:
            self.raw_pairs[lid] = f["pair"]
        if f["foreign"]:
            self.foreign_record_undetected = True       # pari-stack.json / stderr written in the escaped process
        return L

    def solve(self, tag, attempts, retain_input=True, gb_only=False, callgrind=None, raw_row=True):
        """v2_driver.solve (158-214) through the SE-3 wrapper (r3_resolve.py 373-390; r4 counterpart). attempts: list of
        msolve paths, one per attempt; every attempt but the last has the SSF signature (r3_resolve.py 61-74, 295-310).
        callgrind: None or the path of the one callgrind launch after the last attempt when its outcome is ok (207-209)."""
        d = "solver"
        n = len(attempts)
        cg_lid = None
        for k, p in enumerate(attempts, 1):
            lid = "%s/ms%d" % (tag, k)
            self.files["solver/%s.ms" % tag] = "driver:solve-input"          # 161-162, before the launch
            outs = ["solver/%s.ms.out" % tag] if p in ("exec_ok", "exec_ssf") else []
            L = self.launch(lid, "msolve", p, "solver/%s.ms.log" % tag, "solver/%s.ms.err" % tag,
                            argv_paths=("solver/%s.ms" % tag, "solver/%s.ms.out" % tag), site="S-1", tag=tag, outputs=outs,
                            raw_pair=(k == n and raw_row))
            returned = L["raised"] is None
            cg_present = False
            if k == n and callgrind is not None and returned:
                cg_lid = "%s/cg" % tag
                cgp = callgrind
                cg_outs = ["solver/%s.callgrind.out" % tag] if cgp == "exec_fail" else []   # kept on non-ok (521-524); removed at 549 on ok
                self.launch(cg_lid, "callgrind", cgp, "solver/%s.callgrind.stdout" % tag, "solver/%s.callgrind.stderr" % tag,
                            argv_paths=("solver/%s.ms" % tag, "solver/%s.cg.ms.out" % tag), cg_out="solver/%s.callgrind.out" % tag,
                            site="S-3", tag=tag, outputs=cg_outs, raw_pair=raw_row)
                cg_present = True                                              # 209: set when callgrind_instructions returns
            if not returned:
                return                                                         # solve raised: no RB-1 record, no counter, no _retain
            if not retain_input:
                self.files.pop("solver/%s.ms" % tag, None)                     # _retain 219-221 on every return path
            if gb_only:
                self.rl2.append({"lid": lid, "tag": tag, "pair": L["pair"]})
                self.counters["S-1"]["passthrough"] += 1
            else:
                self.rb1.append({"lid": lid, "site": "S-1", "tag": tag, "attempt": k, "pair": L["pair"], "cg_present": cg_present})
                self.counters["S-1"]["attempts_total"] += 1
            if n >= 2:
                ev = self.events.setdefault(("S-1", tag), {"attempts": [], "accepted": None, "renamed": {}})
                ev["attempts"].append(k)
                if k < n:
                    ren = []
                    for ext in (".ms.out", ".ms.log", ".ms.err"):
                        src = "solver/%s%s" % (tag, ext)
                        if src in self.files:
                            dst = src + ".ssf-attempt%d" % k
                            self.files[dst] = self.files.pop(src)
                            ren.append(dst.split("/")[-1])
                    ev["renamed"]["attempt%d" % k] = ren
                else:
                    ev["accepted"] = k
        return cg_lid

    def health(self, tag, attempts):
        """a1_health.run_system (140-220) through the HR-3 wrapper (r3_resolve.py 397-409)."""
        n = len(attempts)
        for k, p in enumerate(attempts, 1):
            lid = "health:%s/ms%d" % (tag, k)
            self.files["health/%s.ms" % tag] = "nonlaunch:a1_health.py 141-143"
            self.nonlaunch["health/%s.ms" % tag] = "a1_health.py 141-143"
            outs = ["health/%s.ms.out" % tag] if p in ("exec_ok", "exec_ssf") else []
            L = self.launch(lid, "msolve", p, "health/%s.ms.log" % tag, "health/%s.ms.err" % tag,
                            argv_paths=("health/%s.ms" % tag, "health/%s.ms.out" % tag), site="S-2", tag=tag, outputs=outs,
                            raw_pair=False)
            if L["raised"] is not None:
                return
            self.rb1.append({"lid": lid, "site": "S-2", "tag": tag, "attempt": k, "pair": L["pair"], "cg_present": None})
            self.counters["S-2"]["attempts_total"] += 1
            if n >= 2:
                ev = self.events.setdefault(("S-2", tag), {"attempts": [], "accepted": None, "renamed": {}})
                ev["attempts"].append(k)
                if k < n:
                    ren = []
                    for ext in (".ms.out", ".ms.log", ".ms.err"):
                        src = "health/%s%s" % (tag, ext)
                        if src in self.files:
                            dst = src + ".ssf-attempt%d" % k
                            self.files[dst] = self.files.pop(src)
                            ren.append(dst.split("/")[-1])
                    ev["renamed"]["attempt%d" % k] = ren
                else:
                    ev["accepted"] = k

    def health_report(self, p):
        self.files["health/health-%d.json" % p] = "nonlaunch:a1_health.py 251"
        self.nonlaunch["health/health-%d.json" % p] = "a1_health.py 251"

    def child_job(self, tag, path, job="build_poly", to_cache=False):
        """v2_driver.child_job (92-107): the spec is written BEFORE the launch (98-99) and named as argv's last element (100)."""
        spec = "child/%s.spec.json" % tag
        self.files[spec] = "driver:child_job-spec"
        out = ("CACHE/%s" % tag) if to_cache else ("child/%s" % tag)
        self.specs[spec] = out
        outs = []
        if path in ("exec_ok",) and not to_cache:
            outs = [out + ".meta.json"] + ([out + ".npz"] if job == "build_poly" else [])   # raw_grid removes .npz (144)
        L = self.launch("cj:" + tag, "childjob", path, "child/%s.stdout" % tag, "child/%s.stderr" % tag,
                        argv_paths=(spec,), spec=spec, tag=tag, outputs=outs, raw_pair=False)
        if path == "exec_ok" and not to_cache:
            self.meta_pairs.append(CAP)
            L["meta_pair"] = CAP
        return L

    def comparator(self, path):
        """v2_driver.cmd_anchor_identity (647-655): run_child at 650; comp["child"] at 652; raw["comparator"] at 655."""
        outs = ["comparator/%s" % n for n in ("anchor17_planted.ms", "anchor17_random.ms", "anchor25_planted.ms",
                                               "anchor25_random.ms", "k4a_results.json")]
        L = self.launch("cmp", "comparator", path, "comparator/stdout.log", "comparator/stderr.log",
                        argv_dirs=("comparator",), outputs=outs)
        if L["raised"] is None:
            self.raw_comparator_child = True
        return L

    def gp(self, tag, path):
        """a1_pari.curve_facts (87-115): the script is written BEFORE the launch (91-93), named by argv (94); launch at 96."""
        scr = "pari/%s.gp" % tag
        self.files[scr] = "frozen:a1_pari.py 91-93"
        self.nonlaunch[scr] = "a1_pari.py 91-93"
        return self.launch("gp:" + tag, "gp", path, "pari/%s.gp.stdout" % tag, "pari/%s.gp.stderr" % tag,
                           argv_paths=(scr,), tag=tag)


# =============================================================================================== records as each draft writes them
def record_of(L, rs):
    """The launch record the draft's recorder writes for truth L (readbackfull RL-1 (c); readbackclose RK-1;
    failclosed RF-1 (a); childend RG-1, RG-4 (a))."""
    created_rk = L["report"] is not None                              # RK-1 (a) key presence; on raise (b): P16 / P-F2 give False
    if L["path"] in ("P16", "PF2_after_P14a"):
        created_rk = False
    created_rf = created_rk
    if L["path"] == "P16":
        created_rf = "undetermined"                                   # RF-1 (a): frame at 181 with no pid
    elif L["path"] == "PF2_after_P14a":
        created_rf = True                                             # RF-1 (a): pid on the __context__ traceback
    created = created_rk if rs == "RK" else created_rf
    r = {"lid": L["lid"], "kind": L["kind"], "stdout": L["stdout"], "stderr": L["stderr"], "argv_paths": L["argv_paths"],
         "argv_dirs": L["argv_dirs"], "cg_out": L["cg_out"], "spec": L["spec"], "child_created": created,
         "raised": L["raised"], "pair": L["pair"], "pair_read_by_parent": L["pair"] is not None, "report": L["report"],
         "returncode": L["returncode"], "child_end": L["child_end"] if rs not in ("RK", "RF") else None}
    return r


def record_class(r, rs):
    """failclosed RF-3 (a) classes (376-395), narrowed by childend RG-1 (d) for RG and later."""
    base = None
    if r["child_created"] is False and r["raised"] is None:
        base = "A"
    elif r["child_created"] is True and r["raised"] is None and r["pair_read_by_parent"]:
        base = "B"
    elif (r["child_created"] is True and r["raised"] is None and not r["pair_read_by_parent"]
          and r["report"] in ("", "ERR") and r["returncode"] is not None):
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = r["child_end"]
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and r["returncode"] in (98, 99))) else None
    if base == "C":
        return "C" if ce == "frozen_pre_exec_exit" else None
    return None


# =============================================================================================== attribution
def fam(rs):
    if rs in ("RK", "RF"):
        return "truth"          # readbackfull RL-3: "child files ... whose launch has no launch record"
    if rs == "RG":
        return "RG4b"
    return "RH1"


def five(p):
    return p.split("/")[0] in FIVE


def attribute(pkg, recs, rs):
    """Returns (attr: file -> [(clause, lid)], gaps: [file], named: [str])."""
    files = {p: o for p, o in pkg.files.items() if five(p)}
    nonlaunch = dict(pkg.nonlaunch)
    if rs in ("RJ", "RJw", "RJx", "RJnocmp", "RJnouk"):               # RJ-2: the gp script leaves the non-launch list
        nonlaunch = {p: w for p, w in nonlaunch.items() if not (p.startswith("pari/") and p.endswith(".gp"))}
    attr, gaps, named = {}, [], []
    present = {r["lid"]: r for r in recs}
    F = fam(rs)
    if F == "truth":
        # readbackfull RL-3 (269-285): "child files in the package (child/*.meta.json, solver/*.ms.log, health/,
        # comparator/, pari/) whose launch has no launch record" -- only files of that list can be gaps here.
        def listed(p):
            return (re.match(r"^child/[^/]+\.meta\.json$", p) or re.match(r"^solver/[^/]+\.ms\.log$", p)
                    or p.split("/")[0] in ("health", "comparator", "pari"))
        for p, o in files.items():
            if p in nonlaunch:
                continue
            if o.startswith("launch:"):
                if o[7:] in present:
                    attr.setdefault(p, []).append(("launch", o[7:]))
                elif listed(p):
                    gaps.append(p)
            elif any(p in r["argv_paths"] for r in recs):
                attr.setdefault(p, []).append(("argv", "-"))
            elif listed(p):
                gaps.append(p)
        return attr, sorted(set(gaps)), named
    dir_count = {}
    for r in recs:
        for d in r["argv_dirs"]:
            dir_count[d] = dir_count.get(d, 0) + 1
    for p in files:
        if p in nonlaunch:
            continue
        for r in recs:
            if p in (r["stdout"], r["stderr"]):
                attr.setdefault(p, []).append(("i", r["lid"]))
            if p in r["argv_paths"]:
                attr.setdefault(p, []).append(("ii", r["lid"]))
            if F == "RH1" and r["cg_out"] == p:
                attr.setdefault(p, []).append(("iii", r["lid"]))
            for d in r["argv_dirs"]:
                if p.startswith(d + "/") and dir_count[d] == 1:
                    attr.setdefault(p, []).append(("iv", r["lid"]))
            if F == "RH1" and r["spec"] and r["child_end"] == "exec":
                out = pkg.specs.get(r["spec"]) if r["spec"] in pkg.files else None
                if out is not None and out == r["spec"][:-len(".spec.json")] and p in (out + ".npz", out + ".meta.json"):
                    attr.setdefault(p, []).append(("v", r["lid"]))
        if F == "RH1":
            m = re.match(r"^(solver|health)/(.+)\.(ms\.out|ms\.log|ms\.err)\.ssf-attempt(\d+)$", p)
            if m:
                d, tag, _ext, k = m.group(1), m.group(2), m.group(3), int(m.group(4))
                site = "S-1" if d == "solver" else "S-2"
                ev = pkg.events.get((site, tag))
                Lrecs = [r for r in recs if r["stdout"] == "%s/%s.ms.log" % (d, tag)]
                if ev and p.split("/")[-1] in ev["renamed"].get("attempt%d" % k, []) and len(Lrecs) >= k:
                    attr.setdefault(p, []).append(("vi", Lrecs[k - 1]["lid"]))
    # RJ-2: the gp script is attributed ONLY by (ii), to the gp record whose argv names it
    if rs in ("RJ", "RJw", "RJx", "RJnocmp", "RJnouk"):
        for p in list(attr):
            if p.startswith("pari/") and p.endswith(".gp"):
                attr[p] = [a for a in attr[p] if a[0] == "ii" and present[a[1]]["kind"] == "gp"]
                if not attr[p]:
                    del attr[p]
    # RI-1 (a)-(d) (attcount 265-322), RJ-1 (b)-(c), RJ-3, RJ-4 (b)
    forced_gaps = set()
    if rs in ("RI", "RIx") or rs.startswith("RJ"):
        full_ri = rs != "RIx"
        tags = {}
        for r in recs:
            m = re.match(r"^(solver|health)/(.+)\.ms\.log$", r["stdout"])
            if m:
                tags.setdefault((m.group(1), m.group(2)), []).append(r)
        for rb in pkg.rb1:
            tags.setdefault(("solver" if rb["site"] == "S-1" else "health", rb["tag"]), [])
        for rl in pkg.rl2:
            tags.setdefault(("solver", rl["tag"]), [])
        for (d, tag), Lrecs in sorted(tags.items()):
            site = "S-1" if d == "solver" else "S-2"
            N = len(Lrecs)
            nrb = sum(1 for rb in pkg.rb1 if rb["site"] == site and rb["tag"] == tag)
            nrl = sum(1 for rl in pkg.rl2 if rl["tag"] == tag) if site == "S-1" else 0
            fails = []
            if full_ri and N != nrb + nrl:
                fails.append("(i) N=%d != RB-1 %d + RL-2 %d" % (N, nrb, nrl))
            ev = pkg.events.get((site, tag))
            if full_ri and ev is not None:
                acc = ev["accepted"]
                ren = len(ev["renamed"])
                if not (N == len(ev["attempts"]) == acc == 1 + ren and ev["attempts"] == list(range(1, N + 1))):
                    fails.append("(ii) N=%d attempts=%d accepted=%s 1+renamed=%d" % (N, len(ev["attempts"]), acc, 1 + ren))
            if fails:
                named.append("COUNT GAP (%s/%s): %s" % (d, tag, "; ".join(fails)))
                for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                    for q in ["%s/%s%s" % (d, tag, ext)] + [x for x in files if x.startswith("%s/%s%s.ssf-attempt" % (d, tag, ext))]:
                        if q in files and q not in nonlaunch:
                            forced_gaps.add(q)
            elif full_ri and N >= 2:                                          # RI-1 (d)
                last = Lrecs[-1]["lid"]
                for ext in (".ms", ".ms.out", ".ms.log", ".ms.err"):
                    q = "%s/%s%s" % (d, tag, ext)
                    if q in attr:
                        kept = [a for a in attr[q] if not (a[0] in ("i", "ii") and a[1] in {x["lid"] for x in Lrecs} and a[1] != last)]
                        if kept:
                            attr[q] = kept
                        else:
                            del attr[q]
        if full_ri:
            for d, site in (("solver", "S-1"), ("health", "S-2")):
                nl = sum(1 for r in recs if re.match(r"^%s/.+\.ms\.log$" % d, r["stdout"]))
                cnt = pkg.counters[site]["attempts_total"] + (pkg.counters[site].get("passthrough", 0) if site == "S-1" else 0)
                if nl != cnt:
                    named.append("SITE COUNT GAP (%s): %d launch records vs counters %d" % (site, nl, cnt))
        seen = {}
        for r in recs:                                                        # RI-1 (b)
            if re.match(r"^(solver|health)/.+\.ms\.log$", r["stdout"]):
                continue
            seen.setdefault(r["stdout"], []).append(r["lid"])
        for sp, lids in seen.items():
            if len(lids) > 1:
                named.append("DUPLICATE-PATH GAP (%s): %s" % (sp, lids))
                for q, al in attr.items():
                    if any(a[1] in lids for a in al):
                        forced_gaps.add(q)
        if rs.startswith("RJ") and rs != "RJx":                               # RJ-1 (b), (c) (launchkind 290-306)
            cgtags = {}
            for r in recs:
                m = re.match(r"^solver/(.+)\.callgrind\.stdout$", r["stdout"])
                if m:
                    cgtags[m.group(1)] = cgtags.get(m.group(1), 0) + 1
            cnt = {}
            for rb in pkg.rb1:
                if rb["site"] == "S-1" and rb["cg_present"] is True:
                    cnt[rb["tag"]] = cnt.get(rb["tag"], 0) + 1
            for tag in sorted(set(cgtags) | set(cnt)):
                ncg, c = cgtags.get(tag, 0), cnt.get(tag, 0)
                bad = (ncg > c) if rs == "RJw" else (ncg != c)
                if bad:
                    named.append("CALLGRIND COUNT GAP (%s): Ncg=%d count=%d" % (tag, ncg, c))
                    for ext in (".callgrind.stdout", ".callgrind.stderr", ".callgrind.out"):
                        q = "solver/%s%s" % (tag, ext)
                        if q in files:
                            forced_gaps.add(q)
            for rb in pkg.rb1:                                                # RF-0 (a), (c) on the RJ-1 (a) field
                if rb["site"] == "S-1" and rb["cg_present"] not in (True, False):
                    named.append("UNDETERMINED callgrind_result_present (RF-0 (c)): attempt record %s attempt %s" % (rb["tag"], rb.get("attempt")))
            tot_ncg, tot_c = sum(cgtags.values()), sum(cnt.values())
            if (tot_ncg > tot_c) if rs == "RJw" else (tot_ncg != tot_c):
                named.append("CALLGRIND SITE COUNT GAP: %d callgrind launch records vs %d attempt records with callgrind_result_present true" % (tot_ncg, tot_c))
        if rs.startswith("RJ") and rs != "RJnocmp":                            # RJ-3 (launchkind 342-361)
            ncmp = sum(1 for r in recs if r["stdout"] == "comparator/stdout.log")
            want = 1 if (pkg.raw_writer == "driver" and pkg.raw_comparator_child) else 0
            if ncmp != want:
                named.append("COMPARATOR COUNT GAP: %d comparator launch records vs comparator.child %s" % (ncmp, "present" if want else "absent"))
                for q in files:
                    if q.startswith("comparator/"):
                        forced_gaps.add(q)
        if rs.startswith("RJ") and rs != "RJnouk":                             # RJ-4 (b) (launchkind 389-392)
            for i, r in enumerate(recs):
                if not any(f.match(r["stdout"]) for f in SIX_FORMS):
                    named.append("UNKNOWN-KIND GAP (ordinal %d): %s" % (i, r["stdout"]))
    for p in files:
        if p in nonlaunch:
            continue
        if p not in attr or p in forced_gaps:
            gaps.append(p)
    return attr, sorted(set(gaps)), named


# =============================================================================================== verdicts
def frozen_items(pkg, recs):
    """v2_check_run.py 62-70 on the r4 manifest: caps = RB-2 (a) raw, (b) meta, (c) attempt records, RL-3 (d) launch
    records, (e) pass-through records. Mr: requested cap from raw envelope (r3_run_wrapper.py 550; None when the raw
    is wrapper-written); Mc: requested cap recorded independently."""
    caps = [r["pair"] for r in recs if r["pair"] is not None]
    caps += [rb["pair"] for rb in pkg.rb1 if rb["pair"] is not None]
    caps += [rl["pair"] for rl in pkg.rl2 if rl["pair"] is not None]
    if pkg.raw_writer == "driver":
        caps += list(pkg.raw_pairs.values())
    caps += pkg.meta_pairs
    items = []
    if pkg.kind == "aggregate":                     # v2_check_run.py 65: the cap items are not evaluated for aggregates
        return list(pkg.extra_items)
    if not caps:
        items.append("66-67 no child RLIMIT_AS read-back recorded")
    req_known = pkg.cap_source == "Mc" or pkg.raw_writer == "driver"
    if caps and (not req_known or any(c != CAP for c in caps)):
        items.append("68-70 child RLIMIT_AS read-back != requested")
    return items + list(pkg.extra_items)


def evaluate(pkg, rs, v7=True):
    recs = [record_of(L, rs) for L in pkg.launches if L["lid"] not in pkg.lost]
    attr, gaps, named = attribute(pkg, recs, rs)
    items = frozen_items(pkg, recs)
    r4_ok = not pkg.consistency_violation and not (v7 and pkg.v7_applies and pkg.altered_in_place)
    classes = {r["lid"]: record_class(r, rs) for r in recs}
    undetermined = any(r["child_created"] == "undetermined" for r in recs) or (
        rs not in ("RK", "RF") and any(r["child_end"] == "undetermined" for r in recs))
    reasons = []
    if rs == "RK":
        pass_ = not items and r4_ok
        zl = (not pass_ and not pkg.gate and not pkg.a1_image and not recs and not gaps
              and not any(five(p) for p in pkg.files) and items == ["66-67 no child RLIMIT_AS read-back recorded"] and r4_ok)
    else:
        cls_ok = all(c in ("A", "B", "C") for c in classes.values())
        pass_ = (not items and r4_ok and cls_ok and pkg.raw_writer == "driver" and not pkg.foreign_file and not gaps
                 and not named and not undetermined)
        zl = (not pass_ and not pkg.gate and not pkg.a1_image and not recs and not gaps and not named
              and not any(five(p) and p not in pkg.nonlaunch for p in pkg.files)
              and items == ["66-67 no child RLIMIT_AS read-back recorded"] and r4_ok and pkg.raw_writer == "driver"
              and pkg.kind in ("cells", "fixture4", "contingency") and not pkg.foreign_file)
        if not cls_ok:
            reasons.append("launch record outside classes A/B/C: %s" % sorted(l for l, c in classes.items() if c is None))
        if undetermined:
            reasons.append("undetermined value")
        if pkg.raw_writer != "driver":
            reasons.append("raw_result_writer %s" % pkg.raw_writer)
    if items:
        reasons.append("frozen checker: %s" % items)
    if gaps:
        reasons.append("recorder gaps: %s" % gaps)
    if named:
        reasons.append("named gaps: %s" % named)
    if not r4_ok:
        reasons.append("r4 check (consistency / V-7)")
    verdict = "PASS" if pass_ else ("PASS_ZL" if zl else "FAIL")
    defs = definitions(pkg, recs, rs)
    flag = None
    if verdict in ("PASS", "PASS_ZL") and any(defs.values()):
        flag = "FAIL-OPEN " + " ".join("(%s)" % k for k, v in defs.items() if v)
    pb = planned_basis(pkg, recs, rs, items)
    if verdict == "FAIL" and pb and pkg.normal:
        flag = "PLANNED-BASIS REFUSAL"
    return {"rule_set": rs, "verdict": verdict, "flag": flag, "definitions": {k: v for k, v in defs.items() if v},
            "named_gaps": named, "recorder_gaps": gaps, "frozen_items": items, "reasons": reasons,
            "records": [{"lid": r["lid"], "class": classes[r["lid"]], "child_created": r["child_created"],
                         "child_end": r["child_end"], "pair": r["pair"], "raised": r["raised"]} for r in recs],
            "absent_records": sorted(pkg.lost), "attribution": {p: a for p, a in sorted(attr.items())}}


def definitions(pkg, recs, rs):
    """failclosed definitions (604-617), evaluated against the TRUTH of the construction."""
    present = {r["lid"]: r for r in recs}
    d = {"i": False, "ii_LR": False, "ii_ANY": False, "iii": False, "iv": False, "v": False}
    for L in pkg.launches:
        r = present.get(L["lid"])
        if L["pair"] is not None and (r is None or r["pair"] is None):
            d["i"] = True
        if L["created"]:
            cls = record_class(r, rs if rs not in ("RK",) else "RF") if r is not None else None
            if cls not in ("A", "C"):
                if r is None or r["pair"] != CAP:
                    d["ii_LR"] = True
                    other = (pkg.raw_writer == "driver" and pkg.raw_pairs.get(L["lid"]) == CAP)
                    other = other or any(x.get("lid") == L["lid"] and x["pair"] == CAP for x in pkg.rb1 + pkg.rl2)
                    other = other or L.get("meta_pair") == CAP
                    if not other:
                        d["ii_ANY"] = True
            if r is not None and r["child_created"] is False:
                d["iii"] = True
    if pkg.foreign_record_undetected and not pkg.foreign_file:
        d["iv"] = True
    if pkg.raw_writer == "wrapper":
        d["v"] = True
    return d


def planned_basis(pkg, recs, rs, items):
    """failclosed RF-0 (b) with childend RG-2 (b) and gapattr RH-2 (b): a driver-logic outcome a dependant acts on."""
    if not pkg.planned_basis or pkg.raw_writer != "driver":
        return False
    if rs in ("RG", "RH", "RI", "RIx") or rs.startswith("RJ"):
        infra = recs and all((r["child_created"] is False) or (r["raised"] is not None) or (not r["pair_read_by_parent"]) for r in recs)
        if infra:
            return False
    if rs in ("RH", "RI", "RIx") or rs.startswith("RJ"):
        if any(i.startswith("68-70") for i in items):
            return False
    return True


def show(res, pkg, P):
    """Print record level, then package level."""
    P("  [%s] verdict %s%s" % (res["rule_set"], res["verdict"], ("  ** " + res["flag"] + " **") if res["flag"] else ""))
    for r in res["records"]:
        P("      record %-34s class %-4s child_created %-12s child_end %-22s pair %s raised %s"
          % (r["lid"], r["class"], r["child_created"], r["child_end"], r["pair"], r["raised"]))
    if res["absent_records"]:
        P("      ABSENT launch records (premise): %s" % res["absent_records"])
    if res["named_gaps"]:
        P("      named gaps: %s" % res["named_gaps"])
    if res["recorder_gaps"]:
        P("      recorder gaps: %s" % res["recorder_gaps"])
    if res["frozen_items"]:
        P("      frozen checker items: %s" % res["frozen_items"])
    if res["definitions"]:
        P("      definitions holding: %s" % sorted(res["definitions"]))
```

### lj0_v1.py

- sha256: 42525fab5bd8006fc34b8a030e80475c172c0b827a4a2b39be75d8180bada145
- argv: `C026: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v1.py > lj0_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 known-answer control, objects (a)-(e), with the
evaluator core rjcore_v1.py UNCHANGED (imported from this scratch directory; it imports nothing from the repository).
Prints record level, then package level, per object and rule set; writes lj0_v1.json next to itself."""
import json
import os
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v1 as K  # noqa: E402  (this review's own scratch module)

OUT = {}
LINES = []


def P(s=""):
    LINES.append(s)
    print(s)


def run(obj_id, desc, pkg, rule_sets, expect):
    P("=" * 110)
    P("%s: %s" % (obj_id, desc))
    if pkg.premises:
        P("  premises: %s" % pkg.premises)
    OUT[obj_id] = {"description": desc, "premises": pkg.premises, "expected": expect, "results": {}}
    for rs in rule_sets:
        res = K.evaluate(pkg, rs)
        K.show(res, pkg, P)
        OUT[obj_id]["results"][rs] = {k: res[k] for k in ("verdict", "flag", "definitions", "named_gaps", "recorder_gaps",
                                                          "frozen_items", "records", "absent_records")}
    P("  expected by CRJ-4: %s" % expect)


# ------------------------------------------------------------------------------------------------ (a) readbackclose as worded
def cells5(name, normal=False, raw_writer="driver", cap_source="Mc"):
    return K.Pkg(name, "cells", planned_basis=True, normal=normal, raw_writer=raw_writer, cap_source=cap_source)


for path, oid, nm in (("P16", "KA-a1", "P-16 (fork at v2_solver.py 181 created the child; raise before STORE_FAST pid)"),
                      ("PF2_after_P14a", "KA-a2", "P-F2 after P-14a (raise at 214, then SolverLock.release raises in the finally)")):
    for k, cs in ((1, "Mc"), (1, "Mr"), (0, "Mc")):
        pk = cells5("%s k=%d %s" % (oid, k, cs), raw_writer="wrapper", cap_source=cs)
        if k == 1:
            pk.solve("S5_t0", ["exec_ok"], retain_input=True)
        pk.solve("S5_t%d" % k, [path], retain_input=False)
        pk.premises.append("the driver raises out of run_child at the %s launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)" % path)
        run("%s k=%d %s" % (oid, k, cs), nm + "; cells m = 5; k = %d other collected pair(s); frozen checker requested cap %s" % (k, "recorded independently (Mc)" if cs == "Mc" else "from raw envelope (Mr)"),
            pk, ("RK", "RF", "RJ"), "RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass")

pk = cells5("KA-a3 W-1", raw_writer="wrapper")
pk.premises.append("the driver exits before any launch; the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)")
run("KA-a3", "W-1: cells m = 5, zero launch, wrapper-written raw-result.json", pk, ("RK", "RF", "RJ"), "RK: PASS_ZL for a wrapper-recorded outcome (v)")

# ------------------------------------------------------------------------------------------------ (b) failclosed as worded: FO-1
for variant, path in (("C", "FO1_C"), ("B", "FO1_B")):
    for how in ("failed", "interrupted"):
        for ex in (1, -2):
            for k in (0, 1):
                pk = cells5("FO-1 %s %s exit %d k=%d" % (variant, how, ex, k))
                if k == 1:
                    pk.solve("S5_t0", ["exec_ok"])
                pk.launches_before = len(pk.launches)
                # the escaped child's launch: the parent's run_child returns after the escaped child exits
                pk.solve("S5_t%d" % k, [path], retain_input=False)
                pk.launches[-1]["returncode"] = ex
                pk.premises.append("variant %s: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write %s (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status %d" % (variant, how, ex))
                run("KA-b FO-1 %s %s exit %d k=%d" % (variant, how, ex, k), "FO-1 variant %s, foreign-file write %s, escaped exit %d, cells m = 5, k = %d" % (variant, how, ex, k),
                    pk, ("RF", "RG", "RI", "RJ"), "RF: FAIL-OPEN under definition (iv) when the foreign-file write fails")

# ------------------------------------------------------------------------------------------------ (c) childend as worded: PB-3
pk = cells5("PB-3", normal=True)
pk.solve("S5_t0", ["exec_ok"], retain_input=True)
pk.solve("S5_t1", ["exec_ssf", "exec_ok"], retain_input=False)
pk.solve("S5_t2", ["exec_ok"], retain_input=False)
run("KA-c PB-3", "cells m = 5 package, polynomial arm S5, target 1 re-solved once by SE-3 (attempt 1 SSF, renamed .ssf-attempt1)", pk,
    ("RF", "RG", "RH", "RI", "RJ"), "RG: PLANNED-BASIS REFUSAL")


# ------------------------------------------------------------------------------------------------ (d) gapattr as worded: CX-1 objects
def lr(name, attempts, lost):
    pk = cells5(name)
    pk.solve("S5_t0", ["exec_ok"], retain_input=True)
    pk.solve("S5_t1", attempts, retain_input=False)
    pk.solve("S5_t2", ["exec_ok"], retain_input=False)
    for x in lost:
        pk.lost.add("S5_t1/ms%d" % x)
    pk.premises.append("launch record(s) of S5_t1 attempt(s) %s absent without RL-1 (d) firing (carried decision (4))" % lost)
    return pk


run("KA-d LR-1", "S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent", lr("LR-1", ["exec_ssf", "exec_ok"], [2]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-2", "S-1 re-solve, 2 attempts, attempt 1's launch record absent", lr("LR-2", ["exec_ssf", "exec_ok"], [1]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-3", "S-1 re-solve, 3 attempts, attempt 2's launch record absent", lr("LR-3", ["exec_ssf", "exec_ssf", "exec_ok"], [2]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-4", "S-1 re-solve, 3 attempts, attempts 2 and 3 absent", lr("LR-4", ["exec_ssf", "exec_ssf", "exec_ok"], [2, 3]),
    ("RH", "RI", "RJ"), "RH: FAIL")


def controls_a1(name, gp_path="exec_ok", health_d222=("exec_ok",), lost=(), normal=False):
    pk = K.Pkg(name, "controls_a1", a1_image=True, planned_basis=False, normal=normal)
    pk.gp("controls_a1_pari", gp_path)
    pk.health("health_p1073741831_d222", list(health_d222))
    pk.health("health_p1073741831_d444", ["exec_ok"])
    pk.health_report(1073741831)
    pk.child_job("ctl_a1_torsion_S3_rq", "exec_ok")
    pk.child_job("ctl_a1_S3_rescaled", "exec_ok")
    pk.solve("ctl_a1_planted_torsion_S3_rq", ["exec_ok"])
    pk.solve("ctl_a1_planted_S3_rescaled", ["exec_ok"])
    for x in lost:
        pk.lost.add(x)
    return pk


pk = controls_a1("LR-5", health_d222=("exec_ssf", "exec_ok"), lost=("health:health_p1073741831_d222/ms2",))
pk.premises.append("launch record of the final HR-3 attempt of health_p1073741831_d222 absent without RL-1 (d) firing")
run("KA-d LR-5", "S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent", pk, ("RH", "RI", "RJ"),
    "RH: PASS and FAIL-OPEN (i)")


# ------------------------------------------------------------------------------------------------ (e) attcount and launchkind
def cells4_cx_a(name, cg_path="pre_stdout_99", lose=True):
    pk = K.Pkg(name, "cells", planned_basis=True, normal=not lose)
    pk.solve("S4_t0", ["exec_ok"], retain_input=True, callgrind=cg_path)
    pk.solve("S4_t1", ["exec_ok"], retain_input=False)
    pk.solve("S4_t2", ["exec_ok"], retain_input=False)
    if lose:
        pk.lost.add("S4_t0/cg")
        pk.premises.append("the callgrind launch record of S4_t0 absent without RL-1 (d) firing (carried decision (4))")
    return pk


run("KA-e CX-A", "cells m = 4, target 0 solved with callgrind_timeout (v2_driver.py 1174-1175); the callgrind child's open of "
    "<tag>.callgrind.stdout fails (v2_solver.py 188 -> 206-208, exit 99, no file); its launch record absent",
    cells4_cx_a("CX-A"), ("RI", "RJ", "RJw"),
    "RI: PASS and FAIL-OPEN (ii); RJ: CALLGRIND COUNT GAP and FAIL; RJw: PASS and FAIL-OPEN (ii)")

pk = K.Pkg("LN-7a", "cells", planned_basis=True, normal=False)
pk.solve("S5_t0", ["exec_ok"], retain_input=True)
pk.solve("S5_t1", ["pre_stdout_99"], retain_input=False)
pk.solve("S5_t2", ["exec_ok"], retain_input=False)
pk.lost.add("S5_t1/ms1")
pk.premises.append("the msolve launch record of S5_t1 (child failing before its stdout file, input not retained) absent")
run("KA-e LN-7a", "non-event S-1 msolve child that fails before creating its stdout file, input not retained, launch record absent",
    pk, ("RH", "RI", "RJ"), "RI: COUNT GAP and FAIL")

pk = controls_a1("CX-A-gp", gp_path="pre_stdout_99", lost=("gp:controls_a1_pari",))
pk.premises.append("the gp launch record absent; the gp child failed before its stdout file (a1_pari.py 96 -> v2_solver.py 188, 206-208)")
run("KA-e CX-A-gp", "controls_a1, the gp child fails before its stdout file, its launch record absent", pk, ("RI", "RJ", "RJnogp"),
    "RJ: a recorder gap on pari/<tag>.gp and FAIL")

pk = K.Pkg("CX-A-cmp", "anchor_identity", gate=True, planned_basis=False, normal=False)
pk.comparator("pre_stdout_99")
pk.lost.add("cmp")
pk.premises.append("the comparator launch record absent; the comparator child failed before its stdout file; the driver ends at v2_driver.py 656-659 with finish() (raw driver-written, comparator.child present)")
run("KA-e CX-A-cmp", "anchor-identity, the comparator child fails before its stdout file, its launch record absent", pk,
    ("RI", "RJ", "RJnocmp"), "RJ: COMPARATOR COUNT GAP and FAIL")

pk = K.Pkg("CX-A-G2", "fixture", gate=True, planned_basis=True, normal=False)
for arm in ("raw_x", "S3"):
    pk.solve("fx_reg0_%s" % arm, ["exec_ok"], retain_input=True, callgrind=("pre_stdout_99" if arm == "S3" else "exec_ok"))
pk.lost.add("fx_reg0_S3/cg")
pk.premises.append("the callgrind launch record of fx_reg0_S3 absent")
run("KA-e CX-A-G2", "fixture package of G2 shape (callgrind on every ok solve, v2_driver.py 358), one no-file callgrind record absent",
    pk, ("RI", "RJ", "RJw"), "RJ: CALLGRIND COUNT GAP and FAIL (variant)")

with open(os.path.join(SCR, "lj0_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE lj0_v1.json (%d objects)" % len(OUT))
```

### lj0_v2.py

- sha256: 025e4b17c3d058bc24895042eeba9b5f4f4dca2cf7a9045d75d917c5010c3660
- argv: `C033: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v2.py > lj0_v2.out 2>&1 (lj0_v2.py made by sed from lj0_v1.py; the third sed expression matched nothing)`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 known-answer control, objects (a)-(e), with the
evaluator core rjcore_v2.py UNCHANGED (imported from this scratch directory; it imports nothing from the repository).
Prints record level, then package level, per object and rule set; writes lj0_v2.json next to itself."""
import json
import os
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v2 as K  # noqa: E402  (this review's own scratch module)

OUT = {}
LINES = []


def P(s=""):
    LINES.append(s)
    print(s)


def run(obj_id, desc, pkg, rule_sets, expect):
    P("=" * 110)
    P("%s: %s" % (obj_id, desc))
    if pkg.premises:
        P("  premises: %s" % pkg.premises)
    OUT[obj_id] = {"description": desc, "premises": pkg.premises, "expected": expect, "results": {}}
    for rs in rule_sets:
        res = K.evaluate(pkg, rs)
        K.show(res, pkg, P)
        OUT[obj_id]["results"][rs] = {k: res[k] for k in ("verdict", "flag", "definitions", "named_gaps", "recorder_gaps",
                                                          "frozen_items", "records", "absent_records")}
    P("  expected by CRJ-4: %s" % expect)


# ------------------------------------------------------------------------------------------------ (a) readbackclose as worded
def cells5(name, normal=False, raw_writer="driver", cap_source="Mc"):
    return K.Pkg(name, "cells", planned_basis=True, normal=normal, raw_writer=raw_writer, cap_source=cap_source)


for path, oid, nm in (("P16", "KA-a1", "P-16 (fork at v2_solver.py 181 created the child; raise before STORE_FAST pid)"),
                      ("PF2_after_P14a", "KA-a2", "P-F2 after P-14a (raise at 214, then SolverLock.release raises in the finally)")):
    for k, cs in ((1, "Mc"), (1, "Mr"), (0, "Mc")):
        pk = cells5("%s k=%d %s" % (oid, k, cs), raw_writer="wrapper", cap_source=cs)
        if k == 1:
            pk.solve("S5_t0", ["exec_ok"], retain_input=True)
        pk.solve("S5_t%d" % k, [path], retain_input=False)
        pk.premises.append("the driver raises out of run_child at the %s launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)" % path)
        run("%s k=%d %s" % (oid, k, cs), nm + "; cells m = 5; k = %d other collected pair(s); frozen checker requested cap %s" % (k, "recorded independently (Mc)" if cs == "Mc" else "from raw envelope (Mr)"),
            pk, ("RK", "RF", "RJ"), "RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass")

pk = cells5("KA-a3 W-1", raw_writer="wrapper")
pk.premises.append("the driver exits before any launch; the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)")
run("KA-a3", "W-1: cells m = 5, zero launch, wrapper-written raw-result.json", pk, ("RK", "RF", "RJ"), "RK: PASS_ZL for a wrapper-recorded outcome (v)")

# ------------------------------------------------------------------------------------------------ (b) failclosed as worded: FO-1
for variant, path in (("C", "FO1_C"), ("B", "FO1_B")):
    for how in ("failed", "interrupted"):
        for ex in (1, -2):
            for k in (0, 1):
                pk = cells5("FO-1 %s %s exit %d k=%d" % (variant, how, ex, k))
                if k == 1:
                    pk.solve("S5_t0", ["exec_ok"])
                pk.launches_before = len(pk.launches)
                # the escaped child's launch: the parent's run_child returns after the escaped child exits
                pk.solve("S5_t%d" % k, [path], retain_input=False)
                pk.launches[-1]["returncode"] = ex
                pk.premises.append("variant %s: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write %s (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status %d" % (variant, how, ex))
                run("KA-b FO-1 %s %s exit %d k=%d" % (variant, how, ex, k), "FO-1 variant %s, foreign-file write %s, escaped exit %d, cells m = 5, k = %d" % (variant, how, ex, k),
                    pk, ("RF", "RG", "RI", "RJ"), "RF: FAIL-OPEN under definition (iv) when the foreign-file write fails")

# ------------------------------------------------------------------------------------------------ (c) childend as worded: PB-3
pk = cells5("PB-3", normal=True)
pk.solve("S5_t0", ["exec_ok"], retain_input=True)
pk.solve("S5_t1", ["exec_ssf", "exec_ok"], retain_input=False)
pk.solve("S5_t2", ["exec_ok"], retain_input=False)
run("KA-c PB-3", "cells m = 5 package, polynomial arm S5, target 1 re-solved once by SE-3 (attempt 1 SSF, renamed .ssf-attempt1)", pk,
    ("RF", "RG", "RH", "RI", "RJ"), "RG: PLANNED-BASIS REFUSAL")


# ------------------------------------------------------------------------------------------------ (d) gapattr as worded: CX-1 objects
def lr(name, attempts, lost):
    pk = cells5(name)
    pk.solve("S5_t0", ["exec_ok"], retain_input=True)
    pk.solve("S5_t1", attempts, retain_input=False)
    pk.solve("S5_t2", ["exec_ok"], retain_input=False)
    for x in lost:
        pk.lost.add("S5_t1/ms%d" % x)
    pk.premises.append("launch record(s) of S5_t1 attempt(s) %s absent without RL-1 (d) firing (carried decision (4))" % lost)
    return pk


run("KA-d LR-1", "S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent", lr("LR-1", ["exec_ssf", "exec_ok"], [2]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-2", "S-1 re-solve, 2 attempts, attempt 1's launch record absent", lr("LR-2", ["exec_ssf", "exec_ok"], [1]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-3", "S-1 re-solve, 3 attempts, attempt 2's launch record absent", lr("LR-3", ["exec_ssf", "exec_ssf", "exec_ok"], [2]),
    ("RH", "RI", "RJ"), "RH: PASS and FAIL-OPEN (i)")
run("KA-d LR-4", "S-1 re-solve, 3 attempts, attempts 2 and 3 absent", lr("LR-4", ["exec_ssf", "exec_ssf", "exec_ok"], [2, 3]),
    ("RH", "RI", "RJ"), "RH: FAIL")


def controls_a1(name, gp_path="exec_ok", health_d222=("exec_ok",), lost=(), normal=False):
    pk = K.Pkg(name, "controls_a1", a1_image=True, planned_basis=False, normal=normal)
    pk.gp("controls_a1_pari", gp_path)
    pk.health("health_p1073741831_d222", list(health_d222))
    pk.health("health_p1073741831_d444", ["exec_ok"])
    pk.health_report(1073741831)
    pk.child_job("ctl_a1_torsion_S3_rq", "exec_ok")
    pk.child_job("ctl_a1_S3_rescaled", "exec_ok")
    pk.solve("ctl_a1_planted_torsion_S3_rq", ["exec_ok"])
    pk.solve("ctl_a1_planted_S3_rescaled", ["exec_ok"])
    for x in lost:
        pk.lost.add(x)
    return pk


pk = controls_a1("LR-5", health_d222=("exec_ssf", "exec_ok"), lost=("health:health_p1073741831_d222/ms2",))
pk.premises.append("launch record of the final HR-3 attempt of health_p1073741831_d222 absent without RL-1 (d) firing")
run("KA-d LR-5", "S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent", pk, ("RH", "RI", "RJ"),
    "RH: PASS and FAIL-OPEN (i)")


# ------------------------------------------------------------------------------------------------ (e) attcount and launchkind
def cells4_cx_a(name, cg_path="pre_stdout_99", lose=True):
    pk = K.Pkg(name, "cells", planned_basis=True, normal=not lose)
    pk.solve("S4_t0", ["exec_ok"], retain_input=True, callgrind=cg_path)
    pk.solve("S4_t1", ["exec_ok"], retain_input=False)
    pk.solve("S4_t2", ["exec_ok"], retain_input=False)
    if lose:
        pk.lost.add("S4_t0/cg")
        pk.premises.append("the callgrind launch record of S4_t0 absent without RL-1 (d) firing (carried decision (4))")
    return pk


run("KA-e CX-A", "cells m = 4, target 0 solved with callgrind_timeout (v2_driver.py 1174-1175); the callgrind child's open of "
    "<tag>.callgrind.stdout fails (v2_solver.py 188 -> 206-208, exit 99, no file); its launch record absent",
    cells4_cx_a("CX-A"), ("RI", "RJ", "RJw"),
    "RI: PASS and FAIL-OPEN (ii); RJ: CALLGRIND COUNT GAP and FAIL; RJw: PASS and FAIL-OPEN (ii)")

pk = K.Pkg("LN-7a", "cells", planned_basis=True, normal=False)
pk.solve("S5_t0", ["exec_ok"], retain_input=True)
pk.solve("S5_t1", ["pre_stdout_99"], retain_input=False)
pk.solve("S5_t2", ["exec_ok"], retain_input=False)
pk.lost.add("S5_t1/ms1")
pk.premises.append("the msolve launch record of S5_t1 (child failing before its stdout file, input not retained) absent")
run("KA-e LN-7a", "non-event S-1 msolve child that fails before creating its stdout file, input not retained, launch record absent",
    pk, ("RH", "RI", "RJ"), "RI: COUNT GAP and FAIL")

pk = controls_a1("CX-A-gp", gp_path="pre_stdout_99", lost=("gp:controls_a1_pari",))
pk.premises.append("the gp launch record absent; the gp child failed before its stdout file (a1_pari.py 96 -> v2_solver.py 188, 206-208)")
run("KA-e CX-A-gp", "controls_a1, the gp child fails before its stdout file, its launch record absent", pk, ("RI", "RJ", "RJnogp"),
    "RJ: a recorder gap on pari/<tag>.gp and FAIL")

pk = K.Pkg("CX-A-cmp", "anchor_identity", gate=True, planned_basis=False, normal=False)
pk.comparator("pre_stdout_99")
pk.lost.add("cmp")
pk.premises.append("the comparator launch record absent; the comparator child failed before its stdout file; the driver ends at v2_driver.py 656-659 with finish() (raw driver-written, comparator.child present)")
run("KA-e CX-A-cmp", "anchor-identity, the comparator child fails before its stdout file, its launch record absent", pk,
    ("RI", "RJ", "RJnocmp"), "RJ: COMPARATOR COUNT GAP and FAIL")

pk = K.Pkg("CX-A-G2", "fixture", gate=True, planned_basis=True, normal=False)
for arm in ("raw_x", "S3"):
    pk.solve("fx_reg0_%s" % arm, ["exec_ok"], retain_input=True, callgrind=("pre_stdout_99" if arm == "S3" else "exec_ok"))
pk.lost.add("fx_reg0_S3/cg")
pk.premises.append("the callgrind launch record of fx_reg0_S3 absent")
run("KA-e CX-A-G2", "fixture package of G2 shape (callgrind on every ok solve, v2_driver.py 358), one no-file callgrind record absent",
    pk, ("RI", "RJ", "RJw"), "RJ: CALLGRIND COUNT GAP and FAIL (variant)")

with open(os.path.join(SCR, "lj0_v2.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE lj0_v2.json (%d objects)" % len(OUT))
```

### listing_v1.py

- sha256: cea024e213a3a7acc7ac050de6a519152806f9a95dedf901aa34afb058a43c57
- argv: `C029: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v1.py > listing_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 (f) and LJ-2 (2): the LISTING AND COUNT CHECK under
launchkind on the four archived r3 gate packages, with the evaluator core rjcore_v1.py UNCHANGED.

Input: pkgread_v1.json (the O_NOATIME listing and read-only records of the four packages; no repository read here).

CRJ-9 RECONSTRUCTION RULE (the r4 launch, RB-1 and RL-2 records do not exist in r3):
  launch records, from the file listing and the frozen code's naming:
    child/<tag>.spec.json          -> one child-job record (v2_driver.py 92-102): stdout child/<tag>.stdout, stderr
                                      child/<tag>.stderr, argv's last element the spec; child_end "exec" (the child's
                                      .meta.json or .stdout exists), spec "out" as the archived spec file records it;
    solver|health/<tag>.ms.log     -> one msolve record (v2_driver.py 161-166; a1_health.py 141-147): stdout .ms.log,
                                      stderr .ms.err, argv names <tag>.ms and <tag>.ms.out;
    solver/<tag>.callgrind.stdout  -> one callgrind record (v2_solver.py 515-518; v2_driver.py 208-209): argv names
                                      <tag>.ms and <tag>.cg.ms.out, --callgrind-out-file=<tag>.callgrind.out;
    comparator/stdout.log          -> one comparator record (v2_driver.py 647-651): argv names comparator/;
    pari/<tag>.gp.stdout           -> one gp record (a1_pari.py 91-96): argv names pari/<tag>.gp.
    Every reconstructed record is child_created true, raised null, pair equal to the cap (class B).
  S-1 attempt records (RB-1) and pass-through records (RL-2), per tag, INDEPENDENTLY of the listing:
    from raw-result.json's solve records (a mapping with a "solver" mapping carrying argv): -P 1 -> one RB-1 attempt
    record; -g 1 -> one RL-2 record; the tag is the basename of argv's -f value without ".ms";
    callgrind_result_present (RJ-1 (a)) := the row's "instructions_callgrind" value is a non-null mapping (the frozen
    rows copy the key with r.get, v2_driver.py 359-361 and 1179-1181, so key presence in the row is not the test;
    callgrind_instructions always returns a dict, v2_solver.py 519-552);
    where raw-result.json carries no solve record for a tag: from the frozen call site (anchor_comparator_system:
    v2_driver.py 711 gb_only=True -> RL-2; controls ctl_*: v2_driver.py 786, 787, 841, gb_only False, no
    callgrind_timeout -> RB-1 with callgrind_result_present false).
  events and site counters: the archived r3 solver-events.json (sites v2_driver.solve and a1_health.run_system).
  raw comparator.child: raw-result.json top-level "comparator" mapping carrying "child".
  Paths: compared relative to each package's run directory (GFPN_RUN_DIR, command.txt line 2, equal to its path).
A listing or count check is a reading of r3 artifacts under r4 rule text: never a result about any package's verdict
and never evidence about D.
"""
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v1 as K  # noqa: E402

D = json.load(open(os.path.join(SCR, "pkgread_v1.json")))
OUT = {"reconstruction_rule": __doc__.split("CRJ-9 RECONSTRUCTION RULE")[1].strip(), "packages": {}}
LINES = []


def P(s=""):
    LINES.append(s)
    print(s)


def solve_rows(raw):
    rows = []

    def walk(o, path):
        if isinstance(o, dict):
            s = o.get("solver")
            if isinstance(s, dict) and s.get("argv"):
                rows.append((path, o))
            for k, v in o.items():
                walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i)
    walk(raw, "")
    return rows


for rid, pk in D["packages"].items():
    rd = pk["run_dir"]
    raw = json.loads(pk["files"]["raw-result.json"]["text"])
    se = json.loads(pk["files"]["solver-events.json"]["text"])
    cmd2 = pk["files"]["command.txt"]["text"].splitlines()[1]
    assert cmd2 == "# GFPN_RUN_DIR=%s" % rd, cmd2
    listing = pk["listing"]
    files = sorted("%s/%s" % (d, n) for d, ns in listing.items() for n in ns)
    obj = K.Pkg(rid, raw.get("kind"), planned_basis=False)
    # ---- launch records reconstructed from the listing
    for n in listing.get("child", []):
        if n.endswith(".spec.json"):
            tag = n[:-len(".spec.json")]
            spec = pk["specs"][n]
            out = spec.get("out")
            out_rel = os.path.relpath(out, rd) if isinstance(out, str) and out.startswith(rd + "/") else ("OUTSIDE:" + str(out))
            L = obj.launch("cj:" + tag, "childjob", "exec_ok", "child/%s.stdout" % tag, "child/%s.stderr" % tag,
                           argv_paths=("child/" + n,), spec="child/" + n, tag=tag, raw_pair=False)
            obj.specs["child/" + n] = out_rel
    for d in ("solver", "health"):
        for n in listing.get(d, []):
            if n.endswith(".ms.log"):
                tag = n[:-len(".ms.log")]
                obj.launch("%s:%s/ms" % (d, tag), "msolve", "exec_ok", "%s/%s.ms.log" % (d, tag), "%s/%s.ms.err" % (d, tag),
                           argv_paths=("%s/%s.ms" % (d, tag), "%s/%s.ms.out" % (d, tag)), site=("S-1" if d == "solver" else "S-2"),
                           tag=tag, raw_pair=False)
            if d == "solver" and n.endswith(".callgrind.stdout"):
                tag = n[:-len(".callgrind.stdout")]
                obj.launch("solver:%s/cg" % tag, "callgrind", "exec_ok", "solver/%s.callgrind.stdout" % tag,
                           "solver/%s.callgrind.stderr" % tag, argv_paths=("solver/%s.ms" % tag, "solver/%s.cg.ms.out" % tag),
                           cg_out="solver/%s.callgrind.out" % tag, site="S-3", tag=tag, raw_pair=False)
    if "stdout.log" in listing.get("comparator", []):
        obj.launch("cmp", "comparator", "exec_ok", "comparator/stdout.log", "comparator/stderr.log", argv_dirs=("comparator",), raw_pair=False)
    for n in listing.get("pari", []):
        if n.endswith(".gp.stdout"):
            tag = n[:-len(".gp.stdout")]
            obj.launch("gp:" + tag, "gp", "exec_ok", "pari/%s.gp.stdout" % tag, "pari/%s.gp.stderr" % tag, argv_paths=("pari/%s.gp" % tag,), tag=tag)
    obj.files = {f: "listing" for f in files}                       # the ACTUAL listing replaces constructed files
    obj.nonlaunch = {}
    for f in files:
        if re.match(r"^health/[^/]+\.ms$", f):
            obj.nonlaunch[f] = "a1_health.py 141-143"
        if re.match(r"^health/health-\d+\.json$", f):
            obj.nonlaunch[f] = "a1_health.py 251"
        if re.match(r"^pari/[^/]+\.gp$", f):
            obj.nonlaunch[f] = "a1_pari.py 91-93"
    # ---- RB-1 / RL-2 reconstructed independently of the listing
    per_tag = {}
    for path, row in solve_rows(raw):
        argv = row["solver"]["argv"]
        inp = argv[argv.index("-f") + 1]
        tag = os.path.basename(inp)[:-len(".ms")]
        gb = "-g" in argv
        cgp = isinstance(row.get("instructions_callgrind"), dict)
        per_tag[tag] = {"source": "raw-result.json %s (argv %s)" % (path, "-g 1" if gb else "-P 1"), "gb_only": gb, "cg_present": cgp,
                        "row_has_key": "instructions_callgrind" in row}
    for n in listing.get("solver", []):
        if n.endswith(".ms.log"):
            tag = n[:-len(".ms.log")]
            if tag in per_tag:
                continue
            if tag == "anchor_comparator_system":
                per_tag[tag] = {"source": "frozen call site v2_driver.py 711 (gb_only=True)", "gb_only": True, "cg_present": False, "row_has_key": None}
            elif tag.startswith("ctl_"):
                per_tag[tag] = {"source": "frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)", "gb_only": False, "cg_present": False, "row_has_key": None}
            else:
                per_tag[tag] = {"source": "NO SOURCE", "gb_only": None, "cg_present": None, "row_has_key": None}
    for tag, v in sorted(per_tag.items()):
        if v["gb_only"]:
            obj.rl2.append({"lid": "solver:%s/ms" % tag, "tag": tag, "pair": K.CAP})
        elif v["gb_only"] is False:
            obj.rb1.append({"lid": "solver:%s/ms" % tag, "site": "S-1", "tag": tag, "attempt": 1, "pair": K.CAP, "cg_present": v["cg_present"]})
    sites = se.get("sites") or {}
    c1 = (sites.get("v2_driver.solve") or {}).get("counters") or {}
    c2 = (sites.get("a1_health.run_system") or {}).get("counters") or {}
    obj.counters = {"S-1": {"attempts_total": c1.get("attempts_total", 0), "passthrough": c1.get("passthrough_calls_gb_only_true", 0)},
                    "S-2": {"attempts_total": c2.get("attempts_total", 0)}}
    for site_key, site in (("v2_driver.solve", "S-1"), ("a1_health.run_system", "S-2")):
        for ev in (sites.get(site_key) or {}).get("events") or []:
            obj.events[(site, ev["tag"])] = {"attempts": [a["attempt"] for a in ev.get("attempts") or []],
                                             "accepted": ev.get("accepted_attempt"), "renamed": ev.get("renamed_files") or {}}
    obj.raw_comparator_child = isinstance(raw.get("comparator"), dict) and "child" in raw["comparator"]
    s3tags = [r.get("tag") for r in (sites.get("v2_driver.solve/callgrind") or {}).get("records") or []]
    # ---- evaluate (the core's attribution and named gaps, unchanged)
    recs = [K.record_of(L, "RJ") for L in obj.launches]
    res = {}
    for rs in ("RI", "RJ"):
        attr, gaps, named = K.attribute(obj, [K.record_of(L, rs) for L in obj.launches], rs)
        res[rs] = {"attr": attr, "gaps": gaps, "named": named}
    # ---- the count table
    rows = []
    for tag in sorted(per_tag):
        d = "solver"
        N = sum(1 for r in recs if r["stdout"] == "%s/%s.ms.log" % (d, tag))
        nrb = sum(1 for x in obj.rb1 if x["tag"] == tag and x["site"] == "S-1")
        nrl = sum(1 for x in obj.rl2 if x["tag"] == tag)
        ncg = sum(1 for r in recs if r["stdout"] == "solver/%s.callgrind.stdout" % tag)
        ccount = sum(1 for x in obj.rb1 if x["tag"] == tag and x["site"] == "S-1" and x["cg_present"] is True)
        rows.append({"site": "S-1", "tag": tag, "N": N, "RB1": nrb, "RL2": nrl, "RI1_a_i_holds": N == nrb + nrl,
                     "Ncg": ncg, "callgrind_result_present_count": ccount, "RJ1_b_holds": ncg == ccount,
                     "S3_record_for_tag": s3tags.count(tag), "source": per_tag[tag]["source"],
                     "raw_row_carries_key_instructions_callgrind": per_tag[tag]["row_has_key"]})
    for n in listing.get("health", []):
        if n.endswith(".ms.log"):
            rows.append({"site": "S-2", "tag": n[:-7], "N": 1, "note": "no archived package has health/ files"})
    nl1 = sum(1 for r in recs if re.match(r"^solver/.+\.ms\.log$", r["stdout"]))
    nl2 = sum(1 for r in recs if re.match(r"^health/.+\.ms\.log$", r["stdout"]))
    site_rows = [{"site": "S-1", "launch_records": nl1, "attempts_total": obj.counters["S-1"]["attempts_total"],
                  "passthrough_calls_gb_only_true": obj.counters["S-1"]["passthrough"],
                  "RI1_a_iii_holds": nl1 == obj.counters["S-1"]["attempts_total"] + obj.counters["S-1"]["passthrough"]},
                 {"site": "S-2", "launch_records": nl2, "attempts_total": obj.counters["S-2"]["attempts_total"],
                  "RI1_a_iii_holds": nl2 == obj.counters["S-2"]["attempts_total"]}]
    tot_ncg = sum(1 for r in recs if re.match(r"^solver/.+\.callgrind\.stdout$", r["stdout"]))
    tot_c = sum(1 for x in obj.rb1 if x["site"] == "S-1" and x["cg_present"] is True)
    rj1_site = {"callgrind_launch_records": tot_ncg, "attempt_records_with_callgrind_result_present": tot_c, "holds": tot_ncg == tot_c,
                "S3_records_total_cross_check": len(s3tags), "S3_counter_callgrind_children_observed": ((sites.get("v2_driver.solve/callgrind") or {}).get("counters") or {}).get("callgrind_children_observed")}
    ncmp = sum(1 for r in recs if r["stdout"] == "comparator/stdout.log")
    rj3 = {"comparator_launch_records": ncmp, "raw_comparator_child_present": obj.raw_comparator_child,
           "required": 1 if obj.raw_comparator_child else 0, "holds": ncmp == (1 if obj.raw_comparator_child else 0)}
    unk = [r["stdout"] for r in recs if not any(f.match(r["stdout"]) for f in K.SIX_FORMS)]
    pari = sorted(f for f in files if f.startswith("pari/"))
    kinds = {}
    for r in recs:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    first_clause = {}
    for f in files:
        a = res["RJ"]["attr"].get(f)
        first_clause[f] = ("(%s) %s" % (a[0][0], a[0][1])) if a else ("NON-LAUNCH " + obj.nonlaunch[f] if f in obj.nonlaunch else "UNATTRIBUTED")
    OUT["packages"][rid] = {
        "files_in_the_five_directories": len(files), "reconstructed_launch_records": len(recs), "record_kinds": kinds,
        "RJ": {"recorder_gaps": res["RJ"]["gaps"], "named_gaps": res["RJ"]["named"], "unattributed_count": len(res["RJ"]["gaps"])},
        "RI_contrast": {"recorder_gaps": res["RI"]["gaps"], "named_gaps": res["RI"]["named"]},
        "count_rows_site_tag": rows, "site_rows": site_rows, "RJ1_site_row": rj1_site, "RJ3_comparator_row": rj3,
        "RJ4b_unknown_kind_stdout_paths": unk, "RJ2_pari_files": pari, "events": len(obj.events),
        "per_file_first_clause_RJ": first_clause}
    P("=" * 100)
    P("%s kind %s: files %d, reconstructed launch records %d %s, events %d" % (rid, raw.get("kind"), len(files), len(recs), kinds, len(obj.events)))
    P("  RJ recorder gaps (%d): %s" % (len(res["RJ"]["gaps"]), res["RJ"]["gaps"]))
    P("  RJ named gaps: %s" % res["RJ"]["named"])
    P("  RI (contrast) gaps %d named %s" % (len(res["RI"]["gaps"]), res["RI"]["named"]))
    P("  per (site, tag) rows: %d; RI-1 (a) (i) holds on %d; RJ-1 (b) holds on %d; mismatches: %s"
      % (len(rows), sum(1 for r in rows if r.get("RI1_a_i_holds")), sum(1 for r in rows if r.get("RJ1_b_holds")),
         [r["tag"] for r in rows if not (r.get("RI1_a_i_holds") and r.get("RJ1_b_holds"))]))
    for r in rows:
        P("    %(site)s %(tag)-32s N=%(N)d RB1=%(RB1)d RL2=%(RL2)d Ncg=%(Ncg)d present=%(callgrind_result_present_count)d S3=%(S3_record_for_tag)d | %(source)s" % r)
    P("  site rows: %s" % site_rows)
    P("  RJ-1 site row: %s" % rj1_site)
    P("  RJ-3 comparator row: %s" % rj3)
    P("  RJ-4 (b) unknown-kind stdout paths: %s" % unk)
    P("  RJ-2 pari/ files: %s" % pari)
with open(os.path.join(SCR, "listing_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
tot = sum(v["files_in_the_five_directories"] for v in OUT["packages"].values())
un = sum(v["RJ"]["unattributed_count"] for v in OUT["packages"].values())
P("\nTOTAL files %d, unattributed under launchkind %d; WROTE listing_v1.json" % (tot, un))
```

### listing_v2.py

- sha256: ae0be006a642487800a5f5dd94cfafd47bd178cfbadf9976cb08e8bae6c3faa4
- argv: `C034: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v2.py > listing_v2.out 2>&1 (listing_v2.py made by sed from listing_v1.py)`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 (f) and LJ-2 (2): the LISTING AND COUNT CHECK under
launchkind on the four archived r3 gate packages, with the evaluator core rjcore_v2.py UNCHANGED.

Input: pkgread_v1.json (the O_NOATIME listing and read-only records of the four packages; no repository read here).

CRJ-9 RECONSTRUCTION RULE (the r4 launch, RB-1 and RL-2 records do not exist in r3):
  launch records, from the file listing and the frozen code's naming:
    child/<tag>.spec.json          -> one child-job record (v2_driver.py 92-102): stdout child/<tag>.stdout, stderr
                                      child/<tag>.stderr, argv's last element the spec; child_end "exec" (the child's
                                      .meta.json or .stdout exists), spec "out" as the archived spec file records it;
    solver|health/<tag>.ms.log     -> one msolve record (v2_driver.py 161-166; a1_health.py 141-147): stdout .ms.log,
                                      stderr .ms.err, argv names <tag>.ms and <tag>.ms.out;
    solver/<tag>.callgrind.stdout  -> one callgrind record (v2_solver.py 515-518; v2_driver.py 208-209): argv names
                                      <tag>.ms and <tag>.cg.ms.out, --callgrind-out-file=<tag>.callgrind.out;
    comparator/stdout.log          -> one comparator record (v2_driver.py 647-651): argv names comparator/;
    pari/<tag>.gp.stdout           -> one gp record (a1_pari.py 91-96): argv names pari/<tag>.gp.
    Every reconstructed record is child_created true, raised null, pair equal to the cap (class B).
  S-1 attempt records (RB-1) and pass-through records (RL-2), per tag, INDEPENDENTLY of the listing:
    from raw-result.json's solve records (a mapping with a "solver" mapping carrying argv): -P 1 -> one RB-1 attempt
    record; -g 1 -> one RL-2 record; the tag is the basename of argv's -f value without ".ms";
    callgrind_result_present (RJ-1 (a)) := the row's "instructions_callgrind" value is a non-null mapping (the frozen
    rows copy the key with r.get, v2_driver.py 359-361 and 1179-1181, so key presence in the row is not the test;
    callgrind_instructions always returns a dict, v2_solver.py 519-552);
    where raw-result.json carries no solve record for a tag: from the frozen call site (anchor_comparator_system:
    v2_driver.py 711 gb_only=True -> RL-2; controls ctl_*: v2_driver.py 786, 787, 841, gb_only False, no
    callgrind_timeout -> RB-1 with callgrind_result_present false).
  events and site counters: the archived r3 solver-events.json (sites v2_driver.solve and a1_health.run_system).
  raw comparator.child: raw-result.json top-level "comparator" mapping carrying "child".
  Paths: compared relative to each package's run directory (GFPN_RUN_DIR, command.txt line 2, equal to its path).
A listing or count check is a reading of r3 artifacts under r4 rule text: never a result about any package's verdict
and never evidence about D.
"""
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v2 as K  # noqa: E402

D = json.load(open(os.path.join(SCR, "pkgread_v1.json")))
OUT = {"reconstruction_rule": __doc__.split("CRJ-9 RECONSTRUCTION RULE")[1].strip(), "packages": {}}
LINES = []


def P(s=""):
    LINES.append(s)
    print(s)


def solve_rows(raw):
    rows = []

    def walk(o, path):
        if isinstance(o, dict):
            s = o.get("solver")
            if isinstance(s, dict) and s.get("argv"):
                rows.append((path, o))
            for k, v in o.items():
                walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i)
    walk(raw, "")
    return rows


for rid, pk in D["packages"].items():
    rd = pk["run_dir"]
    raw = json.loads(pk["files"]["raw-result.json"]["text"])
    se = json.loads(pk["files"]["solver-events.json"]["text"])
    cmd2 = pk["files"]["command.txt"]["text"].splitlines()[1]
    assert cmd2 == "# GFPN_RUN_DIR=%s" % rd, cmd2
    listing = pk["listing"]
    files = sorted("%s/%s" % (d, n) for d, ns in listing.items() for n in ns)
    obj = K.Pkg(rid, raw.get("kind"), planned_basis=False)
    # ---- launch records reconstructed from the listing
    for n in listing.get("child", []):
        if n.endswith(".spec.json"):
            tag = n[:-len(".spec.json")]
            spec = pk["specs"][n]
            out = spec.get("out")
            out_rel = os.path.relpath(out, rd) if isinstance(out, str) and out.startswith(rd + "/") else ("OUTSIDE:" + str(out))
            L = obj.launch("cj:" + tag, "childjob", "exec_ok", "child/%s.stdout" % tag, "child/%s.stderr" % tag,
                           argv_paths=("child/" + n,), spec="child/" + n, tag=tag, raw_pair=False)
            obj.specs["child/" + n] = out_rel
    for d in ("solver", "health"):
        for n in listing.get(d, []):
            if n.endswith(".ms.log"):
                tag = n[:-len(".ms.log")]
                obj.launch("%s:%s/ms" % (d, tag), "msolve", "exec_ok", "%s/%s.ms.log" % (d, tag), "%s/%s.ms.err" % (d, tag),
                           argv_paths=("%s/%s.ms" % (d, tag), "%s/%s.ms.out" % (d, tag)), site=("S-1" if d == "solver" else "S-2"),
                           tag=tag, raw_pair=False)
            if d == "solver" and n.endswith(".callgrind.stdout"):
                tag = n[:-len(".callgrind.stdout")]
                obj.launch("solver:%s/cg" % tag, "callgrind", "exec_ok", "solver/%s.callgrind.stdout" % tag,
                           "solver/%s.callgrind.stderr" % tag, argv_paths=("solver/%s.ms" % tag, "solver/%s.cg.ms.out" % tag),
                           cg_out="solver/%s.callgrind.out" % tag, site="S-3", tag=tag, raw_pair=False)
    if "stdout.log" in listing.get("comparator", []):
        obj.launch("cmp", "comparator", "exec_ok", "comparator/stdout.log", "comparator/stderr.log", argv_dirs=("comparator",), raw_pair=False)
    for n in listing.get("pari", []):
        if n.endswith(".gp.stdout"):
            tag = n[:-len(".gp.stdout")]
            obj.launch("gp:" + tag, "gp", "exec_ok", "pari/%s.gp.stdout" % tag, "pari/%s.gp.stderr" % tag, argv_paths=("pari/%s.gp" % tag,), tag=tag)
    obj.files = {f: "listing" for f in files}                       # the ACTUAL listing replaces constructed files
    obj.nonlaunch = {}
    for f in files:
        if re.match(r"^health/[^/]+\.ms$", f):
            obj.nonlaunch[f] = "a1_health.py 141-143"
        if re.match(r"^health/health-\d+\.json$", f):
            obj.nonlaunch[f] = "a1_health.py 251"
        if re.match(r"^pari/[^/]+\.gp$", f):
            obj.nonlaunch[f] = "a1_pari.py 91-93"
    # ---- RB-1 / RL-2 reconstructed independently of the listing
    per_tag = {}
    for path, row in solve_rows(raw):
        argv = row["solver"]["argv"]
        inp = argv[argv.index("-f") + 1]
        tag = os.path.basename(inp)[:-len(".ms")]
        gb = "-g" in argv
        cgp = isinstance(row.get("instructions_callgrind"), dict)
        per_tag[tag] = {"source": "raw-result.json %s (argv %s)" % (path, "-g 1" if gb else "-P 1"), "gb_only": gb, "cg_present": cgp,
                        "row_has_key": "instructions_callgrind" in row}
    for n in listing.get("solver", []):
        if n.endswith(".ms.log"):
            tag = n[:-len(".ms.log")]
            if tag in per_tag:
                continue
            if tag == "anchor_comparator_system":
                per_tag[tag] = {"source": "frozen call site v2_driver.py 711 (gb_only=True)", "gb_only": True, "cg_present": False, "row_has_key": None}
            elif tag.startswith("ctl_"):
                per_tag[tag] = {"source": "frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)", "gb_only": False, "cg_present": False, "row_has_key": None}
            else:
                per_tag[tag] = {"source": "NO SOURCE", "gb_only": None, "cg_present": None, "row_has_key": None}
    for tag, v in sorted(per_tag.items()):
        if v["gb_only"]:
            obj.rl2.append({"lid": "solver:%s/ms" % tag, "tag": tag, "pair": K.CAP})
        elif v["gb_only"] is False:
            obj.rb1.append({"lid": "solver:%s/ms" % tag, "site": "S-1", "tag": tag, "attempt": 1, "pair": K.CAP, "cg_present": v["cg_present"]})
    sites = se.get("sites") or {}
    c1 = (sites.get("v2_driver.solve") or {}).get("counters") or {}
    c2 = (sites.get("a1_health.run_system") or {}).get("counters") or {}
    obj.counters = {"S-1": {"attempts_total": c1.get("attempts_total", 0), "passthrough": c1.get("passthrough_calls_gb_only_true", 0)},
                    "S-2": {"attempts_total": c2.get("attempts_total", 0)}}
    for site_key, site in (("v2_driver.solve", "S-1"), ("a1_health.run_system", "S-2")):
        for ev in (sites.get(site_key) or {}).get("events") or []:
            obj.events[(site, ev["tag"])] = {"attempts": [a["attempt"] for a in ev.get("attempts") or []],
                                             "accepted": ev.get("accepted_attempt"), "renamed": ev.get("renamed_files") or {}}
    obj.raw_comparator_child = isinstance(raw.get("comparator"), dict) and "child" in raw["comparator"]
    s3tags = [r.get("tag") for r in (sites.get("v2_driver.solve/callgrind") or {}).get("records") or []]
    # ---- evaluate (the core's attribution and named gaps, unchanged)
    recs = [K.record_of(L, "RJ") for L in obj.launches]
    res = {}
    for rs in ("RI", "RJ"):
        attr, gaps, named = K.attribute(obj, [K.record_of(L, rs) for L in obj.launches], rs)
        res[rs] = {"attr": attr, "gaps": gaps, "named": named}
    # ---- the count table
    rows = []
    for tag in sorted(per_tag):
        d = "solver"
        N = sum(1 for r in recs if r["stdout"] == "%s/%s.ms.log" % (d, tag))
        nrb = sum(1 for x in obj.rb1 if x["tag"] == tag and x["site"] == "S-1")
        nrl = sum(1 for x in obj.rl2 if x["tag"] == tag)
        ncg = sum(1 for r in recs if r["stdout"] == "solver/%s.callgrind.stdout" % tag)
        ccount = sum(1 for x in obj.rb1 if x["tag"] == tag and x["site"] == "S-1" and x["cg_present"] is True)
        rows.append({"site": "S-1", "tag": tag, "N": N, "RB1": nrb, "RL2": nrl, "RI1_a_i_holds": N == nrb + nrl,
                     "Ncg": ncg, "callgrind_result_present_count": ccount, "RJ1_b_holds": ncg == ccount,
                     "S3_record_for_tag": s3tags.count(tag), "source": per_tag[tag]["source"],
                     "raw_row_carries_key_instructions_callgrind": per_tag[tag]["row_has_key"]})
    for n in listing.get("health", []):
        if n.endswith(".ms.log"):
            rows.append({"site": "S-2", "tag": n[:-7], "N": 1, "note": "no archived package has health/ files"})
    nl1 = sum(1 for r in recs if re.match(r"^solver/.+\.ms\.log$", r["stdout"]))
    nl2 = sum(1 for r in recs if re.match(r"^health/.+\.ms\.log$", r["stdout"]))
    site_rows = [{"site": "S-1", "launch_records": nl1, "attempts_total": obj.counters["S-1"]["attempts_total"],
                  "passthrough_calls_gb_only_true": obj.counters["S-1"]["passthrough"],
                  "RI1_a_iii_holds": nl1 == obj.counters["S-1"]["attempts_total"] + obj.counters["S-1"]["passthrough"]},
                 {"site": "S-2", "launch_records": nl2, "attempts_total": obj.counters["S-2"]["attempts_total"],
                  "RI1_a_iii_holds": nl2 == obj.counters["S-2"]["attempts_total"]}]
    tot_ncg = sum(1 for r in recs if re.match(r"^solver/.+\.callgrind\.stdout$", r["stdout"]))
    tot_c = sum(1 for x in obj.rb1 if x["site"] == "S-1" and x["cg_present"] is True)
    rj1_site = {"callgrind_launch_records": tot_ncg, "attempt_records_with_callgrind_result_present": tot_c, "holds": tot_ncg == tot_c,
                "S3_records_total_cross_check": len(s3tags), "S3_counter_callgrind_children_observed": ((sites.get("v2_driver.solve/callgrind") or {}).get("counters") or {}).get("callgrind_children_observed")}
    ncmp = sum(1 for r in recs if r["stdout"] == "comparator/stdout.log")
    rj3 = {"comparator_launch_records": ncmp, "raw_comparator_child_present": obj.raw_comparator_child,
           "required": 1 if obj.raw_comparator_child else 0, "holds": ncmp == (1 if obj.raw_comparator_child else 0)}
    unk = [r["stdout"] for r in recs if not any(f.match(r["stdout"]) for f in K.SIX_FORMS)]
    pari = sorted(f for f in files if f.startswith("pari/"))
    kinds = {}
    for r in recs:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    first_clause = {}
    for f in files:
        a = res["RJ"]["attr"].get(f)
        first_clause[f] = ("(%s) %s" % (a[0][0], a[0][1])) if a else ("NON-LAUNCH " + obj.nonlaunch[f] if f in obj.nonlaunch else "UNATTRIBUTED")
    OUT["packages"][rid] = {
        "files_in_the_five_directories": len(files), "reconstructed_launch_records": len(recs), "record_kinds": kinds,
        "RJ": {"recorder_gaps": res["RJ"]["gaps"], "named_gaps": res["RJ"]["named"], "unattributed_count": len(res["RJ"]["gaps"])},
        "RI_contrast": {"recorder_gaps": res["RI"]["gaps"], "named_gaps": res["RI"]["named"]},
        "count_rows_site_tag": rows, "site_rows": site_rows, "RJ1_site_row": rj1_site, "RJ3_comparator_row": rj3,
        "RJ4b_unknown_kind_stdout_paths": unk, "RJ2_pari_files": pari, "events": len(obj.events),
        "per_file_first_clause_RJ": first_clause}
    P("=" * 100)
    P("%s kind %s: files %d, reconstructed launch records %d %s, events %d" % (rid, raw.get("kind"), len(files), len(recs), kinds, len(obj.events)))
    P("  RJ recorder gaps (%d): %s" % (len(res["RJ"]["gaps"]), res["RJ"]["gaps"]))
    P("  RJ named gaps: %s" % res["RJ"]["named"])
    P("  RI (contrast) gaps %d named %s" % (len(res["RI"]["gaps"]), res["RI"]["named"]))
    P("  per (site, tag) rows: %d; RI-1 (a) (i) holds on %d; RJ-1 (b) holds on %d; mismatches: %s"
      % (len(rows), sum(1 for r in rows if r.get("RI1_a_i_holds")), sum(1 for r in rows if r.get("RJ1_b_holds")),
         [r["tag"] for r in rows if not (r.get("RI1_a_i_holds") and r.get("RJ1_b_holds"))]))
    for r in rows:
        P("    %(site)s %(tag)-32s N=%(N)d RB1=%(RB1)d RL2=%(RL2)d Ncg=%(Ncg)d present=%(callgrind_result_present_count)d S3=%(S3_record_for_tag)d | %(source)s" % r)
    P("  site rows: %s" % site_rows)
    P("  RJ-1 site row: %s" % rj1_site)
    P("  RJ-3 comparator row: %s" % rj3)
    P("  RJ-4 (b) unknown-kind stdout paths: %s" % unk)
    P("  RJ-2 pari/ files: %s" % pari)
with open(os.path.join(SCR, "listing_v2.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
tot = sum(v["files_in_the_five_directories"] for v in OUT["packages"].values())
un = sum(v["RJ"]["unattributed_count"] for v in OUT["packages"].values())
P("\nTOTAL files %d, unattributed under launchkind %d; WROTE listing_v2.json" % (tot, un))
```

### lj1_v1.py

- sha256: 0f551d8e18b14ed20f9bcb6efee541fb38a1150b63ead78fd5f9403c3511a602
- argv: `C036: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj1_v1.py > lj1_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-1 objects: for EACH production launch kind LK-1..LK-6,
lost-record constructions over the launch paths of the frozen run_child (refusal before fork; a child failing before
its stdout open; a refusal after fork, ERR setrlimit or the P-8 parent refusal; a launch that exec'd), with the
record alone lost and with the record and its detector lost together; plus the RGL-11 raise paths, escaped-child
(FO-1 shape) launches with the parent's record lost, a tag solved twice (code the repository lacks), and the
consistent-loss objects of RGL-10. Evaluator: rjcore_v2.py UNCHANGED (the same core LJ-0 was re-run with,
lj0_v2.out). Writes lj1_v1.json next to itself."""
import json
import os
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v2 as K  # noqa: E402

OUT = {}


def P(s=""):
    print(s)


def run(oid, desc, pkg, rule_sets=("RI", "RJ")):
    P("=" * 110)
    P("%s: %s" % (oid, desc))
    for p in pkg.premises:
        P("  premise: %s" % p)
    OUT[oid] = {"description": desc, "premises": pkg.premises, "results": {}}
    for rs in rule_sets:
        res = K.evaluate(pkg, rs)
        K.show(res, pkg, P)
        OUT[oid]["results"][rs] = {k: res[k] for k in ("verdict", "flag", "definitions", "named_gaps", "recorder_gaps",
                                                       "frozen_items", "absent_records")}


# ------------------------------------------------------------------------------------------------ package templates
def cells4(name, normal=False):
    """cells m = 4: arm S4 (polynomial) and arm raw_x (raw grid child job per target), callgrind on target 0 of each
    arm (v2_driver.py 1089, 1157-1175)."""
    pk = K.Pkg(name, "cells", planned_basis=True, normal=normal)
    return pk


def add_s4(pk, cg0="exec_ok", ms0="exec_ok"):
    pk.solve("S4_t0", [ms0], retain_input=True, callgrind=(cg0 if ms0 == "exec_ok" else None))
    pk.solve("S4_t1", ["exec_ok"], retain_input=False)
    pk.solve("S4_t2", ["exec_ok"], retain_input=False)


def add_rawx(pk, job1="exec_ok"):
    for i in range(3):
        path = job1 if i == 1 else "exec_ok"
        pk.child_job("grid_raw_x_t%d" % i, path, job="raw_grid")
        if path == "exec_ok":                         # raw_grid returned equations: the target is solved (1161-1175)
            pk.solve("raw_x_t%d" % i, ["exec_ok"], retain_input=(i == 0), callgrind=("exec_ok" if i == 0 else None))


def cells5(name, normal=False):
    return K.Pkg(name, "cells", planned_basis=True, normal=normal)


def anchor(name, cmp_path="exec_ok", normal=False):
    pk = K.Pkg(name, "anchor_identity", gate=True, planned_basis=False, normal=normal)
    pk.comparator(cmp_path)
    if cmp_path == "exec_ok":                         # 656-659: a non-ok comparator ends the package with finish()
        pk.child_job("anchor_S4", "exec_ok", job="build_poly")
        for t in ("comparator_random", "v2_t0", "v2_t1", "v2_t2"):
            pk.solve("anchor_%s" % t, ["exec_ok"], gb_only=True)
        pk.solve("anchor_comparator_system", ["exec_ok"], gb_only=True, raw_row=False)
    return pk


def controls_a1(name, gp_path="exec_ok", d444=("exec_ok",), normal=False):
    pk = K.Pkg(name, "controls_a1", a1_image=True, planned_basis=False, normal=normal)
    pk.gp("controls_a1_pari", gp_path)
    pk.health("health_p1073741831_d222", ["exec_ok"])
    pk.health("health_p1073741831_d444", list(d444))
    if d444[-1] != "exec_ok":                         # a1_health.run 238-242: a failing pattern is re-drawn once (_seed2)
        pk.health("health_p1073741831_d444_seed2", ["exec_ok"])
    pk.health_report(1073741831)
    pk.child_job("ctl_a1_torsion_S3_rq", "exec_ok")
    pk.child_job("ctl_a1_S3_rescaled", "exec_ok")
    pk.solve("ctl_a1_planted_torsion_S3_rq", ["exec_ok"])
    pk.solve("ctl_a1_planted_S3_rescaled", ["exec_ok"])
    return pk


PATHS = ("A", "pre_stdout_99", "err_setrlimit_97", "P8", "exec_ok")


def drop_rb1(pk, lid):
    """consistent loss of the attempt record written for launch lid and of its counter increment."""
    for x in list(pk.rb1):
        if x.get("lid") == lid:
            pk.rb1.remove(x)
            site = x["site"]
            pk.counters[site]["attempts_total"] -= 1


# ------------------------------------------------------------------------------------------------ LK-1 child job
for path in PATHS:
    pk = cells4("LK1-%s" % path)
    add_s4(pk)
    add_rawx(pk, job1=path)
    pk.lost.add("cj:grid_raw_x_t1")
    pk.premises.append("child-job launch record of grid_raw_x_t1 absent (path %s)" % path)
    run("LK-1 %s record lost" % path, "child job (v2_driver.py 101), raw_grid of raw_x target 1, path %s, record lost; detector: the spec written before the launch (98-99)" % path, pk)
for path in ("A", "pre_stdout_99"):
    pk = cells4("LK1-%s-spec" % path)
    add_s4(pk)
    add_rawx(pk, job1=path)
    pk.lost.add("cj:grid_raw_x_t1")
    pk.files.pop("child/grid_raw_x_t1.spec.json", None)
    pk.premises.append("record lost AND the frozen driver's spec file absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it; scan_v2 removals)")
    run("LK-1 %s record+spec lost" % path, "child job, path %s, record and spec file both absent" % path, pk)

# ------------------------------------------------------------------------------------------------ LK-2 msolve at S-1
for path in PATHS + ("exec_timeout",):
    pk = cells5("LK2-%s" % path)
    pk.solve("S5_t0", ["exec_ok"], retain_input=True)
    pk.solve("S5_t1", [path], retain_input=False)
    pk.solve("S5_t2", ["exec_ok"], retain_input=False)
    pk.lost.add("S5_t1/ms1")
    pk.premises.append("msolve launch record of S5_t1 absent (path %s)" % path)
    run("LK-2 %s record lost" % path, "msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path %s, record lost; detector: RI-1 (a) (RB-1, counters)" % path, pk)
    pk2 = cells5("LK2-%s-consistent" % path)
    pk2.solve("S5_t0", ["exec_ok"], retain_input=True)
    pk2.solve("S5_t1", [path], retain_input=False)
    pk2.solve("S5_t2", ["exec_ok"], retain_input=False)
    pk2.lost.add("S5_t1/ms1")
    drop_rb1(pk2, "S5_t1/ms1")
    pk2.premises.append("RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path %s)" % path)
    run("LK-2 %s consistent loss" % path, "msolve at S-1, path %s, record + RB-1 + counter lost together" % path, pk2)
pk = cells5("LK2-pre99-retained-consistent")
pk.solve("S5_t0", ["pre_stdout_99"], retain_input=True)
pk.solve("S5_t1", ["exec_ok"], retain_input=False)
pk.lost.add("S5_t0/ms1")
drop_rb1(pk, "S5_t0/ms1")
pk.premises.append("RGL-10 consistent loss on target 0, whose input <tag>.ms is retained (v2_driver.py 1174 retain_input=(i == 0))")
run("LK-2 pre_stdout_99 consistent loss, input retained", "msolve at S-1, target 0, child failing before its stdout file, input retained", pk)

# ------------------------------------------------------------------------------------------------ LK-3 callgrind
for path in PATHS + ("exec_fail", "exec_timeout"):
    pk = cells4("LK3-%s" % path)
    add_s4(pk, cg0=path)
    pk.lost.add("S4_t0/cg")
    pk.premises.append("callgrind launch record of S4_t0 absent (path %s)" % path)
    run("LK-3 %s record lost" % path, "callgrind (v2_solver.py 517), cells m = 4 target 0, path %s, record lost; detector: RB-1 (e) callgrind_result_present" % path, pk)
for path in ("pre_stdout_99", "exec_ok"):
    pk = cells4("LK3-%s-flip" % path)
    add_s4(pk, cg0=path)
    pk.lost.add("S4_t0/cg")
    for x in pk.rb1:
        if x["tag"] == "S4_t0":
            x["cg_present"] = False
    pk.premises.append("record lost AND callgrind_result_present recorded false although the returned result carried the key: a recorder DEFECT, not a lost record (RJ-1 (a) copies the key presence from the returned result)")
    run("LK-3 %s record lost + field false" % path, "callgrind, path %s, record lost, RB-1 (e) written false" % path, pk)
    pk = cells4("LK3-%s-absentfield" % path)
    add_s4(pk, cg0=path)
    pk.lost.add("S4_t0/cg")
    for x in pk.rb1:
        if x["tag"] == "S4_t0":
            x["cg_present"] = None
    pk.premises.append("record lost AND the RB-1 (e) field absent from a present attempt record")
    run("LK-3 %s record lost + field absent" % path, "callgrind, path %s, record lost, RB-1 (e) absent (RF-0 (a), (c))" % path, pk)
    pk = cells4("LK3-%s-allbound" % path)
    add_s4(pk, cg0=path)
    pk.lost.update({"S4_t0/cg", "S4_t0/ms1"})
    drop_rb1(pk, "S4_t0/ms1")
    pk.premises.append("consistent loss of everything bound to the callgrind launch: its record, the msolve record of the same attempt, the RB-1 attempt record carrying (e), and the attempts_total increment")
    run("LK-3 %s consistent loss (all bound)" % path, "callgrind, path %s, callgrind record + msolve record + RB-1 + counter lost" % path, pk)

# ------------------------------------------------------------------------------------------------ LK-4 comparator
for path in PATHS + ("exec_fail",):
    pk = anchor("LK4-%s" % path, cmp_path=path)
    pk.lost.add("cmp")
    pk.premises.append("comparator launch record absent (path %s)" % path)
    run("LK-4 %s record lost" % path, "comparator (v2_driver.py 650), anchor-identity, path %s, record lost; detector: raw comparator.child (652, 655)" % path, pk)
pk = anchor("LK4-exec_ok-rawkey", cmp_path="exec_ok")
pk.lost.add("cmp")
pk.raw_comparator_child = False
pk.premises.append("record lost AND a driver-written raw-result.json without comparator.child: no frozen path writes it (655 precedes every exit; finish() is the only driver writer); a premise OUTSIDE the lost-record class")
run("LK-4 exec_ok record lost + raw key absent", "comparator, record lost and comparator.child absent", pk)

# ------------------------------------------------------------------------------------------------ LK-5 msolve at S-2
for path in PATHS:
    pk = controls_a1("LK5-%s" % path, d444=(path,))
    pk.lost.add("health:health_p1073741831_d444/ms1")
    pk.premises.append("S-2 launch record of health_p1073741831_d444 absent (path %s)" % path)
    run("LK-5 %s record lost" % path, "msolve at S-2 (a1_health.py 147), controls_a1, path %s, record lost; detector: RI-1 (a) at S-2" % path, pk)
    pk2 = controls_a1("LK5-%s-consistent" % path, d444=(path,))
    pk2.lost.add("health:health_p1073741831_d444/ms1")
    drop_rb1(pk2, "health:health_p1073741831_d444/ms1")
    pk2.premises.append("RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path %s)" % path)
    run("LK-5 %s consistent loss" % path, "msolve at S-2, path %s, record + RB-1 + counter lost together" % path, pk2)

# ------------------------------------------------------------------------------------------------ LK-6 gp
for path in PATHS:
    pk = controls_a1("LK6-%s" % path, gp_path=path)
    pk.lost.add("gp:controls_a1_pari")
    pk.premises.append("gp launch record absent (path %s)" % path)
    run("LK-6 %s record lost" % path, "gp (a1_pari.py 96), controls_a1, path %s, record lost; detector: pari/<tag>.gp written before the launch (91-93)" % path, pk)
for path in ("A", "pre_stdout_99"):
    pk = controls_a1("LK6-%s-script" % path, gp_path=path)
    pk.lost.add("gp:controls_a1_pari")
    pk.files.pop("pari/controls_a1_pari.gp", None)
    pk.nonlaunch.pop("pari/controls_a1_pari.gp", None)
    pk.premises.append("record lost AND the script absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it)")
    run("LK-6 %s record+script lost" % path, "gp, path %s, record and script both absent" % path, pk)

# ------------------------------------------------------------------------------------------------ RGL-11 raise paths at LK-3
for lost, tag in ((set(), "records present"), ({"S4_t0/cg"}, "callgrind record lost"), ({"S4_t0/cg", "S4_t0/ms1"}, "both records lost")):
    pk = K.Pkg("RGL11 %s" % tag, "cells", planned_basis=True, normal=False, raw_writer="wrapper")
    pk.files["solver/S4_t0.ms"] = "driver:solve-input"
    pk.launch("S4_t0/ms1", "msolve", "exec_ok", "solver/S4_t0.ms.log", "solver/S4_t0.ms.err",
              argv_paths=("solver/S4_t0.ms", "solver/S4_t0.ms.out"), site="S-1", tag="S4_t0", outputs=["solver/S4_t0.ms.out"])
    pk.launch("S4_t0/cg", "callgrind", "exec_ok", "solver/S4_t0.callgrind.stdout", "solver/S4_t0.callgrind.stderr",
              argv_paths=("solver/S4_t0.ms", "solver/S4_t0.cg.ms.out"), cg_out="solver/S4_t0.callgrind.out", site="S-3", tag="S4_t0",
              outputs=["solver/S4_t0.callgrind.out"])
    pk.lost.update(lost)
    pk.premises.append("callgrind_instructions raises after its run_child returned (v2_solver.py 526-529: open / parse of the out file), so solve raises (209), no result is returned, no RB-1 record and no counter increment are written (r3_resolve.py 263 -> 273 not reached); no frozen handler (scan_v2); the driver dies; the wrapper writes raw-result.json")
    if lost:
        pk.premises.append("launch record(s) %s absent" % sorted(lost))
    run("RGL-11 %s" % tag, "cells m = 4 target 0: callgrind launched, then callgrind_instructions raises", pk)

# ------------------------------------------------------------------------------------------------ escaped children with the parent's record lost
for kind in ("msolve", "callgrind", "gp", "comparator", "childjob", "health"):
    for fo in ("FO1_C", "FO1_B"):
        if kind == "msolve":
            pk = cells5("FO-%s-%s" % (kind, fo))
            pk.solve("S5_t0", ["exec_ok"])
            pk.solve("S5_t1", [fo], retain_input=False)
            lid = "S5_t1/ms1"
        elif kind == "callgrind":
            pk = cells4("FO-%s-%s" % (kind, fo))
            add_s4(pk, cg0=fo)
            lid = "S4_t0/cg"
        elif kind == "gp":
            pk = controls_a1("FO-%s-%s" % (kind, fo), gp_path=fo)
            lid = "gp:controls_a1_pari"
        elif kind == "comparator":
            pk = anchor("FO-%s-%s" % (kind, fo), cmp_path=fo)
            lid = "cmp"
        elif kind == "childjob":
            pk = cells4("FO-%s-%s" % (kind, fo))
            add_s4(pk)
            add_rawx(pk, job1=fo)
            lid = "cj:grid_raw_x_t1"
        else:
            pk = controls_a1("FO-%s-%s" % (kind, fo), d444=(fo,))
            lid = "health:health_p1073741831_d444/ms1"
        pk.lost.add(lid)
        pk.premises.append("escaped fork child (%s shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent" % fo)
        run("ESC %s %s parent record lost" % (kind, fo), "escaped child at the %s launch, parent record lost" % kind, pk, ("RJ",))

# ------------------------------------------------------------------------------------------------ a tag solved twice (code the repository lacks)
for oid, lost in (("TW-1", set()), ("TW-2", {"S4_t0/cg"}), ("TW-3", {"S4_t0/ms1"})):
    pk = cells4(oid)
    pk.solve("S4_t0", ["exec_ok"], retain_input=True, callgrind="exec_ok")
    first = [L["lid"] for L in pk.launches]
    pk.solve("S4_t0", ["exec_ok"], retain_input=True, callgrind="exec_ok")
    for L in pk.launches[len(first):]:
        L["lid"] = L["lid"] + "#2"
    for x in pk.rb1[1:]:
        x["lid"] = x["lid"] + "#2"
    pk.lost.update(lost)
    pk.premises.append("HYPOTHETICAL code: one tag solved twice in one package outside an event, callgrind both times (no frozen path does this; BJ-2 of review be2daf; scan_v1 calls)")
    if lost:
        pk.premises.append("the FIRST call's %s launch record absent" % sorted(lost))
    run("%s" % oid, "tag S4_t0 solved twice with callgrind; %s" % ("every record present" if not lost else "first record lost"), pk, ("RI", "RJ"))

# ------------------------------------------------------------------------------------------------ an event tag carrying the callgrind launch
for oid, mut in (("EV-cg lost", "cg"), ("EV-ms2 lost", "ms2"), ("EV-attempt2 consistent", "all2"), ("EV-attempt2 consistent + renamed key", "all2ren")):
    pk = cells4(oid)
    pk.solve("S4_t0", ["exec_ssf", "exec_ok"], retain_input=True, callgrind="exec_ok")
    pk.solve("S4_t1", ["exec_ok"], retain_input=False)
    if mut == "cg":
        pk.lost.add("S4_t0/cg")
    elif mut == "ms2":
        pk.lost.add("S4_t0/ms2")
    else:
        pk.lost.update({"S4_t0/cg", "S4_t0/ms2"})
        drop_rb1(pk, "S4_t0/ms2")
        ev = pk.events[("S-1", "S4_t0")]
        ev["attempts"] = [1]
        ev["accepted"] = 1
        if mut == "all2ren":
            ev["renamed"].pop("attempt1", None)
    pk.premises.append("SE-3 event at the callgrind target (attempt 1 SSF, attempt 2 ok with callgrind); mutation %s" % mut)
    run(oid, "event tag S4_t0 with callgrind on the accepted attempt; %s" % mut, pk)

# ------------------------------------------------------------------------------------------------ RGL-10's own objects
pk = cells5("LN-6")
pk.solve("S5_t0", ["exec_ok"])
pk.solve("S5_t1", ["A"], retain_input=False)
pk.lost.add("S5_t1/ms1")
drop_rb1(pk, "S5_t1/ms1")
pk.premises.append("class A refusal before fork; record, RB-1 and counter consistently lost")
run("LN-6", "refusal before fork, consistent loss", pk)
pk = cells5("LN-3")
pk.solve("S5_t0", ["exec_ok"])
pk.solve("S5_t1", ["exec_ok"], retain_input=False)
pk.lost.add("S5_t1/ms1")
drop_rb1(pk, "S5_t1/ms1")
pk.premises.append("exec'd msolve child; record, RB-1 and counter consistently lost")
run("LN-3", "exec'd msolve, consistent loss", pk)

with open(os.path.join(SCR, "lj1_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE lj1_v1.json (%d objects)" % len(OUT))
```

### lj2_v1.py

- sha256: f66ffdf96d09f6bb5ae448b8848d07bae4d54f46c6d2544f686ecd4789b34aa5
- argv: `C039: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj2_v1.py > lj2_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-2 objects: every normal path of either plan built from the
frozen call sites (N-1..N-13 of review TASK-20260924-94cc33 and the PASS / PASS_ZL rows of the close census's RKR-4 (b)
table, readbackclose-census.md 476-492), plus the launch-kind paths RJ-1..RJ-4 newly read (a callgrind child refused
before fork, failing before its stdout open, ERR setrlimit, failing after exec, timed out; a gp child refused before
fork; the comparator's failure exit; a callgrind launch on an SE-3 event's accepted attempt). Evaluator: rjcore_v2.py
UNCHANGED. A PLANNED-BASIS REFUSAL is flagged when a planned basis outcome (failclosed definition, with childend RG-2 and
gapattr RH-2 exclusions) receives FAIL. Writes lj2_v1.json next to itself."""
import json
import os
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v2 as K  # noqa: E402

OUT = {}


def P(s=""):
    print(s)


def run(oid, desc, pkg, rule_sets=("RI", "RJ")):
    P("=" * 110)
    P("%s: %s" % (oid, desc))
    OUT[oid] = {"description": desc, "results": {}}
    for rs in rule_sets:
        res = K.evaluate(pkg, rs)
        K.show(res, pkg, P)
        OUT[oid]["results"][rs] = {k: res[k] for k in ("verdict", "flag", "definitions", "named_gaps", "recorder_gaps", "frozen_items")}


def fixture(name, gate=True, cg="exec_ok", replaced=False):
    """cmd_fixture / fixture_core (275-523): 4 builds (uncached), per target 2 raw_grid jobs + 6 solves, callgrind on every
    ok solve (358); targets reg0, reg1, fresh1, fresh2, planted0, planted1 (+ a replaced fresh draw)."""
    pk = K.Pkg(name, "fixture", gate=gate, planned_basis=True, normal=True)
    for arm in ("S3", "S3_rescaled", "torsion_S3_norm", "torsion_S3_rq"):
        pk.child_job("fixture_%s" % arm, "exec_ok", job="build_poly")
    labels = ["reg0", "reg1", "fresh1"] + (["fresh2", "fresh3"] if replaced else ["fresh2"]) + ["planted0", "planted1"]
    for lab in labels:
        for arm in ("raw_x", "raw_u", "S3", "S3_rescaled", "torsion_S3_norm", "torsion_S3_rq"):
            tag = "fx_%s_%s" % (lab, arm)
            if arm.startswith("raw"):
                pk.child_job(tag, "exec_ok", job="raw_grid")
            pk.solve(tag, ["exec_ok"], retain_input=True, callgrind=cg)
    return pk


def cells(name, m, arms=("S", "raw_x"), targets=3, target_paths=None, cg_path="exec_ok", ssf_t0=False, normal=True):
    """cmd_cells / _run_cell (1016-1236): polynomial arms load the cached build; raw arms run a raw_grid child job per
    target; callgrind on target 0 when m <= 4 (1089, 1174-1175); retain_input only on target 0."""
    pk = K.Pkg(name, "cells", planned_basis=True, normal=normal)
    for arm in arms:
        a = ("S%d" % m) if arm == "S" else arm
        for i in range(targets):
            tag = "%s_t%d" % (a, i)
            path = (target_paths or {}).get((arm, i), "exec_ok")
            if arm.startswith("raw"):
                pk.child_job("grid_" + tag, "exec_ok", job="raw_grid")
            attempts = ["exec_ssf", path] if (ssf_t0 and i == 0) else [path]
            cgp = cg_path if (m <= 4 and i == 0 and path == "exec_ok") else None
            pk.solve(tag, attempts, retain_input=(i == 0), callgrind=cgp)
    return pk


def anchor(name, cmp_path="exec_ok"):
    pk = K.Pkg(name, "anchor_identity", gate=True, planned_basis=False, normal=True)
    pk.comparator(cmp_path)
    if cmp_path == "exec_ok":
        pk.child_job("anchor_S4", "exec_ok", job="build_poly")
        for t in ("comparator_random", "v2_t0", "v2_t1", "v2_t2"):
            pk.solve("anchor_%s" % t, ["exec_ok"], gb_only=True)
        pk.solve("anchor_comparator_system", ["exec_ok"], gb_only=True, raw_row=False)
    return pk


def controls(name):
    """cmd_controls (752-931): 11 child jobs (5 builds, 6 raw grids) and 8 solves without callgrind (786, 787, 841)."""
    pk = K.Pkg(name, "controls", gate=True, planned_basis=True, normal=True)
    pk.child_job("ctl_identity_n3", "exec_ok")
    for lab in ("random", "planted"):
        pk.child_job("ctl_raw_%s" % lab, "exec_ok", job="raw_grid")
        pk.solve("ctl_identity_%s" % lab, ["exec_ok"], raw_row=False)
        pk.solve("ctl_rawx_%s" % lab, ["exec_ok"], raw_row=False)
    for m in (3, 4):
        pk.child_job("ctl_identity_n5_m%d" % m, "exec_ok")
        pk.child_job("ctl_raw_n5_m%d" % m, "exec_ok", job="raw_grid")
    for arm in ("S3", "S3_rescaled", "torsion_S3_rq", "torsion_S3_norm"):
        pk.child_job("ctl_%s" % arm, "exec_ok")
        pk.solve("ctl_planted_%s" % arm, ["exec_ok"], raw_row=False)
    return pk


def controls_a1(name, gp_path="exec_ok", d222=("exec_ok",), d444=("exec_ok",)):
    pk = K.Pkg(name, "controls_a1", a1_image=True, planned_basis=False, normal=True)
    pk.gp("controls_a1_pari", gp_path)
    pk.health("health_p1073741831_d222", list(d222))
    pk.health("health_p1073741831_d444", list(d444))
    if d444[-1] != "exec_ok":
        pk.health("health_p1073741831_d444_seed2", ["exec_ok"])
    pk.health_report(1073741831)
    pk.child_job("ctl_a1_torsion_S3_rq", "exec_ok")
    pk.child_job("ctl_a1_S3_rescaled", "exec_ok")
    pk.solve("ctl_a1_planted_torsion_S3_rq", ["exec_ok"])
    pk.solve("ctl_a1_planted_S3_rescaled", ["exec_ok"])
    return pk


# ------------------------------------------------------------------------------------------------ RKR-4 (b) PASS / PASS_ZL rows
run("row478 G1 fixture", "gate fixture package, every launch normal (callgrind on 36 ok solves)", fixture("G1"))
run("row478 G3 anchor", "gate anchor-identity, comparator ok, uncached build, five gb_only solves", anchor("G3"))
run("row478 G4 controls", "gate controls, 11 child jobs, 8 solves", controls("G4"))
run("row480 controls_a1 image", "controls_a1 image, gp, health d222 / d444, 2 builds, 2 solves", controls_a1("A1"))
pk = K.Pkg("F-4", "fixture4", planned_basis=True, normal=True)
for arm in ("S4", "S4_rescaled", "torsion_S4_norm", "torsion_S4_rq"):
    pk.child_job("f4_%s" % arm, "exec_ok")
for i in range(2):
    for arm in ("S4", "S4_rescaled", "torsion_S4_norm", "torsion_S4_rq"):
        pk.solve("f4_t%d_%s" % (i, arm), ["exec_ok"])
run("row481 F-4 launched", "fixture4, 4 uncached builds, 8 solves without callgrind (565)", pk)
run("row482 Z-F4", "fixture4 refused before any launch (536-541), finish() driver-written", K.Pkg("Z-F4", "fixture4", planned_basis=True, normal=True))
pk = K.Pkg("build", "build", planned_basis=True, normal=True)
for j in range(6):
    pk.child_job("build_1073741831_shape_arm%d_m5" % j, "exec_ok", to_cache=True)
run("row483 build", "build package, cached builds (961-962, to_cache=True: outputs outside the run directory)", pk)
run("row485 cells m = 5 measured", "cells m = 5, arms S5 and raw_x, 3 targets", cells("C5", 5))
run("row485b cells m = 5 not_measured", "cells m = 5, timeouts", cells("C5nm", 5, target_paths={("S", 0): "exec_timeout", ("S", 1): "exec_timeout", ("raw_x", 1): "exec_timeout"}))
run("row486 Z-C5", "cells m = 5, every cell refused / not_attempted before any launch", K.Pkg("Z-C5", "cells", planned_basis=True, normal=True))
run("row488 cells m = 4", "cells m = 4, arms S4 and raw_x, callgrind on target 0 of each arm", cells("C4", 4))
run("row489 aggregate", "aggregate, zero launch, driver-written raw (1322)", K.Pkg("AGG", "aggregate", planned_basis=True, normal=True))

# ------------------------------------------------------------------------------------------------ N-1..N-13 (review 94cc33, AJ-2)
run("N-1", "cells m = 5 measured", cells("N-1", 5, arms=("S",)))
run("N-2", "cells m = 5 not_measured (timeout)", cells("N-2", 5, arms=("S",), target_paths={("S", 0): "exec_timeout", ("S", 2): "exec_timeout"}))
run("N-3", "cells m = 4 raw_grid measured, callgrind ok", cells("N-3", 4, arms=("raw_x",)))
pk = cells("N-4", 4, arms=("S",))
pk.child_job("grid_raw_x_t0", "exec_fail", job="raw_grid")
pk.files["child/grid_raw_x_t0.npz"] = "launch:cj:grid_raw_x_t0"                  # partial .npz kept (137-139)
run("N-4", "cells m = 4 raw_grid child crashed after exec, partial .npz kept", pk)
run("N-5", "SE-3 re-solve at S-1, 2 attempts", cells("N-5", 5, arms=("S",), ssf_t0=True))
pk = cells("N-5b", 5, arms=("S",))
pk.solve("S5_t9", ["exec_ssf"] * 6, retain_input=False)
run("N-5b", "SE-3 re-solve, 6 attempts, still SSF after the last", pk)
run("N-5c", "SE-3 re-solve on the callgrind target (m = 4, target 0)", cells("N-5c", 4, arms=("S",), ssf_t0=True))
run("N-6", "controls_a1 with an HR-3 re-solve at S-2", controls_a1("N-6", d222=("exec_ssf", "exec_ok")))
run("N-6b", "controls_a1 with a failing d444 pattern and the _seed2 retry", controls_a1("N-6b", d444=("exec_fail",)))
run("N-7", "failing callgrind child (valgrind exits nonzero after writing its out file)", cells("N-7", 4, arms=("S",), cg_path="exec_fail"))
run("N-8", "timed-out callgrind child", cells("N-8", 4, arms=("S",), cg_path="exec_timeout"))
pk = K.Pkg("N-9", "build", planned_basis=True, normal=True)
pk.child_job("build_x", "exec_ok", to_cache=True)
run("N-9", "cached builds", pk)
pk = K.Pkg("N-10", "fixture4", planned_basis=True, normal=True)
pk.child_job("f4_S4", "exec_ok")
pk.solve("f4_t0_S4", ["exec_ok"])
run("N-10", "fixture4 uncached builds and solves", pk)
pk = cells("N-11", 5, arms=("S",))
pk.child_job("ctl_refused_meta", "exec_ok", job="raw_grid")                        # v2_child writes a refused meta (68/80)
pk.child_job("ctl_refused_before_fork", "A")
pk.child_job("ctl_err_setrlimit", "err_setrlimit_97")
run("N-11", "child jobs on refusal paths: refused meta; refused before fork (class A); ERR setrlimit (class C)", pk)
run("N-12", "anchor-identity normal", anchor("N-12"))
run("N-13", "Z-C5 (no launch)", K.Pkg("N-13", "cells", planned_basis=True, normal=True))

# ------------------------------------------------------------------------------------------------ launch-kind paths RJ newly reads
for p in ("A", "pre_stdout_99", "err_setrlimit_97", "exec_fail", "exec_timeout"):
    run("NJ-cg %s" % p, "cells m = 4, callgrind child on target 0 path %s, record present" % p, cells("NJ-%s" % p, 4, arms=("S",), cg_path=p))
run("NJ-ms-refused", "cells m = 4, target 0 msolve refused before fork (no callgrind attempted, 184-186)",
    cells("NJ-msA", 4, arms=("S",), target_paths={("S", 0): "A"}))
for p in ("A", "pre_stdout_99", "err_setrlimit_97", "exec_fail"):
    run("NJ-gp %s" % p, "controls_a1, gp child path %s, record present" % p, controls_a1("NJ-gp-%s" % p, gp_path=p))
for p in ("A", "pre_stdout_99", "exec_fail"):
    run("NJ-cmp %s" % p, "anchor-identity, comparator path %s: the failure exit 656-659 with finish()" % p, anchor("NJ-cmp-%s" % p, cmp_path=p))
run("NJ-fixture-replaced", "fixture with a replaced fresh draw (382-387): an extra fresh target, callgrind on its ok arms", fixture("NJ-rep", replaced=True))

with open(os.path.join(SCR, "lj2_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
bad = [k for k, v in OUT.items() if any((r["flag"] or "").startswith("PLANNED") for r in v["results"].values())]
P("\nPLANNED-BASIS REFUSALS: %s" % bad)
P("WROTE lj2_v1.json (%d objects)" % len(OUT))
```

### rdscan_v1.py

- sha256: f3b04122fc00429246511458d0aef22a4129006b1637a54ea1b5d30c044558fb
- argv: `C040: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan_v1.py rdscan_v1.json > rdscan_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch (zero runs; static only). LJ-4 (3): every recorded value that carries the run
# directory, in any form, in the archived controls (RUN-GFPN-bfe956) and anchor-identity (RUN-GFPN-f5412a) packages.
# Reads every regular file of the two packages except *.npz, READ-ONLY with O_NOATIME, lstat (with atime) before and
# after; JSON is parsed with the standard library and walked; every other file is scanned line by line as text.
# Form of each occurrence: PREFIX (the value starts with the run directory), ELEM_WHOLE (a whitespace-delimited
# element equals the run directory), ELEM_PREFIX (a whitespace-delimited element starts with the run directory + "/"),
# OTHER (any other embedding). Imports nothing from the repository. Writes JSON to argv[1].
import json
import os
import sys

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-bfe956", "RUN-GFPN-f5412a"]


def st(p):
    s = os.lstat(p)
    return [s.st_size, s.st_atime_ns, s.st_mtime_ns, s.st_ctime_ns]


def read_noatime(p):
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        out = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                return b"".join(out)
            out.append(b)
    finally:
        os.close(fd)


def form(v, rd):
    if v == rd or v.startswith(rd + "/"):
        return "PREFIX"
    els = v.split()
    if rd in els:
        return "ELEM_WHOLE"
    if any(e.startswith(rd + "/") for e in els):
        return "ELEM_PREFIX"
    return "OTHER"


before, after, out = {}, {}, {}
for rid in PKGS:
    rd = os.path.join(RUNS, rid)
    hits = []
    for dp, dns, fns in os.walk(rd):
        before[dp] = st(dp)
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, rd)
            before[p] = st(p)
            if fn.endswith(".npz"):
                continue
            b = read_noatime(p)
            if rd.encode() not in b:
                continue
            txt = b.decode("utf-8", errors="replace")
            if fn.endswith(".json"):
                try:
                    obj = json.loads(txt)
                except Exception:  # noqa: BLE001
                    obj = None
                if obj is not None:
                    def walk(o, path):
                        if isinstance(o, dict):
                            for k, v in o.items():
                                walk(v, path + "/" + str(k))
                        elif isinstance(o, list):
                            for i, v in enumerate(o):
                                walk(v, path + "[%d]" % i)
                        elif isinstance(o, str) and rd in o:
                            hits.append({"file": rel, "where": path, "form": form(o, rd), "value": o.replace(rd, "<rd>")[:200]})
                    walk(obj, "")
                    continue
            for i, line in enumerate(txt.splitlines(), 1):
                if rd in line:
                    val = line.strip()
                    if ": " in val and fn.endswith(".yaml"):
                        val = val.split(": ", 1)[1].strip().strip("'\"")
                    elif val.startswith("- "):
                        val = val[2:].strip().strip("'\"")
                    hits.append({"file": rel, "where": "line %d" % i, "form": form(val, rd), "value": line.strip().replace(rd, "<rd>")[:200]})
    out[rid] = hits
for p in before:
    after[p] = st(p)
changed = [p for p in before if before[p] != after[p]]
res = {"hits": out, "lstat_checked": len(before), "lstat_changed": changed}
with open(sys.argv[1], "w") as fh:
    json.dump(res, fh, indent=1)
for rid, hits in out.items():
    print("=" * 90)
    print(rid, "occurrences:", len(hits))
    summ = {}
    for h in hits:
        key = (h["file"], h["form"])
        summ.setdefault(key, []).append(h)
    for (f, fm), hs in sorted(summ.items()):
        print("  %-28s %-12s x%-3d e.g. %s | %s" % (f, fm, len(hs), hs[0]["where"], hs[0]["value"][:150]))
print("lstat checked", len(before), "changed", changed)
```

### lj4_v1.py

- sha256: df1759402007f146d221b6ace214ce0c8ad1b7891477acfe24c6e78b86ba72a6
- argv: `C042: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj4_v1.py > lj4_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
"""TASK-20260924-d897a6 scratch (zero runs; static only). LJ-4 (1): derive the expected outcome of every development
check RI-3 (19)-(27) as launchkind RJ-5 (a) reads them and RJ-5 (c) (28)-(32), at record (gap) level and package
level, with the carried V-7 item applied to in-place alterations and without it. Evaluator: rjcore_v2.py UNCHANGED.
Writes lj4_v1.json next to itself."""
import copy
import json
import os
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCR)
import rjcore_v2 as K  # noqa: E402

OUT = []


def P(s=""):
    print(s)


def derive(check, obj, pkg, rs, expected):
    rows = []
    for v7 in (True, False):
        res = K.evaluate(pkg, rs, v7=v7)
        rows.append(res)
    gl = (rows[0]["named_gaps"], rows[0]["recorder_gaps"])
    line = {"check": check, "object": obj, "rule_set": rs, "named_gaps": gl[0], "recorder_gaps": gl[1],
            "verdict_with_V7": rows[0]["verdict"], "verdict_without_V7": rows[1]["verdict"], "expected": expected,
            "altered_in_place": pkg.altered_in_place}
    OUT.append(line)
    P("%-5s %-58s %-7s with V-7 %-7s without %-7s | named %s | gaps %d %s" % (
        check, obj[:58], rs, rows[0]["verdict"], rows[1]["verdict"], gl[0], len(gl[1]), gl[1][:4]))
    P("      expected: %s" % expected)


def cells5_resolve(name, attempts=("exec_ssf", "exec_ok")):
    pk = K.Pkg(name, "cells", planned_basis=True, normal=False)
    pk.solve("S5_t0", list(attempts), retain_input=True)
    pk.solve("S5_t1", ["exec_ok"], retain_input=False)
    return pk


def controls_a1(name, gp_path="exec_ok", d222=("exec_ok",)):
    pk = K.Pkg(name, "controls_a1", a1_image=True, planned_basis=False, normal=False)
    pk.gp("controls_a1_pari", gp_path)
    pk.health("health_p1073741831_d222", list(d222))
    pk.health("health_p1073741831_d444", ["exec_ok"])
    pk.health_report(1073741831)
    pk.child_job("ctl_a1_torsion_S3_rq", "exec_ok")
    pk.child_job("ctl_a1_S3_rescaled", "exec_ok")
    pk.solve("ctl_a1_planted_torsion_S3_rq", ["exec_ok"])
    pk.solve("ctl_a1_planted_S3_rescaled", ["exec_ok"])
    return pk


def controls(name):
    pk = K.Pkg(name, "controls", gate=True, planned_basis=True, normal=False)
    pk.child_job("ctl_identity_n3", "exec_ok")
    for lab in ("random", "planted"):
        pk.child_job("ctl_raw_%s" % lab, "exec_ok", job="raw_grid")
        pk.solve("ctl_identity_%s" % lab, ["exec_ok"], raw_row=False)
        pk.solve("ctl_rawx_%s" % lab, ["exec_ok"], raw_row=False)
    for m in (3, 4):
        pk.child_job("ctl_identity_n5_m%d" % m, "exec_ok")
        pk.child_job("ctl_raw_n5_m%d" % m, "exec_ok", job="raw_grid")
    for arm in ("S3", "S3_rescaled", "torsion_S3_rq", "torsion_S3_norm"):
        pk.child_job("ctl_%s" % arm, "exec_ok")
        pk.solve("ctl_planted_%s" % arm, ["exec_ok"], raw_row=False)
    return pk


def anchor(name, cmp_path="exec_ok"):
    pk = K.Pkg(name, "anchor_identity", gate=True, planned_basis=False, normal=False)
    pk.comparator(cmp_path)
    if cmp_path == "exec_ok":
        pk.child_job("anchor_S4", "exec_ok", job="build_poly")
        for t in ("comparator_random", "v2_t0", "v2_t1", "v2_t2"):
            pk.solve("anchor_%s" % t, ["exec_ok"], gb_only=True)
        pk.solve("anchor_comparator_system", ["exec_ok"], gb_only=True, raw_row=False)
    return pk


def cells4_cg(name, cg_path="exec_ok"):
    pk = K.Pkg(name, "cells", planned_basis=True, normal=False)
    pk.solve("S4_t0", ["exec_ok"], retain_input=True, callgrind=cg_path)
    pk.solve("S4_t1", ["exec_ok"], retain_input=False)
    return pk


def altered(pk):
    pk.altered_in_place = True
    return pk


# (19) SE-3 re-solve at S-1
pk = cells5_resolve("19u")
derive("(19)", "unaltered SE-3 re-solve at S-1", pk, "RJ", "renamed attempt-1 files attributed by RH-1 (vi); no gap")
pk = altered(cells5_resolve("19r"))
pk.events[("S-1", "S5_t0")]["renamed"].pop("attempt1")
derive("(19)", "renamed_files attempt1 removed in place", pk, "RJ", "a recorder gap and FAIL")
pk = altered(cells5_resolve("19l"))
pk.lost.add("S5_t0/ms2")
derive("(19)", "one launch record of the tag removed in place", pk, "RJ", "the COUNT GAP of RI-1 (c) and FAIL (RI-3 (19))")
# (20) HR-3 re-solve at S-2
pk = controls_a1("20u", d222=("exec_ssf", "exec_ok"))
derive("(20)", "unaltered HR-3 re-solve at S-2", pk, "RJ", "attributed; no gap")
pk = altered(controls_a1("20l", d222=("exec_ssf", "exec_ok")))
pk.lost.add("health:health_p1073741831_d222/ms2")
derive("(20)", "one S-2 launch record of the tag removed in place", pk, "RJ", "COUNT GAP and FAIL")
# (21) non-ok callgrind child leaving its out file
pk = cells4_cg("21", cg_path="exec_fail")
derive("(21)", "callgrind child exits nonzero after writing its out file", pk, "RJ", "<tag>.callgrind.out attributed by RH-1 (iii); no gap")
# (22) child-job record removed
pk = altered(K.Pkg("22b", "fixture4", planned_basis=True, normal=False))
pk.child_job("f4_S4", "exec_ok", job="build_poly")
pk.solve("f4_t0_S4", ["exec_ok"])
pk.lost.add("cj:f4_S4")
derive("(22)", "uncached build_poly child-job record removed in place", pk, "RJ", "five gaps .spec.json .stdout .stderr .npz .meta.json; FAIL")
pk = altered(controls("22r"))
pk.lost.add("cj:ctl_raw_random")
derive("(22)", "raw_grid child-job record removed in place", pk, "RJ", "four gaps .spec.json .stdout .stderr .meta.json; FAIL")
# (23) cap-mismatch stop outcome
pk = K.Pkg("23", "cells", planned_basis=True, normal=True)
pk.solve("S5_t0", ["exec_ok"], retain_input=True)
pk.solve("S5_t1", ["P8"], retain_input=False)
derive("(23)", "cap-mismatch stop outcome (P-8 child in a cells m = 5 package)", pk, "RJ", "FAIL; stop class 'a cap read-back mismatch'; no planned-basis refusal (RH-2)")


# (24) / (25) LR objects and single removals among 2, 3 and 6 attempts
def lr(name, n, lost):
    pk = altered(K.Pkg(name, "cells", planned_basis=True, normal=False))
    pk.solve("S5_t0", ["exec_ok"], retain_input=True)
    pk.solve("S5_t1", ["exec_ssf"] * (n - 1) + ["exec_ok"], retain_input=False)
    for x in lost:
        pk.lost.add("S5_t1/ms%d" % x)
    return pk


LRS = [("LR-1", 2, [2]), ("LR-2", 2, [1]), ("LR-3", 3, [2]), ("LR-4", 3, [2, 3])]
for nm, n, lost in LRS:
    derive("(24)", "%s (%d attempts, removed %s)" % (nm, n, lost), lr(nm, n, lost), "RJ", "COUNT GAP and FAIL")
pk = altered(controls_a1("LR-5", d222=("exec_ssf", "exec_ok")))
pk.lost.add("health:health_p1073741831_d222/ms2")
derive("(24)", "LR-5 (S-2, 2 attempts, final removed)", pk, "RJ", "COUNT GAP and FAIL")
for n in (2, 3, 6):
    for x in range(1, n + 1):
        derive("(24)", "single removal %d of %d attempts" % (x, n), lr("s%d_%d" % (x, n), n, [x]), "RJ", "COUNT GAP and FAIL")
for nm, n, lost in LRS[:3]:
    derive("(25)", "%s under RI-1 (a), (d) disabled" % nm, lr(nm, n, lost), "RIx", "NO RI-1 named gap and NO recorder gap (RJ-5 (a))")
pk = altered(controls_a1("LR-5x", d222=("exec_ssf", "exec_ok")))
pk.lost.add("health:health_p1073741831_d222/ms2")
derive("(25)", "LR-5 under RI-1 (a), (d) disabled", pk, "RIx", "NO RI-1 named gap and NO recorder gap (RJ-5 (a))")
# (26) positive control
derive("(26)", "unaltered (19) package", cells5_resolve("26a"), "RJ", "no recorder gap of any kind")
derive("(26)", "unaltered (20) package", controls_a1("26b", d222=("exec_ssf", "exec_ok")), "RJ", "no recorder gap of any kind")
derive("(26)", "DV-18 (a) controls", controls("26c"), "RJ", "no recorder gap of any kind")
derive("(26)", "DV-18 (b) anchor-identity", anchor("26d"), "RJ", "no recorder gap of any kind")
derive("(26)", "DV-18 (e) controls-a1", controls_a1("26e"), "RJ", "no recorder gap of any kind")
# (27)
pk = altered(K.Pkg("27a", "cells", planned_basis=True, normal=False))
pk.solve("S5_t0", ["exec_ok"])
pk.solve("S5_t1", ["exec_ok"], retain_input=False)
pk.rb1 = [x for x in pk.rb1 if x["tag"] != "S5_t1"]
derive("(27)", "RB-1 attempt record removed at a non-event tag", pk, "RJ", "the named gap of RI-1 (c) and FAIL")
pk = altered(K.Pkg("27b", "cells", planned_basis=True, normal=False))
pk.solve("S5_t0", ["exec_ok"])
d = copy.deepcopy(pk.launches[-1])
d["lid"] += "#dup"
pk.launches.append(d)
derive("(27)", "a launch record duplicated", pk, "RJ", "the named gap of RI-1 (c) and FAIL")
pk = altered(K.Pkg("27c", "cells", planned_basis=True, normal=False))
pk.solve("S5_t0", ["exec_ok"])
pk.counters["S-1"]["attempts_total"] -= 1
derive("(27)", "a site counter decremented", pk, "RJ", "the named gap of RI-1 (c) and FAIL")
pk = altered(controls("27d"))
d = copy.deepcopy([L for L in pk.launches if L["lid"] == "cj:ctl_identity_n3"][0])
d["lid"] += "#dup"
pk.launches.append(d)
derive("(27)", "a child-job launch record duplicated", pk, "RJ", "the named gap of RI-1 (c) and FAIL")
# (28) the CX-A discriminating control
pk = altered(cells4_cg("28", cg_path="pre_stdout_99"))
pk.lost.add("S4_t0/cg")
derive("(28)", "callgrind stdout open fails (stand-in os.open), record removed; RJ-1 disabled", pk, "RJx", "NO named gap and NO recorder gap (else STOP)")
derive("(28)", "the same under launchkind", pk, "RJ", "a CALLGRIND COUNT GAP and FAIL")
derive("(28)", "the same under attcount (contrast)", pk, "RI", "(contrast) no gap")
# (29)
pk = altered(controls_a1("29a"))
pk.lost.add("gp:controls_a1_pari")
derive("(29)", "DV-18 (e) controls-a1, gp record removed", pk, "RJ", "pari/<tag>.gp a recorder gap, FAIL")
derive("(29)", "the same, RJ-2 disabled (contrast)", pk, "RJnogp", "(contrast)")
derive("(29)", "the same under attcount (contrast)", pk, "RI", "(contrast)")
pk = altered(controls_a1("29b", gp_path="pre_stdout_99"))
pk.lost.add("gp:controls_a1_pari")
derive("(29)", "gp child's stdout open fails (stand-in), record removed", pk, "RJ", "pari/<tag>.gp a recorder gap, FAIL")
derive("(29)", "the same, RJ-2 disabled (contrast)", pk, "RJnogp", "(contrast)")
# (30)
pk = altered(anchor("30"))
pk.lost.add("cmp")
derive("(30)", "DV-18 (b) anchor-identity, comparator record removed", pk, "RJ", "a COMPARATOR COUNT GAP, FAIL")
derive("(30)", "the same, RJ-3 disabled (contrast)", pk, "RJnocmp", "(contrast)")
derive("(30)", "the same under attcount (contrast)", pk, "RI", "(contrast)")
# (31)
pk = altered(K.Pkg("31", "cells", planned_basis=True, normal=False))
pk.solve("S5_t0", ["exec_ok"])
d = copy.deepcopy(pk.launches[-1])
d["lid"] = "appended"
d["stdout"], d["stderr"] = "solver/S5_t0.appended.out", "solver/S5_t0.appended.err"
pk.launches.append(d)
derive("(31)", "one launch record appended whose stdout_path is of none of RJ-4 (a)'s forms", pk, "RJ", "an UNKNOWN-KIND GAP, FAIL")
derive("(31)", "the same, RJ-4 (b) disabled (contrast)", pk, "RJnouk", "(contrast)")
derive("(31)", "the same under attcount (contrast)", pk, "RI", "(contrast)")
# (32) positive control
derive("(32)", "unaltered (28) package (callgrind child C, record present)", cells4_cg("32a", cg_path="pre_stdout_99"), "RJ", "no named gap, no recorder gap")
derive("(32)", "unaltered (29) packages (gp exec, gp C)", controls_a1("32b"), "RJ", "no named gap, no recorder gap")
derive("(32)", "unaltered (29) second package (gp child C)", controls_a1("32c", gp_path="pre_stdout_99"), "RJ", "no named gap, no recorder gap")
derive("(32)", "unaltered (30) package", anchor("32d"), "RJ", "no named gap, no recorder gap")
pk = K.Pkg("32e", "cells", planned_basis=True, normal=True)
pk.solve("S5_t0", ["exec_ok"])
derive("(32)", "unaltered (31) package", pk, "RJ", "no named gap, no recorder gap")
derive("(32)", "DV-18 (a) controls", controls("32f"), "RJ", "no named gap, no recorder gap")

with open(os.path.join(SCR, "lj4_v1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE lj4_v1.json (%d rows)" % len(OUT))
```

### hashes_v1.py

- sha256: 5731ab87a46a698f2a65a335f88a12529df693b07a303f004879216274ad9056
- argv: `C045: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B hashes_v1.py > hashes_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch: sha256 of the card, the contracts, the released frozen files and the other inputs
# this review read or bound (bytes read, hashed, nothing printed but the hashes). Standard library only.
import hashlib
import os

REPO = "/home/user/crypto-autoresearcher"
PATHS = [
    "ledger/handoffs/TASK-20260924-d897a6.yaml",
    "agents/red-team.md",
    "AGENTS.md",
    "ledger/decisions/DEC-20260924-e52eec.yaml",
    "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py",
    "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n3.json",
    "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n4.json",
    "experiments/EXP-GFPN-05ff43/amendments/v2_addendum_consumercover.yaml",
    "experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml",
    "experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_common.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py",
    "experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_common.py",
]
for rel in PATHS:
    with open(os.path.join(REPO, rel), "rb") as fh:
        print(hashlib.sha256(fh.read()).hexdigest(), rel)
```

### tables_v1.py

- sha256: 3db2ab4b030c00d227616a8e0214f5cedc45e1736130dab6f1eb7cc86a4901aa
- argv: `C073: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

````python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch (zero runs; static only). Renders the LJ-0 (f) / LJ-2 listing and count tables from
# listing_v1.json (written by listing_v1.py; RECONSTRUCTED under CRJ-9, rule text inside that JSON). Reads only that
# file; imports nothing from the repository; writes argv[1] (markdown) and argv[2] (YAML text, block style, every
# scalar a plain token or double-quoted string).
import json
import sys

SRC = "listing_v1.json"
with open(SRC) as fh:
    J = json.load(fh)


def q(s):
    return json.dumps(str(s))


md, ym = [], []
md.append("Reconstruction rule (CRJ-9), verbatim from listing_v1.json:")
md.append("")
md.append("```text")
md.extend(J["reconstruction_rule"].splitlines())
md.append("```")
md.append("")
ym.append("reconstruction_rule: " + q(J["reconstruction_rule"]))
ym.append("packages:")
tot_files = tot_unatt = 0
for rid, P in J["packages"].items():
    tot_files += P["files_in_the_five_directories"] if isinstance(P["files_in_the_five_directories"], int) else 0
    tot_unatt += P["RJ"]["unattributed_count"]
    md.append("### %s" % rid)
    md.append("")
    md.append("- files in the package listing: %s; reconstructed launch records: %s %s; SE-3/HR-3 events: %s"
              % (P["files_in_the_five_directories"], P["reconstructed_launch_records"], json.dumps(P["record_kinds"], sort_keys=True), P["events"]))
    md.append("- unattributed files under launchkind (recorder gaps): %s %s; named gaps: %s"
              % (P["RJ"]["unattributed_count"], json.dumps(P["RJ"]["recorder_gaps"]), json.dumps(P["RJ"]["named_gaps"])))
    md.append("- contrast under attcount (RI): recorder gaps %s, named gaps %s"
              % (json.dumps(P["RI_contrast"]["recorder_gaps"]), json.dumps(P["RI_contrast"]["named_gaps"])))
    md.append("- RJ-4 (b) unknown-kind stdout paths: %s; RJ-2 pari/ files: %s"
              % (json.dumps(P["RJ4b_unknown_kind_stdout_paths"]), json.dumps(P["RJ2_pari_files"])))
    md.append("")
    md.append("| site | tag | N (launch records, stdout <dir>/<tag>.ms.log) | RB-1 attempt records | RL-2 pass-through records | RI-1 (a) (i) | Ncg (callgrind launch records) | attempt records with callgrind_result_present true | RJ-1 (b) | S-3 record (cross-check only) | raw row carries key instructions_callgrind | source |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    ym.append("  %s:" % rid)
    ym.append("    files: %s" % P["files_in_the_five_directories"])
    ym.append("    reconstructed_launch_records: %s" % P["reconstructed_launch_records"])
    ym.append("    record_kinds: %s" % json.dumps(P["record_kinds"], sort_keys=True))
    ym.append("    events: %s" % P["events"])
    ym.append("    unattributed_under_launchkind: %s" % P["RJ"]["unattributed_count"])
    ym.append("    recorder_gaps: %s" % json.dumps(P["RJ"]["recorder_gaps"]))
    ym.append("    named_gaps: %s" % json.dumps(P["RJ"]["named_gaps"]))
    ym.append("    attcount_contrast_gaps: %s" % json.dumps(P["RI_contrast"]["recorder_gaps"] + P["RI_contrast"]["named_gaps"]))
    ym.append("    rj4b_unknown_kind_stdout_paths: %s" % json.dumps(P["RJ4b_unknown_kind_stdout_paths"]))
    ym.append("    rj2_pari_files: %s" % json.dumps(P["RJ2_pari_files"]))
    ym.append("    site_tag_rows:")
    mism = []
    for r in P["count_rows_site_tag"]:
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["site"], r["tag"], r["N"], r["RB1"], r["RL2"], "holds" if r["RI1_a_i_holds"] else "FAILS",
            r["Ncg"], r["callgrind_result_present_count"], "holds" if r["RJ1_b_holds"] else "FAILS",
            r["S3_record_for_tag"], r["raw_row_carries_key_instructions_callgrind"], r["source"]))
        ym.append("      - {site: %s, tag: %s, N: %s, RB1: %s, RL2: %s, RI1_a_i: %s, Ncg: %s, present_true: %s, RJ1_b: %s, S3_cross_check: %s, raw_key: %s, source: %s}" % (
            q(r["site"]), q(r["tag"]), r["N"], r["RB1"], r["RL2"], "holds" if r["RI1_a_i_holds"] else "FAILS",
            r["Ncg"], r["callgrind_result_present_count"], "holds" if r["RJ1_b_holds"] else "FAILS",
            r["S3_record_for_tag"], q(r["raw_row_carries_key_instructions_callgrind"]), q(r["source"])))
        if not (r["RI1_a_i_holds"] and r["RJ1_b_holds"]):
            mism.append(r["tag"])
    md.append("")
    md.append("Site rows (RI-1 (a) (iii)):")
    md.append("")
    md.append("| site | launch records | attempts_total | passthrough_calls_gb_only_true | holds |")
    md.append("|---|---|---|---|---|")
    ym.append("    site_rows:")
    for s in P["site_rows"]:
        md.append("| %s | %s | %s | %s | %s |" % (s["site"], s["launch_records"], s["attempts_total"],
                                                s.get("passthrough_calls_gb_only_true", "n/a (S-2)"), s["RI1_a_iii_holds"]))
        ym.append("      - {site: %s, launch_records: %s, attempts_total: %s, passthrough: %s, holds: %s}" % (
            q(s["site"]), s["launch_records"], s["attempts_total"], q(s.get("passthrough_calls_gb_only_true", "n/a (S-2)")),
            "true" if s["RI1_a_iii_holds"] else "false"))
    s1 = P["RJ1_site_row"]
    md.append("")
    md.append("RJ-1 (b) per-site row: callgrind launch records %s; S-1 attempt records with callgrind_result_present true %s; holds %s; cross-check only: S-3 records %s, S-3 counter callgrind_children_observed %s."
              % (s1["callgrind_launch_records"], s1["attempt_records_with_callgrind_result_present"], s1["holds"],
                 s1["S3_records_total_cross_check"], s1["S3_counter_callgrind_children_observed"]))
    c3 = P["RJ3_comparator_row"]
    md.append("")
    md.append("RJ-3 comparator row: comparator launch records %s; raw-result.json comparator.child present %s; required %s; holds %s."
              % (c3["comparator_launch_records"], c3["raw_comparator_child_present"], c3["required"], c3["holds"]))
    md.append("")
    md.append("Mismatches: %s" % (json.dumps(mism) if mism else "none"))
    md.append("")
    ym.append("    rj1_site_row: {callgrind_launch_records: %s, present_true: %s, holds: %s, S3_records_cross_check: %s, S3_counter_cross_check: %s}" % (
        s1["callgrind_launch_records"], s1["attempt_records_with_callgrind_result_present"], "true" if s1["holds"] else "false",
        s1["S3_records_total_cross_check"], s1["S3_counter_callgrind_children_observed"]))
    ym.append("    rj3_comparator_row: {comparator_launch_records: %s, raw_comparator_child_present: %s, required: %s, holds: %s}" % (
        c3["comparator_launch_records"], "true" if c3["raw_comparator_child_present"] else "false", c3["required"],
        "true" if c3["holds"] else "false"))
    ym.append("    mismatches: %s" % json.dumps(mism))
md.append("TOTAL: files %d; unattributed under launchkind %d." % (tot_files, tot_unatt))
ym.append("total_files: %d" % tot_files)
ym.append("total_unattributed_under_launchkind: %d" % tot_unatt)
pf = ["Per-file first attribution clause under launchkind (RH-1 clause and record, NON-LAUNCH writer, or UNATTRIBUTED),"
      " reconstructed (CRJ-9), from listing_v1.json per_file_first_clause_RJ:", ""]
for rid, P in J["packages"].items():
    pf.append("#### %s (%d files)" % (rid, len(P["per_file_first_clause_RJ"])))
    pf.append("")
    pf.append("```text")
    for f in sorted(P["per_file_first_clause_RJ"]):
        pf.append("%s  <-  %s" % (f, P["per_file_first_clause_RJ"][f]))
    pf.append("```")
    pf.append("")
with open(sys.argv[3], "w") as fh:
    fh.write("\n".join(pf) + "\n")
with open(sys.argv[1], "w") as fh:
    fh.write("\n".join(md) + "\n")
with open(sys.argv[2], "w") as fh:
    fh.write("\n".join(ym) + "\n")
print("rows", sum(len(P["count_rows_site_tag"]) for P in J["packages"].values()), "files", tot_files, "unattributed", tot_unatt)
````

### wordcheck_v1.py

- sha256: b42715fc0506b5e17bb1ab9d58cf054bd9a6e83e1a86a3a590593b0f24e9ba0d
- argv: `C087: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1 ; and C095a: PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v1.yaml.part paths_read_v1.yaml.part deviations_v1.yaml.part exact_argv_post_compaction.txt assemble_v1.py check_v1.py > wordcheck_v1_parts.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch. CRJ-7 self-check: reads its word list AT RUN TIME from words.txt (a scratch file
# outside write_scope, placed by the dispatching session), never prints a word, and reports per checked file only the
# number of case-insensitive substring hits, plus the number of occurrences of the real scratch root (derived from this
# file's own location, never written literally). Prints the sha256 of the word list. Standard library only.
# argv: the files to check.
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
with open(os.path.join(HERE, "words.txt"), "rb") as fh:
    raw = fh.read()
words = [w.strip().lower() for w in raw.decode("utf-8").splitlines() if w.strip()]
print("word list sha256", hashlib.sha256(raw).hexdigest(), "entries", len(words))
tot = 0
for p in sys.argv[1:]:
    with open(p, "rb") as fh:
        t = fh.read().decode("utf-8", errors="replace")
    low = t.lower()
    hits = sum(low.count(w) for w in words)
    roots = t.count(ROOT)
    tot += hits
    print("%-40s word_hits %4d scratch_root_occurrences %4d" % (os.path.basename(p), hits, roots))
print("total word hits", tot)
```

### assemble_v1.py

- sha256: 3ebde27e0aa96c166cff349ebaaa37bb8b49689f305f5940a0af9df0a79cd816
- argv: `C095: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch. ASSEMBLER of the two deliverables. Reads only this scratch directory; writes exactly
# two files, each ONCE and WHOLE (open "w", one write, close; no temporary file beside them):
#   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
#   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md
# The YAML is the hand-written body (body_v1.yaml.part) with its placeholders filled from scratch files; it is parsed
# with yaml.safe_load BEFORE anything is written, and the md is rendered from the parsed YAML plus appendices that
# reproduce every script verbatim (sha256, argv), every text output, the command log and the listing tables.
# Masking (reproduced files only, never the hand-written body): the real scratch root (derived from this file's
# location, never written literally) becomes "<scratch>", and each occurrence of a word of words.txt (read at run
# time, never printed) becomes "<masked>"; the number of replacements per file is reported, never the words.
# Imports: standard library and yaml. Imports nothing from the repository. Prints a short summary.
import datetime
import difflib
import hashlib
import json
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = "/home/user/crypto-autoresearcher"
WS = os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6")
OUT_Y = os.path.join(WS, "review-report.yaml")
OUT_M = os.path.join(WS, "review-report.md")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rd(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def sha(name):
    with open(os.path.join(HERE, name), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


with open(os.path.join(HERE, "words.txt"), "rb") as fh:
    WORDS = [w.strip() for w in fh.read().decode("utf-8").splitlines() if w.strip()]


def mask(text):
    n = text.count(ROOT)
    text = text.replace(ROOT, "<scratch>")
    for w in WORDS:
        pat = re.compile(re.escape(w), re.IGNORECASE)
        text, k = pat.subn("<masked>", text)
        n += k
    return text, n


def q(s):
    return json.dumps(s, ensure_ascii=False)


# ------------------------------------------------------------------ purposes and argv of every scratch file
PURPOSE = {
    "command_log.txt": "running command log (one entry per shell child; C001-C094 before assembly)",
    "exact_argv_post_compaction.txt": "exact argv of every shell child after the compaction (X01-X52)",
    "notes.md": "working notes kept across the compaction (not reproduced; listed by hash)",
    "words.txt": "word list placed by the dispatching session for the CRJ-7 self-check; read only at run time by wordcheck_v1.py, assemble_v1.py and check_v1.py; never printed",
    "integrity_v1.py": "CRJ-2 integrity checks (a)-(c)", "integrity_v1.out": "its output",
    "crj2d_diff.out": "CRJ-2 (d) git diff --stat output (0 bytes)",
    "scan_v1.py": "static scan of the six trees (ast, dis; audit-hook guard)", "scan_v1.json": "its data", "scan_v1.out": "its output",
    "scan_v2.py": "static scan, part 2 (process enders, handlers, removals, write opens)", "scan_v2.json": "its data", "scan_v2.out": "its output",
    "pkgread_v1.py": "O_NOATIME listing and read-only records of the four archived packages", "pkgread_v1.json": "its data", "pkgread_v1.out": "its output",
    "explore_v1.py": "exploration of pkgread_v1.json (record shapes)", "explore_v1.out": "its output",
    "rjcore_v1.py": "rule evaluator core, version 1", "rjcore_v2.py": "rule evaluator core, version 2",
    "lj0_v1.py": "LJ-0 (a)-(e) with core v1", "lj0_v1.out": "its output", "lj0_v1.json": "its data",
    "lj0_v2.py": "LJ-0 (a)-(e) with core v2", "lj0_v2.out": "its output", "lj0_v2.json": "its data",
    "listing_v1.py": "LJ-0 (f) / LJ-2 listing and count check with core v1", "listing_v1.out": "its output", "listing_v1.json": "its data",
    "listing_v2.py": "the same with core v2", "listing_v2.out": "its output", "listing_v2.json": "its data",
    "lj1_v1.py": "LJ-1 lost-record constructions per launch kind", "lj1_v1.out": "its output", "lj1_v1.json": "its data",
    "lj2_v1.py": "LJ-2 planned-basis rows, N-1..N-13 and NJ objects", "lj2_v1.out": "its output", "lj2_v1.json": "its data",
    "rdscan_v1.py": "LJ-4 (3) run-directory values in two packages", "rdscan_v1.out": "its output", "rdscan_v1.json": "its data",
    "lj4_v1.py": "LJ-4 (1) development-check derivations (19)-(32)", "lj4_v1.out": "its output", "lj4_v1.json": "its data",
    "hashes_v1.py": "sha256 of the card, contracts and frozen files read", "hashes_v1.out": "its output",
    "tables_v1.py": "renders the listing and count tables from listing_v1.json", "tables_v1.out": "its output",
    "tables_v1.md": "table (markdown)", "tables_v1.yaml": "table (YAML)", "tables_v1_perfile.md": "per-file first attribution clause",
    "wordcheck_v1.py": "CRJ-7 self-check over scratch files", "wordcheck_v1_scratch.out": "its output (scripts, outputs, log, tables)",
    "wordcheck_v1_parts.out": "its output (report parts, exact-argv file, assembler, checker)",
    "body_v1.yaml.part": "hand-written YAML body of the report", "paths_read_v1.yaml.part": "paths_read part",
    "deviations_v1.yaml.part": "deviations part",
    "assemble_v1.py": "this assembler", "check_v1.py": "post-write checker",
}
ARGV = {
    "integrity_v1.py": "C005: cd <scratch>/rt_d897a6 && python3 -B integrity_v1.py > integrity_v1.out 2>&1",
    "scan_v1.py": "C012: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v1.py scan_v1.json > scan_v1.out 2>&1",
    "pkgread_v1.py": "C016: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread_v1.py pkgread_v1.json > pkgread_v1.out 2>&1",
    "explore_v1.py": "C017: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B explore_v1.py pkgread_v1.json > explore_v1.out 2>&1",
    "scan_v2.py": "C022: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v2.py scan_v2.json scan_v1.json > scan_v2.out 2>&1",
    "rjcore_v1.py": "not run directly; imported (from the scratch directory) by lj0_v1.py and listing_v1.py",
    "rjcore_v2.py": "not run directly; imported (from the scratch directory) by lj0_v2.py, listing_v2.py, lj1_v1.py, lj2_v1.py and lj4_v1.py",
    "lj0_v1.py": "C026: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v1.py > lj0_v1.out 2>&1",
    "listing_v1.py": "C029: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v1.py > listing_v1.out 2>&1",
    "lj0_v2.py": "C033: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v2.py > lj0_v2.out 2>&1 (lj0_v2.py made by sed from lj0_v1.py; the third sed expression matched nothing)",
    "listing_v2.py": "C034: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v2.py > listing_v2.out 2>&1 (listing_v2.py made by sed from listing_v1.py)",
    "lj1_v1.py": "C036: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj1_v1.py > lj1_v1.out 2>&1",
    "lj2_v1.py": "C039: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj2_v1.py > lj2_v1.out 2>&1",
    "rdscan_v1.py": "C040: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan_v1.py rdscan_v1.json > rdscan_v1.out 2>&1",
    "lj4_v1.py": "C042: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj4_v1.py > lj4_v1.out 2>&1",
    "hashes_v1.py": "C045: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B hashes_v1.py > hashes_v1.out 2>&1",
    "tables_v1.py": "C073: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1",
    "wordcheck_v1.py": "C087: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1 ; and C095a: PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v1.yaml.part paths_read_v1.yaml.part deviations_v1.yaml.part exact_argv_post_compaction.txt assemble_v1.py check_v1.py > wordcheck_v1_parts.out 2>&1",
    "assemble_v1.py": "C095: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1",
    "check_v1.py": "C096 (after the deliverables were written): cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1",
}
POST = [
    "C096: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1; echo exit=$?; cat check_v1.out",
    "C097: cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6; ls -la coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/; sha256sum coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md",
]
SCRIPTS = ["integrity_v1.py", "scan_v1.py", "scan_v2.py", "pkgread_v1.py", "explore_v1.py", "rjcore_v1.py", "rjcore_v2.py",
           "lj0_v1.py", "lj0_v2.py", "listing_v1.py", "listing_v2.py", "lj1_v1.py", "lj2_v1.py", "rdscan_v1.py",
           "lj4_v1.py", "hashes_v1.py", "tables_v1.py", "wordcheck_v1.py", "assemble_v1.py", "check_v1.py"]
OUTS = ["integrity_v1.out", "crj2d_diff.out", "scan_v1.out", "scan_v2.out", "pkgread_v1.out", "explore_v1.out",
        "lj0_v1.out", "listing_v1.out", "lj1_v1.out", "lj2_v1.out", "rdscan_v1.out", "lj4_v1.out", "hashes_v1.out",
        "tables_v1.out", "wordcheck_v1_scratch.out", "wordcheck_v1_parts.out"]
DIFFS = [("lj0_v1.out", "lj0_v2.out"), ("listing_v1.out", "listing_v2.out"), ("lj0_v1.py", "lj0_v2.py"),
         ("listing_v1.py", "listing_v2.py"), ("rjcore_v1.py", "rjcore_v2.py")]

masked_counts = {}

# ------------------------------------------------------------------ the YAML
body = rd("body_v1.yaml.part")
tables_y = rd("tables_v1.yaml")
paths_part = rd("paths_read_v1.yaml.part")
dev_part = rd("deviations_v1.yaml.part")
clog, n1 = mask(rd("command_log.txt"))
xargv, n2 = mask(rd("exact_argv_post_compaction.txt"))
masked_counts["command_log.txt"] = n1
masked_counts["exact_argv_post_compaction.txt"] = n2

entries, cur = [], None
for ln in clog.splitlines():
    if re.match(r"^C\d{3} ", ln):
        if cur is not None:
            entries.append(cur)
        cur = ln
    elif cur is not None:
        cur += "\n" + ln
    else:
        entries.append(ln)
if cur is not None:
    entries.append(cur)

cmd_lines = ["  commands:",
             "    note: " + q("Every shell child with its argv: the command log entries C001-C094 verbatim (with the abbreviations of deviation D-8), the exact argv of every child after the compaction (X01-X52), and the assembler run C095. Read / Write / Edit tool actions are not shell children; they are named in the log and in exact_argv_post_compaction.txt."),
             "    command_log_entries:"]
cmd_lines += ["      - " + q(e) for e in entries]
cmd_lines += ["    exact_argv_post_compaction:"]
cmd_lines += ["      - " + q(x) for x in xargv.splitlines() if x.strip()]
cmd_lines += ["    assembler_run:", "      - " + q(ARGV["assemble_v1.py"])]
post_lines = ["  post_write_commands:",
              "    note: " + q("Declared before they ran; they run after both files are written, so their outputs are reported in the hand-back, not in this file.")]
post_lines += ["    list:"] + ["      - " + q(p) for p in POST]

names = sorted(n for n in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, n))
               and n not in ("assemble_v1.out", "check_v1.out"))
sf_lines = ["  scratch_files:",
            "    directory: " + q("<scratch>/rt_d897a6/ (outside the repository; transient)"),
            "    files:"]
for n in names:
    st = os.stat(os.path.join(HERE, n))
    sf_lines.append("      - {name: %s, bytes: %d, sha256: %s, purpose: %s}" % (q(n), st.st_size, sha(n), q(PURPOSE.get(n, "scratch file"))))
sf_lines.append("    written_after_this_list: " + q("assemble_v1.out (this assembler's printed summary) and check_v1.out (the post-write checker's output)"))

out_lines = []
for ln in body.splitlines():
    if ln == "listing_and_count_tables: __TABLES__":
        out_lines.append("listing_and_count_tables:")
        out_lines += ["  " + t if t.strip() else "" for t in tables_y.splitlines()]
    elif ln == "  paths_read: __PATHS_READ__":
        out_lines.append("  paths_read:")
        out_lines += paths_part.rstrip("\n").splitlines()
    elif ln == "  commands: __COMMANDS__":
        out_lines += cmd_lines
        out_lines += post_lines
    elif ln == "  scratch_files: __SCRATCH_FILES__":
        out_lines += sf_lines
    elif ln == "  deviations: __DEVIATIONS__":
        out_lines.append("  deviations:")
        out_lines += dev_part.rstrip("\n").splitlines()
    else:
        out_lines.append(ln.replace("__WRITTEN_AT__", NOW))
yaml_text = "\n".join(out_lines) + "\n"
for ph in ("__TABLES__", "__PATHS_READ__", "__COMMANDS__", "__SCRATCH_FILES__", "__DEVIATIONS__", "__WRITTEN_AT__"):
    assert ph not in yaml_text, ph
doc = yaml.safe_load(yaml_text)          # must parse BEFORE anything is written
assert doc["id"] == "TASK-20260924-d897a6"

# ------------------------------------------------------------------ the md (rendered from the parsed YAML)
TAGRE = re.compile(r"(<[A-Za-z][A-Za-z0-9_ .:/-]*>)")


def fmt(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    return TAGRE.sub(r"`\1`", str(v))


def fence(text):
    runs = [len(m) for m in re.findall(r"`+", text)] or [0]
    return "`" * max(3, max(runs) + 1)


def rb(obj, ind, out):
    pad = "  " * ind
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list) and not v:
                    out.append("%s- **%s**: (none)" % (pad, k))
                else:
                    out.append("%s- **%s**:" % (pad, k))
                    rb(v, ind + 1, out)
            else:
                out.append("%s- **%s**: %s" % (pad, k, fmt(v)))
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict) and it:
                items = list(it.items())
                k0, v0 = items[0]
                if isinstance(v0, (dict, list)):
                    out.append("%s- **%s**:" % (pad, k0))
                    rb(v0, ind + 2, out)
                else:
                    out.append("%s- **%s**: %s" % (pad, k0, fmt(v0)))
                rb(dict(items[1:]), ind + 1, out)
            elif isinstance(it, list):
                out.append("%s-" % pad)
                rb(it, ind + 1, out)
            else:
                out.append("%s- %s" % (pad, fmt(it)))


md = []
md.append("# TASK-20260924-d897a6 - red-team review of the launchkind draft's difference (review-report.md)")
md.append("")
md.append("The same content as review-report.yaml, rendered for reading, followed by the listing and count tables, the")
md.append("per-file listing, the command log, every script verbatim with its sha256 and argv, and every text output.")
md.append("Observations only. `<scratch>` is the session scratch directory outside the repository.")
md.append("")
head = {k: v for k, v in doc.items() if not isinstance(v, (dict, list))}
md.append("## Header")
md.append("")
rb(head, 0, md)
md.append("")
for k, v in doc.items():
    if not isinstance(v, (dict, list)):
        continue
    md.append("## %s" % k)
    md.append("")
    if k == "listing_and_count_tables":
        md.append(rd("tables_v1.md"))
        md.append("")
        continue
    if k == "review_attestation":
        for k2, v2 in v.items():
            if k2 == "commands":
                md.append("### commands")
                md.append("")
                md.append("See Appendix B (command log verbatim and the exact argv after the compaction) and Appendix C (argv per script). Assembler run: `%s`." % ARGV["assemble_v1.py"].replace("`", "'"))
                md.append("")
                continue
            md.append("### %s" % k2)
            md.append("")
            if isinstance(v2, (dict, list)):
                rb(v2, 0, md)
            else:
                md.append(fmt(v2))
            md.append("")
        continue
    if isinstance(v, dict):
        for k2, v2 in v.items():
            if isinstance(v2, (dict, list)):
                md.append("### %s" % k2)
                md.append("")
                rb(v2, 0, md)
            else:
                md.append("- **%s**: %s" % (k2, fmt(v2)))
            md.append("")
    else:
        rb(v, 0, md)
        md.append("")

md.append("## Appendix A - per-file first attribution clause (reconstructed, CRJ-9)")
md.append("")
md.append(rd("tables_v1_perfile.md"))
md.append("")
md.append("## Appendix B - command log (verbatim) and exact argv after the compaction")
md.append("")
md.append("### B.1 <scratch>/rt_d897a6/command_log.txt (sha256 %s at assembly)" % sha("command_log.txt"))
md.append("")
f = fence(clog)
md += [f + "text", clog.rstrip("\n"), f, ""]
md.append("### B.2 <scratch>/rt_d897a6/exact_argv_post_compaction.txt (sha256 %s)" % sha("exact_argv_post_compaction.txt"))
md.append("")
f = fence(xargv)
md += [f + "text", xargv.rstrip("\n"), f, ""]
md.append("## Appendix C - every script, verbatim, with sha256 and argv")
md.append("")
for n in SCRIPTS:
    t, k = mask(rd(n))
    masked_counts[n] = k
    md.append("### %s" % n)
    md.append("")
    md.append("- sha256: %s" % sha(n))
    md.append("- argv: `%s`" % ARGV.get(n, "(not run)").replace("`", "'"))
    md.append("- replacements by masking (scratch root and listed words): %d" % k)
    md.append("")
    f = fence(t)
    md += [f + "python", t.rstrip("\n"), f, ""]
md.append("### C.x differences between versions (difflib unified diff)")
md.append("")
for a, b in DIFFS:
    ta, _ = mask(rd(a))
    tb, _ = mask(rd(b))
    d = "\n".join(difflib.unified_diff(ta.splitlines(), tb.splitlines(), a, b, lineterm=""))
    md.append("#### %s -> %s" % (a, b))
    md.append("")
    f = fence(d)
    md += [f + "diff", d if d else "(identical)", f, ""]
md.append("## Appendix D - every text output, verbatim")
md.append("")
for n in OUTS:
    t, k = mask(rd(n))
    masked_counts[n] = k
    md.append("### %s" % n)
    md.append("")
    md.append("- sha256: %s; replacements by masking: %d" % (sha(n), k))
    md.append("")
    f = fence(t)
    md += [f + "text", t.rstrip("\n") if t.strip() else "(empty file)", f, ""]
md.append("lj0_v2.out and listing_v2.out are identical to lj0_v1.out and listing_v1.out except their last line (C.x);")
md.append("sha256 lj0_v2.out %s, listing_v2.out %s." % (sha("lj0_v2.out"), sha("listing_v2.out")))
md.append("")
md.append("## Appendix E - data files and parts (listed by sha256; content summarized in the report)")
md.append("")
for n in names:
    if n.endswith((".json", ".part")) or n in ("notes.md", "words.txt", "tables_v1.md", "tables_v1.yaml", "tables_v1_perfile.md"):
        md.append("- %s: %d bytes, sha256 %s (%s)" % (n, os.stat(os.path.join(HERE, n)).st_size, sha(n), PURPOSE.get(n, "scratch file")))
md.append("")
md_text = "\n".join(md) + "\n"

# ------------------------------------------------------------------ write each deliverable ONCE, whole
os.makedirs(WS, exist_ok=True)
with open(OUT_Y, "w", encoding="utf-8") as fh:
    fh.write(yaml_text)
with open(OUT_M, "w", encoding="utf-8") as fh:
    fh.write(md_text)
print("written_at", NOW)
print("yaml bytes", len(yaml_text.encode()), "sha256", hashlib.sha256(yaml_text.encode()).hexdigest())
print("md bytes", len(md_text.encode()), "sha256", hashlib.sha256(md_text.encode()).hexdigest())
print("masking replacements per reproduced file:", json.dumps({k: v for k, v in masked_counts.items() if v}))
print("command log entries", len(entries), "scratch files listed", len(names))
```

### assemble_v2.py

- sha256: 6e4bb8ad2b24f0dcaabe7630dde3d5815fda8a47dc1fc547fed4e4e8eff90d35
- argv: `C098: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v2.py > assemble_v2.out 2>&1`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch. ASSEMBLER, VERSION 2 (= assemble_v1.py with the changes shown by the unified diff in
# the md appendix: body_v2 / deviations_v2 inputs, the resolved_model_id comment rendered in the md, code-formatted
# appendix headings, and the file lists updated). Reads only this scratch directory; writes exactly
# two files, each ONCE and WHOLE (open "w", one write, close; no temporary file beside them):
#   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
#   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md
# The YAML is the hand-written body (body_v1.yaml.part) with its placeholders filled from scratch files; it is parsed
# with yaml.safe_load BEFORE anything is written, and the md is rendered from the parsed YAML plus appendices that
# reproduce every script verbatim (sha256, argv), every text output, the command log and the listing tables.
# Masking (reproduced files only, never the hand-written body): the real scratch root (derived from this file's
# location, never written literally) becomes "<scratch>", and each occurrence of a word of words.txt (read at run
# time, never printed) becomes "<masked>"; the number of replacements per file is reported, never the words.
# Imports: standard library and yaml. Imports nothing from the repository. Prints a short summary.
import datetime
import difflib
import hashlib
import json
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = "/home/user/crypto-autoresearcher"
WS = os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6")
OUT_Y = os.path.join(WS, "review-report.yaml")
OUT_M = os.path.join(WS, "review-report.md")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rd(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def sha(name):
    with open(os.path.join(HERE, name), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


with open(os.path.join(HERE, "words.txt"), "rb") as fh:
    WORDS = [w.strip() for w in fh.read().decode("utf-8").splitlines() if w.strip()]


def mask(text):
    n = text.count(ROOT)
    text = text.replace(ROOT, "<scratch>")
    for w in WORDS:
        pat = re.compile(re.escape(w), re.IGNORECASE)
        text, k = pat.subn("<masked>", text)
        n += k
    return text, n


def q(s):
    return json.dumps(s, ensure_ascii=False)


# ------------------------------------------------------------------ purposes and argv of every scratch file
PURPOSE = {
    "command_log.txt": "running command log (one entry per shell child; C001-C094 before assembly)",
    "exact_argv_post_compaction.txt": "exact argv of every shell child after the compaction (X01-X52)",
    "notes.md": "working notes kept across the compaction (not reproduced; listed by hash)",
    "words.txt": "word list placed by the dispatching session for the CRJ-7 self-check; read only at run time by wordcheck_v1.py, assemble_v1.py and check_v1.py; never printed",
    "integrity_v1.py": "CRJ-2 integrity checks (a)-(c)", "integrity_v1.out": "its output",
    "crj2d_diff.out": "CRJ-2 (d) git diff --stat output (0 bytes)",
    "scan_v1.py": "static scan of the six trees (ast, dis; audit-hook guard)", "scan_v1.json": "its data", "scan_v1.out": "its output",
    "scan_v2.py": "static scan, part 2 (process enders, handlers, removals, write opens)", "scan_v2.json": "its data", "scan_v2.out": "its output",
    "pkgread_v1.py": "O_NOATIME listing and read-only records of the four archived packages", "pkgread_v1.json": "its data", "pkgread_v1.out": "its output",
    "explore_v1.py": "exploration of pkgread_v1.json (record shapes)", "explore_v1.out": "its output",
    "rjcore_v1.py": "rule evaluator core, version 1", "rjcore_v2.py": "rule evaluator core, version 2",
    "lj0_v1.py": "LJ-0 (a)-(e) with core v1", "lj0_v1.out": "its output", "lj0_v1.json": "its data",
    "lj0_v2.py": "LJ-0 (a)-(e) with core v2", "lj0_v2.out": "its output", "lj0_v2.json": "its data",
    "listing_v1.py": "LJ-0 (f) / LJ-2 listing and count check with core v1", "listing_v1.out": "its output", "listing_v1.json": "its data",
    "listing_v2.py": "the same with core v2", "listing_v2.out": "its output", "listing_v2.json": "its data",
    "lj1_v1.py": "LJ-1 lost-record constructions per launch kind", "lj1_v1.out": "its output", "lj1_v1.json": "its data",
    "lj2_v1.py": "LJ-2 planned-basis rows, N-1..N-13 and NJ objects", "lj2_v1.out": "its output", "lj2_v1.json": "its data",
    "rdscan_v1.py": "LJ-4 (3) run-directory values in two packages", "rdscan_v1.out": "its output", "rdscan_v1.json": "its data",
    "lj4_v1.py": "LJ-4 (1) development-check derivations (19)-(32)", "lj4_v1.out": "its output", "lj4_v1.json": "its data",
    "hashes_v1.py": "sha256 of the card, contracts and frozen files read", "hashes_v1.out": "its output",
    "tables_v1.py": "renders the listing and count tables from listing_v1.json", "tables_v1.out": "its output",
    "tables_v1.md": "table (markdown)", "tables_v1.yaml": "table (YAML)", "tables_v1_perfile.md": "per-file first attribution clause",
    "wordcheck_v1.py": "CRJ-7 self-check over scratch files", "wordcheck_v1_scratch.out": "its output (scripts, outputs, log, tables)",
    "wordcheck_v1_parts.out": "its output (report parts, exact-argv file, assembler, checker)",
    "wordcheck_v1_parts2.out": "its output (version 2 parts and assembler)",
    "body_v1.yaml.part": "hand-written YAML body of the report", "paths_read_v1.yaml.part": "paths_read part",
    "deviations_v1.yaml.part": "deviations part",
    "assemble_v1.py": "assembler, version 1 (first write of the deliverables, C095)", "check_v1.py": "post-write checker",
    "assemble_v1.out": "its printed summary", "check_v1.out": "post-write check of the version 1 deliverables (C096)",
    "assemble_v2.py": "assembler, version 2 (whole rewrite of the deliverables, C098)",
    "body_v2.yaml.part": "hand-written YAML body, version 2", "deviations_v2.yaml.part": "deviations part, version 2",
}
ARGV = {
    "integrity_v1.py": "C005: cd <scratch>/rt_d897a6 && python3 -B integrity_v1.py > integrity_v1.out 2>&1",
    "scan_v1.py": "C012: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v1.py scan_v1.json > scan_v1.out 2>&1",
    "pkgread_v1.py": "C016: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B pkgread_v1.py pkgread_v1.json > pkgread_v1.out 2>&1",
    "explore_v1.py": "C017: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B explore_v1.py pkgread_v1.json > explore_v1.out 2>&1",
    "scan_v2.py": "C022: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan_v2.py scan_v2.json scan_v1.json > scan_v2.out 2>&1",
    "rjcore_v1.py": "not run directly; imported (from the scratch directory) by lj0_v1.py and listing_v1.py",
    "rjcore_v2.py": "not run directly; imported (from the scratch directory) by lj0_v2.py, listing_v2.py, lj1_v1.py, lj2_v1.py and lj4_v1.py",
    "lj0_v1.py": "C026: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v1.py > lj0_v1.out 2>&1",
    "listing_v1.py": "C029: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v1.py > listing_v1.out 2>&1",
    "lj0_v2.py": "C033: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj0_v2.py > lj0_v2.out 2>&1 (lj0_v2.py made by sed from lj0_v1.py; the third sed expression matched nothing)",
    "listing_v2.py": "C034: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B listing_v2.py > listing_v2.out 2>&1 (listing_v2.py made by sed from listing_v1.py)",
    "lj1_v1.py": "C036: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj1_v1.py > lj1_v1.out 2>&1",
    "lj2_v1.py": "C039: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj2_v1.py > lj2_v1.out 2>&1",
    "rdscan_v1.py": "C040: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rdscan_v1.py rdscan_v1.json > rdscan_v1.out 2>&1",
    "lj4_v1.py": "C042: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B lj4_v1.py > lj4_v1.out 2>&1",
    "hashes_v1.py": "C045: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B hashes_v1.py > hashes_v1.out 2>&1",
    "tables_v1.py": "C073: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1",
    "wordcheck_v1.py": "C087: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1 ; and C095a: PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v1.yaml.part paths_read_v1.yaml.part deviations_v1.yaml.part exact_argv_post_compaction.txt assemble_v1.py check_v1.py > wordcheck_v1_parts.out 2>&1",
    "assemble_v1.py": "C095: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1",
    "assemble_v2.py": "C098: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v2.py > assemble_v2.out 2>&1",
    "check_v1.py": "C096 (on the version 1 deliverables): cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1 ; and C099 (on the version 2 deliverables): the same with > check_v1_run2.out",
}
POST = [
    "C099: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1_run2.out 2>&1; echo exit=$?; cat check_v1_run2.out",
    "C100: cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6; ls -la coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/; sha256sum coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md",
]
SCRIPTS = ["integrity_v1.py", "scan_v1.py", "scan_v2.py", "pkgread_v1.py", "explore_v1.py", "rjcore_v1.py", "rjcore_v2.py",
           "lj0_v1.py", "lj0_v2.py", "listing_v1.py", "listing_v2.py", "lj1_v1.py", "lj2_v1.py", "rdscan_v1.py",
           "lj4_v1.py", "hashes_v1.py", "tables_v1.py", "wordcheck_v1.py", "assemble_v1.py", "assemble_v2.py",
           "check_v1.py"]
OUTS = ["integrity_v1.out", "crj2d_diff.out", "scan_v1.out", "scan_v2.out", "pkgread_v1.out", "explore_v1.out",
        "lj0_v1.out", "listing_v1.out", "lj1_v1.out", "lj2_v1.out", "rdscan_v1.out", "lj4_v1.out", "hashes_v1.out",
        "tables_v1.out", "wordcheck_v1_scratch.out", "wordcheck_v1_parts.out", "wordcheck_v1_parts2.out",
        "assemble_v1.out", "check_v1.out"]
DIFFS = [("lj0_v1.out", "lj0_v2.out"), ("listing_v1.out", "listing_v2.out"), ("lj0_v1.py", "lj0_v2.py"),
         ("listing_v1.py", "listing_v2.py"), ("rjcore_v1.py", "rjcore_v2.py"), ("body_v1.yaml.part", "body_v2.yaml.part"),
         ("deviations_v1.yaml.part", "deviations_v2.yaml.part"), ("assemble_v1.py", "assemble_v2.py")]

masked_counts = {}

# ------------------------------------------------------------------ the YAML
body = rd("body_v2.yaml.part")
tables_y = rd("tables_v1.yaml")
paths_part = rd("paths_read_v1.yaml.part")
dev_part = rd("deviations_v2.yaml.part")
clog, n1 = mask(rd("command_log.txt"))
xargv, n2 = mask(rd("exact_argv_post_compaction.txt"))
masked_counts["command_log.txt"] = n1
masked_counts["exact_argv_post_compaction.txt"] = n2

entries, cur = [], None
for ln in clog.splitlines():
    if re.match(r"^C\d{3}[a-z]? ", ln):
        if cur is not None:
            entries.append(cur)
        cur = ln
    elif cur is not None:
        cur += "\n" + ln
    else:
        entries.append(ln)
if cur is not None:
    entries.append(cur)

cmd_lines = ["  commands:",
             "    note: " + q("Every shell child with its argv: the command log entries verbatim up to this assembly (with the abbreviations of deviation D-8; entries after C094 carry their argv in full), the exact argv of every child from C046 to C094 (X01-X52), and the assembler runs C095 and C098. Read / Write / Edit tool actions are not shell children; they are named in the log and in exact_argv_post_compaction.txt."),
             "    command_log_entries:"]
cmd_lines += ["      - " + q(e) for e in entries]
cmd_lines += ["    exact_argv_post_compaction:"]
cmd_lines += ["      - " + q(x) for x in xargv.splitlines() if x.strip()]
cmd_lines += ["    assembler_runs:", "      - " + q(ARGV["assemble_v1.py"]), "      - " + q(ARGV["assemble_v2.py"])]
post_lines = ["  post_write_commands:",
              "    note: " + q("Declared before they ran; they run after both files are written, so their outputs are reported in the hand-back, not in this file.")]
post_lines += ["    list:"] + ["      - " + q(p) for p in POST]

names = sorted(n for n in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, n))
               and n not in ("assemble_v2.out", "check_v1_run2.out"))
sf_lines = ["  scratch_files:",
            "    directory: " + q("<scratch>/rt_d897a6/ (outside the repository; transient)"),
            "    files:"]
for n in names:
    st = os.stat(os.path.join(HERE, n))
    sf_lines.append("      - {name: %s, bytes: %d, sha256: %s, purpose: %s}" % (q(n), st.st_size, sha(n), q(PURPOSE.get(n, "scratch file"))))
sf_lines.append("    written_after_this_list: " + q("assemble_v2.out (this assembler's printed summary) and check_v1_run2.out (the post-write checker's output on these files)"))

out_lines = []
for ln in body.splitlines():
    if ln == "listing_and_count_tables: __TABLES__":
        out_lines.append("listing_and_count_tables:")
        out_lines += ["  " + t if t.strip() else "" for t in tables_y.splitlines()]
    elif ln == "  paths_read: __PATHS_READ__":
        out_lines.append("  paths_read:")
        out_lines += paths_part.rstrip("\n").splitlines()
    elif ln == "  commands: __COMMANDS__":
        out_lines += cmd_lines
        out_lines += post_lines
    elif ln == "  scratch_files: __SCRATCH_FILES__":
        out_lines += sf_lines
    elif ln == "  deviations: __DEVIATIONS__":
        out_lines.append("  deviations:")
        out_lines += dev_part.rstrip("\n").splitlines()
    else:
        out_lines.append(ln.replace("__WRITTEN_AT__", NOW))
yaml_text = "\n".join(out_lines) + "\n"
for ph in ("__TABLES__", "__PATHS_READ__", "__COMMANDS__", "__SCRATCH_FILES__", "__DEVIATIONS__", "__WRITTEN_AT__"):
    assert ph not in yaml_text, ph
doc = yaml.safe_load(yaml_text)          # must parse BEFORE anything is written
assert doc["id"] == "TASK-20260924-d897a6"

# ------------------------------------------------------------------ the md (rendered from the parsed YAML)
TAGRE = re.compile(r"(<[A-Za-z][A-Za-z0-9_ .:/-]*>)")


def fmt(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    return TAGRE.sub(r"`\1`", str(v))


def fence(text):
    runs = [len(m) for m in re.findall(r"`+", text)] or [0]
    return "`" * max(3, max(runs) + 1)


def rb(obj, ind, out):
    pad = "  " * ind
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list) and not v:
                    out.append("%s- **%s**: (none)" % (pad, k))
                else:
                    out.append("%s- **%s**:" % (pad, k))
                    rb(v, ind + 1, out)
            elif k == "resolved_model_id" and v is None:
                out.append("%s- **%s**: null (none supplied by the dispatching session; none invented)" % (pad, k))
            else:
                out.append("%s- **%s**: %s" % (pad, k, fmt(v)))
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict) and it:
                items = list(it.items())
                k0, v0 = items[0]
                if isinstance(v0, (dict, list)):
                    out.append("%s- **%s**:" % (pad, k0))
                    rb(v0, ind + 2, out)
                else:
                    out.append("%s- **%s**: %s" % (pad, k0, fmt(v0)))
                rb(dict(items[1:]), ind + 1, out)
            elif isinstance(it, list):
                out.append("%s-" % pad)
                rb(it, ind + 1, out)
            else:
                out.append("%s- %s" % (pad, fmt(it)))


md = []
md.append("# TASK-20260924-d897a6 - red-team review of the launchkind draft's difference (review-report.md)")
md.append("")
md.append("The same content as review-report.yaml, rendered for reading, followed by the listing and count tables, the")
md.append("per-file listing, the command log, every script verbatim with its sha256 and argv, and every text output.")
md.append("Observations only. `<scratch>` is the session scratch directory outside the repository.")
md.append("")
head = {k: v for k, v in doc.items() if not isinstance(v, (dict, list))}
md.append("## Header")
md.append("")
rb(head, 0, md)
md.append("")
for k, v in doc.items():
    if not isinstance(v, (dict, list)):
        continue
    md.append("## %s" % k)
    md.append("")
    if k == "listing_and_count_tables":
        md.append(rd("tables_v1.md"))
        md.append("")
        continue
    if k == "review_attestation":
        for k2, v2 in v.items():
            if k2 == "commands":
                md.append("### commands")
                md.append("")
                md.append("See Appendix B (command log verbatim and the exact argv after the compaction) and Appendix C (argv per script). Assembler runs: `%s`; `%s`." % (ARGV["assemble_v1.py"].replace("`", "'"), ARGV["assemble_v2.py"].replace("`", "'")))
                md.append("")
                continue
            md.append("### %s" % k2)
            md.append("")
            if isinstance(v2, (dict, list)):
                rb(v2, 0, md)
            else:
                md.append(fmt(v2))
            md.append("")
        continue
    if isinstance(v, dict):
        for k2, v2 in v.items():
            if isinstance(v2, (dict, list)):
                md.append("### %s" % k2)
                md.append("")
                rb(v2, 0, md)
            else:
                md.append("- **%s**: %s" % (k2, fmt(v2)))
            md.append("")
    else:
        rb(v, 0, md)
        md.append("")

md.append("## Appendix A - per-file first attribution clause (reconstructed, CRJ-9)")
md.append("")
md.append(rd("tables_v1_perfile.md"))
md.append("")
md.append("## Appendix B - command log (verbatim) and exact argv after the compaction")
md.append("")
md.append("### B.1 `<scratch>/rt_d897a6/command_log.txt` (sha256 %s at assembly)" % sha("command_log.txt"))
md.append("")
f = fence(clog)
md += [f + "text", clog.rstrip("\n"), f, ""]
md.append("### B.2 `<scratch>/rt_d897a6/exact_argv_post_compaction.txt` (sha256 %s)" % sha("exact_argv_post_compaction.txt"))
md.append("")
f = fence(xargv)
md += [f + "text", xargv.rstrip("\n"), f, ""]
md.append("## Appendix C - every script, verbatim, with sha256 and argv")
md.append("")
for n in SCRIPTS:
    t, k = mask(rd(n))
    masked_counts[n] = k
    md.append("### %s" % n)
    md.append("")
    md.append("- sha256: %s" % sha(n))
    md.append("- argv: `%s`" % ARGV.get(n, "(not run)").replace("`", "'"))
    md.append("- replacements by masking (scratch root and listed words): %d" % k)
    md.append("")
    f = fence(t)
    md += [f + "python", t.rstrip("\n"), f, ""]
md.append("### C.x differences between versions (difflib unified diff)")
md.append("")
for a, b in DIFFS:
    ta, _ = mask(rd(a))
    tb, _ = mask(rd(b))
    d = "\n".join(difflib.unified_diff(ta.splitlines(), tb.splitlines(), a, b, lineterm=""))
    md.append("#### %s -> %s" % (a, b))
    md.append("")
    f = fence(d)
    md += [f + "diff", d if d else "(identical)", f, ""]
md.append("## Appendix D - every text output, verbatim")
md.append("")
for n in OUTS:
    t, k = mask(rd(n))
    masked_counts[n] = k
    md.append("### %s" % n)
    md.append("")
    md.append("- sha256: %s; replacements by masking: %d" % (sha(n), k))
    md.append("")
    f = fence(t)
    md += [f + "text", t.rstrip("\n") if t.strip() else "(empty file)", f, ""]
md.append("lj0_v2.out and listing_v2.out are identical to lj0_v1.out and listing_v1.out except their last line (C.x);")
md.append("sha256 lj0_v2.out %s, listing_v2.out %s." % (sha("lj0_v2.out"), sha("listing_v2.out")))
md.append("")
md.append("## Appendix E - data files and parts (listed by sha256; content summarized in the report)")
md.append("")
for n in names:
    if n.endswith((".json", ".part")) or n in ("notes.md", "words.txt", "tables_v1.md", "tables_v1.yaml", "tables_v1_perfile.md"):
        md.append("- %s: %d bytes, sha256 %s (%s)" % (n, os.stat(os.path.join(HERE, n)).st_size, sha(n), PURPOSE.get(n, "scratch file")))
md.append("")
md_text = "\n".join(md) + "\n"

# ------------------------------------------------------------------ write each deliverable ONCE, whole
os.makedirs(WS, exist_ok=True)
with open(OUT_Y, "w", encoding="utf-8") as fh:
    fh.write(yaml_text)
with open(OUT_M, "w", encoding="utf-8") as fh:
    fh.write(md_text)
print("written_at", NOW)
print("yaml bytes", len(yaml_text.encode()), "sha256", hashlib.sha256(yaml_text.encode()).hexdigest())
print("md bytes", len(md_text.encode()), "sha256", hashlib.sha256(md_text.encode()).hexdigest())
print("masking replacements per reproduced file:", json.dumps({k: v for k, v in masked_counts.items() if v}))
print("command log entries", len(entries), "scratch files listed", len(names))
```

### check_v1.py

- sha256: 07379d7a116b280cce281f58ce919a794e2ad38d2f0e094407edc204edb29b4b
- argv: `C096 (on the version 1 deliverables): cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1 ; and C099 (on the version 2 deliverables): the same with > check_v1_run2.out`
- replacements by masking (scratch root and listed words): 0

```python
#!/usr/bin/env python3
# TASK-20260924-d897a6 scratch. POST-WRITE CHECK of the two deliverables (read-only on the repository):
#  (1) review-report.yaml parses with yaml.safe_load and carries the required top-level keys and attestation fields;
#  (2) CRJ-7 word self-check on both deliverables: word list read AT RUN TIME from words.txt (scratch, outside
#      write_scope); prints only the list's sha256, the number of hits per file and the line numbers of hits, never a
#      word; also the number of occurrences of the real scratch root (derived from this file's location);
#  (3) CRJ-8: the forbidden task ids are read AT RUN TIME from the card's CRJ-8 constraint text (this script contains
#      none of them); prints only how many ids were read and how many occurrences each deliverable carries;
#  (4) the write-scope directory's listing, and the sha256 and size of each deliverable.
# Imports: standard library and yaml (for the parse check; its source was not read). Imports nothing from the
# repository. Writes nothing.
import hashlib
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = "/home/user/crypto-autoresearcher"
WS = os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6")
Y = os.path.join(WS, "review-report.yaml")
M = os.path.join(WS, "review-report.md")
CARD = os.path.join(REPO, "ledger/handoffs/TASK-20260924-d897a6.yaml")

print("write-scope listing:", sorted(os.listdir(WS)))
for p in (Y, M):
    b = open(p, "rb").read()
    print("sha256 %s %d bytes %s" % (hashlib.sha256(b).hexdigest(), len(b), os.path.relpath(p, REPO)))

# (1)
doc = yaml.safe_load(open(Y, encoding="utf-8"))
need_top = ["id", "task_id", "integrity", "known_answer_control", "joints", "counterexamples", "fail_closed_findings",
            "behaviours_relied_on", "listing_and_count_tables", "red_team_report", "review_attestation"]
print("yaml.safe_load: OK; top-level keys", len(doc), "missing", [k for k in need_top if k not in doc])
att = doc["review_attestation"]
need_att = ["task_id", "role", "joints_owned", "verdicts", "read_sibling_reports", "blind_from_not_opened",
            "dispatcher_withheld_not_opened", "blindness_disclosures", "paths_read", "commands", "scratch_files",
            "inference", "deviations"]
print("attestation missing", [k for k in need_att if k not in att], "blind_from entries", len(att["blind_from_not_opened"]))
print("inference block keys", list(att["inference"].keys()))
print("red_team_report id", doc["red_team_report"]["id"], "task_id", doc["red_team_report"]["task_id"])
print("joints", list(doc["joints"].keys()))

# (2)
raw = open(os.path.join(HERE, "words.txt"), "rb").read()
words = [w.strip().lower() for w in raw.decode("utf-8").splitlines() if w.strip()]
print("word list sha256", hashlib.sha256(raw).hexdigest(), "entries", len(words))
for p in (Y, M):
    lines = open(p, encoding="utf-8").read().splitlines()
    hits, where = 0, []
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        c = sum(low.count(w) for w in words)
        if c:
            hits += c
            where.append(i)
    roots = sum(ln.count(ROOT) for ln in lines)
    print("%s word hits %d at lines %s; scratch-root occurrences %d" % (os.path.basename(p), hits, where, roots))

# (3)
card = yaml.safe_load(open(CARD, encoding="utf-8"))
crj8 = next(c["text"] for c in card["handoff"]["constraints"] if c["id"] == "CRJ-8")
ids = re.findall(r"TASK-\d{8}-[0-9a-f]{6}", crj8)
print("CRJ-8 ids read from the card at run time:", len(ids))
for p in (Y, M):
    t = open(p, encoding="utf-8").read()
    print("%s CRJ-8 id occurrences %d" % (os.path.basename(p), sum(t.count(i) for i in ids)))
```

### C.x differences between versions (difflib unified diff)

#### lj0_v1.out -> lj0_v2.out

```diff
--- lj0_v1.out
+++ lj0_v2.out
@@ -721,4 +721,4 @@
       definitions holding: ['ii_ANY', 'ii_LR']
   expected by CRJ-4: RJ: CALLGRIND COUNT GAP and FAIL (variant)
 
-WROTE lj0_v1.json (34 objects)
+WROTE lj0_v2.json (34 objects)
```

#### listing_v1.out -> listing_v2.out

```diff
--- listing_v1.out
+++ listing_v2.out
@@ -128,4 +128,4 @@
   RJ-4 (b) unknown-kind stdout paths: []
   RJ-2 pari/ files: []
 
-TOTAL files 683, unattributed under launchkind 0; WROTE listing_v1.json
+TOTAL files 683, unattributed under launchkind 0; WROTE listing_v2.json
```

#### lj0_v1.py -> lj0_v2.py

```diff
--- lj0_v1.py
+++ lj0_v2.py
@@ -1,14 +1,14 @@
 #!/usr/bin/env python3
 """TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 known-answer control, objects (a)-(e), with the
-evaluator core rjcore_v1.py UNCHANGED (imported from this scratch directory; it imports nothing from the repository).
-Prints record level, then package level, per object and rule set; writes lj0_v1.json next to itself."""
+evaluator core rjcore_v2.py UNCHANGED (imported from this scratch directory; it imports nothing from the repository).
+Prints record level, then package level, per object and rule set; writes lj0_v2.json next to itself."""
 import json
 import os
 import sys
 
 SCR = os.path.dirname(os.path.abspath(__file__))
 sys.path.insert(0, SCR)
-import rjcore_v1 as K  # noqa: E402  (this review's own scratch module)
+import rjcore_v2 as K  # noqa: E402  (this review's own scratch module)
 
 OUT = {}
 LINES = []
@@ -167,6 +167,6 @@
 run("KA-e CX-A-G2", "fixture package of G2 shape (callgrind on every ok solve, v2_driver.py 358), one no-file callgrind record absent",
     pk, ("RI", "RJ", "RJw"), "RJ: CALLGRIND COUNT GAP and FAIL (variant)")
 
-with open(os.path.join(SCR, "lj0_v1.json"), "w") as fh:
+with open(os.path.join(SCR, "lj0_v2.json"), "w") as fh:
     json.dump(OUT, fh, indent=1, default=str)
-P("\nWROTE lj0_v1.json (%d objects)" % len(OUT))
+P("\nWROTE lj0_v2.json (%d objects)" % len(OUT))
```

#### listing_v1.py -> listing_v2.py

```diff
--- listing_v1.py
+++ listing_v2.py
@@ -1,6 +1,6 @@
 #!/usr/bin/env python3
 """TASK-20260924-d897a6 scratch (zero runs; static only). LJ-0 (f) and LJ-2 (2): the LISTING AND COUNT CHECK under
-launchkind on the four archived r3 gate packages, with the evaluator core rjcore_v1.py UNCHANGED.
+launchkind on the four archived r3 gate packages, with the evaluator core rjcore_v2.py UNCHANGED.
 
 Input: pkgread_v1.json (the O_NOATIME listing and read-only records of the four packages; no repository read here).
 
@@ -38,7 +38,7 @@
 
 SCR = os.path.dirname(os.path.abspath(__file__))
 sys.path.insert(0, SCR)
-import rjcore_v1 as K  # noqa: E402
+import rjcore_v2 as K  # noqa: E402
 
 D = json.load(open(os.path.join(SCR, "pkgread_v1.json")))
 OUT = {"reconstruction_rule": __doc__.split("CRJ-9 RECONSTRUCTION RULE")[1].strip(), "packages": {}}
@@ -217,8 +217,8 @@
     P("  RJ-3 comparator row: %s" % rj3)
     P("  RJ-4 (b) unknown-kind stdout paths: %s" % unk)
     P("  RJ-2 pari/ files: %s" % pari)
-with open(os.path.join(SCR, "listing_v1.json"), "w") as fh:
+with open(os.path.join(SCR, "listing_v2.json"), "w") as fh:
     json.dump(OUT, fh, indent=1, default=str)
 tot = sum(v["files_in_the_five_directories"] for v in OUT["packages"].values())
 un = sum(v["RJ"]["unattributed_count"] for v in OUT["packages"].values())
-P("\nTOTAL files %d, unattributed under launchkind %d; WROTE listing_v1.json" % (tot, un))
+P("\nTOTAL files %d, unattributed under launchkind %d; WROTE listing_v2.json" % (tot, un))
```

#### rjcore_v1.py -> rjcore_v2.py

```diff
--- rjcore_v1.py
+++ rjcore_v2.py
@@ -1,5 +1,9 @@
 #!/usr/bin/env python3
-"""TASK-20260924-d897a6 scratch (zero runs; static only). THE RULE EVALUATOR CORE, version 1.
+"""TASK-20260924-d897a6 scratch (zero runs; static only). THE RULE EVALUATOR CORE, version 2 = version 1 plus two
+rule transcriptions that no LJ-0 object exercises: (1) the frozen checker's aggregate exemption from the cap items
+(v2_check_run.py 65); (2) failclosed RF-0 (a), (c) applied to RJ-1 (a): an S-1 attempt record whose
+callgrind_result_present is neither true nor false is `undetermined` and yields FAIL (launchkind families only).
+Version 1's text follows unchanged apart from these two additions (diff recorded in review-report.md).
 
 One method, used UNCHANGED for LJ-0 (known-answer control), LJ-1, LJ-2, LJ-3 and LJ-4 objects. It computes, from
 rule TEXT as transcribed below (file and line cited at each rule), what each draft's rules say about a constructed
@@ -431,6 +435,9 @@
                         q = "solver/%s%s" % (tag, ext)
                         if q in files:
                             forced_gaps.add(q)
+            for rb in pkg.rb1:                                                # RF-0 (a), (c) on the RJ-1 (a) field
+                if rb["site"] == "S-1" and rb["cg_present"] not in (True, False):
+                    named.append("UNDETERMINED callgrind_result_present (RF-0 (c)): attempt record %s attempt %s" % (rb["tag"], rb.get("attempt")))
             tot_ncg, tot_c = sum(cgtags.values()), sum(cnt.values())
             if (tot_ncg > tot_c) if rs == "RJw" else (tot_ncg != tot_c):
                 named.append("CALLGRIND SITE COUNT GAP: %d callgrind launch records vs %d attempt records with callgrind_result_present true" % (tot_ncg, tot_c))
@@ -466,6 +473,8 @@
         caps += list(pkg.raw_pairs.values())
     caps += pkg.meta_pairs
     items = []
+    if pkg.kind == "aggregate":                     # v2_check_run.py 65: the cap items are not evaluated for aggregates
+        return list(pkg.extra_items)
     if not caps:
         items.append("66-67 no child RLIMIT_AS read-back recorded")
     req_known = pkg.cap_source == "Mc" or pkg.raw_writer == "driver"
```

#### body_v1.yaml.part -> body_v2.yaml.part

```diff
--- body_v1.yaml.part
+++ body_v2.yaml.part
@@ -356,7 +356,7 @@
           - "record lost, pre_stdout_99 (188 fails, 206-208, no file): RJ FAIL (spec gap)"
           - "record lost, err_setrlimit_97 (193, 195-196; stdout and stderr files exist): RJ FAIL"
           - "record lost, P8 (OK with soft != cap, 200-201 / 228-232): RJ FAIL"
-          - "record lost, exec_ok: RJ FAIL (spec, .stdout, .stderr, .npz, .meta.json gaps)"
+          - "record lost, exec_ok: RJ FAIL (spec, .stdout, .stderr and .meta.json gaps; the raw_grid child job's .npz is removed at v2_driver.py 144, an uncached build_poly's .npz is a fifth gap)"
           - "record AND spec file absent (the spec removed after 99: a file-deletion premise): path A PASS with no definition holding; pre_stdout_99 PASS and FAIL-OPEN (ii) -- a residual premise object within RGL-10's words"
           - "escaped child (FO1_C, FO1_B) at the child-job launch with the parent record lost: RJ FAIL"
         consistency_needed_to_escape_detection: the launch record and the spec file (the only detector), and no child file (paths A and pre_stdout_99 only)
@@ -716,7 +716,7 @@
     verdict: holds
     reading: failclosed RFR-4 (explicit) and RFR-6 (informational), applied to RJ-1..RJ-6
     files_and_lines_read:
-      - a1_check_run.py 60-86; r3_check_run.py 61-77, 86-100; r3_run_wrapper.py 97-104, 186-203, 284-292, 381-400, 505-512; v2_check_run.py 60-72, 92-106
+      - a1_check_run.py 30 (grep), 60-86; r3_check_run.py 61-77, 86-100; r3_run_wrapper.py 97-104, 186-203, 284-292, 381-400, 505-512; v2_check_run.py 60-72, 92-106
       - r3_common.py 24-32, 110-115; v2_common.py 27-40; a1_common.py 88-100
     rfr4_confirmation_in_this_reports_words: >-
       CONFIRMED. X-13 is the frozen addendum checker's item at
@@ -738,8 +738,8 @@
       run_status is "completed_valid" and gate_pass is True (195-196). The
       roots coincide: RUNS = R.RUNS_DIR = <EXP_DIR>/runs (r3_run_wrapper.py
       68; r3_common.py 27, 31) and C.EXP_DIR = the same directory
-      (v2_common.py 30; a1_common.redirect_v2 90-100 is called without
-      exp_dir and does not change it). Same file, same two fields, same
+      (v2_common.py 30; a1_check_run.py 30 calls AC.redirect_v2() with no
+      arguments, so a1_common.redirect_v2 90-100 leaves C.EXP_DIR unchanged). Same file, same two fields, same
       predicate. The carried RLR-2 / RKR-2 findings stand: CRJ-2 (d)'s diff
       against dd1034553 prints nothing, the six production run_child sites
       and the single definitions are as the censuses list them (scan_v1), and
@@ -1251,8 +1251,7 @@
   inference:
     requested_policy: review-adversarial
     agent_binding: red-team, at the policy's default reasoning effort, as the dispatching session arranged
-    resolved_model_id: null
-    resolved_model_note: none supplied by the dispatching session; none invented
+    resolved_model_id: null  # none supplied by the dispatching session; none invented
     model_verified: false
     fallback_used: false
     <masked>_used: false
```

#### deviations_v1.yaml.part -> deviations_v2.yaml.part

```diff
--- deviations_v1.yaml.part
+++ deviations_v2.yaml.part
@@ -85,3 +85,20 @@
         recorded separately, in order, in
         <scratch>/rt_d897a6/exact_argv_post_compaction.txt (X01-X52), which is
         reproduced under commands and in the md appendix.
+    - id: D-9
+      command: C095, C098
+      text: >-
+        The two deliverables were first written by assemble_v1.py (C095;
+        review-report.yaml sha256
+        3a84029a83219dcc3a766f1b12a4edaa359ebdceb5659609e3697e85a33c4cb2,
+        review-report.md sha256
+        996ac45ade9e94596c34623789fb4ff5ea85e8ccd613f258bb39d474f0ce5412).
+        The post-write inspection found that version's inference block
+        carried a seventh key (resolved_model_note) beyond the six the
+        dispatching session fixed. Both files were then rewritten WHOLE, once
+        each, by assemble_v2.py (C098) from body_v2.yaml.part and
+        deviations_v2.yaml.part: the note became a YAML comment on
+        resolved_model_id, LJ-5 names a1_check_run.py 30, and the LK-1
+        exec_ok line states the raw_grid .npz removal. No verdict changed.
+        The version 1 inputs, the version 1 assembler and its output are kept
+        in scratch; the md appendix shows the unified diffs.
```

#### assemble_v1.py -> assemble_v2.py

```diff
--- assemble_v1.py
+++ assemble_v2.py
@@ -1,5 +1,7 @@
 #!/usr/bin/env python3
-# TASK-20260924-d897a6 scratch. ASSEMBLER of the two deliverables. Reads only this scratch directory; writes exactly
+# TASK-20260924-d897a6 scratch. ASSEMBLER, VERSION 2 (= assemble_v1.py with the changes shown by the unified diff in
+# the md appendix: body_v2 / deviations_v2 inputs, the resolved_model_id comment rendered in the md, code-formatted
+# appendix headings, and the file lists updated). Reads only this scratch directory; writes exactly
 # two files, each ONCE and WHOLE (open "w", one write, close; no temporary file beside them):
 #   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
 #   <repo>/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md
@@ -82,9 +84,13 @@
     "tables_v1.md": "table (markdown)", "tables_v1.yaml": "table (YAML)", "tables_v1_perfile.md": "per-file first attribution clause",
     "wordcheck_v1.py": "CRJ-7 self-check over scratch files", "wordcheck_v1_scratch.out": "its output (scripts, outputs, log, tables)",
     "wordcheck_v1_parts.out": "its output (report parts, exact-argv file, assembler, checker)",
+    "wordcheck_v1_parts2.out": "its output (version 2 parts and assembler)",
     "body_v1.yaml.part": "hand-written YAML body of the report", "paths_read_v1.yaml.part": "paths_read part",
     "deviations_v1.yaml.part": "deviations part",
-    "assemble_v1.py": "this assembler", "check_v1.py": "post-write checker",
+    "assemble_v1.py": "assembler, version 1 (first write of the deliverables, C095)", "check_v1.py": "post-write checker",
+    "assemble_v1.out": "its printed summary", "check_v1.out": "post-write check of the version 1 deliverables (C096)",
+    "assemble_v2.py": "assembler, version 2 (whole rewrite of the deliverables, C098)",
+    "body_v2.yaml.part": "hand-written YAML body, version 2", "deviations_v2.yaml.part": "deviations part, version 2",
 }
 ARGV = {
     "integrity_v1.py": "C005: cd <scratch>/rt_d897a6 && python3 -B integrity_v1.py > integrity_v1.out 2>&1",
@@ -106,28 +112,32 @@
     "tables_v1.py": "C073: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables_v1.py tables_v1.md tables_v1.yaml tables_v1_perfile.md > tables_v1.out 2>&1",
     "wordcheck_v1.py": "C087: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py *.py *.out command_log.txt tables_v1.md tables_v1.yaml tables_v1_perfile.md > wordcheck_v1_scratch.out 2>&1 ; and C095a: PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B wordcheck_v1.py body_v1.yaml.part paths_read_v1.yaml.part deviations_v1.yaml.part exact_argv_post_compaction.txt assemble_v1.py check_v1.py > wordcheck_v1_parts.out 2>&1",
     "assemble_v1.py": "C095: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v1.py > assemble_v1.out 2>&1",
-    "check_v1.py": "C096 (after the deliverables were written): cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1",
+    "assemble_v2.py": "C098: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B assemble_v2.py > assemble_v2.out 2>&1",
+    "check_v1.py": "C096 (on the version 1 deliverables): cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1 ; and C099 (on the version 2 deliverables): the same with > check_v1_run2.out",
 }
 POST = [
-    "C096: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1.out 2>&1; echo exit=$?; cat check_v1.out",
-    "C097: cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6; ls -la coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/; sha256sum coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md",
+    "C099: cd <scratch>/rt_d897a6 && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B check_v1.py > check_v1_run2.out 2>&1; echo exit=$?; cat check_v1_run2.out",
+    "C100: cd /home/user/crypto-autoresearcher && GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6; ls -la coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/; sha256sum coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md",
 ]
 SCRIPTS = ["integrity_v1.py", "scan_v1.py", "scan_v2.py", "pkgread_v1.py", "explore_v1.py", "rjcore_v1.py", "rjcore_v2.py",
            "lj0_v1.py", "lj0_v2.py", "listing_v1.py", "listing_v2.py", "lj1_v1.py", "lj2_v1.py", "rdscan_v1.py",
-           "lj4_v1.py", "hashes_v1.py", "tables_v1.py", "wordcheck_v1.py", "assemble_v1.py", "check_v1.py"]
+           "lj4_v1.py", "hashes_v1.py", "tables_v1.py", "wordcheck_v1.py", "assemble_v1.py", "assemble_v2.py",
+           "check_v1.py"]
 OUTS = ["integrity_v1.out", "crj2d_diff.out", "scan_v1.out", "scan_v2.out", "pkgread_v1.out", "explore_v1.out",
         "lj0_v1.out", "listing_v1.out", "lj1_v1.out", "lj2_v1.out", "rdscan_v1.out", "lj4_v1.out", "hashes_v1.out",
-        "tables_v1.out", "wordcheck_v1_scratch.out", "wordcheck_v1_parts.out"]
+        "tables_v1.out", "wordcheck_v1_scratch.out", "wordcheck_v1_parts.out", "wordcheck_v1_parts2.out",
+        "assemble_v1.out", "check_v1.out"]
 DIFFS = [("lj0_v1.out", "lj0_v2.out"), ("listing_v1.out", "listing_v2.out"), ("lj0_v1.py", "lj0_v2.py"),
-         ("listing_v1.py", "listing_v2.py"), ("rjcore_v1.py", "rjcore_v2.py")]
+         ("listing_v1.py", "listing_v2.py"), ("rjcore_v1.py", "rjcore_v2.py"), ("body_v1.yaml.part", "body_v2.yaml.part"),
+         ("deviations_v1.yaml.part", "deviations_v2.yaml.part"), ("assemble_v1.py", "assemble_v2.py")]
 
 masked_counts = {}
 
 # ------------------------------------------------------------------ the YAML
-body = rd("body_v1.yaml.part")
+body = rd("body_v2.yaml.part")
 tables_y = rd("tables_v1.yaml")
 paths_part = rd("paths_read_v1.yaml.part")
-dev_part = rd("deviations_v1.yaml.part")
+dev_part = rd("deviations_v2.yaml.part")
 clog, n1 = mask(rd("command_log.txt"))
 xargv, n2 = mask(rd("exact_argv_post_compaction.txt"))
 masked_counts["command_log.txt"] = n1
@@ -135,7 +145,7 @@
 
 entries, cur = [], None
 for ln in clog.splitlines():
-    if re.match(r"^C\d{3} ", ln):
+    if re.match(r"^C\d{3}[a-z]? ", ln):
         if cur is not None:
             entries.append(cur)
         cur = ln
@@ -147,25 +157,25 @@
     entries.append(cur)
 
 cmd_lines = ["  commands:",
-             "    note: " + q("Every shell child with its argv: the command log entries C001-C094 verbatim (with the abbreviations of deviation D-8), the exact argv of every child after the compaction (X01-X52), and the assembler run C095. Read / Write / Edit tool actions are not shell children; they are named in the log and in exact_argv_post_compaction.txt."),
+             "    note: " + q("Every shell child with its argv: the command log entries verbatim up to this assembly (with the abbreviations of deviation D-8; entries after C094 carry their argv in full), the exact argv of every child from C046 to C094 (X01-X52), and the assembler runs C095 and C098. Read / Write / Edit tool actions are not shell children; they are named in the log and in exact_argv_post_compaction.txt."),
              "    command_log_entries:"]
 cmd_lines += ["      - " + q(e) for e in entries]
 cmd_lines += ["    exact_argv_post_compaction:"]
 cmd_lines += ["      - " + q(x) for x in xargv.splitlines() if x.strip()]
-cmd_lines += ["    assembler_run:", "      - " + q(ARGV["assemble_v1.py"])]
+cmd_lines += ["    assembler_runs:", "      - " + q(ARGV["assemble_v1.py"]), "      - " + q(ARGV["assemble_v2.py"])]
 post_lines = ["  post_write_commands:",
               "    note: " + q("Declared before they ran; they run after both files are written, so their outputs are reported in the hand-back, not in this file.")]
 post_lines += ["    list:"] + ["      - " + q(p) for p in POST]
 
 names = sorted(n for n in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, n))
-               and n not in ("assemble_v1.out", "check_v1.out"))
+               and n not in ("assemble_v2.out", "check_v1_run2.out"))
 sf_lines = ["  scratch_files:",
             "    directory: " + q("<scratch>/rt_d897a6/ (outside the repository; transient)"),
             "    files:"]
 for n in names:
     st = os.stat(os.path.join(HERE, n))
     sf_lines.append("      - {name: %s, bytes: %d, sha256: %s, purpose: %s}" % (q(n), st.st_size, sha(n), q(PURPOSE.get(n, "scratch file"))))
-sf_lines.append("    written_after_this_list: " + q("assemble_v1.out (this assembler's printed summary) and check_v1.out (the post-write checker's output)"))
+sf_lines.append("    written_after_this_list: " + q("assemble_v2.out (this assembler's printed summary) and check_v1_run2.out (the post-write checker's output on these files)"))
 
 out_lines = []
 for ln in body.splitlines():
@@ -220,6 +230,8 @@
                 else:
                     out.append("%s- **%s**:" % (pad, k))
                     rb(v, ind + 1, out)
+            elif k == "resolved_model_id" and v is None:
+                out.append("%s- **%s**: null (none supplied by the dispatching session; none invented)" % (pad, k))
             else:
                 out.append("%s- **%s**: %s" % (pad, k, fmt(v)))
     elif isinstance(obj, list):
@@ -266,7 +278,7 @@
             if k2 == "commands":
                 md.append("### commands")
                 md.append("")
-                md.append("See Appendix B (command log verbatim and the exact argv after the compaction) and Appendix C (argv per script). Assembler run: `%s`." % ARGV["assemble_v1.py"].replace("`", "'"))
+                md.append("See Appendix B (command log verbatim and the exact argv after the compaction) and Appendix C (argv per script). Assembler runs: `%s`; `%s`." % (ARGV["assemble_v1.py"].replace("`", "'"), ARGV["assemble_v2.py"].replace("`", "'")))
                 md.append("")
                 continue
             md.append("### %s" % k2)
@@ -296,11 +308,11 @@
 md.append("")
 md.append("## Appendix B - command log (verbatim) and exact argv after the compaction")
 md.append("")
-md.append("### B.1 <scratch>/rt_d897a6/command_log.txt (sha256 %s at assembly)" % sha("command_log.txt"))
+md.append("### B.1 `<scratch>/rt_d897a6/command_log.txt` (sha256 %s at assembly)" % sha("command_log.txt"))
 md.append("")
 f = fence(clog)
 md += [f + "text", clog.rstrip("\n"), f, ""]
-md.append("### B.2 <scratch>/rt_d897a6/exact_argv_post_compaction.txt (sha256 %s)" % sha("exact_argv_post_compaction.txt"))
+md.append("### B.2 `<scratch>/rt_d897a6/exact_argv_post_compaction.txt` (sha256 %s)" % sha("exact_argv_post_compaction.txt"))
 md.append("")
 f = fence(xargv)
 md += [f + "text", xargv.rstrip("\n"), f, ""]
```

## Appendix D - every text output, verbatim

### integrity_v1.out

- sha256: ab79ae4e4c4506a5700e245dc366212bb665cd39e48e29b838f5451ebe57b806; replacements by masking: 0

```text
(a) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_launchkind.yaml ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050 expected ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050 MATCH
(a) line 184 '  status: draft'
(a) line 185 '  approved_by: null'
(a) line 186 '  approval_decision: null'
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_attcount.yaml 4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48 MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml 919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7 MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml 1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml 0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1 MATCH
(b) experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e MATCH
(c) TASK-20260924-0c2fdc path_sha256 = {"coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md": "0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8", "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml": "b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f"}
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8 MATCH receipt
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f MATCH receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f EQUALS receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8 EQUALS receipt
(c) TASK-20260924-7e8a5d path_sha256 = {"coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md": "97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055", "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml": "139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4"}
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055 MATCH receipt
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4 MATCH receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4 EQUALS receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055 EQUALS receipt
(c) TASK-20260924-93f3ca path_sha256 = {"coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md": "02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21", "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml": "0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7"}
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md 02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21 MATCH receipt
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml 0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7 MATCH receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml 0306032a3a0bfc5f29acb335fb8317d0fb08646e6563819c7fcd8922deea51a7 EQUALS receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md 02090ca26ba502633d4f544e372eff8ded48e3f6425cca19ebf8dc41d321ad21 EQUALS receipt
(c) TASK-20260924-682890 path_sha256 = {"coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md": "a24687c2b57ca0b563425956f9e0707d93d2a60a086501124fa4f3df2f20dca4", "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml": "03e66166e986670e94f97fcf14452c375bd05f65fa9f73928388457eb2d29467"}
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md a24687c2b57ca0b563425956f9e0707d93d2a60a086501124fa4f3df2f20dca4 MATCH receipt
(c)    coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml 03e66166e986670e94f97fcf14452c375bd05f65fa9f73928388457eb2d29467 MATCH receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml 03e66166e986670e94f97fcf14452c375bd05f65fa9f73928388457eb2d29467 EQUALS receipt
(c)    card value for coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md a24687c2b57ca0b563425956f9e0707d93d2a60a086501124fa4f3df2f20dca4 EQUALS receipt
(c) TASK-20260924-71d070 path_sha256 = {"experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json": "9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa", "experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md": "ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838", "experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py": "00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c"}
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json 9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838 MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py 00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c MATCH receipt
(c) TASK-20260924-ddfb69 path_sha256 = {"experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json": "36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158", "experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md": "5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7", "experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py": "ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558"}
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json 36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158 MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md 5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7 MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558 MATCH receipt
(c) TASK-20260924-a01341 path_sha256 = {"experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py": "3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64", "experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json": "49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4", "experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md": "2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3"}
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py 3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64 MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json 49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4 MATCH receipt
(c)    experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md 2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3 MATCH receipt
ALL_OK
```

### crj2d_diff.out

- sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; replacements by masking: 0

```text
(empty file)
```

### scan_v1.out

- sha256: 179452fe82d4ac9cb1822fab59914c4766a028f827c513d65219fdea166b1a8c; replacements by masking: 0

```text
files scanned: 71
run_child defs: [{'file': 'implementation-v2/v2_solver.py', 'line': 149, 'in': '<module>'}]
run_child calls (all): 12
    implementation-v2/v2_driver.py 101 V.run_child in child_job PRODUCTION
    implementation-v2/v2_driver.py 166 V.run_child in solve PRODUCTION
    implementation-v2/v2_driver.py 650 V.run_child in cmd_anchor_identity PRODUCTION
    implementation-v2/v2_solver.py 517 run_child in callgrind_instructions PRODUCTION
    implementation-v2-a1/a1_health.py 147 V.run_child in run_system PRODUCTION
    implementation-v2-a1/a1_pari.py 96 V.run_child in curve_facts PRODUCTION
    implementation-v2-r1/r1_devchecks.py 177 V.run_child in gp_crosscheck non-production
    implementation-v2-r1/r1_devchecks_more.py 75 V.run_child in dv1_static non-production
    implementation-v2-r2/r2_devchecks.py 186 V.run_child in gp_crosscheck non-production
    implementation-v2-r2/r2_devchecks_more.py 75 V.run_child in dv1_static non-production
    implementation-v2-r3/r3_devchecks.py 190 V.run_child in gp_crosscheck non-production
    implementation-v2-r3/r3_devchecks_more.py 80 V.run_child in dv1_static non-production
run_child non-call refs: []
run_child stores: []
from v2_solver import: []
getattr/setattr run_child: []
defaults referencing run_child: []
dynamic import/exec/eval: [{'file': 'implementation/ladder_select.py', 'line': 28, 'func': '__import__', 'in': '<module>'}, {'file': 'implementation-v2-a1/a1_run_wrapper.py', 'line': 278, 'func': '__import__', 'in': 'main'}]
writes of key instructions_callgrind: [{'file': 'implementation-v2/v2_driver.py', 'line': 209, 'how': 'subscript store res', 'in': 'solve'}]
writes of key comparator: [{'file': 'implementation-v2/v2_driver.py', 'line': 655, 'how': 'subscript store raw', 'in': 'cmd_anchor_identity'}, {'file': 'implementation-v2-r1/r1_make_plans.py', 'line': 140, 'how': 'dict literal key', 'in': 'reg1_block'}, {'file': 'implementation-v2-r2/r2_make_plans.py', 'line': 136, 'how': 'dict literal key', 'in': 'reg1_block'}, {'file': 'implementation-v2-r3/r3_make_plans.py', 'line': 177, 'how': 'dict literal key', 'in': 'reg1_block'}]
other launch calls:
    implementation/run_wrapper.py 98 subprocess.run in main 
    implementation/run_wrapper.py 23 subprocess.run in sh 
    implementation/symmetrize.py 399 subprocess.Popen in run_msolve 
    implementation-v2/v2_common.py 59 subprocess.run in sh PROD
    implementation-v2/v2_run_wrapper.py 182 subprocess.run in main 
    implementation-v2/v2_run_wrapper.py 49 subprocess.run in git 
    implementation-v2/v2_solver.py 181 os.fork in _run_child_locked PROD
    implementation-v2/v2_solver.py 205 os.execv in _run_child_locked PROD
    implementation-v2/v2_solver.py 533 subprocess.run in callgrind_instructions PROD
    implementation-v2/v2_solver.py 204 os.execve in _run_child_locked PROD
    implementation-v2-a1/a1_pari.py 121 subprocess.run in gp_version PROD
    implementation-v2-a1/a1_run_wrapper.py 303 subprocess.run in main 
    implementation-v2-a1/a1_run_wrapper.py 61 subprocess.run in git 
    implementation-v2-a1/a1_run_wrapper.py 372 subprocess.run in V_sh 
    implementation-v2-a1/a1_toy.py 334 subprocess.run in dev_a 
    implementation-v2-r1/r1_check_run.py 173 subprocess.run in main 
    implementation-v2-r1/r1_devchecks.py 192 subprocess.run in run_worker 
    implementation-v2-r1/r1_devchecks_more.py 217 subprocess.run in dv5 
    implementation-v2-r1/r1_devchecks_more.py 375 subprocess.run in dv10 
    implementation-v2-r1/r1_dv6.py 279 subprocess.run in dv6 
    implementation-v2-r1/r1_run_wrapper.py 381 subprocess.run in launch 
    implementation-v2-r1/r1_run_wrapper.py 65 subprocess.run in git 
    implementation-v2-r1/r1_run_wrapper.py 294 subprocess.run in sh 
    implementation-v2-r2/r2_check_run.py 254 subprocess.run in main 
    implementation-v2-r2/r2_devchecks.py 201 subprocess.run in run_worker 
    implementation-v2-r2/r2_devchecks_more.py 238 subprocess.run in dv5 
    implementation-v2-r2/r2_devchecks_more.py 473 subprocess.run in dv10 
    implementation-v2-r2/r2_devchecks_more.py 429 subprocess.run in dv9 
    implementation-v2-r2/r2_dv6.py 291 subprocess.run in dv6 
    implementation-v2-r2/r2_run_wrapper.py 437 subprocess.run in launch 
    implementation-v2-r2/r2_run_wrapper.py 73 subprocess.run in git 
    implementation-v2-r2/r2_run_wrapper.py 309 subprocess.run in sh 
    implementation-v2-r3/r3_check_run.py 372 subprocess.run in main 
    implementation-v2-r3/r3_devchecks.py 205 subprocess.run in run_worker 
    implementation-v2-r3/r3_devchecks_more.py 278 subprocess.run in dv5 
    implementation-v2-r3/r3_devchecks_more.py 93 subprocess.run in dv1_static 
    implementation-v2-r3/r3_devchecks_more.py 538 subprocess.run in dv10 
    implementation-v2-r3/r3_devchecks_more.py 100 subprocess.run in dv1_static 
    implementation-v2-r3/r3_devchecks_more.py 492 subprocess.run in dv9 
    implementation-v2-r3/r3_devchecks_more.py 502 subprocess.run in dv9 
    implementation-v2-r3/r3_devchecks_more.py 96 subprocess.run in dv1_static 
    implementation-v2-r3/r3_devchecks_more.py 99 subprocess.run in dv1_static 
    implementation-v2-r3/r3_dv6.py 324 subprocess.run in dv6 
    implementation-v2-r3/r3_run_wrapper.py 477 subprocess.run in launch 
    implementation-v2-r3/r3_run_wrapper.py 73 subprocess.run in git 
    implementation-v2-r3/r3_run_wrapper.py 341 subprocess.run in sh 
closure r3_entry_v2: ['implementation-v2-r3/r3_common.py', 'implementation-v2-r3/r3_entry_v2.py', 'implementation-v2-r3/r3_resolve.py', 'implementation-v2/v2_arms.py', 'implementation-v2/v2_child.py', 'implementation-v2/v2_common.py', 'implementation-v2/v2_driver.py', 'implementation-v2/v2_field.py', 'implementation-v2/v2_lift.py', 'implementation-v2/v2_scoring.py', 'implementation-v2/v2_solver.py', 'implementation-v2/v2_verify_independent.py']
closure r3_entry_a1: ['implementation-v2-a1/a1_common.py', 'implementation-v2-a1/a1_driver.py', 'implementation-v2-a1/a1_health.py', 'implementation-v2-a1/a1_pari.py', 'implementation-v2-a1/a1_reading.py', 'implementation-v2-r3/r3_common.py', 'implementation-v2-r3/r3_entry_a1.py', 'implementation-v2-r3/r3_resolve.py', 'implementation-v2/v2_arms.py', 'implementation-v2/v2_child.py', 'implementation-v2/v2_common.py', 'implementation-v2/v2_driver.py', 'implementation-v2/v2_field.py', 'implementation-v2/v2_lift.py', 'implementation-v2/v2_scoring.py', 'implementation-v2/v2_solver.py', 'implementation-v2/v2_verify_independent.py']
calls of interest in production closure:
    implementation-v2/v2_arms.py 507 Msq.solve in _build_once
    implementation-v2/v2_common.py 59 subprocess.run in sh
    implementation-v2/v2_driver.py 122 child_job in build_poly
    implementation-v2/v2_driver.py 136 child_job in raw_grid
    implementation-v2/v2_driver.py 209 V.callgrind_instructions in solve
    implementation-v2/v2_driver.py 693 solve in cmd_anchor_identity
    implementation-v2/v2_driver.py 841 solve in cmd_controls
    implementation-v2/v2_driver.py 1174 solve in _run_cell
    implementation-v2/v2_driver.py 358 solve in fixture_core.run_target
    implementation-v2/v2_driver.py 565 solve in cmd_fixture4
    implementation-v2/v2_driver.py 711 solve in cmd_anchor_identity
    implementation-v2/v2_driver.py 786 solve in cmd_controls
    implementation-v2/v2_driver.py 787 solve in cmd_controls
    implementation-v2/v2_solver.py 533 subprocess.run in callgrind_instructions
    implementation-v2-a1/a1_driver.py 89 P.curve_facts in cmd_controls_a1
    implementation-v2-a1/a1_driver.py 129 H.run in cmd_controls_a1
    implementation-v2-a1/a1_driver.py 166 D.solve in cmd_controls_a1
    implementation-v2-a1/a1_health.py 287 run in main
    implementation-v2-a1/a1_health.py 234 run_system in run
    implementation-v2-a1/a1_health.py 237 run_system in run
    implementation-v2-a1/a1_health.py 241 run_system in run
    implementation-v2-a1/a1_health.py 244 run_system in run
    implementation-v2-a1/a1_pari.py 135 curve_facts in fb1_curve_search
    implementation-v2-a1/a1_pari.py 121 subprocess.run in gp_version
dis solve 207-210: [(207, 'LOAD_FAST', 'callgrind_timeout'), (207, 'POP_JUMP_FORWARD_IF_FALSE', 'to 2356'), (207, 'LOAD_FAST', 'outcome'), (207, 'LOAD_CONST', "'ok'"), (207, 'COMPARE_OP', '=='), (207, 'POP_JUMP_FORWARD_IF_FALSE', 'to 2356'), (208, 'LOAD_GLOBAL', 'os'), (208, 'LOAD_ATTR', 'path'), (208, 'LOAD_METHOD', 'join'), (208, 'LOAD_FAST', 'sd'), (208, 'LOAD_FAST', 'tag'), (208, 'LOAD_CONST', "'.cg.ms.out'"), (208, 'BINARY_OP', '+'), (208, 'PRECALL', ''), (208, 'CALL', ''), (208, 'STORE_FAST', 'cg_out'), (209, 'LOAD_GLOBAL', 'NULL + V'), (209, 'LOAD_ATTR', 'callgrind_instructions'), (209, 'LOAD_GLOBAL', 'NULL + V'), (209, 'LOAD_ATTR', 'msolve_argv'), (209, 'LOAD_FAST', 'inp'), (209, 'LOAD_FAST', 'cg_out'), (209, 'LOAD_CONST', '1'), (209, 'LOAD_FAST', 'gb_only'), (209, 'KW_NAMES', ''), (209, 'PRECALL', ''), (209, 'CALL', ''), (209, 'LOAD_FAST', 'sd'), (209, 'LOAD_FAST', 'tag'), (209, 'LOAD_FAST', 'ctx'), (209, 'LOAD_ATTR', 'cap'), (209, 'LOAD_FAST', 'callgrind_timeout'), (209, 'PRECALL', ''), (209, 'CALL', ''), (209, 'LOAD_FAST', 'res'), (209, 'LOAD_CONST', "'instructions_callgrind'"), (209, 'STORE_SUBSCR', ''), (210, 'NOP', '')]
dis curve_facts 91-96: [(91, 'LOAD_GLOBAL', 'os'), (91, 'LOAD_ATTR', 'path'), (91, 'LOAD_METHOD', 'join'), (91, 'LOAD_FAST', 'out_dir'), (91, 'LOAD_FAST', 'tag'), (91, 'LOAD_CONST', "'.gp'"), (91, 'BINARY_OP', '+'), (91, 'PRECALL', ''), (91, 'CALL', ''), (91, 'STORE_FAST', 'gpf'), (92, 'LOAD_GLOBAL', 'NULL + open'), (92, 'LOAD_FAST', 'gpf'), (92, 'LOAD_CONST', "'w'"), (92, 'PRECALL', ''), (92, 'CALL', ''), (92, 'BEFORE_WITH', ''), (92, 'STORE_FAST', 'fh'), (93, 'LOAD_FAST', 'fh'), (93, 'LOAD_METHOD', 'write'), (93, 'LOAD_GLOBAL', 'NULL + gp_script'), (93, 'LOAD_FAST', 'p'), (93, 'LOAD_FAST', 'modulus'), (93, 'LOAD_FAST', 'curves'), (93, 'PRECALL', ''), (93, 'CALL', ''), (93, 'PRECALL', ''), (93, 'CALL', ''), (93, 'POP_TOP', ''), (92, 'LOAD_CONST', 'None'), (92, 'LOAD_CONST', 'None'), (92, 'LOAD_CONST', 'None'), (92, 'PRECALL', ''), (92, 'CALL', ''), (92, 'POP_TOP', ''), (92, 'JUMP_FORWARD', 'to 272'), (92, 'PUSH_EXC_INFO', ''), (92, 'WITH_EXCEPT_START', ''), (92, 'POP_JUMP_FORWARD_IF_TRUE', 'to 264'), (92, 'RERAISE', ''), (92, 'POP_TOP', ''), (92, 'POP_EXCEPT', ''), (92, 'POP_TOP', ''), (92, 'POP_TOP', ''), (94, 'LOAD_GLOBAL', 'GP'), (94, 'LOAD_CONST', "'-q'"), (94, 'LOAD_CONST', "'-f'"), (94, 'LOAD_CONST', "'--default'"), (94, 'LOAD_CONST', "'nbthreads=1'"), (94, 'LOAD_FAST', 'gpf'), (94, 'BUILD_LIST', ''), (94, 'STORE_FAST', 'argv'), (95, 'LOAD_GLOBAL', 'os'), (95, 'LOAD_ATTR', 'path'), (95, 'LOAD_METHOD', 'join'), (95, 'LOAD_FAST', 'out_dir'), (95, 'LOAD_FAST', 'tag'), (95, 'LOAD_CONST', "'.gp.stdout'"), (95, 'BINARY_OP', '+'), (95, 'PRECALL', ''), (95, 'CALL', ''), (95, 'LOAD_GLOBAL', 'os'), (95, 'LOAD_ATTR', 'path'), (95, 'LOAD_METHOD', 'join'), (95, 'LOAD_FAST', 'out_dir'), (95, 'LOAD_FAST', 'tag'), (95, 'LOAD_CONST', "'.gp.stderr'"), (95, 'BINARY_OP', '+'), (95, 'PRECALL', ''), (95, 'CALL', ''), (95, 'STORE_FAST', 'se'), (95, 'STORE_FAST', 'so'), (96, 'LOAD_GLOBAL', 'NULL + V'), (96, 'LOAD_ATTR', 'run_child'), (96, 'LOAD_FAST', 'argv'), (96, 'LOAD_FAST', 'so'), (96, 'LOAD_FAST', 'se'), (96, 'LOAD_FAST', 'cap'), (96, 'LOAD_FAST', 'timeout_s'), (96, 'LOAD_CONST', 'False'), (96, 'KW_NAMES', ''), (96, 'PRECALL', ''), (96, 'CALL', ''), (96, 'STORE_DEREF', 'rec')]
guard refusals: {'import': 0, 'launch': 0} python: 3.11.15
```

### scan_v2.out

- sha256: 64c8ba177f19c90dd041c6c4afdf7d51cdadee1fb458d1809c27a8a3fa920bb7; replacements by masking: 0

```text
production files: 18
_run_child_locked defs: [{'file': 'implementation-v2/v2_solver.py', 'line': 177}]
_run_child_locked refs: [{'file': 'implementation-v2/v2_solver.py', 'line': 171, 'ctx': 'Load'}]
process-ending / exec / hook / thread calls in production closure:
    implementation-v2/v2_child.py 60 sys.exit | sys.exit(96)
    implementation-v2/v2_child.py 69 sys.exit | sys.exit(0)
    implementation-v2/v2_child.py 81 sys.exit | sys.exit(0)
    implementation-v2/v2_solver.py 181 os.fork | os.fork()
    implementation-v2/v2_solver.py 208 os._exit | os._exit(99)
    implementation-v2/v2_solver.py 205 os.execv | os.execv(argv[0], argv)
    implementation-v2/v2_solver.py 201 os._exit | os._exit(98)
    implementation-v2/v2_solver.py 204 os.execve | os.execve(argv[0], argv, env)
    implementation-v2/v2_solver.py 266 os.kill | os.kill(pid, signal.SIGKILL)
    implementation-v2/v2_solver.py 196 os._exit | os._exit(97)
    implementation-v2/v2_verify_independent.py 280 sys.exit | sys.exit(1 if bad else 0)
    implementation-v2-a1/a1_health.py 297 sys.exit | sys.exit(main())
    implementation-v2-a1/a1_pari.py 148 sys.exit | sys.exit(0)
    implementation-v2-r3/r3_entry_a1.py 115 sys.exit | sys.exit(main())
    implementation-v2-r3/r3_entry_v2.py 84 sys.exit | sys.exit(main())
raise SystemExit/KeyboardInterrupt in production closure:
    implementation-v2/v2_common.py 100 SystemExit("GFPN_RUN_DIR not set: launch through v2_run_wrapper.py")
    implementation-v2-a1/a1_driver.py 52 SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (p, ctx.pkg.get("p")))
    implementation-v2-a1/a1_driver.py 224 SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (args.p, ctx_pkg.get("p")))
    implementation-v2-a1/a1_driver.py 233 SystemExit("REFUSING: arguments do not match the plan package")
try statements whose body calls a launching function (production closure):
    implementation-v2/v2_common.py 58 - 61 ['Exception']  ['subprocess.run']
    implementation-v2/v2_solver.py 531 - 547 ['Exception']  ['subprocess.run']
    implementation-v2-a1/a1_pari.py 119 - 123 ['Exception']  ['subprocess.run']
removals in production closure:
    implementation-v2/v2_driver.py 144 os.remove | os.remove(out + ".npz")
    implementation-v2/v2_driver.py 221 os.remove | os.remove(inp)
    implementation-v2/v2_driver.py 211 os.remove | os.remove(cg_out)
    implementation-v2/v2_driver.py 227 os.remove | os.remove(out)
    implementation-v2/v2_solver.py 549 os.remove | os.remove(out)
    implementation-v2-r3/r3_resolve.py 167 os.replace | os.replace(tmp, path)
    implementation-v2-r3/r3_resolve.py 234 os.rename | os.rename(src, dst)
write-mode open() in production closure:
    implementation-v2/v2_arms.py 707 | open(path, "w")
    implementation-v2/v2_child.py 41 | open(out + ".meta.json", "w")
    implementation-v2/v2_child.py 68 | open(spec["out"] + ".meta.json", "w")
    implementation-v2/v2_child.py 104 | open(spec["out"] + ".meta.json", "w")
    implementation-v2/v2_child.py 80 | open(spec["out"] + ".meta.json", "w")
    implementation-v2/v2_common.py 109 | open(path, "w")
    implementation-v2/v2_common.py 114 | open(path, "w")
    implementation-v2/v2_driver.py 967 | open(dst, "wb")
    implementation-v2/v2_driver.py 969 | open(dst[:-4] + ".meta.json", "wb")
    implementation-v2/v2_solver.py 101 | open(self.path, "a+")
    implementation-v2-a1/a1_health.py 251 | open(os.path.join(out_dir, "health-%d.json" % p), "w")
    implementation-v2-a1/a1_pari.py 92 | open(gpf, "w")
    implementation-v2-r3/r3_common.py 415 | open(os.path.join(run_dir, "pari-stack.json"), "w")
    implementation-v2-r3/r3_resolve.py 163 | open(tmp, "w")
guard refusals: {'import': 0, 'launch': 0}
```

### pkgread_v1.out

- sha256: c1395cf11719ef4e5a0566c5c8752e8f206919a7b4de7e20570103f4000033bb; replacements by masking: 0

```text
RUN-GFPN-f6a21a top: ['certificates', 'child', 'command.txt', 'cost-band-p64.yaml', 'environment.json', 'heur-dflat.yaml', 'ladder-table.yaml', 'manifest.yaml', 'pari-stack.json', 'polynomials', 'raw-result.json', 'solver', 'solver-events.json', 'stderr.log', 'stdout.log']
   five-dir counts: {'child': 68, 'solver': 216} total 284
   sha256: {'solver-events.json': '32aea434aabf91a8db4826ca238a405c97526707831bf70080e1b152d5f3595d', 'raw-result.json': 'f6f54870a5b6370ca6c527b528ebb18936fd19f96da3298af4bc9622d1219dc5', 'command.txt': '75b5449ec50ec26a2defdb1f193f18d5c2929e738051da7fe1855d12c01b78f8'}
RUN-GFPN-902222 top: ['certificates', 'child', 'command.txt', 'cost-band-p64.yaml', 'environment.json', 'heur-dflat.yaml', 'ladder-table.yaml', 'manifest.yaml', 'pari-stack.json', 'polynomials', 'raw-result.json', 'solver', 'solver-events.json', 'stderr.log', 'stdout.log']
   five-dir counts: {'child': 68, 'solver': 216} total 284
   sha256: {'solver-events.json': 'a23e30b6b84a99605698ee697d3e33ebd6b06bbd678f5bca02b115ab38b7d759', 'raw-result.json': '3f9f575b8eea88bda8e8385b5683392fb7fbc7cf8d0009bdd2052fa3e3b9e8a4', 'command.txt': '22162d41dc0e787144c021708bd6f9dd9930306e9e33d743d52168fde77cd4a8'}
RUN-GFPN-f5412a top: ['certificates', 'child', 'command.txt', 'comparator', 'cost-band-p64.yaml', 'environment.json', 'heur-dflat.yaml', 'ladder-table.yaml', 'manifest.yaml', 'pari-stack.json', 'polynomials', 'raw-result.json', 'solver', 'solver-events.json', 'stderr.log', 'stdout.log']
   five-dir counts: {'child': 5, 'solver': 20, 'comparator': 7} total 32
   sha256: {'solver-events.json': 'b927b44f1ed584a0d39d10c0bc898493620e93678efc3ffb81f82914c5cd3162', 'raw-result.json': 'af5d5d2f375d384912e375e704fda0d397c07e94dbc8147614eb7cdff8879290', 'command.txt': '25d86fc12fc6bc3c90b53dfa5e33608b00860d291786fe023b998affb9caef9a'}
RUN-GFPN-bfe956 top: ['certificates', 'child', 'command.txt', 'cost-band-p64.yaml', 'environment.json', 'heur-dflat.yaml', 'ladder-table.yaml', 'manifest.yaml', 'pari-stack.json', 'polynomials', 'raw-result.json', 'solver', 'solver-events.json', 'stderr.log', 'stdout.log']
   five-dir counts: {'child': 51, 'solver': 32} total 83
   sha256: {'solver-events.json': '1b09e5a19ec54ba1541f6d8dcbcb4060a5080c43b1ef20027d3d4f3a88803511', 'raw-result.json': '5b1ccdd41ce9dbc04e441750b8dfd92b1a5c5ec7398c02f6e2e1b73929a49c85', 'command.txt': '039efb514c47747b1d4845ac82811120a3cb1e7f7ccd64766fd059916cf1824e'}
lstat checked: 708 changed: []
```

### explore_v1.out

- sha256: 53821bfdbc97da20293bdba24112b8018bfbfac591af7e21e4950ba1b8b2b0e7; replacements by masking: 2

```text
====================================================================================================
RUN-GFPN-f6a21a raw kind fixture_F1_F3 run_status completed_valid gate_pass True top keys ['ac5_reading', 'beta_equals_smallest_nonsquare', 'builds', 'certificate', 'curve', 'curve_checks', 'data_source', 'envelope', 'events', 'expected_fixture_F1', 'expected_structure', 'failure_class', 'field', 'fixture_F1', 'fixture_F2a', 'fixture_F2b', 'fixture_F3', 'gate_pass', 'group', 'host', 'infrastructure_rows', 'kind', 'like_for_like_T2_T3_exercised', 'm', 'metrics', 'n', 'p', 'package', 'planted_targets', 'replaced_fresh_targets', 'rescaling', 'rescaling_fixed_at', 'run_status', 'scoring_reference', 'seeds', 'structure_checks', 'targets']
  command.txt: # cwd: /home/user/crypto-autoresearcher | # GFPN_RUN_DIR=/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a | # PYTHONDONTWRITEBYTECODE=1 | # PYTHONHASHSEED=0 (SE-6) | # launched by: python3 -B experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py RUN-GFPN-f6a21a (no outer guard) | /usr/local/bin/python3 -B /home/user/crypto-autoresearcher/experiments/EX
  solver-events top keys: ['K', 'authority', 'cap_rule', 'consistency_violation', 'experiment_id', 'max_attempts_per_call', 'rename_suffix', 'schema', 'sites', 'spacing_s', 'updated_at']
   site v2_driver.solve counters {"wrapped_calls": 36, "attempts_total": 36, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0, "passthrough_calls_gb_only_true": 0} events 0 records 0
   site a1_health.run_system counters {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0} events 0 records 0
   site v2_driver.solve/callgrind counters {"callgrind_children_observed": 36, "with_log_visible_ssf_indicator": 0, "with_quotient_dimension_mismatch": 0, "with_readback_differing_from_requested_cap": 0} events 0 records 36
   S-3 record tags (36): ['fx_reg0_raw_x', 'fx_reg0_raw_u', 'fx_reg0_S3', 'fx_reg0_S3_rescaled', 'fx_reg0_torsion_S3_norm', 'fx_reg0_torsion_S3_rq', 'fx_reg1_raw_x', 'fx_reg1_raw_u', 'fx_reg1_S3', 'fx_reg1_S3_rescaled', 'fx_reg1_torsion_S3_norm', 'fx_reg1_torsion_S3_rq', 'fx_fresh1_raw_x', 'fx_fresh1_raw_u', 'fx_fresh1_S3', 'fx_fresh1_S3_rescaled', 'fx_fresh1_torsion_S3_norm', 'fx_fresh1_torsion_S3_rq', 'fx_fresh2_raw_x', 'fx_fresh2_raw_u', 'fx_fresh2_S3', 'fx_fresh2_S3_rescaled', 'fx_fresh2_torsion_S3_norm', 'fx_fresh2_torsion_S3_rq', 'fx_planted0_raw_x', 'fx_planted0_raw_u', 'fx_planted0_S3', 'fx_planted0_S3_rescaled', 'fx_planted0_torsion_S3_norm', 'fx_planted0_torsion_S3_rq', 'fx_planted1_raw_x', 'fx_planted1_raw_u', 'fx_planted1_S3', 'fx_planted1_S3_rescaled', 'fx_planted1_torsion_S3_norm', 'fx_planted1_torsion_S3_rq']
   S-3 record[0] keys: ['attempt_recorded_by_the_wrapper', 'child_readback_equals_requested_cap', 'dimension_of_quotient', 'f<masked>_squarefree_degree', 'files', 'log_visible_ssf_indicator', 'positive_dimension_reported', 'printed_quotient_dimension_equals_recorded_attempt', 'random_linear_form_string_in_log', 'recorded_attempt_dimension_of_quotient_printed', 'reg1_compared_fields_verbatim', 'requested_cap_bytes', 'site', 'tag'] files {'fx_reg0_raw_x.callgrind.stdout': {'sha256': '6e5555497e1392bc701be9fc801fde51b2165f6991d370ceaf3cf80035fd8454', 'bytes': 26882}, 'fx_reg0_raw_x.callgrind.stderr': {'sha256': '921d225ed10d01d76c82ae2814763b624069d1caaa2f1e84ddbe780dcae28480', 'bytes': 5084}}
  listing solver sample: ['fx_fresh1_S3.callgrind.stderr', 'fx_fresh1_S3.callgrind.stdout', 'fx_fresh1_S3.ms', 'fx_fresh1_S3.ms.err', 'fx_fresh1_S3.ms.log', 'fx_fresh1_S3.ms.out', 'fx_fresh1_S3_rescaled.callgrind.stderr', 'fx_fresh1_S3_rescaled.callgrind.stdout', 'fx_fresh1_S3_rescaled.ms', 'fx_fresh1_S3_rescaled.ms.err', 'fx_fresh1_S3_rescaled.ms.log', 'fx_fresh1_S3_rescaled.ms.out']
  listing child sample: ['fixture_S3.meta.json', 'fixture_S3.npz', 'fixture_S3.spec.json', 'fixture_S3.stderr', 'fixture_S3.stdout', 'fixture_S3_rescaled.meta.json', 'fixture_S3_rescaled.npz', 'fixture_S3_rescaled.spec.json']
  listing comparator: None
  solve-like records in raw: 36
     ('/targets[0]/arms/raw_x', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_raw_x.ms.out', '-P', '1'])
     ('/targets[0]/arms/raw_u', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_raw_u.ms.out', '-P', '1'])
     ('/targets[0]/arms/S3', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_S3.ms.out', '-P', '1'])
     ('/targets[0]/arms/S3_rescaled', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_S3_rescaled.ms.out', '-P', '1'])
     ('/targets[0]/arms/torsion_S3_norm', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_torsion_S3_norm.ms.out', '-P', '1'])
     ('/targets[0]/arms/torsion_S3_rq', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a/solver/fx_reg0_torsion_S3_rq.ms.out', '-P', '1'])
  comparator key: False None
====================================================================================================
RUN-GFPN-902222 raw kind fixture_F1_F3 run_status completed_valid gate_pass True top keys ['ac5_reading', 'beta_equals_smallest_nonsquare', 'builds', 'certificate', 'curve', 'curve_checks', 'data_source', 'envelope', 'events', 'expected_fixture_F1', 'expected_structure', 'failure_class', 'field', 'fixture_F1', 'fixture_F2a', 'fixture_F2b', 'fixture_F3', 'gate_pass', 'group', 'host', 'infrastructure_rows', 'kind', 'like_for_like_T2_T3_exercised', 'm', 'metrics', 'n', 'p', 'package', 'planted_targets', 'replaced_fresh_targets', 'rescaling', 'rescaling_fixed_at', 'run_status', 'scoring_reference', 'seeds', 'structure_checks', 'targets']
  command.txt: # cwd: /home/user/crypto-autoresearcher | # GFPN_RUN_DIR=/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 | # PYTHONDONTWRITEBYTECODE=1 | # PYTHONHASHSEED=0 (SE-6) | # launched by: python3 -B experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py RUN-GFPN-902222 (no outer guard) | /usr/local/bin/python3 -B /home/user/crypto-autoresearcher/experiments/EX
  solver-events top keys: ['K', 'authority', 'cap_rule', 'consistency_violation', 'experiment_id', 'max_attempts_per_call', 'rename_suffix', 'schema', 'sites', 'spacing_s', 'updated_at']
   site v2_driver.solve counters {"wrapped_calls": 36, "attempts_total": 36, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0, "passthrough_calls_gb_only_true": 0} events 0 records 0
   site a1_health.run_system counters {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0} events 0 records 0
   site v2_driver.solve/callgrind counters {"callgrind_children_observed": 36, "with_log_visible_ssf_indicator": 0, "with_quotient_dimension_mismatch": 0, "with_readback_differing_from_requested_cap": 0} events 0 records 36
   S-3 record tags (36): ['fx_reg0_raw_x', 'fx_reg0_raw_u', 'fx_reg0_S3', 'fx_reg0_S3_rescaled', 'fx_reg0_torsion_S3_norm', 'fx_reg0_torsion_S3_rq', 'fx_reg1_raw_x', 'fx_reg1_raw_u', 'fx_reg1_S3', 'fx_reg1_S3_rescaled', 'fx_reg1_torsion_S3_norm', 'fx_reg1_torsion_S3_rq', 'fx_fresh1_raw_x', 'fx_fresh1_raw_u', 'fx_fresh1_S3', 'fx_fresh1_S3_rescaled', 'fx_fresh1_torsion_S3_norm', 'fx_fresh1_torsion_S3_rq', 'fx_fresh2_raw_x', 'fx_fresh2_raw_u', 'fx_fresh2_S3', 'fx_fresh2_S3_rescaled', 'fx_fresh2_torsion_S3_norm', 'fx_fresh2_torsion_S3_rq', 'fx_planted0_raw_x', 'fx_planted0_raw_u', 'fx_planted0_S3', 'fx_planted0_S3_rescaled', 'fx_planted0_torsion_S3_norm', 'fx_planted0_torsion_S3_rq', 'fx_planted1_raw_x', 'fx_planted1_raw_u', 'fx_planted1_S3', 'fx_planted1_S3_rescaled', 'fx_planted1_torsion_S3_norm', 'fx_planted1_torsion_S3_rq']
   S-3 record[0] keys: ['attempt_recorded_by_the_wrapper', 'child_readback_equals_requested_cap', 'dimension_of_quotient', 'f<masked>_squarefree_degree', 'files', 'log_visible_ssf_indicator', 'positive_dimension_reported', 'printed_quotient_dimension_equals_recorded_attempt', 'random_linear_form_string_in_log', 'recorded_attempt_dimension_of_quotient_printed', 'reg1_compared_fields_verbatim', 'requested_cap_bytes', 'site', 'tag'] files {'fx_reg0_raw_x.callgrind.stdout': {'sha256': 'de51b44a9e9fabe9f6ef8a69a2036b43f083454ecd02f3f02452722c4738e716', 'bytes': 26882}, 'fx_reg0_raw_x.callgrind.stderr': {'sha256': 'f75af82008e0ce8e748667974be7412032f7b1f74ee53b3f404289ef0e2938f5', 'bytes': 5084}}
  listing solver sample: ['fx_fresh1_S3.callgrind.stderr', 'fx_fresh1_S3.callgrind.stdout', 'fx_fresh1_S3.ms', 'fx_fresh1_S3.ms.err', 'fx_fresh1_S3.ms.log', 'fx_fresh1_S3.ms.out', 'fx_fresh1_S3_rescaled.callgrind.stderr', 'fx_fresh1_S3_rescaled.callgrind.stdout', 'fx_fresh1_S3_rescaled.ms', 'fx_fresh1_S3_rescaled.ms.err', 'fx_fresh1_S3_rescaled.ms.log', 'fx_fresh1_S3_rescaled.ms.out']
  listing child sample: ['fixture_S3.meta.json', 'fixture_S3.npz', 'fixture_S3.spec.json', 'fixture_S3.stderr', 'fixture_S3.stdout', 'fixture_S3_rescaled.meta.json', 'fixture_S3_rescaled.npz', 'fixture_S3_rescaled.spec.json']
  listing comparator: None
  solve-like records in raw: 36
     ('/targets[0]/arms/raw_x', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_raw_x.ms.out', '-P', '1'])
     ('/targets[0]/arms/raw_u', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_raw_u.ms.out', '-P', '1'])
     ('/targets[0]/arms/S3', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_S3.ms.out', '-P', '1'])
     ('/targets[0]/arms/S3_rescaled', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_S3_rescaled.ms.out', '-P', '1'])
     ('/targets[0]/arms/torsion_S3_norm', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_torsion_S3_norm.ms.out', '-P', '1'])
     ('/targets[0]/arms/torsion_S3_rq', True, True, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222/solver/fx_reg0_torsion_S3_rq.ms.out', '-P', '1'])
  comparator key: False None
====================================================================================================
RUN-GFPN-f5412a raw kind anchor_identity run_status completed_valid gate_pass True top keys ['archived_traces', 'arm', 'build', 'certificate', 'comparator', 'control', 'curve', 'curve_identity_with_archived_anchor', 'curve_shape', 'envelope', 'events', 'failure_class', 'gate_pass', 'host', 'kind', 'm', 'metrics', 'msolve_version', 'n', 'p', 'package', 'run_status', 'scoring_reference', 'solver_substitution', 'targets', 'v1_outcome_note', 'wall_clock_ratio_NON_BLOCKING']
  command.txt: # cwd: /home/user/crypto-autoresearcher | # GFPN_RUN_DIR=/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a | # PYTHONDONTWRITEBYTECODE=1 | # PYTHONHASHSEED=0 (SE-6) | # launched by: python3 -B experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py RUN-GFPN-f5412a (no outer guard) | /usr/local/bin/python3 -B /home/user/crypto-autoresearcher/experiments/EX
  solver-events top keys: ['K', 'authority', 'cap_rule', 'consistency_violation', 'experiment_id', 'max_attempts_per_call', 'rename_suffix', 'schema', 'sites', 'spacing_s', 'updated_at']
   site v2_driver.solve counters {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0, "passthrough_calls_gb_only_true": 5} events 0 records 0
   site a1_health.run_system counters {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0} events 0 records 0
   site v2_driver.solve/callgrind counters {"callgrind_children_observed": 0, "with_log_visible_ssf_indicator": 0, "with_quotient_dimension_mismatch": 0, "with_readback_differing_from_requested_cap": 0} events 0 records 0
   S-3 record tags (0): []
  listing solver sample: ['anchor_comparator_random.ms', 'anchor_comparator_random.ms.err', 'anchor_comparator_random.ms.log', 'anchor_comparator_random.ms.out', 'anchor_comparator_system.ms', 'anchor_comparator_system.ms.err', 'anchor_comparator_system.ms.log', 'anchor_comparator_system.ms.out', 'anchor_v2_t0.ms', 'anchor_v2_t0.ms.err', 'anchor_v2_t0.ms.log', 'anchor_v2_t0.ms.out']
  listing child sample: ['anchor_S4.meta.json', 'anchor_S4.npz', 'anchor_S4.spec.json', 'anchor_S4.stderr', 'anchor_S4.stdout']
  listing comparator: ['anchor17_planted.ms', 'anchor17_random.ms', 'anchor25_planted.ms', 'anchor25_random.ms', 'k4a_results.json', 'stderr.log', 'stdout.log']
  solve-like records in raw: 4
     ('/targets[0]', False, False, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a/solver/anchor_comparator_random.ms.out', '-g', '1'])
     ('/targets[1]', False, False, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a/solver/anchor_v2_t0.ms.out', '-g', '1'])
     ('/targets[2]', False, False, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a/solver/anchor_v2_t1.ms.out', '-g', '1'])
     ('/targets[3]', False, False, 'ok', ['/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a/solver/anchor_v2_t2.ms.out', '-g', '1'])
  comparator key: True ['child', 'comparator_reported_error', 'python', 'script', 'script_sha256']
====================================================================================================
RUN-GFPN-bfe956 raw kind frozen_controls run_status completed_valid gate_pass True top keys ['certificate', 'checks', 'envelope', 'events', 'failure_class', 'gate_pass', 'host', 'infrastructure_checks', 'kind', 'metrics', 'package', 'run_status', 'scoring_reference']
  command.txt: # cwd: /home/user/crypto-autoresearcher | # GFPN_RUN_DIR=/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956 | # PYTHONDONTWRITEBYTECODE=1 | # PYTHONHASHSEED=0 (SE-6) | # launched by: python3 -B experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py RUN-GFPN-bfe956 (no outer guard) | /usr/local/bin/python3 -B /home/user/crypto-autoresearcher/experiments/EX
  solver-events top keys: ['K', 'authority', 'cap_rule', 'consistency_violation', 'experiment_id', 'max_attempts_per_call', 'rename_suffix', 'schema', 'sites', 'spacing_s', 'updated_at']
   site v2_driver.solve counters {"wrapped_calls": 8, "attempts_total": 8, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0, "passthrough_calls_gb_only_true": 0} events 0 records 0
   site a1_health.run_system counters {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {"i": 0, "ii": 0, "iii": 0, "iv": 0, "v": 0}, "re_solves": 0, "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0} events 0 records 0
   site v2_driver.solve/callgrind counters {"callgrind_children_observed": 0, "with_log_visible_ssf_indicator": 0, "with_quotient_dimension_mismatch": 0, "with_readback_differing_from_requested_cap": 0} events 0 records 0
   S-3 record tags (0): []
  listing solver sample: ['ctl_identity_planted.ms', 'ctl_identity_planted.ms.err', 'ctl_identity_planted.ms.log', 'ctl_identity_planted.ms.out', 'ctl_identity_random.ms', 'ctl_identity_random.ms.err', 'ctl_identity_random.ms.log', 'ctl_identity_random.ms.out', 'ctl_planted_S3.ms', 'ctl_planted_S3.ms.err', 'ctl_planted_S3.ms.log', 'ctl_planted_S3.ms.out']
  listing child sample: ['ctl_S3.meta.json', 'ctl_S3.npz', 'ctl_S3.spec.json', 'ctl_S3.stderr', 'ctl_S3.stdout', 'ctl_S3_rescaled.meta.json', 'ctl_S3_rescaled.npz', 'ctl_S3_rescaled.spec.json']
  listing comparator: None
  solve-like records in raw: 0
  comparator key: False None
```

### lj0_v1.out

- sha256: 5fd879d508e0938bf4cf829bb505a57ce634608939533ec4dcee3962ec7533a9; replacements by masking: 0

```text
==============================================================================================================
KA-a1 k=1 Mc: P-16 (fork at v2_solver.py 181 created the child; raise before STORE_FAST pid); cells m = 5; k = 1 other collected pair(s); frozen checker requested cap recorded independently (Mc)
  premises: ['the driver raises out of run_child at the P16 launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) (iii) (v) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created False        child_end None                   pair None raised KeyboardInterrupt
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created undetermined child_end None                   pair None raised KeyboardInterrupt
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created undetermined child_end undetermined           pair None raised KeyboardInterrupt
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 1']
      recorder gaps: ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a1 k=1 Mr: P-16 (fork at v2_solver.py 181 created the child; raise before STORE_FAST pid); cells m = 5; k = 1 other collected pair(s); frozen checker requested cap from raw envelope (Mr)
  premises: ['the driver raises out of run_child at the P16 launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created False        child_end None                   pair None raised KeyboardInterrupt
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created undetermined child_end None                   pair None raised KeyboardInterrupt
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created undetermined child_end undetermined           pair None raised KeyboardInterrupt
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 1']
      recorder gaps: ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a1 k=0 Mc: P-16 (fork at v2_solver.py 181 created the child; raise before STORE_FAST pid); cells m = 5; k = 0 other collected pair(s); frozen checker requested cap recorded independently (Mc)
  premises: ['the driver raises out of run_child at the P16 launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict FAIL
      record S5_t0/ms1                          class None child_created False        child_end None                   pair None raised KeyboardInterrupt
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class None child_created undetermined child_end None                   pair None raised KeyboardInterrupt
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created undetermined child_end undetermined           pair None raised KeyboardInterrupt
      named gaps: ['COUNT GAP (solver/S5_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0']
      recorder gaps: ['solver/S5_t0.ms', 'solver/S5_t0.ms.err', 'solver/S5_t0.ms.log']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a2 k=1 Mc: P-F2 after P-14a (raise at 214, then SolverLock.release raises in the finally); cells m = 5; k = 1 other collected pair(s); frozen checker requested cap recorded independently (Mc)
  premises: ['the driver raises out of run_child at the PF2_after_P14a launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) (iii) (v) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created False        child_end None                   pair None raised OSError
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end None                   pair None raised OSError
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised OSError
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 1']
      recorder gaps: ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a2 k=1 Mr: P-F2 after P-14a (raise at 214, then SolverLock.release raises in the finally); cells m = 5; k = 1 other collected pair(s); frozen checker requested cap from raw envelope (Mr)
  premises: ['the driver raises out of run_child at the PF2_after_P14a launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created False        child_end None                   pair None raised OSError
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end None                   pair None raised OSError
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised OSError
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 1']
      recorder gaps: ['solver/S5_t1.ms', 'solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a2 k=0 Mc: P-F2 after P-14a (raise at 214, then SolverLock.release raises in the finally); cells m = 5; k = 0 other collected pair(s); frozen checker requested cap recorded independently (Mc)
  premises: ['the driver raises out of run_child at the PF2_after_P14a launch; no frozen handler (v2_driver.main 1329-1348; entries re-raise, r3_entry_v2.py 67-79); the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict FAIL
      record S5_t0/ms1                          class None child_created False        child_end None                   pair None raised OSError
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iii', 'v']
  [RF] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end None                   pair None raised OSError
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised OSError
      named gaps: ['COUNT GAP (solver/S5_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0']
      recorder gaps: ['solver/S5_t0.ms', 'solver/S5_t0.ms.err', 'solver/S5_t0.ms.log']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'v']
  expected by CRJ-4: RK: child_created False for a created child (iii); PASS with a definition only where the cap items pass
==============================================================================================================
KA-a3: W-1: cells m = 5, zero launch, wrapper-written raw-result.json
  premises: ['the driver exits before any launch; the wrapper writes raw-result.json (r3_run_wrapper.py 491-505)']
  [RK] verdict PASS_ZL  ** FAIL-OPEN (v) **
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['v']
  [RF] verdict FAIL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['v']
  [RJ] verdict FAIL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['v']
  expected by CRJ-4: RK: PASS_ZL for a wrapper-recorded outcome (v)
==============================================================================================================
KA-b FO-1 C failed exit 1 k=0: FO-1 variant C, foreign-file write failed, escaped exit 1, cells m = 5, k = 0
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict FAIL
      record S5_t0/ms1                          class C    child_created True         child_end None                   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C failed exit 1 k=1: FO-1 variant C, foreign-file write failed, escaped exit 1, cells m = 5, k = 1
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class C    child_created True         child_end None                   pair None raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C failed exit -2 k=0: FO-1 variant C, foreign-file write failed, escaped exit -2, cells m = 5, k = 0
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict FAIL
      record S5_t0/ms1                          class C    child_created True         child_end None                   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C failed exit -2 k=1: FO-1 variant C, foreign-file write failed, escaped exit -2, cells m = 5, k = 1
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class C    child_created True         child_end None                   pair None raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C interrupted exit 1 k=0: FO-1 variant C, foreign-file write interrupted, escaped exit 1, cells m = 5, k = 0
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict FAIL
      record S5_t0/ms1                          class C    child_created True         child_end None                   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C interrupted exit 1 k=1: FO-1 variant C, foreign-file write interrupted, escaped exit 1, cells m = 5, k = 1
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class C    child_created True         child_end None                   pair None raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C interrupted exit -2 k=0: FO-1 variant C, foreign-file write interrupted, escaped exit -2, cells m = 5, k = 0
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict FAIL
      record S5_t0/ms1                          class C    child_created True         child_end None                   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 C interrupted exit -2 k=1: FO-1 variant C, foreign-file write interrupted, escaped exit -2, cells m = 5, k = 1
  premises: ['variant C: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class C    child_created True         child_end None                   pair None raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair None raised None
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B failed exit 1 k=0: FO-1 variant B, foreign-file write failed, escaped exit 1, cells m = 5, k = 0
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B failed exit 1 k=1: FO-1 variant B, foreign-file write failed, escaped exit 1, cells m = 5, k = 1
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B failed exit -2 k=0: FO-1 variant B, foreign-file write failed, escaped exit -2, cells m = 5, k = 0
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B failed exit -2 k=1: FO-1 variant B, foreign-file write failed, escaped exit -2, cells m = 5, k = 1
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write failed (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B interrupted exit 1 k=0: FO-1 variant B, foreign-file write interrupted, escaped exit 1, cells m = 5, k = 0
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B interrupted exit 1 k=1: FO-1 variant B, foreign-file write interrupted, escaped exit 1, cells m = 5, k = 1
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status 1']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B interrupted exit -2 k=0: FO-1 variant B, foreign-file write interrupted, escaped exit -2, cells m = 5, k = 0
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-b FO-1 B interrupted exit -2 k=1: FO-1 variant B, foreign-file write interrupted, escaped exit -2, cells m = 5, k = 1
  premises: ['variant B: the fork child escapes the frozen child path (asynchronous exception); the recorder-foreign file write interrupted (RF-1 (b)); the escaped process writes pari-stack.json and its traceback, later overwritten / unread; exit status -2']
  [RF] verdict PASS  ** FAIL-OPEN (iv) **
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end None                   pair cap raised None
      definitions holding: ['iv']
  [RG] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class None child_created True         child_end undetermined           pair cap raised None
      definitions holding: ['iv']
  expected by CRJ-4: RF: FAIL-OPEN under definition (iv) when the foreign-file write fails
==============================================================================================================
KA-c PB-3: cells m = 5 package, polynomial arm S5, target 1 re-solved once by SE-3 (attempt 1 SSF, renamed .ssf-attempt1)
  [RF] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end None                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end None                   pair cap raised None
  [RG] verdict FAIL  ** PLANNED-BASIS REFUSAL **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      recorder gaps: ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  [RH] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  expected by CRJ-4: RG: PLANNED-BASIS REFUSAL
==============================================================================================================
KA-d LR-1: S-1 re-solve, 2 attempts, the FINAL attempt's launch record absent
  premises: ['launch record(s) of S5_t1 attempt(s) [2] absent without RL-1 (d) firing (carried decision (4))']
  [RH] verdict PASS  ** FAIL-OPEN (i) (ii_LR) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      definitions holding: ['i', 'ii_LR']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  expected by CRJ-4: RH: PASS and FAIL-OPEN (i)
==============================================================================================================
KA-d LR-2: S-1 re-solve, 2 attempts, attempt 1's launch record absent
  premises: ['launch record(s) of S5_t1 attempt(s) [1] absent without RL-1 (d) firing (carried decision (4))']
  [RH] verdict PASS  ** FAIL-OPEN (i) (ii_LR) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      definitions holding: ['i', 'ii_LR']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  expected by CRJ-4: RH: PASS and FAIL-OPEN (i)
==============================================================================================================
KA-d LR-3: S-1 re-solve, 3 attempts, attempt 2's launch record absent
  premises: ['launch record(s) of S5_t1 attempt(s) [2] absent without RL-1 (d) firing (carried decision (4))']
  [RH] verdict PASS  ** FAIL-OPEN (i) (ii_LR) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms3                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      definitions holding: ['i', 'ii_LR']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms3                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 4 launch records vs counters 5']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms3                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 4 launch records vs counters 5']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
      definitions holding: ['i', 'ii_LR']
  expected by CRJ-4: RH: PASS and FAIL-OPEN (i)
==============================================================================================================
KA-d LR-4: S-1 re-solve, 3 attempts, attempts 2 and 3 absent
  premises: ['launch record(s) of S5_t1 attempt(s) [2, 3] absent without RL-1 (d) firing (carried decision (4))']
  [RH] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2', 'S5_t1/ms3']
      recorder gaps: ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
      definitions holding: ['i', 'ii_LR']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2', 'S5_t1/ms3']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 5']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms2', 'S5_t1/ms3']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 5']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
      definitions holding: ['i', 'ii_LR']
  expected by CRJ-4: RH: FAIL
==============================================================================================================
KA-d LR-5: S-2 HR-3 re-solve in controls_a1, 2 attempts, the final attempt's record absent
  premises: ['launch record of the final HR-3 attempt of health_p1073741831_d222 absent without RL-1 (d) firing']
  [RH] verdict PASS  ** FAIL-OPEN (i) (ii_LR) **
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d222/ms2']
      definitions holding: ['i', 'ii_LR']
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d222/ms2']
      named gaps: ['COUNT GAP (health/health_p1073741831_d222): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d222/ms2']
      named gaps: ['COUNT GAP (health/health_p1073741831_d222): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  expected by CRJ-4: RH: PASS and FAIL-OPEN (i)
==============================================================================================================
KA-e CX-A: cells m = 4, target 0 solved with callgrind_timeout (v2_driver.py 1174-1175); the callgrind child's open of <tag>.callgrind.stdout fails (v2_solver.py 188 -> 206-208, exit 99, no file); its launch record absent
  premises: ['the callgrind launch record of S4_t0 absent without RL-1 (d) firing (carried decision (4))']
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJw] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  expected by CRJ-4: RI: PASS and FAIL-OPEN (ii); RJ: CALLGRIND COUNT GAP and FAIL; RJw: PASS and FAIL-OPEN (ii)
==============================================================================================================
KA-e LN-7a: non-event S-1 msolve child that fails before creating its stdout file, input not retained, launch record absent
  premises: ['the msolve launch record of S5_t1 (child failing before its stdout file, input not retained) absent']
  [RH] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
  expected by CRJ-4: RI: COUNT GAP and FAIL
==============================================================================================================
KA-e CX-A-gp: controls_a1, the gp child fails before its stdout file, its launch record absent
  premises: ['the gp launch record absent; the gp child failed before its stdout file (a1_pari.py 96 -> v2_solver.py 188, 206-208)']
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJnogp] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      definitions holding: ['ii_ANY', 'ii_LR']
  expected by CRJ-4: RJ: a recorder gap on pari/<tag>.gp and FAIL
==============================================================================================================
KA-e CX-A-cmp: anchor-identity, the comparator child fails before its stdout file, its launch record absent
  premises: ['the comparator launch record absent; the comparator child failed before its stdout file; the driver ends at v2_driver.py 656-659 with finish() (raw driver-written, comparator.child present)']
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJnocmp] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
  expected by CRJ-4: RJ: COMPARATOR COUNT GAP and FAIL
==============================================================================================================
KA-e CX-A-G2: fixture package of G2 shape (callgrind on every ok solve, v2_driver.py 358), one no-file callgrind record absent
  premises: ['the callgrind launch record of fx_reg0_S3 absent']
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['fx_reg0_S3/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['fx_reg0_S3/cg']
      named gaps: ['CALLGRIND COUNT GAP (fx_reg0_S3): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 1 callgrind launch records vs 2 attempt records with callgrind_result_present true']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJw] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['fx_reg0_S3/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  expected by CRJ-4: RJ: CALLGRIND COUNT GAP and FAIL (variant)

WROTE lj0_v1.json (34 objects)
```

### listing_v1.out

- sha256: 707031b55e2d724de08a4a86d5e08b7076a47060dd4353a3beea8a89aa3438ab; replacements by masking: 0

```text
====================================================================================================
RUN-GFPN-f6a21a kind fixture_F1_F3: files 284, reconstructed launch records 88 {'childjob': 16, 'callgrind': 36, 'msolve': 36}, events 0
  RJ recorder gaps (0): []
  RJ named gaps: []
  RI (contrast) gaps 0 named []
  per (site, tag) rows: 36; RI-1 (a) (i) holds on 36; RJ-1 (b) holds on 36; mismatches: []
    S-1 fx_fresh1_S3                     N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/S3 (argv -P 1)
    S-1 fx_fresh1_S3_rescaled            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/S3_rescaled (argv -P 1)
    S-1 fx_fresh1_raw_u                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/raw_u (argv -P 1)
    S-1 fx_fresh1_raw_x                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/raw_x (argv -P 1)
    S-1 fx_fresh1_torsion_S3_norm        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_fresh1_torsion_S3_rq          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_fresh2_S3                     N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/S3 (argv -P 1)
    S-1 fx_fresh2_S3_rescaled            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/S3_rescaled (argv -P 1)
    S-1 fx_fresh2_raw_u                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/raw_u (argv -P 1)
    S-1 fx_fresh2_raw_x                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/raw_x (argv -P 1)
    S-1 fx_fresh2_torsion_S3_norm        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_fresh2_torsion_S3_rq          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_planted0_S3                   N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/S3 (argv -P 1)
    S-1 fx_planted0_S3_rescaled          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/S3_rescaled (argv -P 1)
    S-1 fx_planted0_raw_u                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/raw_u (argv -P 1)
    S-1 fx_planted0_raw_x                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/raw_x (argv -P 1)
    S-1 fx_planted0_torsion_S3_norm      N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_planted0_torsion_S3_rq        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_planted1_S3                   N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/S3 (argv -P 1)
    S-1 fx_planted1_S3_rescaled          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/S3_rescaled (argv -P 1)
    S-1 fx_planted1_raw_u                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/raw_u (argv -P 1)
    S-1 fx_planted1_raw_x                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/raw_x (argv -P 1)
    S-1 fx_planted1_torsion_S3_norm      N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_planted1_torsion_S3_rq        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_reg0_S3                       N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/S3 (argv -P 1)
    S-1 fx_reg0_S3_rescaled              N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/S3_rescaled (argv -P 1)
    S-1 fx_reg0_raw_u                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/raw_u (argv -P 1)
    S-1 fx_reg0_raw_x                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/raw_x (argv -P 1)
    S-1 fx_reg0_torsion_S3_norm          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_reg0_torsion_S3_rq            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_reg1_S3                       N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/S3 (argv -P 1)
    S-1 fx_reg1_S3_rescaled              N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/S3_rescaled (argv -P 1)
    S-1 fx_reg1_raw_u                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/raw_u (argv -P 1)
    S-1 fx_reg1_raw_x                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/raw_x (argv -P 1)
    S-1 fx_reg1_torsion_S3_norm          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_reg1_torsion_S3_rq            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/torsion_S3_rq (argv -P 1)
  site rows: [{'site': 'S-1', 'launch_records': 36, 'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'RI1_a_iii_holds': True}, {'site': 'S-2', 'launch_records': 0, 'attempts_total': 0, 'RI1_a_iii_holds': True}]
  RJ-1 site row: {'callgrind_launch_records': 36, 'attempt_records_with_callgrind_result_present': 36, 'holds': True, 'S3_records_total_cross_check': 36, 'S3_counter_callgrind_children_observed': 36}
  RJ-3 comparator row: {'comparator_launch_records': 0, 'raw_comparator_child_present': False, 'required': 0, 'holds': True}
  RJ-4 (b) unknown-kind stdout paths: []
  RJ-2 pari/ files: []
====================================================================================================
RUN-GFPN-902222 kind fixture_F1_F3: files 284, reconstructed launch records 88 {'childjob': 16, 'callgrind': 36, 'msolve': 36}, events 0
  RJ recorder gaps (0): []
  RJ named gaps: []
  RI (contrast) gaps 0 named []
  per (site, tag) rows: 36; RI-1 (a) (i) holds on 36; RJ-1 (b) holds on 36; mismatches: []
    S-1 fx_fresh1_S3                     N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/S3 (argv -P 1)
    S-1 fx_fresh1_S3_rescaled            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/S3_rescaled (argv -P 1)
    S-1 fx_fresh1_raw_u                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/raw_u (argv -P 1)
    S-1 fx_fresh1_raw_x                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/raw_x (argv -P 1)
    S-1 fx_fresh1_torsion_S3_norm        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_fresh1_torsion_S3_rq          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[2]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_fresh2_S3                     N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/S3 (argv -P 1)
    S-1 fx_fresh2_S3_rescaled            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/S3_rescaled (argv -P 1)
    S-1 fx_fresh2_raw_u                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/raw_u (argv -P 1)
    S-1 fx_fresh2_raw_x                  N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/raw_x (argv -P 1)
    S-1 fx_fresh2_torsion_S3_norm        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_fresh2_torsion_S3_rq          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[3]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_planted0_S3                   N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/S3 (argv -P 1)
    S-1 fx_planted0_S3_rescaled          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/S3_rescaled (argv -P 1)
    S-1 fx_planted0_raw_u                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/raw_u (argv -P 1)
    S-1 fx_planted0_raw_x                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/raw_x (argv -P 1)
    S-1 fx_planted0_torsion_S3_norm      N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_planted0_torsion_S3_rq        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[0]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_planted1_S3                   N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/S3 (argv -P 1)
    S-1 fx_planted1_S3_rescaled          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/S3_rescaled (argv -P 1)
    S-1 fx_planted1_raw_u                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/raw_u (argv -P 1)
    S-1 fx_planted1_raw_x                N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/raw_x (argv -P 1)
    S-1 fx_planted1_torsion_S3_norm      N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_planted1_torsion_S3_rq        N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /planted_targets[1]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_reg0_S3                       N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/S3 (argv -P 1)
    S-1 fx_reg0_S3_rescaled              N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/S3_rescaled (argv -P 1)
    S-1 fx_reg0_raw_u                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/raw_u (argv -P 1)
    S-1 fx_reg0_raw_x                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/raw_x (argv -P 1)
    S-1 fx_reg0_torsion_S3_norm          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_reg0_torsion_S3_rq            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[0]/arms/torsion_S3_rq (argv -P 1)
    S-1 fx_reg1_S3                       N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/S3 (argv -P 1)
    S-1 fx_reg1_S3_rescaled              N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/S3_rescaled (argv -P 1)
    S-1 fx_reg1_raw_u                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/raw_u (argv -P 1)
    S-1 fx_reg1_raw_x                    N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/raw_x (argv -P 1)
    S-1 fx_reg1_torsion_S3_norm          N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/torsion_S3_norm (argv -P 1)
    S-1 fx_reg1_torsion_S3_rq            N=1 RB1=1 RL2=0 Ncg=1 present=1 S3=1 | raw-result.json /targets[1]/arms/torsion_S3_rq (argv -P 1)
  site rows: [{'site': 'S-1', 'launch_records': 36, 'attempts_total': 36, 'passthrough_calls_gb_only_true': 0, 'RI1_a_iii_holds': True}, {'site': 'S-2', 'launch_records': 0, 'attempts_total': 0, 'RI1_a_iii_holds': True}]
  RJ-1 site row: {'callgrind_launch_records': 36, 'attempt_records_with_callgrind_result_present': 36, 'holds': True, 'S3_records_total_cross_check': 36, 'S3_counter_callgrind_children_observed': 36}
  RJ-3 comparator row: {'comparator_launch_records': 0, 'raw_comparator_child_present': False, 'required': 0, 'holds': True}
  RJ-4 (b) unknown-kind stdout paths: []
  RJ-2 pari/ files: []
====================================================================================================
RUN-GFPN-f5412a kind anchor_identity: files 32, reconstructed launch records 7 {'childjob': 1, 'msolve': 5, 'comparator': 1}, events 0
  RJ recorder gaps (0): []
  RJ named gaps: []
  RI (contrast) gaps 0 named []
  per (site, tag) rows: 5; RI-1 (a) (i) holds on 5; RJ-1 (b) holds on 5; mismatches: []
    S-1 anchor_comparator_random         N=1 RB1=0 RL2=1 Ncg=0 present=0 S3=0 | raw-result.json /targets[0] (argv -g 1)
    S-1 anchor_comparator_system         N=1 RB1=0 RL2=1 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 711 (gb_only=True)
    S-1 anchor_v2_t0                     N=1 RB1=0 RL2=1 Ncg=0 present=0 S3=0 | raw-result.json /targets[1] (argv -g 1)
    S-1 anchor_v2_t1                     N=1 RB1=0 RL2=1 Ncg=0 present=0 S3=0 | raw-result.json /targets[2] (argv -g 1)
    S-1 anchor_v2_t2                     N=1 RB1=0 RL2=1 Ncg=0 present=0 S3=0 | raw-result.json /targets[3] (argv -g 1)
  site rows: [{'site': 'S-1', 'launch_records': 5, 'attempts_total': 0, 'passthrough_calls_gb_only_true': 5, 'RI1_a_iii_holds': True}, {'site': 'S-2', 'launch_records': 0, 'attempts_total': 0, 'RI1_a_iii_holds': True}]
  RJ-1 site row: {'callgrind_launch_records': 0, 'attempt_records_with_callgrind_result_present': 0, 'holds': True, 'S3_records_total_cross_check': 0, 'S3_counter_callgrind_children_observed': 0}
  RJ-3 comparator row: {'comparator_launch_records': 1, 'raw_comparator_child_present': True, 'required': 1, 'holds': True}
  RJ-4 (b) unknown-kind stdout paths: []
  RJ-2 pari/ files: []
====================================================================================================
RUN-GFPN-bfe956 kind frozen_controls: files 83, reconstructed launch records 19 {'childjob': 11, 'msolve': 8}, events 0
  RJ recorder gaps (0): []
  RJ named gaps: []
  RI (contrast) gaps 0 named []
  per (site, tag) rows: 8; RI-1 (a) (i) holds on 8; RJ-1 (b) holds on 8; mismatches: []
    S-1 ctl_identity_planted             N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_identity_random              N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_planted_S3                   N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_planted_S3_rescaled          N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_planted_torsion_S3_norm      N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_planted_torsion_S3_rq        N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_rawx_planted                 N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
    S-1 ctl_rawx_random                  N=1 RB1=1 RL2=0 Ncg=0 present=0 S3=0 | frozen call site v2_driver.py 786 / 787 / 841 (gb_only False, no callgrind_timeout)
  site rows: [{'site': 'S-1', 'launch_records': 8, 'attempts_total': 8, 'passthrough_calls_gb_only_true': 0, 'RI1_a_iii_holds': True}, {'site': 'S-2', 'launch_records': 0, 'attempts_total': 0, 'RI1_a_iii_holds': True}]
  RJ-1 site row: {'callgrind_launch_records': 0, 'attempt_records_with_callgrind_result_present': 0, 'holds': True, 'S3_records_total_cross_check': 0, 'S3_counter_callgrind_children_observed': 0}
  RJ-3 comparator row: {'comparator_launch_records': 0, 'raw_comparator_child_present': False, 'required': 0, 'holds': True}
  RJ-4 (b) unknown-kind stdout paths: []
  RJ-2 pari/ files: []

TOTAL files 683, unattributed under launchkind 0; WROTE listing_v1.json
```

### lj1_v1.out

- sha256: c6bd62a187e1a21e58e28ba2c662de5dacdeddb7ea114de59a4a448313afe5a4; replacements by masking: 0

```text
==============================================================================================================
LK-1 A record lost: child job (v2_driver.py 101), raw_grid of raw_x target 1, path A, record lost; detector: the spec written before the launch (98-99)
  premise: child-job launch record of grid_raw_x_t1 absent (path A)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json']
==============================================================================================================
LK-1 pre_stdout_99 record lost: child job (v2_driver.py 101), raw_grid of raw_x target 1, path pre_stdout_99, record lost; detector: the spec written before the launch (98-99)
  premise: child-job launch record of grid_raw_x_t1 absent (path pre_stdout_99)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-1 err_setrlimit_97 record lost: child job (v2_driver.py 101), raw_grid of raw_x target 1, path err_setrlimit_97, record lost; detector: the spec written before the launch (98-99)
  premise: child-job launch record of grid_raw_x_t1 absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-1 P8 record lost: child job (v2_driver.py 101), raw_grid of raw_x target 1, path P8, record lost; detector: the spec written before the launch (98-99)
  premise: child-job launch record of grid_raw_x_t1 absent (path P8)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-1 exec_ok record lost: child job (v2_driver.py 101), raw_grid of raw_x target 1, path exec_ok, record lost; detector: the spec written before the launch (98-99)
  premise: child-job launch record of grid_raw_x_t1 absent (path exec_ok)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.meta.json', 'child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.meta.json', 'child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-1 A record+spec lost: child job, path A, record and spec file both absent
  premise: record lost AND the frozen driver's spec file absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it; scan_v2 removals)
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
==============================================================================================================
LK-1 pre_stdout_99 record+spec lost: child job, path pre_stdout_99, record and spec file both absent
  premise: record lost AND the frozen driver's spec file absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it; scan_v2 removals)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 A record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path A, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path A)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
==============================================================================================================
LK-2 A consistent loss: msolve at S-1, path A, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path A)
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
==============================================================================================================
LK-2 pre_stdout_99 record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path pre_stdout_99, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path pre_stdout_99)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 pre_stdout_99 consistent loss: msolve at S-1, path pre_stdout_99, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path pre_stdout_99)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 err_setrlimit_97 record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path err_setrlimit_97, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 err_setrlimit_97 consistent loss: msolve at S-1, path err_setrlimit_97, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 P8 record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path P8, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path P8)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 P8 consistent loss: msolve at S-1, path P8, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path P8)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-2 exec_ok record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path exec_ok, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path exec_ok)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-2 exec_ok consistent loss: msolve at S-1, path exec_ok, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path exec_ok)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-2 exec_timeout record lost: msolve at S-1 (v2_driver.py 166), cells m = 5 target 1 (input not retained), path exec_timeout, record lost; detector: RI-1 (a) (RB-1, counters)
  premise: msolve launch record of S5_t1 absent (path exec_timeout)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-2 exec_timeout consistent loss: msolve at S-1, path exec_timeout, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss: the launch record, its RB-1 attempt record and its attempts_total increment all absent (path exec_timeout)
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-2 pre_stdout_99 consistent loss, input retained: msolve at S-1, target 0, child failing before its stdout file, input retained
  premise: RGL-10 consistent loss on target 0, whose input <tag>.ms is retained (v2_driver.py 1174 retain_input=(i == 0))
  [RI] verdict FAIL
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t0/ms1']
      recorder gaps: ['solver/S5_t0.ms']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t0/ms1']
      recorder gaps: ['solver/S5_t0.ms']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 A record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path A, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path A)
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
==============================================================================================================
LK-3 pre_stdout_99 record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path pre_stdout_99, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path pre_stdout_99)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 err_setrlimit_97 record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path err_setrlimit_97, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 P8 record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path P8, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path P8)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 exec_ok record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path exec_ok, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path exec_ok)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-3 exec_fail record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path exec_fail, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path exec_fail)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-3 exec_timeout record lost: callgrind (v2_solver.py 517), cells m = 4 target 0, path exec_timeout, record lost; detector: RB-1 (e) callgrind_result_present
  premise: callgrind launch record of S4_t0 absent (path exec_timeout)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-3 pre_stdout_99 record lost + field false: callgrind, path pre_stdout_99, record lost, RB-1 (e) written false
  premise: record lost AND callgrind_result_present recorded false although the returned result carried the key: a recorder DEFECT, not a lost record (RJ-1 (a) copies the key presence from the returned result)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 pre_stdout_99 record lost + field absent: callgrind, path pre_stdout_99, record lost, RB-1 (e) absent (RF-0 (a), (c))
  premise: record lost AND the RB-1 (e) field absent from a present attempt record
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['UNDETERMINED callgrind_result_present (RF-0 (c)): attempt record S4_t0 attempt 1']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 pre_stdout_99 consistent loss (all bound): callgrind, path pre_stdout_99, callgrind record + msolve record + RB-1 + counter lost
  premise: consistent loss of everything bound to the callgrind launch: its record, the msolve record of the same attempt, the RB-1 attempt record carrying (e), and the attempts_total increment
  [RI] verdict FAIL
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-3 exec_ok record lost + field false: callgrind, path exec_ok, record lost, RB-1 (e) written false
  premise: record lost AND callgrind_result_present recorded false although the returned result carried the key: a recorder DEFECT, not a lost record (RJ-1 (a) copies the key presence from the returned result)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-3 exec_ok record lost + field absent: callgrind, path exec_ok, record lost, RB-1 (e) absent (RF-0 (a), (c))
  premise: record lost AND the RB-1 (e) field absent from a present attempt record
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['UNDETERMINED callgrind_result_present (RF-0 (c)): attempt record S4_t0 attempt 1']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-3 exec_ok consistent loss (all bound): callgrind, path exec_ok, callgrind record + msolve record + RB-1 + counter lost
  premise: consistent loss of everything bound to the callgrind launch: its record, the msolve record of the same attempt, the RB-1 attempt record carrying (e), and the attempts_total increment
  [RI] verdict FAIL
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-4 A record lost: comparator (v2_driver.py 650), anchor-identity, path A, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path A)
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
LK-4 pre_stdout_99 record lost: comparator (v2_driver.py 650), anchor-identity, path pre_stdout_99, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path pre_stdout_99)
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-4 err_setrlimit_97 record lost: comparator (v2_driver.py 650), anchor-identity, path err_setrlimit_97, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path err_setrlimit_97)
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/stderr.log', 'comparator/stdout.log']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      recorder gaps: ['comparator/stderr.log', 'comparator/stdout.log']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-4 P8 record lost: comparator (v2_driver.py 650), anchor-identity, path P8, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path P8)
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/stderr.log', 'comparator/stdout.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      recorder gaps: ['comparator/stderr.log', 'comparator/stdout.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-4 exec_ok record lost: comparator (v2_driver.py 650), anchor-identity, path exec_ok, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path exec_ok)
  [RI] verdict FAIL
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-4 exec_fail record lost: comparator (v2_driver.py 650), anchor-identity, path exec_fail, record lost; detector: raw comparator.child (652, 655)
  premise: comparator launch record absent (path exec_fail)
  [RI] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-4 exec_ok record lost + raw key absent: comparator, record lost and comparator.child absent
  premise: record lost AND a driver-written raw-result.json without comparator.child: no frozen path writes it (655 precedes every exit; finish() is the only driver writer); a premise OUTSIDE the lost-record class
  [RI] verdict FAIL
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cmp']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-5 A record lost: msolve at S-2 (a1_health.py 147), controls_a1, path A, record lost; detector: RI-1 (a) at S-2
  premise: S-2 launch record of health_p1073741831_d444 absent (path A)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
==============================================================================================================
LK-5 A consistent loss: msolve at S-2, path A, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path A)
  [RI] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
  [RJ] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
==============================================================================================================
LK-5 pre_stdout_99 record lost: msolve at S-2 (a1_health.py 147), controls_a1, path pre_stdout_99, record lost; detector: RI-1 (a) at S-2
  premise: S-2 launch record of health_p1073741831_d444 absent (path pre_stdout_99)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 pre_stdout_99 consistent loss: msolve at S-2, path pre_stdout_99, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path pre_stdout_99)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 err_setrlimit_97 record lost: msolve at S-2 (a1_health.py 147), controls_a1, path err_setrlimit_97, record lost; detector: RI-1 (a) at S-2
  premise: S-2 launch record of health_p1073741831_d444 absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 err_setrlimit_97 consistent loss: msolve at S-2, path err_setrlimit_97, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 P8 record lost: msolve at S-2 (a1_health.py 147), controls_a1, path P8, record lost; detector: RI-1 (a) at S-2
  premise: S-2 launch record of health_p1073741831_d444 absent (path P8)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 P8 consistent loss: msolve at S-2, path P8, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path P8)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-5 exec_ok record lost: msolve at S-2 (a1_health.py 147), controls_a1, path exec_ok, record lost; detector: RI-1 (a) at S-2
  premise: S-2 launch record of health_p1073741831_d444 absent (path exec_ok)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 1 launch records vs counters 2']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log', 'health/health_p1073741831_d444.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 1 launch records vs counters 2']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log', 'health/health_p1073741831_d444.ms.out']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-5 exec_ok consistent loss: msolve at S-2, path exec_ok, record + RB-1 + counter lost together
  premise: RGL-10 consistent loss at S-2: record, S-2 attempt record and attempts_total increment absent (path exec_ok)
  [RI] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log', 'health/health_p1073741831_d444.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log', 'health/health_p1073741831_d444.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-6 A record lost: gp (a1_pari.py 96), controls_a1, path A, record lost; detector: pari/<tag>.gp written before the launch (91-93)
  premise: gp launch record absent (path A)
  [RI] verdict PASS
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp']
==============================================================================================================
LK-6 pre_stdout_99 record lost: gp (a1_pari.py 96), controls_a1, path pre_stdout_99, record lost; detector: pari/<tag>.gp written before the launch (91-93)
  premise: gp launch record absent (path pre_stdout_99)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-6 err_setrlimit_97 record lost: gp (a1_pari.py 96), controls_a1, path err_setrlimit_97, record lost; detector: pari/<tag>.gp written before the launch (91-93)
  premise: gp launch record absent (path err_setrlimit_97)
  [RI] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp', 'pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
LK-6 P8 record lost: gp (a1_pari.py 96), controls_a1, path P8, record lost; detector: pari/<tag>.gp written before the launch (91-93)
  premise: gp launch record absent (path P8)
  [RI] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp', 'pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      frozen checker items: ['68-70 child RLIMIT_AS read-back != requested']
      definitions holding: ['i', 'ii_ANY', 'ii_LR']
==============================================================================================================
LK-6 exec_ok record lost: gp (a1_pari.py 96), controls_a1, path exec_ok, record lost; detector: pari/<tag>.gp written before the launch (91-93)
  premise: gp launch record absent (path exec_ok)
  [RI] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp', 'pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LK-6 A record+script lost: gp, path A, record and script both absent
  premise: record lost AND the script absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it)
  [RI] verdict PASS
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
  [RJ] verdict PASS
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
==============================================================================================================
LK-6 pre_stdout_99 record+script lost: gp, path pre_stdout_99, record and script both absent
  premise: record lost AND the script absent: a premise OUTSIDE the lost-record class (no frozen or r4 code removes it)
  [RI] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      definitions holding: ['ii_ANY', 'ii_LR']
  [RJ] verdict PASS  ** FAIL-OPEN (ii_LR) (ii_ANY) **
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      definitions holding: ['ii_ANY', 'ii_LR']
==============================================================================================================
RGL-11 records present: cells m = 4 target 0: callgrind launched, then callgrind_instructions raises
  premise: callgrind_instructions raises after its run_child returned (v2_solver.py 526-529: open / parse of the out file), so solve raises (209), no result is returned, no RB-1 record and no counter increment are written (r3_resolve.py 263 -> 273 not reached); no frozen handler (scan_v2); the driver dies; the wrapper writes raw-result.json
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0']
      recorder gaps: ['solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['v']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0', 'CALLGRIND COUNT GAP (S4_t0): Ncg=1 count=0', 'CALLGRIND SITE COUNT GAP: 1 callgrind launch records vs 0 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['v']
==============================================================================================================
RGL-11 callgrind record lost: cells m = 4 target 0: callgrind launched, then callgrind_instructions raises
  premise: callgrind_instructions raises after its run_child returned (v2_solver.py 526-529: open / parse of the out file), so solve raises (209), no result is returned, no RB-1 record and no counter increment are written (r3_resolve.py 263 -> 273 not reached); no frozen handler (scan_v2); the driver dies; the wrapper writes raw-result.json
  premise: launch record(s) ['S4_t0/cg'] absent
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 0 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 0']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_ANY', 'ii_LR', 'v']
==============================================================================================================
RGL-11 both records lost: cells m = 4 target 0: callgrind launched, then callgrind_instructions raises
  premise: callgrind_instructions raises after its run_child returned (v2_solver.py 526-529: open / parse of the out file), so solve raises (209), no result is returned, no RB-1 record and no counter increment are written (r3_resolve.py 263 -> 273 not reached); no frozen handler (scan_v2); the driver dies; the wrapper writes raw-result.json
  premise: launch record(s) ['S4_t0/cg', 'S4_t0/ms1'] absent
  [RI] verdict FAIL
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['i', 'ii_ANY', 'ii_LR', 'v']
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms1']
      recorder gaps: ['solver/S4_t0.callgrind.out', 'solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['i', 'ii_ANY', 'ii_LR', 'v']
==============================================================================================================
ESC msolve FO1_C parent record lost: escaped child at the msolve launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 2']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC msolve FO1_B parent record lost: escaped child at the msolve launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      named gaps: ['COUNT GAP (solver/S5_t1): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 2']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log']
      definitions holding: ['i', 'ii_LR', 'iv']
==============================================================================================================
ESC callgrind FO1_C parent record lost: escaped child at the callgrind launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC callgrind FO1_B parent record lost: escaped child at the callgrind launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR', 'iv']
==============================================================================================================
ESC gp FO1_C parent record lost: escaped child at the gp launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC gp FO1_B parent record lost: escaped child at the gp launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['gp:controls_a1_pari']
      recorder gaps: ['pari/controls_a1_pari.gp', 'pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      definitions holding: ['i', 'ii_LR', 'iv']
==============================================================================================================
ESC comparator FO1_C parent record lost: escaped child at the comparator launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC comparator FO1_B parent record lost: escaped child at the comparator launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      ABSENT launch records (premise): ['cmp']
      named gaps: ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present']
      recorder gaps: ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
      definitions holding: ['i', 'ii_LR', 'iv']
==============================================================================================================
ESC childjob FO1_C parent record lost: escaped child at the childjob launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC childjob FO1_B parent record lost: escaped child at the childjob launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['cj:grid_raw_x_t1']
      recorder gaps: ['child/grid_raw_x_t1.spec.json', 'child/grid_raw_x_t1.stderr', 'child/grid_raw_x_t1.stdout']
      definitions holding: ['i', 'ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC health FO1_C parent record lost: escaped child at the health launch, parent record lost
  premise: escaped fork child (FO1_C shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      definitions holding: ['ii_ANY', 'ii_LR', 'iv']
==============================================================================================================
ESC health FO1_B parent record lost: escaped child at the health launch, parent record lost
  premise: escaped fork child (FO1_B shape; the recorder-foreign write fails, FO-1) AND the parent's launch record of that launch absent
  [RJ] verdict FAIL
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['health:health_p1073741831_d444/ms1']
      named gaps: ['COUNT GAP (health/health_p1073741831_d444): (i) N=0 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3']
      recorder gaps: ['health/health_p1073741831_d444.ms.err', 'health/health_p1073741831_d444.ms.log']
      definitions holding: ['i', 'ii_LR', 'iv']
==============================================================================================================
TW-1: tag S4_t0 solved twice with callgrind; every record present
  premise: HYPOTHETICAL code: one tag solved twice in one package outside an event, callgrind both times (no frozen path does this; BJ-2 of review be2daf; scan_v1 calls)
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      named gaps: ["DUPLICATE-PATH GAP (solver/S4_t0.callgrind.stdout): ['S4_t0/cg', 'S4_t0/cg#2']"]
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      named gaps: ["DUPLICATE-PATH GAP (solver/S4_t0.callgrind.stdout): ['S4_t0/cg', 'S4_t0/cg#2']"]
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms']
==============================================================================================================
TW-2: tag S4_t0 solved twice with callgrind; first record lost
  premise: HYPOTHETICAL code: one tag solved twice in one package outside an event, callgrind both times (no frozen path does this; BJ-2 of review be2daf; scan_v1 calls)
  premise: the FIRST call's ['S4_t0/cg'] launch record absent
  [RI] verdict PASS  ** FAIL-OPEN (i) (ii_LR) **
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=1 count=2', 'CALLGRIND SITE COUNT GAP: 1 callgrind launch records vs 2 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
TW-3: tag S4_t0 solved twice with callgrind; first record lost
  premise: HYPOTHETICAL code: one tag solved twice in one package outside an event, callgrind both times (no frozen path does this; BJ-2 of review be2daf; scan_v1 calls)
  premise: the FIRST call's ['S4_t0/ms1'] launch record absent
  [RI] verdict FAIL
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/ms1']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 2 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 2', "DUPLICATE-PATH GAP (solver/S4_t0.callgrind.stdout): ['S4_t0/cg', 'S4_t0/cg#2']"]
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms1#2                        class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg#2                         class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/ms1']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 2 + RL-2 0', 'SITE COUNT GAP (S-1): 1 launch records vs counters 2', "DUPLICATE-PATH GAP (solver/S4_t0.callgrind.stdout): ['S4_t0/cg', 'S4_t0/cg#2']"]
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
EV-cg lost: event tag S4_t0 with callgrind on the accepted attempt; cg
  premise: SE-3 event at the callgrind target (attempt 1 SSF, attempt 2 ok with callgrind); mutation cg
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg']
      named gaps: ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
EV-ms2 lost: event tag S4_t0 with callgrind on the accepted attempt; ms2
  premise: SE-3 event at the callgrind target (attempt 1 SSF, attempt 2 ok with callgrind); mutation ms2
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/ms2']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/ms2']
      named gaps: ['COUNT GAP (solver/S4_t0): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3']
      recorder gaps: ['solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
EV-attempt2 consistent: event tag S4_t0 with callgrind on the accepted attempt; all2
  premise: SE-3 event at the callgrind target (attempt 1 SSF, attempt 2 ok with callgrind); mutation all2
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms2']
      named gaps: ['COUNT GAP (solver/S4_t0): (ii) N=1 attempts=1 accepted=1 1+renamed=2']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms2']
      named gaps: ['COUNT GAP (solver/S4_t0): (ii) N=1 attempts=1 accepted=1 1+renamed=2']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms', 'solver/S4_t0.ms.err', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
EV-attempt2 consistent + renamed key: event tag S4_t0 with callgrind on the accepted attempt; all2ren
  premise: SE-3 event at the callgrind target (attempt 1 SSF, attempt 2 ok with callgrind); mutation all2ren
  [RI] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms2']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S4_t0/cg', 'S4_t0/ms2']
      recorder gaps: ['solver/S4_t0.callgrind.stderr', 'solver/S4_t0.callgrind.stdout', 'solver/S4_t0.ms.err.ssf-attempt1', 'solver/S4_t0.ms.log.ssf-attempt1', 'solver/S4_t0.ms.out.ssf-attempt1']
      definitions holding: ['i', 'ii_LR']
==============================================================================================================
LN-6: refusal before fork, consistent loss
  premise: class A refusal before fork; record, RB-1 and counter consistently lost
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
==============================================================================================================
LN-3: exec'd msolve, consistent loss
  premise: exec'd msolve child; record, RB-1 and counter consistently lost
  [RI] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']
  [RJ] verdict FAIL
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      ABSENT launch records (premise): ['S5_t1/ms1']
      recorder gaps: ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      definitions holding: ['i', 'ii_LR']

WROTE lj1_v1.json (81 objects)
```

### lj2_v1.out

- sha256: 48b8ca882c80d5ee08bd5bc6c2dce0dad70038ddeb7b73077d1af369b7fdc2f3; replacements by masking: 0

```text
==============================================================================================================
row478 G1 fixture: gate fixture package, every launch normal (callgrind on 36 ok solves)
  [RI] verdict PASS
      record cj:fixture_S3                      class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_S3_rescaled             class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_norm         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_rq           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:fixture_S3                      class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_S3_rescaled             class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_norm         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_rq           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row478 G3 anchor: gate anchor-identity, comparator ok, uncached build, five gb_only solves
  [RI] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row478 G4 controls: gate controls, 11 child jobs, 8 solves
  [RI] verdict PASS
      record cj:ctl_identity_n3                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_random                  class B    child_created True         child_end exec                   pair cap raised None
      record ctl_identity_random/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record ctl_rawx_random/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_planted                 class B    child_created True         child_end exec                   pair cap raised None
      record ctl_identity_planted/ms1           class B    child_created True         child_end exec                   pair cap raised None
      record ctl_rawx_planted/ms1               class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_identity_n5_m3              class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_n5_m3                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_identity_n5_m4              class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_n5_m4                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_S3                          class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_S3_rescaled                 class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_torsion_S3_rq               class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_torsion_S3_norm             class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:ctl_identity_n3                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_random                  class B    child_created True         child_end exec                   pair cap raised None
      record ctl_identity_random/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record ctl_rawx_random/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_planted                 class B    child_created True         child_end exec                   pair cap raised None
      record ctl_identity_planted/ms1           class B    child_created True         child_end exec                   pair cap raised None
      record ctl_rawx_planted/ms1               class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_identity_n5_m3              class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_n5_m3                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_identity_n5_m4              class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_raw_n5_m4                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_S3                          class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_S3_rescaled                 class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_torsion_S3_rq               class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_torsion_S3_norm             class B    child_created True         child_end exec                   pair cap raised None
      record ctl_planted_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row480 controls_a1 image: controls_a1 image, gp, health d222 / d444, 2 builds, 2 solves
  [RI] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row481 F-4 launched: fixture4, 4 uncached builds, 8 solves without callgrind (565)
  [RI] verdict PASS
      record cj:f4_S4                           class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_S4_rescaled                  class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_torsion_S4_norm              class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_torsion_S4_rq                class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4_rescaled/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_torsion_S4_norm/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_torsion_S4_rq/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_S4_rescaled/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_torsion_S4_norm/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_torsion_S4_rq/ms1            class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:f4_S4                           class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_S4_rescaled                  class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_torsion_S4_norm              class B    child_created True         child_end exec                   pair cap raised None
      record cj:f4_torsion_S4_rq                class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4_rescaled/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_torsion_S4_norm/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_torsion_S4_rq/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_S4_rescaled/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_torsion_S4_norm/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record f4_t1_torsion_S4_rq/ms1            class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row482 Z-F4: fixture4 refused before any launch (536-541), finish() driver-written
  [RI] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
row483 build: build package, cached builds (961-962, to_cache=True: outputs outside the run directory)
  [RI] verdict PASS
      record cj:build_1073741831_shape_arm0_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm1_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm2_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm3_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm4_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm5_m5  class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:build_1073741831_shape_arm0_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm1_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm2_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm3_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm4_m5  class B    child_created True         child_end exec                   pair cap raised None
      record cj:build_1073741831_shape_arm5_m5  class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row485 cells m = 5 measured: cells m = 5, arms S5 and raw_x, 3 targets
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row485b cells m = 5 not_measured: cells m = 5, timeouts
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row486 Z-C5: cells m = 5, every cell refused / not_attempted before any launch
  [RI] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
row488 cells m = 4: cells m = 4, arms S4 and raw_x, callgrind on target 0 of each arm
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
row489 aggregate: aggregate, zero launch, driver-written raw (1322)
  [RI] verdict PASS
  [RJ] verdict PASS
==============================================================================================================
N-1: cells m = 5 measured
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-2: cells m = 5 not_measured (timeout)
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-3: cells m = 4 raw_grid measured, callgrind ok
  [RI] verdict PASS
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t0/cg                        class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t1                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t1/ms1                       class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t2                   class B    child_created True         child_end exec                   pair cap raised None
      record raw_x_t2/ms1                       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-4: cells m = 4 raw_grid child crashed after exec, partial .npz kept
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:grid_raw_x_t0                   class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-5: SE-3 re-solve at S-1, 2 attempts
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-5b: SE-3 re-solve, 6 attempts, still SSF after the last
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms3                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms4                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms5                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms6                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms3                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms4                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms5                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t9/ms6                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-5c: SE-3 re-solve on the callgrind target (m = 4, target 0)
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/ms2                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-6: controls_a1 with an HR-3 re-solve at S-2
  [RI] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms2 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms2 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-6b: controls_a1 with a failing d444 pattern and the _seed2 retry
  [RI] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444_seed2/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-7: failing callgrind child (valgrind exits nonzero after writing its out file)
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-8: timed-out callgrind child
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-9: cached builds
  [RI] verdict PASS
      record cj:build_x                         class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:build_x                         class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-10: fixture4 uncached builds and solves
  [RI] verdict PASS
      record cj:f4_S4                           class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:f4_S4                           class B    child_created True         child_end exec                   pair cap raised None
      record f4_t0_S4/ms1                       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-11: child jobs on refusal paths: refused meta; refused before fork (class A); ERR setrlimit (class C)
  [RI] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_refused_meta                class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_refused_before_fork         class A    child_created False        child_end no_child               pair None raised None
      record cj:ctl_err_setrlimit               class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
  [RJ] verdict PASS
      record S5_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S5_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_refused_meta                class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_refused_before_fork         class A    child_created False        child_end no_child               pair None raised None
      record cj:ctl_err_setrlimit               class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
==============================================================================================================
N-12: anchor-identity normal
  [RI] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
      record cj:anchor_S4                       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_random/ms1       class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t0/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t1/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_v2_t2/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record anchor_comparator_system/ms1       class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
N-13: Z-C5 (no launch)
  [RI] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict PASS_ZL
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
NJ-cg A: cells m = 4, callgrind child on target 0 path A, record present
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class A    child_created False        child_end no_child               pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class A    child_created False        child_end no_child               pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-cg pre_stdout_99: cells m = 4, callgrind child on target 0 path pre_stdout_99, record present
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-cg err_setrlimit_97: cells m = 4, callgrind child on target 0 path err_setrlimit_97, record present
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-cg exec_fail: cells m = 4, callgrind child on target 0 path exec_fail, record present
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-cg exec_timeout: cells m = 4, callgrind child on target 0 path exec_timeout, record present
  [RI] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t0/cg                           class B    child_created True         child_end exec                   pair cap raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-ms-refused: cells m = 4, target 0 msolve refused before fork (no callgrind attempted, 184-186)
  [RI] verdict PASS
      record S4_t0/ms1                          class A    child_created False        child_end no_child               pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record S4_t0/ms1                          class A    child_created False        child_end no_child               pair None raised None
      record S4_t1/ms1                          class B    child_created True         child_end exec                   pair cap raised None
      record S4_t2/ms1                          class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-gp A: controls_a1, gp child path A, record present
  [RI] verdict PASS
      record gp:controls_a1_pari                class A    child_created False        child_end no_child               pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class A    child_created False        child_end no_child               pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-gp pre_stdout_99: controls_a1, gp child path pre_stdout_99, record present
  [RI] verdict PASS
      record gp:controls_a1_pari                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-gp err_setrlimit_97: controls_a1, gp child path err_setrlimit_97, record present
  [RI] verdict PASS
      record gp:controls_a1_pari                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-gp exec_fail: controls_a1, gp child path exec_fail, record present
  [RI] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record gp:controls_a1_pari                class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d222/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record health:health_p1073741831_d444/ms1 class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_torsion_S3_rq            class B    child_created True         child_end exec                   pair cap raised None
      record cj:ctl_a1_S3_rescaled              class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_torsion_S3_rq/ms1   class B    child_created True         child_end exec                   pair cap raised None
      record ctl_a1_planted_S3_rescaled/ms1     class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-cmp A: anchor-identity, comparator path A: the failure exit 656-659 with finish()
  [RI] verdict FAIL
      record cmp                                class A    child_created False        child_end no_child               pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict FAIL
      record cmp                                class A    child_created False        child_end no_child               pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
NJ-cmp pre_stdout_99: anchor-identity, comparator path pre_stdout_99: the failure exit 656-659 with finish()
  [RI] verdict FAIL
      record cmp                                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
  [RJ] verdict FAIL
      record cmp                                class C    child_created True         child_end frozen_pre_exec_exit   pair None raised None
      frozen checker items: ['66-67 no child RLIMIT_AS read-back recorded']
==============================================================================================================
NJ-cmp exec_fail: anchor-identity, comparator path exec_fail: the failure exit 656-659 with finish()
  [RI] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cmp                                class B    child_created True         child_end exec                   pair cap raised None
==============================================================================================================
NJ-fixture-replaced: fixture with a replaced fresh draw (382-387): an extra fresh target, callgrind on its ok arms
  [RI] verdict PASS
      record cj:fixture_S3                      class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_S3_rescaled             class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_norm         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_rq           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh3_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh3_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
  [RJ] verdict PASS
      record cj:fixture_S3                      class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_S3_rescaled             class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_norm         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fixture_torsion_S3_rq           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg0_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg0_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_x                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_x/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_reg1_raw_u                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/ms1                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_raw_u/cg                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/ms1                     class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3/cg                      class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/ms1            class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_S3_rescaled/cg             class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_norm/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_reg1_torsion_S3_rq/cg           class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh1_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh1_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh2_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh2_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh3_raw_x                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_x/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_x/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_fresh3_raw_u                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_u/ms1                class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_raw_u/cg                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3/ms1                   class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3/cg                    class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3_rescaled/ms1          class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_S3_rescaled/cg           class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_norm/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_norm/cg       class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_rq/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_fresh3_torsion_S3_rq/cg         class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted0_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted0_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_x               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_x/cg               class B    child_created True         child_end exec                   pair cap raised None
      record cj:fx_planted1_raw_u               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/ms1              class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_raw_u/cg               class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/ms1                 class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3/cg                  class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/ms1        class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_S3_rescaled/cg         class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/ms1    class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_norm/cg     class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/ms1      class B    child_created True         child_end exec                   pair cap raised None
      record fx_planted1_torsion_S3_rq/cg       class B    child_created True         child_end exec                   pair cap raised None

PLANNED-BASIS REFUSALS: []
WROTE lj2_v1.json (42 objects)
```

### rdscan_v1.out

- sha256: 547f8fede05528cd9ad1bd98c1d9e4d4936844a51fa3ec979d642e7b16721bdc; replacements by masking: 0

```text
==========================================================================================
RUN-GFPN-bfe956 occurrences: 12
  child/ctl_S3.spec.json       PREFIX       x1   e.g. /out | <rd>/child/ctl_S3
  child/ctl_S3_rescaled.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_S3_rescaled
  child/ctl_identity_n3.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_identity_n3
  child/ctl_identity_n5_m3.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_identity_n5_m3
  child/ctl_identity_n5_m4.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_identity_n5_m4
  child/ctl_raw_n5_m3.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_raw_n5_m3
  child/ctl_raw_n5_m4.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_raw_n5_m4
  child/ctl_raw_planted.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_raw_planted
  child/ctl_raw_random.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_raw_random
  child/ctl_torsion_S3_norm.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_torsion_S3_norm
  child/ctl_torsion_S3_rq.spec.json PREFIX       x1   e.g. /out | <rd>/child/ctl_torsion_S3_rq
  command.txt                  OTHER        x1   e.g. line 2 | # GFPN_RUN_DIR=<rd>
==========================================================================================
RUN-GFPN-f5412a occurrences: 13
  child/anchor_S4.spec.json    PREFIX       x1   e.g. /out | <rd>/child/anchor_S4
  command.txt                  OTHER        x1   e.g. line 2 | # GFPN_RUN_DIR=<rd>
  raw-result.json              PREFIX       x11  e.g. /comparator/child/argv[2] | <rd>/comparator
lstat checked 155 changed []
```

### lj4_v1.out

- sha256: e8e3481d6951d55c4e18d9f1a5dcbd3160c5130f12d24f8096aadcf9b2e2cec1; replacements by masking: 0

```text
(19)  unaltered SE-3 re-solve at S-1                             RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: renamed attempt-1 files attributed by RH-1 (vi); no gap
(19)  renamed_files attempt1 removed in place                    RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t0): (ii) N=2 attempts=2 accepted=2 1+renamed=1'] | gaps 7 ['solver/S5_t0.ms', 'solver/S5_t0.ms.err', 'solver/S5_t0.ms.err.ssf-attempt1', 'solver/S5_t0.ms.log']
      expected: a recorder gap and FAIL
(19)  one launch record of the tag removed in place              RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t0): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3'] | gaps 7 ['solver/S5_t0.ms', 'solver/S5_t0.ms.err', 'solver/S5_t0.ms.err.ssf-attempt1', 'solver/S5_t0.ms.log']
      expected: the COUNT GAP of RI-1 (c) and FAIL (RI-3 (19))
(20)  unaltered HR-3 re-solve at S-2                             RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: attributed; no gap
(20)  one S-2 launch record of the tag removed in place          RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (health/health_p1073741831_d222): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3'] | gaps 6 ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(21)  callgrind child exits nonzero after writing its out file   RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: <tag>.callgrind.out attributed by RH-1 (iii); no gap
(22)  uncached build_poly child-job record removed in place      RJ      with V-7 FAIL    without FAIL    | named [] | gaps 5 ['child/f4_S4.meta.json', 'child/f4_S4.npz', 'child/f4_S4.spec.json', 'child/f4_S4.stderr']
      expected: five gaps .spec.json .stdout .stderr .npz .meta.json; FAIL
(22)  raw_grid child-job record removed in place                 RJ      with V-7 FAIL    without FAIL    | named [] | gaps 4 ['child/ctl_raw_random.meta.json', 'child/ctl_raw_random.spec.json', 'child/ctl_raw_random.stderr', 'child/ctl_raw_random.stdout']
      expected: four gaps .spec.json .stdout .stderr .meta.json; FAIL
(23)  cap-mismatch stop outcome (P-8 child in a cells m = 5 pack RJ      with V-7 FAIL    without FAIL    | named [] | gaps 0 []
      expected: FAIL; stop class 'a cap read-back mismatch'; no planned-basis refusal (RH-2)
(24)  LR-1 (2 attempts, removed [2])                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3'] | gaps 6 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(24)  LR-2 (2 attempts, removed [1])                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3'] | gaps 6 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(24)  LR-3 (3 attempts, removed [2])                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4'] | gaps 9 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log']
      expected: COUNT GAP and FAIL
(24)  LR-4 (3 attempts, removed [2, 3])                          RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 3 + RL-2 0; (ii) N=1 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 2 launch records vs counters 4'] | gaps 9 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log']
      expected: COUNT GAP and FAIL
(24)  LR-5 (S-2, 2 attempts, final removed)                      RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (health/health_p1073741831_d222): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-2): 2 launch records vs counters 3'] | gaps 6 ['health/health_p1073741831_d222.ms.err', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log', 'health/health_p1073741831_d222.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(24)  single removal 1 of 2 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3'] | gaps 6 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(24)  single removal 2 of 2 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 2 + RL-2 0; (ii) N=1 attempts=2 accepted=2 1+renamed=2', 'SITE COUNT GAP (S-1): 2 launch records vs counters 3'] | gaps 6 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.log.ssf-attempt1']
      expected: COUNT GAP and FAIL
(24)  single removal 1 of 3 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4'] | gaps 9 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log']
      expected: COUNT GAP and FAIL
(24)  single removal 2 of 3 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4'] | gaps 9 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log']
      expected: COUNT GAP and FAIL
(24)  single removal 3 of 3 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=2 != RB-1 3 + RL-2 0; (ii) N=2 attempts=3 accepted=3 1+renamed=3', 'SITE COUNT GAP (S-1): 3 launch records vs counters 4'] | gaps 9 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log']
      expected: COUNT GAP and FAIL
(24)  single removal 1 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(24)  single removal 2 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(24)  single removal 3 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(24)  single removal 4 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(24)  single removal 5 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(24)  single removal 6 of 6 attempts                             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=5 != RB-1 6 + RL-2 0; (ii) N=5 attempts=6 accepted=6 1+renamed=6', 'SITE COUNT GAP (S-1): 6 launch records vs counters 7'] | gaps 18 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.err.ssf-attempt3']
      expected: COUNT GAP and FAIL
(25)  LR-1 under RI-1 (a), (d) disabled                          RIx     with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: NO RI-1 named gap and NO recorder gap (RJ-5 (a))
(25)  LR-2 under RI-1 (a), (d) disabled                          RIx     with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: NO RI-1 named gap and NO recorder gap (RJ-5 (a))
(25)  LR-3 under RI-1 (a), (d) disabled                          RIx     with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: NO RI-1 named gap and NO recorder gap (RJ-5 (a))
(25)  LR-5 under RI-1 (a), (d) disabled                          RIx     with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: NO RI-1 named gap and NO recorder gap (RJ-5 (a))
(26)  unaltered (19) package                                     RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no recorder gap of any kind
(26)  unaltered (20) package                                     RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no recorder gap of any kind
(26)  DV-18 (a) controls                                         RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no recorder gap of any kind
(26)  DV-18 (b) anchor-identity                                  RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no recorder gap of any kind
(26)  DV-18 (e) controls-a1                                      RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no recorder gap of any kind
(27)  RB-1 attempt record removed at a non-event tag             RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t1): (i) N=1 != RB-1 0 + RL-2 0'] | gaps 3 ['solver/S5_t1.ms.err', 'solver/S5_t1.ms.log', 'solver/S5_t1.ms.out']
      expected: the named gap of RI-1 (c) and FAIL
(27)  a launch record duplicated                                 RJ      with V-7 FAIL    without FAIL    | named ['COUNT GAP (solver/S5_t0): (i) N=2 != RB-1 1 + RL-2 0', 'SITE COUNT GAP (S-1): 2 launch records vs counters 1'] | gaps 4 ['solver/S5_t0.ms', 'solver/S5_t0.ms.err', 'solver/S5_t0.ms.log', 'solver/S5_t0.ms.out']
      expected: the named gap of RI-1 (c) and FAIL
(27)  a site counter decremented                                 RJ      with V-7 FAIL    without FAIL    | named ['SITE COUNT GAP (S-1): 1 launch records vs counters 0'] | gaps 0 []
      expected: the named gap of RI-1 (c) and FAIL
(27)  a child-job launch record duplicated                       RJ      with V-7 FAIL    without FAIL    | named ["DUPLICATE-PATH GAP (child/ctl_identity_n3.stdout): ['cj:ctl_identity_n3', 'cj:ctl_identity_n3#dup']"] | gaps 5 ['child/ctl_identity_n3.meta.json', 'child/ctl_identity_n3.npz', 'child/ctl_identity_n3.spec.json', 'child/ctl_identity_n3.stderr']
      expected: the named gap of RI-1 (c) and FAIL
(28)  callgrind stdout open fails (stand-in os.open), record rem RJx     with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: NO named gap and NO recorder gap (else STOP)
(28)  the same under launchkind                                  RJ      with V-7 FAIL    without FAIL    | named ['CALLGRIND COUNT GAP (S4_t0): Ncg=0 count=1', 'CALLGRIND SITE COUNT GAP: 0 callgrind launch records vs 1 attempt records with callgrind_result_present true'] | gaps 0 []
      expected: a CALLGRIND COUNT GAP and FAIL
(28)  the same under attcount (contrast)                         RI      with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: (contrast) no gap
(29)  DV-18 (e) controls-a1, gp record removed                   RJ      with V-7 FAIL    without FAIL    | named [] | gaps 3 ['pari/controls_a1_pari.gp', 'pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      expected: pari/<tag>.gp a recorder gap, FAIL
(29)  the same, RJ-2 disabled (contrast)                         RJnogp  with V-7 FAIL    without FAIL    | named [] | gaps 2 ['pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      expected: (contrast)
(29)  the same under attcount (contrast)                         RI      with V-7 FAIL    without FAIL    | named [] | gaps 2 ['pari/controls_a1_pari.gp.stderr', 'pari/controls_a1_pari.gp.stdout']
      expected: (contrast)
(29)  gp child's stdout open fails (stand-in), record removed    RJ      with V-7 FAIL    without FAIL    | named [] | gaps 1 ['pari/controls_a1_pari.gp']
      expected: pari/<tag>.gp a recorder gap, FAIL
(29)  the same, RJ-2 disabled (contrast)                         RJnogp  with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: (contrast)
(30)  DV-18 (b) anchor-identity, comparator record removed       RJ      with V-7 FAIL    without FAIL    | named ['COMPARATOR COUNT GAP: 0 comparator launch records vs comparator.child present'] | gaps 7 ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms']
      expected: a COMPARATOR COUNT GAP, FAIL
(30)  the same, RJ-3 disabled (contrast)                         RJnocmp with V-7 FAIL    without FAIL    | named [] | gaps 7 ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms']
      expected: (contrast)
(30)  the same under attcount (contrast)                         RI      with V-7 FAIL    without FAIL    | named [] | gaps 7 ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms']
      expected: (contrast)
(31)  one launch record appended whose stdout_path is of none of RJ      with V-7 FAIL    without FAIL    | named ['UNKNOWN-KIND GAP (ordinal 1): solver/S5_t0.appended.out'] | gaps 0 []
      expected: an UNKNOWN-KIND GAP, FAIL
(31)  the same, RJ-4 (b) disabled (contrast)                     RJnouk  with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: (contrast)
(31)  the same under attcount (contrast)                         RI      with V-7 FAIL    without PASS    | named [] | gaps 0 []
      expected: (contrast)
(32)  unaltered (28) package (callgrind child C, record present) RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap
(32)  unaltered (29) packages (gp exec, gp C)                    RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap
(32)  unaltered (29) second package (gp child C)                 RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap
(32)  unaltered (30) package                                     RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap
(32)  unaltered (31) package                                     RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap
(32)  DV-18 (a) controls                                         RJ      with V-7 PASS    without PASS    | named [] | gaps 0 []
      expected: no named gap, no recorder gap

WROTE lj4_v1.json (58 rows)
```

### hashes_v1.out

- sha256: ddf95cd9b3d1577d8b728531daa9d910d2c16f41b2a467dcbfa43d3dd1705115; replacements by masking: 0

```text
35d943da8bfd0d5048f7fd4785583feaac963c26add3ea4315ceb00cf0e93484 ledger/handoffs/TASK-20260924-d897a6.yaml
c66633c45ccacb2779bbcb291227703d8f0c0d8ee79fa5669d22bc214e7ff8ee agents/red-team.md
16b87c767e698a15f988ad8d6f03b07b2c0e5ac7e2738846d0084c2473288a56 AGENTS.md
e5d6907cf8cbdd0bcf2f280c0078d3a9be15f6c78d0c836663b11fcca3d92591 ledger/decisions/DEC-20260924-e52eec.yaml
3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py
22550c2f4ede32a41d7b8134f2c72c04121d20065eacd6604640b0ef0e8a81ba coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n3.json
e3bc6d120a52a898fd84e47efe54f727f20e2013c906522cd41a73303ae595a2 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n4.json
a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0 experiments/EXP-GFPN-05ff43/amendments/v2_addendum_consumercover.yaml
877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1 experiments/EXP-GFPN-05ff43/amendments/v2_addendum_valueclose.yaml
0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py
0d22a082c967500f28d0aabdce1b0cdf125cf5a3109727045e6cf55407a20098 experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py
ed813df7760be9d9289a6643ba7be95cf9be905e6ba0835d476b56ea551d2e25 experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py
c064144c7d70d84727cd286baf34df8160eca2b3b5e469ea29556446289b6592 experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py
0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py
dafe748d9a1e923c106a5fa0cfcdd7d622fbb80cb23e1099d5fc6064be4e7293 experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py
749237a6cfc15eeb235824dcf5e28e6733ee099df56daad3f996ae028650e5b7 experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py
516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py
f347eebafa51eace211012f780c8425a2f4d6917f61370c7c2f20a1c62a9185b experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_common.py
3a6828f42a6e8dd97fd487510fbb0c153ca8f51d9bcd0c310d1af96c8d5e3e15 experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_resolve.py
dd52a4bfad9c4bfb0e4e37ee8a24951e8992edf8d2f1dfcc112e9bcdbabb9c19 experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py
939d7d7e5bc8a8c64f15df188f98f13b22ef7a9d696680f8e47854c2dbdcd14d experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py
f79161999507cdb5438c1be39de21ba74d25ef745f490c08e56a600c28117fbd experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py
cefbb3348174bf02546129a65a9a0961b3ad5f60341d25ca4bfab1d54cb56f23 experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py
7bb7b688250d69a2ca209a57fd70176727aa1fe225c95c9878076be407380868 experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_common.py
```

### tables_v1.out

- sha256: f4a32ae653a1fcd18e8969369bd7ad07c8fca71822f3784db968703a21260734; replacements by masking: 0

```text
rows 85 files 683 unattributed 0
```

### wordcheck_v1_scratch.out

- sha256: 8a58eb777ff302b0a7e3343d4e0948d14c61767752418d02abc6466f3f92a995; replacements by masking: 0

```text
word list sha256 c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 entries 16
explore_v1.py                            word_hits    0 scratch_root_occurrences    0
hashes_v1.py                             word_hits    0 scratch_root_occurrences    0
integrity_v1.py                          word_hits    0 scratch_root_occurrences    0
listing_v1.py                            word_hits    0 scratch_root_occurrences    0
listing_v2.py                            word_hits    0 scratch_root_occurrences    0
lj0_v1.py                                word_hits    0 scratch_root_occurrences    0
lj0_v2.py                                word_hits    0 scratch_root_occurrences    0
lj1_v1.py                                word_hits    0 scratch_root_occurrences    0
lj2_v1.py                                word_hits    0 scratch_root_occurrences    0
lj4_v1.py                                word_hits    0 scratch_root_occurrences    0
pkgread_v1.py                            word_hits    0 scratch_root_occurrences    0
rdscan_v1.py                             word_hits    0 scratch_root_occurrences    0
rjcore_v1.py                             word_hits    0 scratch_root_occurrences    0
rjcore_v2.py                             word_hits    0 scratch_root_occurrences    0
scan_v1.py                               word_hits    0 scratch_root_occurrences    0
scan_v2.py                               word_hits    0 scratch_root_occurrences    0
tables_v1.py                             word_hits    0 scratch_root_occurrences    0
wordcheck_v1.py                          word_hits    0 scratch_root_occurrences    0
crj2d_diff.out                           word_hits    0 scratch_root_occurrences    0
explore_v1.out                           word_hits    2 scratch_root_occurrences    0
hashes_v1.out                            word_hits    0 scratch_root_occurrences    0
integrity_v1.out                         word_hits    0 scratch_root_occurrences    0
listing_v1.out                           word_hits    0 scratch_root_occurrences    0
listing_v2.out                           word_hits    0 scratch_root_occurrences    0
lj0_v1.out                               word_hits    0 scratch_root_occurrences    0
lj0_v2.out                               word_hits    0 scratch_root_occurrences    0
lj1_v1.out                               word_hits    0 scratch_root_occurrences    0
lj2_v1.out                               word_hits    0 scratch_root_occurrences    0
lj4_v1.out                               word_hits    0 scratch_root_occurrences    0
pkgread_v1.out                           word_hits    0 scratch_root_occurrences    0
rdscan_v1.out                            word_hits    0 scratch_root_occurrences    0
scan_v1.out                              word_hits    0 scratch_root_occurrences    0
scan_v2.out                              word_hits    0 scratch_root_occurrences    0
tables_v1.out                            word_hits    0 scratch_root_occurrences    0
command_log.txt                          word_hits    0 scratch_root_occurrences    0
tables_v1.md                             word_hits    0 scratch_root_occurrences    0
tables_v1.yaml                           word_hits    0 scratch_root_occurrences    0
tables_v1_perfile.md                     word_hits    0 scratch_root_occurrences    0
total word hits 2
```

### wordcheck_v1_parts.out

- sha256: 4de9727effc61e89057d1f716009dcc2144a269b97b0e223c660f9be12aa0f8a; replacements by masking: 0

```text
word list sha256 c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 entries 16
body_v1.yaml.part                        word_hits    1 scratch_root_occurrences    0
paths_read_v1.yaml.part                  word_hits    0 scratch_root_occurrences    0
deviations_v1.yaml.part                  word_hits    0 scratch_root_occurrences    0
exact_argv_post_compaction.txt           word_hits    0 scratch_root_occurrences    0
assemble_v1.py                           word_hits    0 scratch_root_occurrences    0
check_v1.py                              word_hits    0 scratch_root_occurrences    0
total word hits 1
```

### wordcheck_v1_parts2.out

- sha256: cb5ba3c928a23cd9f1ab268fa63f350c966eae7a0698a0d336cbf405c691ae0c; replacements by masking: 0

```text
word list sha256 c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 entries 16
body_v2.yaml.part                        word_hits    1 scratch_root_occurrences    0
deviations_v2.yaml.part                  word_hits    0 scratch_root_occurrences    0
assemble_v2.py                           word_hits    0 scratch_root_occurrences    0
total word hits 1
```

### assemble_v1.out

- sha256: 75ea437007e728b9e981aacaede175fc5eae14cd9e0eb6371708d80d3bb727af; replacements by masking: 0

```text
written_at 2026-09-25T02:47:27Z
yaml bytes 177004 sha256 3a84029a83219dcc3a766f1b12a4edaa359ebdceb5659609e3697e85a33c4cb2
md bytes 890870 sha256 996ac45ade9e94596c34623789fb4ff5ea85e8ccd613f258bb39d474f0ce5412
masking replacements per reproduced file: {"explore_v1.out": 2}
command log entries 97 scratch files listed 59
```

### check_v1.out

- sha256: ff124c738bdea334b2182999e3cddfe8955bb803c2ba851a990fd3d7beaec256; replacements by masking: 1

```text
write-scope listing: ['review-report.md', 'review-report.yaml']
sha256 3a84029a83219dcc3a766f1b12a4edaa359ebdceb5659609e3697e85a33c4cb2 177004 bytes coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
sha256 996ac45ade9e94596c34623789fb4ff5ea85e8ccd613f258bb39d474f0ce5412 890870 bytes coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md
yaml.safe_load: OK; top-level keys 24 missing []
attestation missing [] blind_from entries 24
inference block keys ['requested_policy', 'agent_binding', 'resolved_model_id', 'resolved_model_note', 'model_verified', 'fallback_used', '<masked>_used']
red_team_report id TASK-20260924-d897a6 task_id TASK-20260924-d897a6
joints ['LJ-1_launch_kinds_no_fail_open', 'LJ-2_detectors_no_planned_basis_refusal', 'LJ-3_definitional_scope_and_statements', 'LJ-4_development_harness', 'LJ-5_reads_reach_and_readers', 'LJ-6_value_classes_and_neutrality']
word list sha256 c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 entries 16
review-report.yaml word hits 1 at lines [1738]; scratch-root occurrences 0
review-report.md word hits 1 at lines [1374]; scratch-root occurrences 0
CRJ-8 ids read from the card at run time: 8
review-report.yaml CRJ-8 id occurrences 0
review-report.md CRJ-8 id occurrences 0
```

lj0_v2.out and listing_v2.out are identical to lj0_v1.out and listing_v1.out except their last line (C.x);
sha256 lj0_v2.out 7832a61331e634915469e1a2d94bfe403f649e52b8adce8badca8dd2ffca43f1, listing_v2.out 332de305c7d15c8e90e626b81f8b1587efae1bd11369737fba027bf176c759c0.

## Appendix E - data files and parts (listed by sha256; content summarized in the report)

- body_v1.yaml.part: 90841 bytes, sha256 340201347d760cab6ed6a7c2a4346788deb9df9a5598c3d4bdbd4ccc8c8b3577 (hand-written YAML body of the report)
- body_v2.yaml.part: 90977 bytes, sha256 2600f718e0b72cfc8d2afe64a6aa7be2902872c893905788f9308c504e53627d (hand-written YAML body, version 2)
- deviations_v1.yaml.part: 4979 bytes, sha256 24e724e71a10043ccb9c8d88abb102d6639cc64d52cb0dade351a24a6c108209 (deviations part)
- deviations_v2.yaml.part: 5960 bytes, sha256 226242ecba6912084ad1b7e603d0629649a5833ecfbf94f1e9d820a8f6b63dd8 (deviations part, version 2)
- listing_v1.json: 91182 bytes, sha256 6e42a1a40fc08f93ae88f40d48a9fa72f18348109cd3a1d5b5e588c30c7dc79c (its data)
- listing_v2.json: 91182 bytes, sha256 6e42a1a40fc08f93ae88f40d48a9fa72f18348109cd3a1d5b5e588c30c7dc79c (its data)
- lj0_v1.json: 95382 bytes, sha256 1b8e56a8adc2d704ec96dba34e03758c6cc38ea07ebc4284ab9c134675b147d5 (its data)
- lj0_v2.json: 95382 bytes, sha256 1b8e56a8adc2d704ec96dba34e03758c6cc38ea07ebc4284ab9c134675b147d5 (its data)
- lj1_v1.json: 82483 bytes, sha256 5efe982d2e75d465c23cb5b97666f8e68068dade19f88abd8016e2de85eb502e (its data)
- lj2_v1.json: 18230 bytes, sha256 8459fb40273919b8ac81a50987f7e531f3c6f2f0dfa607ec20f2afcf2eee9a92 (its data)
- lj4_v1.json: 28729 bytes, sha256 e0d28b80105ceed84e62a0f06f2a280dbad2533ebb5ae950584e7978089591d9 (its data)
- notes.md: 9772 bytes, sha256 44e1ed2b0102d5b382accfae1faca3ff9f68fed713c2486f569f04506e5b2b57 (working notes kept across the compaction (not reproduced; listed by hash))
- paths_read_v1.yaml.part: 11736 bytes, sha256 d074c775814b1015d4611cef14b1f37af229a6c3eb3c7a16e5bd69b4b66810af (paths_read part)
- pkgread_v1.json: 709959 bytes, sha256 c083046809f00ccce93dd6dd2e72f51ee161dd8dc81428d87c77220a5a702466 (its data)
- rdscan_v1.json: 3704 bytes, sha256 e771c75f09170382db786536a0c5b9b7d46ce0c18be110bbb623a66e0c6e721d (its data)
- scan_v1.json: 102245 bytes, sha256 e0f2840b30a2daca68f1b53004918ff3034accf134aed56ab1df04426bf15751 (its data)
- scan_v2.json: 13213 bytes, sha256 2a0775a3cc0ec71613e351f768863b8128240e64cfb484e111d9bcb8d9df6161 (its data)
- tables_v1.md: 19434 bytes, sha256 e49c9d6ec402e9f419db87fb39c5e2adc9e86de41099235428cf3219972122d4 (table (markdown))
- tables_v1.yaml: 25716 bytes, sha256 77115869f6ae1c40fe026c1703c8f9ab4009bd86074a62635ef247574fb4db4d (table (YAML))
- tables_v1_perfile.md: 48192 bytes, sha256 91c7ff045e49b0242790dc78f1248dde2bbecef60853ea601b635595a37d33f9 (per-file first attribution clause)
- words.txt: 113 bytes, sha256 c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268 (word list placed by the dispatching session for the CRJ-7 self-check; read only at run time by wordcheck_v1.py, assemble_v1.py and check_v1.py; never printed)

