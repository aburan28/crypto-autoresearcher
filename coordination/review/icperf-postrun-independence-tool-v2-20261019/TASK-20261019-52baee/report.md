# Independent checker review: TASK-20261019-52baee

## Scope and verdict

I reviewed only the corrected `tools/check_review_independence.py` admission behavior and its exact frozen-plan binding under `REVIEW-ICPERF-INDEPENDENCE-CHECKER-V2-20261019`. **V1: holds. V2: holds.** The verdict is for the combined CLI gate supplied with the externally frozen SHA-256 below. It does not authenticate whether the scientific reviewers' `sources_read` declarations are truthful, validate their P1–P4 conclusions, change the historical run's output status, or establish a cost or performance result. No solver or scientific trial was run.

The independently checked baseline was the frozen P1–P4 plan plus only the sealed Red Team `attestation.yaml` and the Validator's additive `attestation-addendum.yaml`. I did not read any original scientific reviewer report, including any of the three paths in this tool round's `blind_rederivation.blind_from`.

## Pre-code derivation and read order

1. I read `AGENTS.md`, `agents/validator.md`, `ledger/handoffs/TASK-20261019-52baee.yaml`, and this tool round's `review-plan.yaml`. The handoff and tool review plan were read before the checker or author tests.
2. I then read `coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml` and independently computed its SHA-256 with `shasum -a 256`: **`1242a62527951bd0f2bb7f908fd2be50e85dcd79cf7a0db0dd09d69de64a29db`**, matching the external pin. Before reading the checker or author tests, I derived these exact associations from that file:

   | ID | Owner | Full statement |
   | --- | --- | --- |
   | P1 | `TASK-20261019-bb87e3` | An independently derived inventory of permitted original raw archive members has exact paths, sizes and SHA-256 values, with omitted or duplicate members identified without a producer inventory. |
   | P2 | `TASK-20261019-bb87e3` | The frozen plan requires two missing top-level outputs; public inputs specify exactly one monitor control and three positive requests; a satisfying witness refutes a contradictory no-solution assertion. |
   | P3 | `TASK-20261019-02a5c2` | The candidate manifest and bundle agree with all original run files, failed release, Git anchors and explicit absence statements; the later task does not claim authorship of earlier candidate bytes. |
   | P4 | `TASK-20261019-02a5c2` | Monitor and three positive stops retain their raw censor classes, and missing end-to-end terms remain unmeasured. |

3. From the tool review plan, before inspecting implementation, I recorded the expected false-fixture labels: `empty_statement`, `swapped_statements`, `scalar_multi_joint`, `wrong_owner`, `blind_leak`, and `missing_attestation`. The handoff additionally required wrong ID, duplicate, missing verdict, invalid verdict, and sibling-read refusals. I then read the source snapshot receipt, the two permitted original attestation artifacts, the snapshot-bound queue, and only afterward the checker and its author tests.

## Source custody and admission

The snapshot receipt at `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-b541a8/snapshot-receipt.json` identifies content commit `b271ae5e1534db2fe6958af7dae1cba2fe8742f7`. That commit is an ancestor of the exact published review head `efe5933f95e1091eb38e63284d3ad96cb1732b78`; its changed-path list contains exactly the checker and its focused test file. The receipt was committed separately at `11a4af22ef7cf4f5cf26e01008748e6afe673dd5`, whose parent is the content commit. The receipt's bytes at that commit and in the worktree both hash to `63181c17e02bf8149c59c1c9594d48839189073ef97d1915ba0de059cac73d9a`.

| Source | Receipt SHA-256 | Worktree SHA-256 | Content-commit blob SHA-256 |
| --- | --- | --- | --- |
| `tools/check_review_independence.py` | `546d6ccaf03194804f5f551f609e0c5a32c1512feeaa567c22028a65df94dab0` | same | same |
| `tools/test_check_review_independence.py` | `220567fd38609ab947e659a21eabd28fdfe36d083dec6e401a57c2a2e2bd1477` | same | same |

The direct pinned command was:

```sh
python3 tools/check_review_independence.py --plan coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml --expected-plan-sha256 1242a62527951bd0f2bb7f908fd2be50e85dcd79cf7a0db0dd09d69de64a29db --reports coordination/review/icperf-prime63-m2-postrun-20261019/TASK-20261019-02a5c2/attestation.yaml coordination/review/icperf-prime63-m2-postrun-20261019/TASK-20261019-7b08c1/attestation-addendum.yaml
```

