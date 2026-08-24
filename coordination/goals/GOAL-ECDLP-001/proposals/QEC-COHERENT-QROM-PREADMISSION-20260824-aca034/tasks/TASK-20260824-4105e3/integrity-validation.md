# J2 integrity validation and independent resource recount

`TASK-20260824-4105e3` passes as an admissibility validation of an immutable, reproducible `failed_implementation` receipt. This does **not** pass the implementation. The single reproduction again ran 6 tests with 4 passes and 2 failures, and its 4,145-byte machine result is byte-identical to the archived result. The complete basis-domain signed-translation failure remains a valid implementation failure. Separately, the reported inverse-unload failure is a false negative in the producer's metadata equality checker: the actual qROM unload gate sequence is the exact reverse of load and the qROM/work cleanup obligations hold.

This report owns only `J2-artifact-reproduction-cleanup-and-accounting`. It gives no whole-claim verdict, performs no blind rederivation, changes no research state, and assigns no scientific meaning to an implementation failure.

Procedure deviation: a final worktree-wide `git status --short --untracked-files=all` check printed untracked sibling artifact pathnames. No sibling file, report, receipt, result, message, or content was opened or used, so sibling report/message blindness remains intact; nevertheless, the stricter task prohibition against listing sibling artifact paths was breached. No further worktree-wide status listing was performed.

## Validation report

```yaml
validation_report:
  id: VAL-20260824-4105e3
  task_id: TASK-20260824-4105e3
  run_ids:
    - TASK-20260824-aca034-RUN-1
  artifact_checks:
    - snapshot commit and exact parent verified
    - exact 14-path snapshot diff verified
    - all 13 producer artifact sizes and SHA-256 values verified against current files and committed blobs
    - producer receipt hashes all 12 preceding artifacts
    - patch applies to the pinned upstream commit and reconstructs the archived source byte-for-byte
  metric_recomputations:
    - X/CX/MCX counts and phase splits
    - emitted and logical positive/negative control arities
    - qROM load/unload/total accesses
    - arithmetic primitive invocations
    - register widths, phase intervals, register live intervals, and ancilla peaks
  control_checks:
    - one deterministic implementation/control reproduction
    - zero scientific experiments
    - byte-identical machine result
    - actual load-use-unload cleanup checked independently
  heuristic_validation_checks: []
  cost_model_checks:
    - exact counts apply only to the emitted failed deterministic control instance
    - no cryptographic-scale or leading-coefficient claim accepted
  proof_architecture_checks: []
  verdict: passed
  limitations:
    - implementation remains failed_implementation
    - inverse-unload test failure is a checker false negative, not an operational unload defect
    - creation chronology is self-attested and not recoverable from a single commit, although the full hash chain is verified
    - J2 only; no whole-claim or scientific verdict
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-4105e3/integrity-validation.md
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-4105e3/reproduction-results.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-4105e3/receipt.json
```

## Opening and snapshot binding

- Opening HEAD: `f6ff6f9ffd63dfbaa020fec574d08cc82cbb19cf`; opening worktree clean.
- Committed dispatch binding supplied for this invocation: queue SHA-256 `0aa9718be416fd3cc81121fed596c534d6fa22de52a70f32e7643192d918dbfa`; dispatcher-plan SHA-256 `cb34d235a48eecb2f225907fd618606b0c798ba4c4f213ce83e0e384e66a73e6`; all 10 opening gates true.
- Repository harness preflight: `READY` for native Codex; no fallback, degradation, or Bedrock.
- Snapshot commit: `8f6cdf62ea32629d15d4b99cde41d5e7a3d5ee41`; exact parent `3fc5fd8da1326b853da0383236f845bdfa177177`; reachable from opening HEAD.
- The snapshot commit changes exactly 14 paths: the 13 declared producer artifacts and the content-first snapshot receipt. Every committed blob equals the current file and the recorded size/SHA-256.
- Snapshot receipt: 12,165 bytes, SHA-256 `e2f17708be5a0c7333f840dc123069d4dc3c77d01210a274f753e94aa35a1b02`; byte-identical to the committed blob.
- Snapshot-time queue binding `9796eaebf54173c423c47f0e76df930b6d15ed74d3df9670a7cdaaef3aeeab68` and review-plan binding `7161c6d053e650ae900d777339d06654b3714a492775d132d5d9aa8f525e842d` both match their blobs in the snapshot commit.
- The producer receipt contains and correctly binds all 12 artifacts that precede it. Its `created_last: true` field is present. Chronological creation order cannot be independently recovered from one Git commit; what is independently verified is the complete one-way hash chain and exact commit membership.

