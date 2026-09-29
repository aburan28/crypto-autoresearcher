# J2 integrity validation: deterministic reproduction, exhaustive domains, and qROM cleanup

Task `TASK-20260824-15217b` completed its assigned J2 review work. Content-first custody, deterministic reproduction, the three positive enumeration domains, both coherent alias controls, actual qROM load/use/inverse-unload, and final cleanup all verify. The J2 joint nevertheless **breaks**, and the validation verdict is **failed**, because the archived package is reproducibly a terminal `failed_implementation`: its mandatory payload-row known-false test asserts two aggregate failure markers but the helper emits four, so the runner stops at test 4 and never reaches or serializes its mirror-negative assertions. This is a validator verdict on J2 only, not a whole-claim verdict or a scientific conclusion.

## Authority and launch gates

- The worktree was clean at launch. `HEAD` and its configured upstream both resolved to `1c1f475fbd30be5ac2714b5bb3af91d61e30fc53`.
- Canonical Codex preflight passed: generated bindings, role bindings, Python/dependencies, repository root, and harness doctor were ready. Optional API credentials were unset, while the permitted local backend was ready; no backend request or model probe was made.
- A fresh dispatcher render selected J2 with both dependencies terminal `completed`, no J2 deferral, and all ten gates true.
- The rendered `source_queue_sha256` is `56b2ec2ae50c76158be407e4a63115396928dafa84f70544aec7a107c18ee2e1`; the rendered `plan_sha256` is `b9666a2ece41096bc5e37a8e1387c37b08025364f8590388a8d970dfa37a656f`. Both equal the frozen launch bindings.
- J2 was launched as a fresh independent Validator session with requested policy `review-adversarial`, requested reasoning effort `xhigh`, configured resolved model `gpt-5.6-sol`, `model_verified: false`, and `probe_not_performed`. No fallback, degradation, or Bedrock provider was used.

## Content-first custody

Snapshot receipt `TASK-20260824-9db64e` binds exactly the following 13 producer files. Every current byte size and SHA-256 matches both the snapshot receipt and the Git content at the reachable snapshot commit.

| Producer artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `circuit-spec.yaml` | 3,775 | `cb12ece7008e0d6fe90895d9ec0f9caf278f90a3b5408b42e79311639bc91ad8` |
| `control-matrix.json` | 2,465 | `6f7dccf3320984a8cd1f6bad655cdca6fcd56cea5ce38b22dd40ec4881c43016` |
| `integration/upstream-b5e4c664de212bdb0981d93d70964a1dca1a0ec9.patch` | 27,458 | `74e61d6c4158f547e3912b6f7f86f5a92e9fd27ffd7ad6b64ab5f998102c4086` |
| `receipt.json` | 5,763 | `92cb5f1b060b5878c61f98800b7a123a19bf88bdc7712a7a746fff99ce9f03bf` |
| `resource-accounting.json` | 2,667 | `c549064fd5db72140b8a3a3278ab462c29de59fa37c2c47d77b66c746a185acd` |
| `run/command.txt` | 739 | `95a878d66718d1a701e667aeb352f2a743ebc514a2f8ce133edfa742a3f77b3d` |
| `run/results.json` | 7,373 | `0598f7940e628ddc51f677179f74c403a6e19ab44c3a2e8c9b8e2de4ba54f1fb` |
| `run/run-manifest.json` | 3,058 | `6396c4c9aa7db163844633aa47563140386b6783767c151cfc6fe3a4b8b4a644` |
| `run/stderr.txt` | 31 | `4512a2a7b92fd2f2c09d8b7ad85f8792cdefaaa986323b979f047827cd535c19` |
| `run/stdout.txt` | 1,739 | `e719b801987d623e874c5d08a5c80f4af8852553036ee2be414957fd54a52962` |
| `source-provenance.json` | 2,836 | `52234f35ecf398ff874e42186cc4b6a63df2f148ee2dc523953a49df07c938b7` |
| `src/label_block_qrom_backend.py` | 25,593 | `369692b8dfec765aca793bf432dd916e89ade7ef845919510afcc8ef27013172` |
| `tests/test_label_block_qrom_backend.py` | 7,582 | `ecc5b9f898ef95b4ea9f802d1ba137e33c63859be4a715b0bfb2840048b186a8` |