It exited `0`: `PASS: 2 report(s), every joint owned and attested, blindness respected, controls declared`. The additive Validator attestation carries its nested `review_attestation`; a synthetic copy using only the original sealed top-level Validator schema was refused as missing that attestation. This is schema admission, not retroactive verification of the addendum's history.

## Independent falsification controls

I built a fresh in-memory mutation harness from the frozen plan and the two allowed attestations, materialized each case in a self-cleaning temporary directory inside this worktree, and invoked the CLI as a subprocess with `--plan`, `--reports`, and the frozen external pin. The harness did not import or use the author tests as an oracle. There were **21 cases: one genuine baseline passed and all 20 false cases rejected**. Exit `2` denotes plan admission refusal; exit `1` denotes independence-check refusal.

| Case(s) | Result and decisive diagnostic |
| --- | --- |
| Missing pin; altered pin | `2`, explicit IDs require external pin; SHA-256 mismatch. |
| P3 statement empty; P3 whitespace; P3/P4 statements swapped | Each `2`, SHA-256 mismatch against frozen plan. |
| Plan P3 ID changed; plan P4 ID duplicated as P3; plan P3 owner changed | Each `2`, SHA-256 mismatch against frozen plan. |
| Red Team attestation owner changed; P3 claimed as P9; duplicate Red Team attestation | Each `1`, absent owner / unassigned P9 / duplicate attestation respectively. |
| Validator attestation missing; original unadapted top-level schema substituted | Each `1`, P1 and P2 owner filed no recognized `review_attestation`. |
| Red Team verdict omitted; P4 verdict omitted; P3 verdict `pass`; two-joint scalar `holds` | Each `1`, missing verdict, missing P4 entry, invalid enum, or required per-joint mapping respectively. |
| Validator `read_sibling_reports: true`; Red Team attestation path injected into Validator `sources_read` | Each `1`, unauthorized sibling read. |
| A frozen `blind_from` path injected into Validator `sources_read` | `1`, blind-from path read by re-deriver. |

Separately, direct `check()` calls rejected an empty P3 statement, a whitespace P3 statement, and a P3 statement equal only to its ID with a `full statement` diagnostic. The full author test command, `PYTHONPATH=tools python3 -m unittest tools.test_check_review_independence`, ran 21 tests and exited `0`; this was supplemental and did not define my expected outcomes.

**Boundary observed:** the generic `check()` function accepts an explicit-ID joint if its `joint` key is omitted entirely, and accepts a one-character nonempty statement. It cannot establish semantic completeness from arbitrary untrusted plan text. The combined CLI with the frozen external digest rejects either changed plan file before composition, so neither variant is a false acceptance under the reviewed exact-plan admission boundary. Callers must supply the recorded external pin and must not treat direct `check()` as exact-plan authentication.

## Provenance and procedure

The independent session was dispatched as `review-adversarial`, `xhigh`, model `gpt-6-sol`, with no fallback or degradation authorized. That model/effort identification is parent dispatch metadata and was not independently resolved by this runtime. Local environment reported `CODEX_SESSION_ID=01a14825-a902-78c3-8ff1-6a192b46a2ba` and `CODEX_THREAD_ID=01a157c7-15a6-7df1-a599-e571c51169ab`. Conductor allowed the two output paths under `T-4515`, fencing epoch `1`; the snapshot-bound queue task claim was published at commit `da5d0c7ce1` with owner `reviewer-icperf-checker-v2-52baee`.

Procedure deviation in claim publication: `goal_lanes.py claim --publish` created the write-once claim file but its internal `git add` failed because the sandbox could not create the parent repository's worktree `index.lock`. I then used approved escalated `git add`, `git commit`, and `git push` on that exact claim file and verified publication before reviewing checker behavior. This changed no review fixture or frozen source. No other review-plan deviation occurred. The checker emitted one Python `DeprecationWarning` about positional `maxsplit`; it did not affect any exit code or verdict.

## Review attestation

The machine-readable `review_attestation`, complete source inventory, and report hash are in `attestation.yaml` beside this report. I also checked that file against this tool round's plan with `python3 tools/check_review_independence.py --plan coordination/review/icperf-postrun-independence-tool-v2-20261019/review-plan.yaml --expected-plan-sha256 71b842e59e12e54d1e451e3f311ed7874e4de4560c6097825e2f0622c89c3559 --reports coordination/review/icperf-postrun-independence-tool-v2-20261019/TASK-20261019-52baee/attestation.yaml`; it exited `0` with one report, both joints owned and attested, blindness respected, and controls declared. The Coordinator owns the later snapshot, ledger decision, and any scientific composition.