### Producer artifact custody

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `circuit-spec.yaml` | 2,441 | `5c297d8e3edb9ea8966ec08407648e706c6845880d8d36aa77270f19213f6e65` |
| `control-matrix.json` | 2,439 | `c7f5f0b295ad4ff12c718611be404af07380184fb9b90bece7b428d020e08b75` |
| `integration/upstream-b5e4c664de212bdb0981d93d70964a1dca1a0ec9.patch` | 28,650 | `ba41596c4723e2a93ae9f733f053e28e7c71509890f2acfb125a9b28d1e0ff8d` |
| `receipt.json` | 3,776 | `c055470a41e7917bd8c45a88da562ebe7546fa229f08a524ba8e67926bf2d194` |
| `resource-accounting.json` | 1,914 | `cab741689b70733ea5156dfda6dedcba64c0b2ee940b368649cb9061fa7a2129` |
| `run/command.txt` | 678 | `37cbdaed0f432c785394f5542690f134f5603e7ad8b4be690a4ba0d9884f38fe` |
| `run/results.json` | 4,145 | `932f7148ba767d7d1c2783673436edef5d109b3e13a862aee6253210dd8880cf` |
| `run/run-manifest.json` | 2,911 | `9a1d49e6a4af8952634e30192a7fb34330c5064aeac7610a9b3d082732b18ac9` |
| `run/stderr.txt` | 29 | `a700bedfb7434ff8ec365cd211a530fe7fbb7bc46232e73f0386fa4e0107bdc6` |
| `run/stdout.txt` | 3,069 | `7c10720d2945b31624d7d35ebd88f39be04df9668b01437c60e0bbeecfe22107` |
| `source-provenance.json` | 2,406 | `e24600b8c849aefc4b3f277162d57e0b476b0e13624d78eb3bea0b2ff2de33f2` |
| `src/coherent_signed_qrom_backend.py` | 27,595 | `523505ff8e5739473cb9a3055eeda409afc86684d896f94e09263eb52e3528f5` |
| `tests/test_coherent_signed_qrom_backend.py` | 8,154 | `598c9725af246d92dcd9edecbdfd75661b4b1e6ce10f4f25ae7133e3ff2f0673` |

## Source and patch custody

The upstream checkout is clean at commit `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`, tree `38fe0708f2d7256f490e4685670dad3eed6bb9a2`. `git apply --check` succeeds there. The patch is one new 736-line file (736 insertions, 0 deletions). Reconstructing that file directly from the patch yields 27,595 bytes and SHA-256 `523505ff8e5739473cb9a3055eeda409afc86684d896f94e09263eb52e3528f5`, byte-identical to the archived implementation source.

## Deterministic reproduction

Exactly one reproduction was run; the scientific-experiment count remained zero. Output destinations were relocated to `/tmp/qec-val4105e3.vWfbTF/` so no immutable producer artifact was overwritten. The source, test, upstream checkout, and substantive arguments were unchanged.