The content-first snapshot commit is `052bce8a4e90a71206696d59d5ec5a9603df2299`, with parent `17ed85b8f6a53687867b5893771fa725eeeed577`. It is reachable from `HEAD` and changes exactly the 13 producer files above plus the self-neutral snapshot receipt. The packet output set, snapshot artifact set, and producer receipt artifact set are identical. All 12 producer receipt `preceding_artifact_sha256` bindings verify, and `receipt.json` is the last-mtime file in the frozen 13-file producer set.

The run manifest, raw paths, result, stdout, stderr, control matrix, resource accounting, source provenance, and receipt agree on the exact command, one performed run, zero reruns, zero scientific experiments, pinned upstream commit `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`, upstream tree `38fe0708f2d7256f490e4685670dad3eed6bb9a2`, exit 1, 6 tests, 5 passes, 1 failure, and terminal `failed_implementation`. Applying the archived patch to that exact upstream tree succeeds and recreates the archived backend byte-for-byte. Git reports one blank-line whitespace warning at the patch EOF; the apply result and content hash are otherwise exact.

## Sole deterministic reproduction

One reproduction was performed from `2026-08-24T21:32:45Z` through `2026-08-24T21:33:32Z`. It used the archived runner, source, seed, patch, and pinned upstream checkout. The result path was redirected into `/tmp` and `PYTHONDONTWRITEBYTECODE=1` was set so no immutable producer output was overwritten.

- Upstream checkout: exact commit `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`, exact tree `38fe0708f2d7256f490e4685670dad3eed6bb9a2`.
- Runner result: exit 1, `failed_implementation`, 6 run, 1 failure, 0 errors, 0 skipped.
- Reproduced machine-readable result: 7,373 bytes, SHA-256 `0598f7940e628ddc51f677179f74c403a6e19ab44c3a2e8c9b8e2de4ba54f1fb`, byte-identical to the archived `run/results.json`.
- Reproduced stdout: 1,739 bytes, SHA-256 `cd0dbc22d59924d02a4b2b44a2b7724a8c41108d1269e2f90be6eb02852ea3be`; its semantic test trace matches the archive, while elapsed test time differs as expected.
- Reproduced timing stderr: 31 bytes, SHA-256 `fe52d42f0c7aef00b6d1c5cc8537d793dee973d54564f65287590f8f1aac28a7`; host timing differs from the archive as expected.
- Producer reruns: 0. Validator reproductions: 1. Scientific experiments: 0.

## Independent J2 metric recomputations

The validator independently implemented the expected affine group law for the fixed `p=5, a=2, b=1` control, checked the producer table against independent multiples of `(0,1)`, and enumerated the emitted circuit without calling the producer's aggregate assertions.

| Gate | Checked | Failures | Additional checks |
| --- | ---: | ---: | --- |
| Exhaustive label/enable/accumulator code space | 4,096 | 0 | 0 label failures; 0 accumulator failures; 0 cleanup failures |
| Valid encoded curve states | 224 | 0 | exact enabled/nonzero-digit affine translation |
| Exceptional `O`, `A`, `-A`, `-2A` states | 32 | 0 | every declared exceptional block reached |
| Invalid accumulator codes | included above | 0 changes | identity behavior verified |

For every one of the 4,096 final states, the validator separately checked `effective_enable`, `qrom_address`, `qrom_sign`, `qrom_valid`, all four `qrom_checks`, all five `comparison_flags`, `route_enable`, and the zero-width `arithmetic_work` register. Every nonzero count is zero.

Both required coherent alias controls pass independently:

- Positive labels `(2,0)` and `(3,1)` retain distinct labels and amplitudes `3/5` and `-4/7`, preserve relative sign/phase, each receive exactly one translation to the equal payload `(3,3)`, do not collide because the label is unchanged, and end clean.
- Mirror-negative labels `(2,1)` and `(3,0)` retain distinct labels and the same amplitudes, preserve relative sign/phase, each receive exactly one translation to the equal payload `(3,2)`, do not collide, and end clean.

The qROM handle has eight physical bits: two address, one sign, one valid, and four checks. All eight labels load their exact record. The validator checked 395 logical-operation boundaries per label: the selected handle is restored at every boundary. All 272 arithmetic MCXs carry the full route, unchanged label, and selected-record controls. The eight unload gates are the exact inverse of the eight load gates, every label unloads to zero, and the final work state is clean. Explicit negative-control X sandwiches transiently invert control wires inside a logical pattern gate, as declared in the circuit specification; each sandwich closes exactly and does not select or retain a different record.

