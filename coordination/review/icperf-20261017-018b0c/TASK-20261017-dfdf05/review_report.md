# Independent J1–J4 review of EXP-ICPERF-018b0c

Task `TASK-20261017-dfdf05`; review plan `REVIEW-ICPERF-20261017-dfdf05`. This review covers only the frozen ordinary-binary GF(2^61) k11 m=8 pilot, B=316 in each of two bases, two planted positives, eight common public subgroup targets, and four raw channels each. The observations are bounded at 300 seconds per attempted solver call. This report changes no scientific status.

## Custody and scope

I recomputed SHA-256 for all 4 blind files, all 26 fixed raw run files, and all 6 visual report files against their separate content-first snapshot receipts. All matched; marker commits `63a0c29a17c861abd05684a1c1367cb3132c6088`, `72d96cc75e90db9fbe59b0b7fdb970f727beed1e`, and `1a577c84e72fd480e0e019cec64656c9f7153b91` are ancestors of this checkout. Both raw execution receipts report `output_validated` with process and checker exit code 0. I also checked all 21 frozen trial-plan source/input digests, all 64 compressed natural formulas against both compressed and decompressed hashes, both calls-manifest file lists and all tar members against their sizes and hashes. There are 12 positive raw call files (6,178,945 uncompressed bytes) and zero natural raw call files. The run report is the exact separately archived six-file report; its count and scope statements match the underlying run records. A run-time dirty-tree flag is absent from the environment receipts, so this review cannot attest clean-tree execution. The runtime lock fields are null. These are receipt limitations despite the frozen source and input hashes. This is content and output validation, not an execution-proof-chain attestation.

## Joint verdicts

| Joint | Verdict | Exact basis and limit |
| --- | --- | --- |
| J1 common target schedule and order | **holds**, for prepared schedule and executed prefix | Blind J0 has 8 admitted counters 0–7, zero rejected candidates, 32 raw channels, and 64 natural labels. Every scalar, subgroup point, channel point and phi value matches the target manifest. Independent curve multiplication confirms `[4]R_c=Q_i` for all 32 channels. The 64 formula rows have unique `(target, base, channel)` keys and their target constants match the blind schedule. The only executed solver order was weighted positive then local-random positive, matching call indices 0–1. Natural call order was untested in execution because the gate stopped it. |
| J2 accepted model validity | **inconclusive** | Both attempted solver processes ended wall-censored with empty stdout/stderr, no solver status line, zero accepted and zero rejected models, and no point certificate. Thus there is no executed model on which to test the universal statement. Independent checks of the *prepared* known satisfying assignments pass every CNF/XOR row and the full-point sum, but do not turn them into solver output. |
| J3 complete bounded cost/yield classification | **holds** | The planned 66 labels reconcile to two attempted planted controls and 64 natural labels explicitly `not_attempted_after_positive_gate`. Each attempted call has one attempt, 300-second watchdog censoring, no model, and no certified row. Observed distinct certified rows are 0 among attempted calls; natural relation yield and useful rank remain unmeasured. See `cost_reconciliation.json` for all 66 call classes and measured terms. |
| J4 bounded inference | **holds** | The run report confines itself to the one curve/size and says no useful rank, linear algebra, natural relation yield, degree of regularity, unknown-target recovery, matched rho, or full pipeline `S` was measured. The equal archived static formula counts do not imply an observed base advantage. A base-superiority ratio or complete `S` cannot be built from these receipts. |

## Raw-call and cost reconciliation

| Call | State | Solver wall (s) | Sampled user + system CPU (s) | Input bytes | Peak sampled RSS (bytes) | Certified rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0 weighted planted | wall-censored | 300.015663000 | 271.031035392 | 3,089,305 | 207,814,656 | 0 observed |
| 1 local-random planted | wall-censored | 300.021395959 | 243.695254528 | 3,082,298 | 222,822,400 | 0 observed |
| 2–65, eight targets × two bases × four channels | not attempted after gate | no process | no process | no runtime input copy | no process | unmeasured |