- Process exit: `1`; terminal status: `failed_implementation`.
- Tests: 6 run, 4 passed, 2 failed, 0 errors, 0 skipped.
- Reproduced failures: inverse-unload structural equality checker and complete basis-domain signed translation.
- Reproduced machine result: 4,145 bytes, SHA-256 `932f7148ba767d7d1c2783673436edef5d109b3e13a862aee6253210dd8880cf`; byte-identical to the archived result.
- Reproduced stdout: 3,069 bytes, SHA-256 `678d86877a6a5f9c5ed1568b40011cb4e4f428faa32b3a0875fe87b5e359490b`. It differs from archived stdout only at `Ran 6 tests in 0.680s` versus `0.706s`.
- Reproduced stderr: 29 bytes, SHA-256 `e7cf0762ced5682be41eb0766b0928ec25431c87f8414bcc1e5296940db24ea4`. It differs only in `/usr/bin/time` values: `0.96/0.74/0.06` versus `0.90/0.75/0.05` real/user/sys seconds.

The raw observations, test outcomes, upstream commit/tree, patch hash, and patch-apply result are mutually consistent. Timing is an expected nondeterministic field and is not used as evidence.

## Independent cleanup, liveness, and accounting

I independently reconstructed the fixed curve/table and abstract operation sequence using a separate standard-library counter. It did not invoke the producer's `operation_counts()` or `liveness()` functions. The recount agrees with the archived resource totals.

| Phase | Inclusive operation interval | X | CX | MCX |
| --- | --- | ---: | ---: | ---: |
| derive effective enable | 0–2 | 2 | 0 | 1 |
| qROM load | 3–205 | 150 | 0 | 53 |
| arithmetic | 206–5033 | 4,556 | 0 | 272 |
| qROM unload | 5034–5236 | 150 | 0 | 53 |
| uncompute effective enable | 5237–5239 | 2 | 0 | 1 |
| **Total** | **0–5239** | **4,860** | **0** | **380** |

The emitted IR contains only positive-control MCX gates because every negative polarity is decomposed into a closed X sandwich. Emitted MCX positive-control arities are: arity 2 → 2 gates; arity 3 → 106 gates; arity 18 → 272 gates. There are zero explicit negative-control MCX gates. Before decomposition, the logical positive/negative-control pair distribution is:

| Logical controls | Gates | Logical controls | Gates |
| --- | ---: | --- | ---: |
| 0 positive / 3 negative | 10 | 1 positive / 1 negative | 2 |
| 1 positive / 2 negative | 40 | 2 positive / 1 negative | 40 |
| 3 positive / 0 negative | 16 | 7 positive / 11 negative | 28 |
| 8 positive / 10 negative | 32 | 9 positive / 9 negative | 67 |
| 10 positive / 8 negative | 69 | 11 positive / 7 negative | 45 |
| 12 positive / 6 negative | 25 | 13 positive / 5 negative | 6 |

Those polarities require 2,430 X-sandwich pairs, accounting for all 4,860 X gates. Every pair closes within its operation block.

- qROM terms: 53 load + 53 unload = 106 total accesses under the frozen definition.
- Arithmetic primitive invocations: 272 payload-controlled adjacent Gray-state-swap MCX gates.
- Peak clean ancillas: 12 (`effective_enable` 1 + qROM coordinates/O 7 + masks 4 + arithmetic work 0).
- Peak dirty ancillas: 0.

Exact register widths and inclusive live intervals are:

| Register | Width | Live interval |
| --- | ---: | --- |
| address | 2 | 3–5236 |
| sign | 1 | 5–5234 |
| zero digit | 1 | 0–5239 |
| external enable | 1 | 1–5238 |
| effective enable | 1 | 1–5238 |
| accumulator | 7 | 212–5030 |
| qROM x | 3 | 65–5174 |
| qROM y | 3 | 6–5233 |
| qROM O | 1 | 211–5031 |
| qROM masks | 4 | 13–5226 |
| arithmetic work | 0 | not allocated |