## Mandatory known-false control and verdict

The payload-row-iterated backend is detected, but the frozen test's marker cardinality is wrong:

- Positive pair: both branches actually apply the equal payload twice, producing `(0,4)` instead of the one-translation `(3,3)`. Both branches also leave `comparison_flags` dirty. The helper therefore emits 2 translation-mismatch markers + 2 cleanup markers = 4 aggregate markers.
- Mirror-negative pair: both branches apply the equal payload twice, producing `(0,1)` instead of `(3,2)`, and both leave `comparison_flags` dirty. It likewise emits 4 aggregate markers.
- The frozen runner asserts `positive["failures"] == 2`, observes 4, and stops before its `negative["failures"] == 2` assertion and before serializing either detailed report.

Thus the acceptance method is sensitive to the known-false implementation, but the required known-false gate does not complete under its own frozen assertion. The independently observed mirror-negative failure cannot retroactively make the archived 5/6 run complete. Repair would require a fresh Coordinator-approved successor; no rerun or in-place edit is authorized.

## Limitations and procedure notes

- `docs/research-lifecycle.md`, listed in J2's declared read scope, does not exist at the frozen `HEAD`. No similarly named out-of-scope document was substituted. The binding contract, Validator role contract, packet, plan, snapshot, and producer inputs were present, so J2 execution could finish, but the missing declared path is an administrative source defect.
- The implementation and all enumerations are the finite `p=5`, `n=3`, `w=3` deterministic control. They do not establish scalable arithmetic, leading `3n+O(log n)`, exact coefficients, performance, general-curve transfer, P1553, B71, novelty, support, closure, or breakthrough.
- A transient ignored Python cache was created by a validator import and moved to Trash immediately. The producer tree was restored to its frozen 13-file set; no bound byte changed.
- A concurrent blind-review task path became visible through final Git status after launch. Its contents were never opened, read, contacted, or used. No J1, J3, or blind-rederiver report or message was read.

```yaml
validation_report:
  id: VAL-20260824-15217b
  task_id: TASK-20260824-15217b
  run_ids:
    - TASK-20260824-1e8b78-RUN-01
  artifact_checks:
    - check: canonical_preflight_and_dispatch_binding
      outcome: passed
      detail: all ten gates true; J2 selected; source queue and plan hashes exact
    - check: content_first_snapshot
      outcome: passed
      detail: 13 producer artifacts plus self-neutral snapshot receipt at reachable commit 052bce8a4e90a71206696d59d5ec5a9603df2299
    - check: producer_internal_bindings
      outcome: passed
      detail: packet, snapshot, receipt, manifest, raw results, raw output, patch, provenance, and resource-accounting paths/hashes agree
    - check: declared_read_scope
      outcome: incomplete
      detail: docs/research-lifecycle.md is absent; no substitution was read
  metric_recomputations:
    - metric: exhaustive_code_space
      value: {tested: 4096, failures: 0}
    - metric: valid_code_space
      value: {tested: 224, failures: 0}
    - metric: exceptional_code_space
      value: {tested: 32, failures: 0}
    - metric: final_work_register_nonzero_counts
      value: {effective_enable: 0, qrom_address: 0, qrom_sign: 0, qrom_valid: 0, qrom_checks: 0, comparison_flags: 0, route_enable: 0, arithmetic_work: 0}
    - metric: deterministic_reproduction
      value: {tests: 6, passed: 5, failed: 1, exit_code: 1, status: failed_implementation, raw_results_byte_equal: true}
  control_checks:
    - control: positive_equal_payload_alias
      outcome: passed
    - control: mirror_negative_equal_payload_alias
      outcome: passed
    - control: qrom_load_use_same_record_inverse_unload
      outcome: passed
    - control: payload_row_iterated_known_false
      outcome: failed
      detail: both pairs double-translate and dirty comparison flags, yielding four helper markers per pair while the runner freezes an expected value of two and stops before mirror-negative assertions
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: failed
  limitations:
    - Producer package remains terminal failed_implementation despite reproducible positive observations.
    - Missing declared docs/research-lifecycle.md source.
    - Finite p=5 control only; no scalable or scientific transfer.
    - No whole-claim verdict; J2 only.
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-15217b/integrity-validation.md
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-15217b/reproduction-results.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-15217b/review-attestation.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-15217b/receipt.json
```
