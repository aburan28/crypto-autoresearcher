# TASK-20260923-6599cf: zero-run msolve characterization (EXP-GFPN-05ff43 repair)

**This is a DEVELOPMENT characterization. It is not a run package, not evidence, and not a result.**

- **Run packages:** zero were created. No byte was written under `experiments/EXP-GFPN-05ff43/runs/`, any frozen tree or `implementation-v2-r1/`.
- **Values:** no D, degree or quotient dimension reported here is a result.
  - Toy values (p' = 1033) are harness parameters.
  - The p' = 4111 values are the archived RUN-GFPN-ac4487 values, re-observed.
  - Nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
  - Nothing here is a security statement about EcGFp5 or EcMasFp5.
- **Scope of the task:**
  - It reports numbers, findings and the pre-declared readings CR-1..CR-3, computed by the draft's formulas.
  - It decides nothing and makes no approval recommendation.
  - The approval act (reserved TASK-20260923-ad3016) applies CR-1..CR-5.

- **Card:** `ledger/handoffs/TASK-20260923-6599cf.yaml`, which binds CH-1..CH-10.
- **Ordered by:** DEC-20260923-582d6b, R-3.
- **Formulas:** the `characterization_readings` of the DRAFT `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_solverevent.yaml`.
  - sha256 011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f.
  - This equals `addendum_sha256` in the TASK-20260923-4eee3b receipt.
- **Bundle hash:** read through CORR-20260923-9abefc.
- **Archival task:** TASK-20260923-683f34.

## 1. Provenance, environment, inference

| item | value |
|---|---|
| git HEAD at run start | `b2ede15605f344d7a60b000fca3a4b0c88af8f51`, branch `claude/pollard-rho-speedup-hypotheses-yu8qwp` |
| tree state at run start | dirty only by `?? experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/char_msolve.py` (this harness); recorded by the harness in `run-meta` at 2026-09-23T22:57:53.136145Z |
| harness | `char_msolve.py`, sha256 `a99e9e1cc5f6995c3b56e07c9f9efdca182a140b699ac35ef9debb478e407ac8`; bytes identical at launch and after the run (checked) |
| command (integrity) | `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -B experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/char_msolve.py integrity --work <scratch>/work` |
| command (run) | `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 nohup python3 -B .../char_msolve.py run --work <scratch>/work` (pid 6841) |
| command (analyze) | `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -B .../char_msolve.py analyze --work <scratch>/work --out experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization` |
| scratch | `<scratch>` = `/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/char6599cf` (session scratchpad; never the repository) |
| frozen code imported (never edited) | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py` (run_child, msolve_argv, parse_msolve_log, parse_msolve_param, rational_solutions, classify_solve); `v2_common.py` only for its fixture data path in the S_ub derivation |
| msolve | `/usr/bin/msolve`, sha256 `c2722288d22c3a1eab00c0b818d0204d4a98104d059b2fd4ecb7343e8ef759fa`; dpkg `msolve 0.6.5-1build2 amd64`, `libmsolve-0.6.5 0.6.5-1build2 amd64`; links `libneogb-0.6.5.so` |
| python | 3.11.15; python-flint 0.9.0 |
| host | Ubuntu 24.04.4 LTS; 4 CPUs; MemTotal 16481980 kB; SwapTotal 0; MemAvailable 15582336 kB at run start |
| machine protection | each child ran through the frozen `v2_solver.run_child` with `cap_bytes` 10737418240, set in the child and read back with getrlimit. The dispatcher's DP-5 guard threshold is MemAvailable < 2621440 kB (about 13.2 GB used), which is above 12.0 GB, so the cap was not lowered. Per-child timeout was 600 s (declared; never reached). No outer guard was used beyond the dispatching session's guard (pid 875). The frozen host lock `/tmp/gfpn-v2-solver.lock` and the frozen other-solver scan applied to every launch. One solver process ran at a time. |
| randomness | the harness uses none. msolve's internal randomness is characterized in section 8 (C-3 (d)). `PYTHONHASHSEED=0` was set for the harness process; children inherit its environment. |

**Inference:**

- requested_policy: `executor-implementation`
- resolved_model_id: `null` (the dispatching session supplied none; none is invented)
- fallback_used: false
- bedrock_used: false
- reasoning_effort: the policy default (card: null)

Nothing written here carries TASK-20260923-cd932c, TASK-20260923-6c7f55, TASK-20260923-3aa31e or TASK-20260923-292052 as its own task id.

## 2. Integrity (CH-3), checked by the harness before any solve

All checks passed (`integrity` exit 0, "CH-3 PASS"). Nothing was solved before this.

| check | observed | expected / bound | pass |
|---|---|---|---|
| draft addendum | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` | TASK-20260923-4eee3b receipt `addendum_sha256` = same | yes |
| (a) bundle `experiments/EXP-GFPN-05ff43/dev-evidence/stageR1-dv7/stageR1-dv7-evidence.tar.gz`, 717023 bytes | `70b83d61bfd05fcc92208c9f2bdba58fea0e7b587a927d54141bb72ccd35bd14` | TASK-20260923-53a47d receipt `path_sha256` = same; `bundle_status: committed`; CORR-20260923-9abefc value = same | yes |
| (b) event input `fx_reg0_torsion_S3_norm.ms`, world A and world B copies | both `541b57b904e0c16956f9ea4615a32f1aaaae1cdfe7ca9c3b767f3b5f22d537c8` | same | yes |
| (c) world A output `.ms.out` | `d2878f4f2b276162c78fd8b7fb31ae2fbc0a04984222a344fed047fef9cf07da` | prefix `d2878f4f2b276162` | yes |
| (c) world B output `.ms.out` | `201812d43b7c7a9dab2c8a1270e2a9a022a671ccb4992775aa1e431b48ef0569` | prefix `201812d43b7c7a9d` | yes |
| (c) world A `.ms.log` / `.ms.err` | `016a2101033c7dd683bcce83c19078fede046957ba7143078bb45ef0505a89a4` / `7f884412f77e07d906b1434df3609e23f33ca89ba2d539f90876d2bfaa037429` | recorded | n/a |
| (c) world B `.ms.log` / `.ms.err` | `3eb2eac30d62b713ff1fe4b3d199de59984a030c113754b7c897a20777ab2588` / `fc962b47b9406a96cb10ced9b29d8b55750fed13f1ff44e1e94186ab16d910a1` | recorded | n/a |
| (d) every RUN-GFPN-ac4487 file read: 36 `.ms`, 36 `.ms.out`, 36 `.ms.log`, 36 `.ms.err`, `manifest.yaml`, `raw-result.json` (146 files) | 0 mismatches | TASK-20260923-0fa03f `post-run-receipt.json` `path_sha256` (receipt commit_sha f9188ae34d591a833c46e1cb655a6518f89d5d00) | yes |
| (e) the other 35 toy inputs of the world B toy G1 package (`RUN-GFPN-a61a10` toy label, a retired id used here only as the bundle's directory name) | 35 found; all 35 byte-identical to world A's | 35 | gap 0 |

- The bundle was extracted only into `<scratch>/work/bundle` by the harness.
- An earlier manual listing extraction went into `<scratch>/bundle`, also scratch (see deviations).
- Per-input sha256 values of the 35 toy inputs and the 36 ac4487 inputs are in `summary.json` under `integrity`.

## 3. Design as run (fixed before any solve; not changed in flight)

Every solve used the frozen argv `v2_solver.msolve_argv(IN, OUT, threads=1)`, which is `/usr/bin/msolve -v 2 -t 1 -f IN -o OUT -P 1` with no `-c`. The C-3 (c) diagnostics append `-c 0` or `-c 1` after `-P 1`. Each solve had a fresh output, log and error path in scratch.

| order | label | class | inputs | solves per input | pacing | planned | recorded | window (UTC, 2026-09-23) |
|---|---|---|---|---|---|---|---|---|
| 0 | C-3 (b) | help | `msolve -h` in a capped child (60 s timeout) | 1 | n/a | 1 | 1 | 22:57:53.46 |
| 1 | C-1a | C-1a | event input | 500 | back to back | 500 | 500 | 22:57:53.68 to 22:59:35.95 |
| 2 | C-1b | C-1b | event input | 500 | each start at least 1.1 s after the previous child ended (min observed gap 1.100151 s) | 500 | 500 | 22:59:35.95 to 23:10:27.33 |
| 3 | C-1c | C-1c | the 35 other toy inputs, sorted by name | 100 | back to back | 3500 | 3500 | 23:10:27.33 to 23:22:24.44 |
| 4 | C-2 | C-2 | the 36 RUN-GFPN-ac4487 inputs, sorted by name | 100 | back to back | 3600 | 3600 | 23:22:24.44 to 23:34:42.08 |
| 5 | C-3c-event-c0 | C-3 (c) | event input, `-c 0` | 200 | back to back | 200 | 200 | 23:34:42.08 to 23:35:23.05 |
| 6 | C-3c-event-c1 | C-3 (c) | event input, `-c 1` | 200 | back to back | 200 | 200 | 23:35:23.05 to 23:36:04.02 |
| 7 | C-3c-ac4487-c1 | C-3 (c) | each ac4487 input, `-c 1` | 5 | back to back | 180 | 180 | 23:36:04.02 to 23:36:40.89 |

- **Totals:**
  - 8680 solver children plus the help child.
  - Every child was run_child outcome `ok`.
  - Every child read back getrlimit soft = hard = 10737418240.
  - Every child showed `/proc/<pid>/limits` = 10737418240 after exec.
- **Limits and resources:**
  - 0 timeouts; the maximum child wall time was 0.277 s.
  - Maximum child VmHWM was 20934656 B; maximum VmPeak was 1091055616 B.
  - Maximum harness RSS before a launch was 33570816 B.
- **Interruptions:** there were no interruptions, refusals or envelope stops, so no `-r2` label exists.
- **Every class ran to its declared count.**
- **Timestamps:** start and end UTC are harness timestamps taken immediately before the frozen `run_child` call and after it returned. They include the frozen pre-launch `/proc` scan and lock. `run_child` polls the child every 0.2 s, so child wall times have about 0.2 s granularity.
- **Input integrity:** each input was hashed before and after its class. The values were unchanged.

## 4. Classification (CH-5)

Every solve was classified exactly as `v2_driver.solve` does:

1. Log text = `.ms.log` + "\n" + `.ms.err` + "\n".
2. `parse_msolve_log`.
3. If the child exited ok: `parse_msolve_param`, then, if `param`, `rational_solutions(payload, p, nvars)`. Here p and nvars come from the input's first two lines.
4. `classify_solve(..., n_sub_fail = 0)`.

- **Substitution:** it is not re-run, because no descended system exists here (n_sub_fail = 0 by the card). A supplementary substitution diagnostic is reported separately in section 10 and enters no reading.
- **NSP flag:** exactly the draft's SE-1. The outcome is `degenerate_parametrisation` and the reason is (i) "eliminating polynomial is not square-free", (ii) starts "eliminating polynomial degree ", or (iii) starts "msolve reports square-free part degree ".
- **D_as_driver_would_record:** the driver's D logic applied to the classification. It is a harness value, not a result.

**Class references:**

| class | reference |
|---|---|
| C-1a, C-1b | the world B output (`201812d4…`) |
| C-2 | the archived RUN-GFPN-ac4487 `.ms.out` |
| C-1c | the modal output of that input over its default-flag solves; ties go to the smallest sha256 (none occurred) |
| C-3 (c) | the input's default-flag modal output; equality with the archived ac4487 output and with world A/B is also recorded |

- **Parsed comparison (SE-4 (d)):** parse kind, header degree, eliminating degree, square-free flag, the F_p-rational solution set as a set (compared by the sha256 of its sorted list), and D.
- **Input keys:** inputs are keyed by input set plus file stem (`event/…`, `toy35/…`, `ac4487/…`), because toy and ac4487 stems coincide.
- **Per-solve fields:** every field CH-5 lists is in `solves.jsonl`, one record per child (8680 records).

## 5. Per-class counts and CR-2

The formula: n_c = solves whose child exited ok; x_c = those with the NSP signature. u_c is the one-sided 95% Clopper–Pearson upper bound, P(Binomial(n_c, u_c) ≤ x_c) = 0.05, which for x_c = 0 is 1 − 0.05^(1/n_c).

| class | n_c | x_c | u_c | classify outcomes | outputs differing in bytes from the class reference |
|---|---|---|---|---|---|
| C-1a | 500 | 0 | 0.005973551516349596 | ok 500 | 4 (#247–#250) |
| C-1b | 500 | 0 | 0.005973551516349596 | ok 500 | 0 |
| C-1c | 3500 | 0 | 0.0008555573086916901 | ok 3500 | 0 |
| C-2 | 3600 | 0 | 0.0008318017147593837 | ok 3600 | 5 (fx_reg1_S3_rescaled #95–#99) |

- **u_max** = max over C-1a, C-1b, C-1c and C-2 = **0.005973551516349596** (C-1a and C-1b). All four classes are complete, and no partial class exists.
- **No NSP-signature solve occurred in any class.** This includes C-3 (c). The world A event was not reproduced in 9100 default-flag solves of these inputs, 1000 of which were on the event input itself.

### S_ub (derivation; a parameter count, not an outcome)

S_ub is an upper bound on the `v2_driver.solve()` calls with `gb_only` false that all packages of the frozen plans can make:

- `trial-plan-v2.json`, sha256 `16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16`;
- `trial-plan-v2-a1.json`, sha256 `2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6`.

A static search found every call site of `solve(` in `v2_driver.py` and `a1_driver.py`:

- `v2_driver.py` lines 358 (fixture), 565 (fixture4), 693 and 711 (anchor, both `gb_only=True`), 786, 787 and 841 (controls), and 1174 (cells);
- `a1_driver.py` line 166 (controls_a1).

`a1_driver` build and cells delegate to `v2_driver.cmd_build` and `cmd_cells`.

Per-package bounds from the code:

| package kind | bound per package | code basis |
|---|---|---|
| fixture (p' = 4111 and 16777291) | (2 regression + 12 fresh draws + 2 planted) × 6 arms = 96 | `fixture_core`: one solve per arm per `run_target`. Regression targets = 2 at both primes (fixture data `square_analogue_n3.json`). Fresh loop `while fresh_ok < 2 and draws < 12`: at most one `run_target` per draw. Planted `range(2)`. |
| fixture4 | 2 targets × 4 arms = 8 | `cmd_fixture4` |
| controls | 2 labels × (identity + raw_x) + 4 planted arms = 8 | `cmd_controls` |
| anchor | 0 | both call sites `gb_only=True` |
| build, aggregate, aggregate_a1 | 0 | no `solve()` call |
| cells | len(cells) × targets_per_cell = 5 × 20 = 100 | `_run_cell` calls `solve()` at most once per target. Cells with disposition `not_attempted`, refused or condition-unmet cells make 0 calls but are counted (upper bound). |
| controls_a1 | 2 | two planted arms |
| contingency | max over the plan's non-gate packages = 100 | contingency_rule: re-runs, with identical driver arguments, one non-gate package with failure_class infrastructure_error. Gate packages and controls_a1 are never replaced. |

| plan | packages | subtotal |
|---|---|---|
| trial-plan-v2.json | 2 fixture (96 + 96) + anchor 0 + controls 8 + fixture4 8 + 3 build 0 + 18 cells × 100 + aggregate 0 + 4 contingency × 100 | 2408 |
| trial-plan-v2-a1.json | controls_a1 2 + build 0 + 6 cells × 100 + aggregate_a1 0 + 2 contingency × 100 | 802 |

**S_ub = 3210.** The per-package table is in `summary.json` under `CR-2.S_ub_derivation`.

### K (CR-2 formula: least k in {2, 3, 4, 5} with S_ub · u_max^(k+1) ≤ 0.01)

| k | S_ub · u_max^(k+1) | ≤ 0.01 |
|---|---|---|
| 2 | 0.000684231198696659 | yes |
| 3 | 4.087290314508129e-06 | yes |
| 4 | 2.4415639255991048e-08 | yes |
| 5 | 1.4584807890027001e-10 | yes |

**K = 2** by the formula.

**Assumptions the formula rests on** (the draft's own, restated here and not assessed):

- attempts spaced at least 2 s apart in fresh processes are independent (SJ-2);
- the ladder-prime rate does not exceed u_max (SJ-4).

Section 7 records time-structure observations relevant to the first assumption.

## 6. CR-1 and CR-3

### CR-1: other nondeterminism

The formula is applied per input, pooled over every solve of C-1a, C-1b, C-1c and C-2 whose child exited ok. C-1a and C-1b share the event input. Each C-2 output is also compared with the archived output.

It checks for:

- a different printed quotient dimension;
- two ok-classified outputs with different parsed solution sets, eliminating degree or D;
- an outcome-class change other than to or from the NSP signature;
- a C-2 parsed disagreement with the archived output.

**One instance was found (CR-1's condition is met by 1 instance):**

- **Input:** `event/fx_reg0_torsion_S3_norm` (p' = 1033; sha256 `541b57b9…`).
- **Solves:** `C-1a#0` (output `201812d43b7c7a9dab2c8a1270e2a9a022a671ccb4992775aa1e431b48ef0569`, the world B bytes) and `C-1a#247` (output `ec54fd1520eafb2216fc1c6606db5f660b8867f8d176631b9da950acf10248ee`).
  - **C-1a#0 group (996 solves in total):** all of C-1a except #247–#250, plus all of C-1b.
    - D = 64, eliminating degree 64, square-free, 2 F_p-rational solutions.
    - Solution-set sha256 `611489e3aa0054455a1b788668029fae72ba0bd574378d88d753e41f2073e879`.
  - **C-1a#247 group:** #247, #248, #249 and #250.
    - Classify outcome `ok`; D = 64, eliminating degree 64, square-free, 2 F_p-rational solutions.
    - Solution-set sha256 `254892d948106519d8e42592b9505565460b86a41de3ebe74a01db0ac779e6ab`, which differs from the other group.
- **What is equal and what differs:**
  - Same: printed quotient dimension (64 in all 1000), header (char 1033, nvars 3, degree 64, linform [0, 0, 1]), eliminating and denominator polynomials.
  - Differs: at least one parametrisation polynomial. This is where the parsed solution sets diverge.
- **Timing:** the four solves ran back to back.
  - Starts: 22:58:44.195789Z, 22:58:44.399989Z, 22:58:44.604469Z and 22:58:44.808788Z.
  - Ends: 22:58:44.399715Z, 22:58:44.604172Z, 22:58:44.808466Z and 22:58:45.013472Z.
  - #246 (start 22:58:43.99) and #251 (start 22:58:45.01) gave the world B bytes.
- **NSP:** none of the four has the NSP signature. They are not the world-A event (bytes differ from `d2878f4f…`).
- **Retention:** the output bytes and all four solves' logs are in `distinct-outputs.tar.gz`.

No printed-quotient-dimension difference and no outcome-class change occurred in any input of the four classes. There was no C-2 parsed disagreement with an archived output.

### CR-3: the REG-1 (d) branch

The formula: d-parsed if, for any C-2 input, an ok-classified output differs in bytes from another ok-classified output of the same input, or from the archived `.ms.out`, while its SE-4 (d) parsed comparison agrees. Otherwise d-bytes.

**Branch by the formula: d-parsed (1 instance).**

- **Input:** `ac4487/fx_reg1_S3_rescaled`.
- **Solves:** `C-2#95` to `C-2#99` (5 solves, back to back; starts 23:33:19.102550Z to 23:33:19.927990Z, all within UTC second 23:33:19).
- **Output:** `7e283c2834f024429d50347a1cfb42d560b4eaf1b5643a818c96c9e58cb45f06`.
- **Archived output and #0–#94:** `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2`.
- **Parsed comparison agrees:** param, header degree 64, eliminating degree 64, square-free, solution set empty in both (0 F_p-rational solutions), D = 64.

All other 35 C-2 inputs gave, in all 100 solves each, output bytes identical to the archived RUN-GFPN-ac4487 `.ms.out`.

## 7. Time structure (observations for the independence assumption; no reading)

| label | distinct UTC start seconds | children per start second (count of seconds) | consecutive pairs with both children inside one UTC second | of which identical output bytes |
|---|---|---|---|---|
| C-1a | 103 | 5 per second: 90; 4: 12; 2: 1 | 295 | 295 |
| C-1b | 500 | 1 per second: 500 | 0 | 0 |
| C-1c | 718 | 5: 630; 4: 87; 2: 1 | 2049 | 2049 |
| C-2 | 738 | 5: 649; 4: 88; 3: 1 | 2102 | 2102 |
| C-3c-event-c0 | 41 | 5: 36; 4: 5 | 118 | 118 |
| C-3c-event-c1 | 41 | 5: 36; 4: 5 | 119 | 119 |
| C-3c-ac4487-c1 | 37 | 5: 32; 4: 5 | 82 | 82 |

- Every consecutive pair of children that both started and ended within the same UTC second produced byte-identical output: 4765 of 4765 pairs over all labels.
- Both differing-output groups (C-1a #247–#250 and C-2 fx_reg1_S3_rescaled #95–#99) consist of consecutive solves inside one UTC second.
- The C-1b solves, each in its own second, gave the world B bytes 500 of 500 times.

**How n_c relates to seconds:** the CR-2 formula counts solves. C-1a's 500 solves fell in 103 distinct start seconds; C-1c's 3500 in 718; C-2's 3600 in 738. These counts are reported next to n_c. They do not replace it.

## 8. C-3 diagnostics

### C-3 (a): world A versus world B (bundle; no solve)

| field | world A | world B |
|---|---|---|
| output sha256 | `d2878f4f2b276162c78fd8b7fb31ae2fbc0a04984222a344fed047fef9cf07da` | `201812d43b7c7a9dab2c8a1270e2a9a022a671ccb4992775aa1e431b48ef0569` |
| header (char, nvars, degree, varnames, linform) | 1033, 3, 64, [e1, e2, e3], [0, 0, 1] | 1033, 3, 64, [e1, e2, e3], [0, 0, 1] |
| printed quotient dimension | 64 | 64 |
| "Degree of the square-free part" | 63 | (not printed) |
| eliminating degree (parsed) | 63 | 64 |
| square-free flag (parsed) | true | true |
| classify_solve | degenerate_parametrisation: "eliminating polynomial degree 63 != quotient dimension 64 (the minimal polynomial is not square-free: non-radical ideal)"; NSP (SE-1 (ii)) | ok; D = 64 |
| F_p-rational solutions parsed | 1 | 2 |

Verbatim unified diff of the msolve stderr (`.ms.err`), which carries the FGLM lines:

```diff
--- world_A/fx_reg0_torsion_S3_norm.ms.err
+++ world_B/fx_reg0_torsion_S3_norm.ms.err
@@ -19,11 +19,9 @@
 Dimension of quotient: 64
 [64, 12], Non trivial / Trivial = 18.75%
 Density of non-trivial part 94.79%
-Time spent to generate sequence (elapsed): 0.00 sec (0.38 Gops/sec)
-Degree of the square-free part: 63
-[64, 63, 63]
+Time spent to generate sequence (elapsed): 0.00 sec (0.40 Gops/sec)
 Time spent to compute eliminating polynomial (elapsed): 0.00 sec
-Elimination polynomial is not squarefree.
+Elimination polynomial has degree 64.
 Time for rational param:          0.00 (elapsed) sec /  0.00 sec (cpu)
 
 ------------------------------------------------------------------------------------
```

Verbatim unified diff of the msolve stdout (`.ms.log`):

```diff
--- world_A/fx_reg0_torsion_S3_norm.ms.log
+++ world_B/fx_reg0_torsion_S3_norm.ms.log
@@ -29,11 +29,11 @@
 ---------------- TIMINGS ---------------
 overall(elapsed)        0.00 sec
 overall(cpu)            0.00 sec
-select                  0.00 sec  11.8%
-symbolic prep.          0.00 sec  15.1%
-update                  0.00 sec  19.6%
-convert                 0.00 sec  28.6%
-linear algebra          0.00 sec   9.8%
+select                  0.00 sec  12.6%
+symbolic prep.          0.00 sec  14.5%
+update                  0.00 sec  21.3%
+convert                 0.00 sec  25.8%
+linear algebra          0.00 sec   8.9%
 reduce gb               0.00 sec   0.0%
 -----------------------------------------
 
```

The F4 rounds in stdout (first 28 lines) are identical in the two worlds. Both diffs above are reproduced verbatim from `c3a/` in `distinct-outputs.tar.gz`.

### C-3 (b): help text, version, search

- **How it ran:** `msolve -h` ran through the frozen `run_child` with the 10737418240 cap (read back); exit code 1, which the frozen runner labels `crashed` because it is nonzero.
- **Help text:** the full help text (sha256 `281e5fb5663bb35f2360445ebbb4cc68a0d4eaee2d512cc877383e27f41d2d3b` over stdout + stderr) is archived verbatim as `c3b/msolve-h.stdout` and `c3b/msolve-h.stderr` in `distinct-outputs.tar.gz`. It matches, line for line, the dispatcher's `-c GEN` excerpt:
  > "-c GEN Handling genericity: If the staircase is not generic enough, msolve can automatically try to fix this situation via first trying a change of the order of variables and finally adding a random linear form with a new variable (smallest w.r.t. DRL) / 0 - Nothing is done, msolve quits. / 1 - Change order of variables. / 2 - Change order of variables, then try adding a random linear form. (default)"
- **Version:** msolve 0.6.5 prints no version string. `-h` shows none, there is no version option, and the `-v 2` log shows none. The installed version is from dpkg: `msolve 0.6.5-1build2 amd64`, `libmsolve-0.6.5 0.6.5-1build2 amd64`. The frozen `v2_common.msolve_version()` reads the same dpkg field.
- **Search of the help text for seed / random / generic:** 3 lines, all inside the `-c GEN` entry (help lines 53, 56 and 61). **No seed option exists in the help text.** Other options are described as probabilistic: `-l 42` and `-l 44`, "(probabilistic)".

### C-3 (c): `-c 0` and `-c 1`. DIAGNOSTIC ONLY; nothing is adopted.

| label | solves | classify outcomes | NSP | distinct outputs | bytes = default-flag modal | bytes = archived ac4487 | bytes = world B | bytes = world A |
|---|---|---|---|---|---|---|---|---|
| event input, `-c 0` | 200 | ok 200 | 0 | 1 | 200 | n/a | 200 | 0 |
| event input, `-c 1` | 200 | ok 200 | 0 | 1 | 200 | n/a | 200 | 0 |
| each ac4487 input, `-c 1` (36 × 5) | 180 | ok 120; positive_dimensional 60 | 0 | 25 | 120 | 120 | n/a | n/a |

- **The 60 positive_dimensional solves** are all 5 solves of each of the 12 `raw_x` / `raw_u` inputs (fresh1, fresh2, planted0, planted1, reg0, reg1).
  - Under `-c 1`, msolve printed "Staircase is not generic" and "=====> Computation failed <=====" and wrote an empty output file (sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
  - The frozen classifier reads that as "output does not parse as a zero-dimensional parametrisation", which maps to positive_dimensional.
- **The same 12 inputs under the default flags:** every default-flag solve (C-1c at 1033 and C-2 at 4111) carries linform `[1, 2, 3, 1]`. The log reads "Changing variable order for possibly more generic staircase", then "Adding a linear form with an extra variable … [coefficients of linear form are k^0 …]" and "… k^1 …".
- **The other 24 ac4487 inputs** under `-c 1` gave bytes equal to the archived output, 5 of 5 each.

### C-3 (d): source. Obtained; provenance `retrieved`.

**How the source was obtained:**

- **Upstream refused.** The GitHub tag `https://github.com/algebraic-solving/msolve/archive/refs/tags/v0.6.5.tar.gz` was refused by the session's GitHub policy. The proxy returned the JSON body: "GitHub access to this repository is not enabled for this session. Use add_repo to request access. …". That route was not pursued further.
- **Ubuntu source package used instead.** It is the distribution's source package for exactly the installed version, fetched from `https://archive.ubuntu.com/ubuntu/pool/universe/m/msolve/`:
  - `msolve_0.6.5-1build2.dsc`;
  - `msolve_0.6.5.orig.tar.gz`, sha256 `30e3712eab4077438e2b3228d5958adb7e8488e523244a02320f80bd8c412c89`, equal to the dsc's Checksums-Sha256;
  - `msolve_0.6.5-1build2.debian.tar.xz`, sha256 `ef2099a74d6de7421c33e8aeb92aeaeccbd26ff5e8d7d807056c1fcf40fbed44`, equal to the dsc.
  - The debian tarball carries no `patches/` directory.
  - Read by: this Executor, TASK-20260923-6599cf, 2026-09-23.
- **Link to the installed binary:** `nm -D /usr/bin/msolve` lists undefined `srand`, `rand` and `time` (GLIBC). `libneogb-0.6.5.so` lists undefined `rand` and `gettimeofday`. That the binary was built from this exact source is the distribution's packaging claim; it was not rebuilt here.

**Where randomness enters, with file and line in `msolve-0.6.5/src`:**

1. **FGLM Wiedemann / Berlekamp–Massey projection vector.**
   - `fglm/fglm_core.c` lines 1424–1443 (`initialize_fglm_data`) call `srand(time(0));` at line 1434. Lines 1435–1437 then fill `data->vecinit[i] = (CF_t)rand() % prime`.
   - It is called from `nmod_fglm_compute_trace_data` (line 1693), which the prime-field path calls at `msolve/msolve.c` line 1824.
   - The minimal polynomial is computed from the projected sequence (`compute_elim_poly`, lines 820–826; `compute_minpoly`, lines 899–917).
   - `make_square_free_elim_poly` (lines 830–864) prints "Degree of the square-free part: %ld" and "[dimquot, dim, deg]" when the Berlekamp–Massey polynomial is not square-free or its degree `dim` differs from `dimquot`.
   - `nmod_fglm_compute_trace_data` then branches at line 1743 (`dimquot == dim` prints "Elimination polynomial has degree …", line 1746) or else prints "Elimination polynomial is not squarefree." (line 1763) and computes the parametrisation of the radical.
   - World A's log lines ("Degree of the square-free part: 63", "[64, 63, 63]", "Elimination polynomial is not squarefree.") are the strings of this branch.
   - **Seed:** `time(0)`, i.e. wall-clock seconds, re-seeded in each process at FGLM start. No seed option or environment input exists.
2. **Genericity handling (`-c`), prime-field branch (`msolve/msolve.c` lines 4875–4935).**
   - When `b == 1` (staircase not generic), `-c ≥ 1` first calls `change_variable_order_in_input_system`. Then, only for `-c 2`, it calls `add_linear_form_to_input_system` (lines 532–626). That function is **deterministic**: its coefficients are k^(bcf−1) over variable index k (message at line 615).
   - When `b == 2`, `-c 2` calls `add_random_linear_form_to_input_system` (lines 634–750), which calls `srand(time(0));` at line 718 and `rand()` at lines 725–741. It prints "[coefficients of linear form are randomly chosen]" (line 716).
   - No solve in this characterization printed that message. The default-flag raw-arm solves printed the deterministic k^j message.
3. **Other `rand()` sites (not seeded separately):**
   - `neogb/la_ff_32.c` line 188, and in `la_ff_8.c`, `la_ff_16.c` and `la_ff_32.c` inside linear-algebra routines, including the probabilistic `-l 42/44` variants;
   - `fglm/fglm_core.c` lines 693–694 and 1260/1368;
   - `srand(time(0))` for multi-modular prime choice at `msolve/msolve.c` 2153, 4506 and 4689, and `lifting-gb.c` 1247 (the rational-coefficient paths).
   - Which of these the frozen argv (`-l` default 2, prime field) reaches beyond item 1 was not traced.

**What the source reading does and does not establish:**

- **Established from the source:** a `time(0)`-seeded random vector enters FGLM on every prime-field `-P 1` solve. A projected minimal polynomial of degree `dim < dimquot` produces exactly the world-A log signature.
- **Consistent with section 7:** same-second children always gave identical bytes, and every differing output occurred in one-second runs.
- **Not established here:** whether the C-1a #247–#250 parametrisation difference (section 6) arises in the same FGLM step. The eliminating polynomial agreed, but a parametrisation polynomial differed. It is recorded as an observation.
- **Standing:** this is source reading with provenance `retrieved`. Its use is for the approval act under CR-4.

## 9. C-4: read-only census of retained msolve logs

- **Scope:** all 50 run directories under `experiments/EXP-GFPN-05ff43/runs/`: the 48 v1 packages, RUN-GFPN-ac4487 and RUN-GFPN-3377f1.
- **Logs counted:** `*.ms.log` in the package root (v1) and in `solver/` (v2), each read together with its `.ms.err` where one exists. The RUN-GFPN-ac4487 files were hash-verified against the TASK-20260923-0fa03f receipt.
- **Prime and m:** taken from the manifest command (`--p`, `--m`) or the `cell:` string. Where the manifest gives neither, m comes from the log file name and is labelled.
- **Counts only; no D value is read.**
- **The v1 logs** come from runs with `-t 4` (a different invocation from the frozen v2 argv).

| prime and m | retained logs | logs printing a quotient dimension | NSP signature (card) | "not squarefree" text | square-free part below dimension | "not square-free" text (separate; not the card's signature) | packages |
|---|---|---|---|---|---|---|---|
| p=4111 m=3 | 96 | 96 | 0 | 0 | 0 | 0 | RUN-GFPN-49f7c5, RUN-GFPN-5f9840, RUN-GFPN-ac4487, RUN-GFPN-cdf887 |
| p=4111 m=4 | 145 | 45 | 0 | 0 | 0 | 0 | RUN-GFPN-137b58, RUN-GFPN-73e6fd, RUN-GFPN-84d6b3, RUN-GFPN-b1f5d2, RUN-GFPN-ce58c1, RUN-GFPN-f888a7, RUN-GFPN-fa08ca, RUN-GFPN-fb0726 |
| p=4111 m=5 | 5 | 0 | 0 | 0 | 0 | 0 | RUN-GFPN-61a67b, RUN-GFPN-805701, RUN-GFPN-8f1b50 |
| p=262151 m=3 | 60 | 60 | 0 | 0 | 0 | 0 | RUN-GFPN-64df61, RUN-GFPN-7580cd, RUN-GFPN-d3f21e |
| p=262151 m=4 | 85 | 45 | 0 | 0 | 0 | 0 | RUN-GFPN-26a539, RUN-GFPN-2926e7, RUN-GFPN-7795bd, RUN-GFPN-9424ba, RUN-GFPN-c7a3e9 |
| p=16777291 m=3 | 60 | 60 | 0 | 0 | 0 | 0 | RUN-GFPN-ae92c4, RUN-GFPN-afc06e, RUN-GFPN-d4415d |
| p=16777291 m=4 | 85 | 45 | 0 | 0 | 0 | 0 | RUN-GFPN-4892c7, RUN-GFPN-7b9ab6, RUN-GFPN-9172cf, RUN-GFPN-adaec1, RUN-GFPN-d8e114 |
| p=16777291, m not in manifest (cell anchor-n4-p16777291) | 5 | 0 | 0 | 0 | 0 | 0 | RUN-GFPN-61bba9 |
| p=65551, m not in manifest (cell anchor-n4-p65551) | 5 | 0 | 0 | 0 | 0 | 0 | RUN-GFPN-bbed6f |
| p not in manifest (cell validate), m=3 from log file name | 10 | 10 | 0 | 0 | 0 | 0 | RUN-GFPN-4892a8, RUN-GFPN-650471, RUN-GFPN-a0fb62, RUN-GFPN-b336b6, RUN-GFPN-f55fbd |
| p not in manifest (cell validate), m=4 from log file name | 9 | 9 | 0 | 0 | 0 | 0 | same five |
| **total** | **565** | **370** | **0** | 0 | 0 | 0 | |

- **Logs not retained:** 12 packages hold no msolve log: RUN-GFPN-3377f1, RUN-GFPN-405554, RUN-GFPN-40908e, RUN-GFPN-42a000, RUN-GFPN-44084f, RUN-GFPN-4a0f31, RUN-GFPN-5632dc, RUN-GFPN-a716d4, RUN-GFPN-c16d20, RUN-GFPN-ca7b88, RUN-GFPN-db0f68 and RUN-GFPN-e633a2. RUN-GFPN-3377f1 failed before any measurement.
- **What the census covers:** retained logs only. It says nothing about solves whose logs were not kept.
- **The anchor logs** (`-g`-style runs) print no quotient dimension.

## 10. Supplementary diagnostic (NOT part of any reading; unexpected observation, preserved)

**Why this was run:** the CR-1 instance involves two ok-classified outputs with different F_p-rational solution sets. After the run, a scratch script substituted each parsed solution into the input system, using the frozen `v2_driver._parse_ms_file` and `v2_solver.substitute`. This is the check the frozen driver makes (`n_sub_fail`), which this card sets to 0.

**Bytes read:** the outputs are those archived in `distinct-outputs.tar.gz` or in the bundle and ac4487.

**Script:** `<scratch>/subst_diag.py`, sha256 `d241dcebd25d4296a2e64b76a3f7206516e7b12191cd5ae9f2ec59b58635f32c`. Output sha256 `79d4e6f00dd9cb674b44e65fc9b0a7fa22e6373b2f8dfe0f6c4468596d3f4175`. The core of the script is:

```python
names, p, eqs = v2_driver._parse_ms_file(input_ms)
kind, payload = v2_solver.parse_msolve_param(output)
sols, info = v2_solver.rational_solutions(payload, p, len(names))
n_satisfy = sum(1 for s in sols if v2_solver.substitute(eqs, s, p))
```

| input | output | parsed F_p-rational solutions | satisfy the input system |
|---|---|---|---|
| event (p' = 1033) | world B / modal `201812d4…` | (685, 1001, 911), (822, 543, 295) | 2 of 2 |
| event | world A (NSP) `d2878f4f…` | (685, 1001, 911) | 1 of 1 |
| event | C-1a#247–#250 `ec54fd15…` | (305, 278, 911), (1004, 160, 295) | **0 of 2** |
| ac4487 fx_reg1_S3_rescaled (p' = 4111) | archived `3b232b2b…` | none | n/a |
| ac4487 fx_reg1_S3_rescaled | C-2#95–#99 `7e283c28…` | none | n/a |

**Observation:**

- **The mismatch:** in the four C-1a outputs `ec54fd15…`, the last coordinate (the root of the eliminating polynomial) matches the modal output, but the other two coordinates do not satisfy the input system.
- **How the frozen driver would treat them:** substitution with this input as the system gives `n_sub_fail = 2`, so the classification is `degenerate_parametrisation` with the substitution reason (`v2_solver.py` line 507). The draft's SE-1 excludes that reason from the NSP signature.
- **Caveat:** in a real package the driver substitutes into the descended system from which the `.ms` file was written. The two are assumed equivalent here and this was not checked.
- **Status:** this observation enters no CR reading. CR-1 fires on the parsed solution sets alone.

## 11. Retention (CH-7)

`distinct-outputs.tar.gz` is deterministic (mtime 0, uid/gid 0, sorted). It holds:

- one copy of each distinct output byte string per input: 86 files, under `distinct-outputs/<set>/<stem>/<sha256>.ms.out`, with `distinct-outputs/index.json` mapping each sha256 to its solves;
- the `.ms.log` and `.ms.err` of every solve whose output differs in bytes from its class reference:
  - C-1a #247–#250;
  - C-2 fx_reg1_S3_rescaled #95–#99;
  - the 60 C-3c-ac4487-c1 raw-arm solves (whose reference is the default-flag modal output).
  - There were no NSP-signature solves, so no NSP logs;
- the C-3 (a) diffs (`c3a/`);
- the C-3 (b) help output (`c3b/`).

Everything else is kept as sha256 only, in `solves.jsonl`. Work files remain in `<scratch>/work`, which is not durable.

## 12. Deviations, disclosures and interruptions

1. **Two msolve invocations outside `run_child` before the harness existed.** During orientation, `/usr/bin/msolve -h` and `/usr/bin/msolve -V` were run directly in the shell, without the cap. `-V` was rejected as an invalid option. Neither solved anything. CH-2 requires every msolve child to go through `run_child`; these two did not. The recorded C-3 (b) help text comes from the capped child in the harness.
2. **Harness defect found and fixed before any solve.** A dry run of `analyze` on archived outputs (no msolve launched) showed that toy and ac4487 input stems coincide. Per-input grouping was changed to key by input set plus stem. Two cosmetic edits were also made. The harness sha256 at launch (`a99e9e1c…`) equals the final file, and no edit was made after the first solve.
3. **Manual scratch extraction.** For orientation, the bundle was first extracted manually into `<scratch>/bundle` and the event hashes were checked by hand. The harness later extracted it afresh into `<scratch>/work/bundle`. Both locations are scratch; nothing was extracted into the repository.
4. **C-3 (d) source route.** The upstream GitHub tag was refused by the session's GitHub access policy (message quoted in section 8). No workaround was attempted for that route. The distribution's source package, which the card names as an alternative, was fetched from archive.ubuntu.com through the configured proxy.
5. **Harness choices where the card is silent:**
   - C-3 (c) solves ran back to back.
   - The C-1c modal-output tie rule is the smallest sha256 (no tie occurred).
   - CR-1 is pooled per input over all four classes; C-1a and C-1b share the event input.
   - C-2 outputs are also compared with the archived output (CR-3's "a parsed disagreement is CR-1").
   - Start and end timestamps are taken around `run_child` (section 3).
6. **CH-3 (d) superset.** The integrity check verified 146 RUN-GFPN-ac4487 files (inputs, outputs, logs, err, manifest, raw-result), all of which were read, against the receipt.
7. **Pre-harness reads of ac4487 files.** Before the harness, I read RUN-GFPN-ac4487 `raw-result.json` (for archived per-solve wall times) and the 72 solver `.ms` / `.ms.out` files. All were hash-checked against the receipt at that time and again by the harness.
8. **Supplementary substitution diagnostic (section 10).** This goes beyond the card's design. It is reported separately and enters no reading.
9. **Frozen host lock.** The frozen default host lock file `/tmp/gfpn-v2-solver.lock` (pre-existing) was used as `run_child` requires. It is outside the repository.
10. **Interruptions:** none. No class was re-run, and there is no `-r2` label.
11. **`analyzed_at`** in `summary.json` is the analysis time. Re-running `analyze` on the same work directory reproduces every other field.

## 13. Artifacts

| path | sha256 |
|---|---|
| experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/char_msolve.py | a99e9e1cc5f6995c3b56e07c9f9efdca182a140b699ac35ef9debb478e407ac8 |
| experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/summary.json | 66c5c39600a268ba3a308f22cf426e699f75e68736ef2a8768dc821ea92cbb48 |
| experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/solves.jsonl | eb9e3c446ac1bcc08a74e2ff1baea439d8d4084c89df6b0dcacd5d4e443ea644 |
| experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/distinct-outputs.tar.gz | 05a0817173b7335535ba825c0a0ba813faa3659f83bc6ed7592cdc44b9424994 |
| experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/characterization.md | (this file; hash reported in the Executor's return) |

**Tested scope:**

- msolve 0.6.5 (Ubuntu 0.6.5-1build2) at `-t 1` with the frozen v2 argv, on one 4-CPU host.
- Toy EcGFp5-shaped inputs at p' = 1033 (36 inputs of the stage-R1 toy G1 package).
- The 36 RUN-GFPN-ac4487 fixture inputs at p' = 4111 (n = m = 3).
- Known-scalar, toy public parameters.

**Transfer:** nothing here transfers to p' = 262151, 16777291 or 1073741831, or to p = 2^64 − 2^32 + 1. The draft's own transfer assumption for CR-2 (the ladder-prime rate does not exceed u_max) is restated, not tested.