The qROM masks are live across the full arithmetic phase. Arithmetic gates target only accumulator wires. The qROM unload sequence is the exact operational reverse of load; the effective-enable uncompute is the exact inverse of its derivation; every negative-control X sandwich closes. Consequently `qrom_x`, `qrom_y`, `qrom_o`, `qrom_masks`, `effective_enable`, and the zero-width arithmetic workspace are clean at return, while address, sign, zero digit, and external enable are unchanged.

### Inverse-unload checker discrepancy

The producer's observed `inverse_unload_exact=false` is reproducible, but it does not identify an unload defect. In `liveness()`, the comparison reconstructs every reversed unload gate with `logical_access="load"`. Original qROM-load X-sandwich gates have `logical_access=None`; only the central payload-toggle MCX gates carry `"load"`. Tuple equality therefore fails on non-operational metadata attached to X gates. Ignoring the phase/tag/access annotations, the reversed unload gates are exactly the load gates and apply the same self-inverse basis permutations in reverse order.

This correction does not make the implementation valid. The separate complete basis-domain signed-translation control still fails and reproduced independently through the frozen runner. The receipt is therefore admissible as `failed_implementation`, with the inverse-unload reason narrowed to a checker false negative. Neither failure has mathematical or scientific meaning.

## Validity classification

- Validation verdict: `passed` for receipt admissibility.
- J2 joint verdict: `holds` with the checker discrepancy above.
- Run classification: reproducible `failed_implementation` implementation/control run.
- Resource-accounting classification: valid only for the 5,240-operation failed deterministic control instance.
- Cleanup/liveness classification: holds independently; the producer checker result is a false negative.
- Scientific experiment count: 0.
- Scientific transition, claim effect, and whole-claim verdict: none.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260824-4105e3
  role: validator
  requested_policy: review-adversarial
  reasoning_effort: xhigh
  resolved_model_id: gpt-5
  independent_session: true
  fallback_used: false
  degraded_requirements: []
  bedrock_used: false
  joints_owned:
    - J2-artifact-reproduction-cleanup-and-accounting
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - .agents/skills/crypto-autoresearcher-harness/SKILL.md
    - plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/SKILL.md
    - docs/task-lifecycle.md
    - docs/dynamic-subagent-dispatch.md
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/packet.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/review-plan.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/dispatch_queue.json (target TASK-20260824-4105e3 object only)
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/archives/TASK-20260824-74edc9/snapshot-receipt.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/circuit-spec.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/control-matrix.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/integration/upstream-b5e4c664de212bdb0981d93d70964a1dca1a0ec9.patch
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/receipt.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/resource-accounting.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/command.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/results.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/run-manifest.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/stderr.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/stdout.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/source-provenance.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/src/coherent_signed_qrom_backend.py
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/tests/test_coherent_signed_qrom_backend.py
    - upstream Git commit b5e4c664de212bdb0981d93d70964a1dca1a0ec9 and tree 38fe0708f2d7256f490e4685670dad3eed6bb9a2
    - /tmp/qec-val4105e3.vWfbTF/reproduction-raw-results.json
    - /tmp/qec-val4105e3.vWfbTF/stdout.txt
    - /tmp/qec-val4105e3.vWfbTF/stderr.txt
    - /Users/adamburan/.codex/memories/MEMORY.md (keyword search only; no task-relevant hit or reliance)
  read_sibling_reports: false
  sibling_reports_read: []
  sibling_messages_read: false
  sibling_messages_contacted: false
  blind_rederivation_performed: false
  mutual_blindness_respected: true
  procedure_deviations:
    - >-
      A final worktree-wide git status check printed untracked sibling artifact
      pathnames. No sibling content or messages were opened or used; review-content
      blindness remained intact, but the stricter path-listing prohibition was breached.
  verdict: holds
  verdict_scope: J2 only
```

The Coordinator must compose this J2 result with the separately blinded joints. This artifact authorizes no commit, queue edit, ledger record, state transition, producer repair, or scientific/resource promotion.