The two solver process walls sum to **600.037058959 s**; sampled user CPU is **501.183840256 s** and sampled system CPU **13.542449664 s**. The two call-wrapper walls sum to **600.084675125 s**. Positive driver wall is **601.239486541 s**, including **0.723282459 s** packaging wall; the difference after wrapper and packaging is **0.431528957 s** of other driver overhead, with only **0.012913625 s** separately identified as input decompression. The gated natural driver wall is **0.002667708 s**, including **0.000529750 s** packaging. Two driver wall totals sum to **601.242154249 s**, a sequential stage accounting identity, not a preparation-to-recovery cost. Bundle CPU charges are 0.693361000 s and 0.000530000 s; complete driver CPU was not recorded. Tar sizes are 1,394,072 and 45 bytes, plus manifest sizes 2,429 and 204 bytes. The 6,178,945 raw-call bytes include both XCNF inputs, JSON files and empty solver streams; they should not be added to the compressed tar byte count as if they were disjoint scientific work.

## False-object controls

The two prepared known models have 88,930 weighted and 88,842 local-random assigned variables. I independently evaluated all 89,122 CNF clauses and 62,687 / 62,599 native XOR rows respectively: zero failures in each original model. The seven direct field equations evaluate to zero for each model. Independent curve arithmetic found exactly one of 256 sign assignments matching its planted raw target, with `[4]` of the sum equal to the planted subgroup point.

* **First primary bit flipped:** the first coordinate changes from 4096 to 4097. The weighted membership check fails; the local-random membership check passes, but the first field equation evaluates to `70364449406991` (nonzero) in both arms. With the independently lifted altered first point, none of 256 sign assignments sums to the original raw target in either arm. Holding the remaining full Boolean model fixed also falsifies one native XOR row (`x-7779 1 12 0`) per arm. The altered objects are rejected.
* **Valid row relabeled to a different raw channel:** adding the fixture's order-four torsion point to each planted raw target gives a distinct channel point with the same `[4]` projection. The original eight summands, with every one of 256 sign assignments tested, sum to neither relabeled raw point. An argument checking only projected subgroup equality would accept this false object; exact raw-point comparison rejects it.

The static controls test certificate discrimination. They do not supply a model produced by either timed solver call.

## Obstruction and next check

**Specific obstruction:** at the frozen 300-second cap, neither planted satisfiable formula produced a solver model. The positive gate therefore prevented all 64 natural solver calls. This leaves actual solver-to-certificate viability and natural relation yield unmeasured; it is a censored instrument observation, not evidence of absent relations or a mathematical obstruction. The full-pipeline improvement question also lacks observed useful-rank, linear-algebra, target, verification and matched-rho costs. The Coordinator can link this review to `problems/full-width-ic-arity-grid-unmeasured.md` and decide the next frozen, controlled instrument test. A checkable unblocking event would be an independently validated full-point model from both planted arms under a declared cap, followed by admitted common-target natural calls and complete cost/rank receipts. Longer time alone is not a proof of feasibility; another timeout remains censored.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20261017-dfdf05
  review_plan_id: REVIEW-ICPERF-20261017-dfdf05
  joints_owned:
  - J1 -- The executed panel follows one common target schedule and unchanged fixed call order.
  - J2 -- Every accepted solver model is a valid full-point projected subgroup row.
  - J3 -- Reported bounded cost and distinct certified yield include all attempted and unattempted calls.
  - J4 -- Conclusions remain within bounded relation feasibility on one fixed curve and size.
  sources_read:
  - .claude/skills/review-evidence/SKILL.md
  - /Volumes/SSD990-2/.codex/memories/MEMORY.md
  - AGENTS.md
  - agents/validator.md
  - coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-35c5a6/archives/TASK-20261017-433fb1/snapshot-receipt.json
  - coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-35c5a6/archives/TASK-20261017-bbccbb/snapshot-receipt.json
  - coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-35c5a6/archives/TASK-20261017-da78be/snapshot-receipt.json
  - coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-35c5a6/dispatch_queue.postblind-20261017T1437Z.json
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/blind_counts.json
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/independent_schedule.py
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/report.md
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/review_attestation.yaml
  - experiments/EXP-ICPERF-018b0c/implementation/check.py
  - experiments/EXP-ICPERF-018b0c/implementation/verify_run.py
  - experiments/EXP-ICPERF-018b0c/inputs/formula_manifest.json
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_00_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_01_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_02_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_03_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_04_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_05_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_06_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_local_random_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_local_random_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_local_random_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_local_random_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_weighted_channel_0.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_weighted_channel_1.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_weighted_channel_2.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/natural_07_weighted_channel_3.xcnf.gz
  - experiments/EXP-ICPERF-018b0c/inputs/positive_manifest.json
  - experiments/EXP-ICPERF-018b0c/inputs/target_manifest.json
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/chart.py
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/diagram.svg
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/plot-data.json
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/report.md
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/report.pdf
  - experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/report.typ
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/calls-manifest.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/calls.tar.gz
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/check.stderr.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/check.stdout.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/command.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/environment.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/execution-receipt.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/independent_check.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/launch.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/manifest.yaml
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/raw-result.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/stderr.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-1c8bfe/stdout.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls-manifest.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls.tar.gz
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/attempt-0001/attempt.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/attempt-0001/input.xcnf
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/attempt-0001/stderr.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/attempt-0001/stdout.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/intent.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_local_random/summary.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/attempt-0001/attempt.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/attempt-0001/input.xcnf
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/attempt-0001/stderr.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/attempt-0001/stdout.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/intent.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/calls/positive_weighted/summary.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/check.stderr.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/check.stdout.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/command.txt
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/environment.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/execution-receipt.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/independent_check.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/launch.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/manifest.yaml
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/raw-result.json
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/stderr.log
  - experiments/EXP-ICPERF-018b0c/runs/RUN-ICPERF-712e85/stdout.log
  - experiments/EXP-ICPERF-018b0c/specification.yaml
  - experiments/EXP-ICPERF-018b0c/trial-plan.json
  - ledger/handoffs/TASK-20261017-dfdf05.yaml
  - problems/
  - problems/binary-twist-cofactor-stage1-conflict.md
  - problems/full-width-ic-arity-grid-unmeasured.md
  - problems/icperf-d6-archive-commit-unreachable.md
  - research/icperf_binary_k11_planted_xcnf_20261017/complete/local_random.known_model.txt
  - research/icperf_binary_k11_planted_xcnf_20261017/complete/weighted.known_model.txt
  - research/icperf_binary_k11_root_certificate_20261017/synthetic_controls.json
  - research/icperf_binary_torsion_k11_local_control_20261017/base.json
  - research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json
  - research/icperf_binary_torsion_k11_weighted_20261017/base.json
  - research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json
  - research/icperf_binary_torsion_m8_chain_20261017/chain.json
  - research/icperf_ordinary_binary_fixture_20261017/fixture.json
  - templates/research-records.md
  - tools/check_review_independence.py
  - tools/icperf_binary_root_certificate.py
  read_sibling_reports: false
  blind_j0_inputs_read:
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/independent_schedule.py
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/blind_counts.json
  - coordination/review/icperf-20261017-018b0c/TASK-20261017-fb2b88/review_attestation.yaml
  verdict:
    J1: holds
    J2: inconclusive
    J3: holds
    J4: holds
  verdict_scope: J1 is verified for prepared 64-label schedule and executed two-call positive prefix; natural call
    execution was gated. J2 has zero accepted solver models and cannot be tested on an executed model. J3 and J4
    apply only to the archived bounded stages.
  proves_too_much_controls:
    first_primary_bit_flip: rejected by independent XOR/field/full-point tests for both prepared planted assignments
    relabel_valid_row_to_other_channel: rejected by independent 256-sign full-point comparison for both prepared
      planted assignments
  scientific_state_changed: false
```
