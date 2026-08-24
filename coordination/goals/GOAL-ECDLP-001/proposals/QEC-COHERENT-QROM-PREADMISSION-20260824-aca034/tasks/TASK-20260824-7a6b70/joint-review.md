# J1 semantic review — TASK-20260824-7a6b70

## Scope and outcome

- Joint owned: `J1-coherent-semantic-action-and-integration` only.
- Joint verdict: `breaks`.
- Whole-claim verdict: not issued.
- Producer status remains `failed_implementation`. This report treats that status and every failed check as operational implementation/control evidence only; it makes no mathematical, scientific, performance, parameter, resource, or research-state inference.
- Scientific experiment runs: `0`.
- Deterministic non-scientific checks: `1`.

The single check independently traversed every computational-basis accumulator code with clean work registers for all address, sign, zero-digit, and external-enable labels. That is 4,096 basis states per backend: 224 states with valid point encodings and 3,872 states with invalid encodings, which the archived circuit specification declares must be fixed. The same acceptance rubric was then applied to the producer circuit and each of the six frozen known-false objects. The check also fetched the exact pinned upstream commit into a temporary detached checkout and ran `git apply --check` without modifying the archived producer artifacts.

## Frozen binding

- Opening worktree HEAD: `f6ff6f9ffd63dfbaa020fec574d08cc82cbb19cf` (matches the supplied `f6ff6f9ff` prefix).
- Opening worktree state: clean.
- Coordinator-supplied canonical queue digest: `0aa9718be416fd3cc81121fed596c534d6fa22de52a70f32e7643192d918dbfa`.
- Coordinator-supplied dispatcher-plan digest: `cb34d235a48eecb2f225907fd618606b0c798ba4c4f213ce83e0e384e66a73e6`.
- Raw file digests at opening were separately observed as `8a14fe783aacbaa0292b6b885e5a1337ec31cb18658f9e687efb0f7ace2611cf` for `dispatch_queue.json` and `7161c6d053e650ae900d777339d06654b3714a492775d132d5d9aa8f525e842d` for `review-plan.yaml`. These are raw-file hash layers and are not substituted for the supplied canonical queue and rendered-plan bindings.
- The authorized content-first snapshot receipt is self-neutral and binds exactly the 13 producer artifacts. It records one implementation/control run, zero scientific runs, and the terminal producer outcome `failed_implementation`.

## Finding J1-1 — complete coherent action breaks

The emitted object is a concrete materialized `X`/`MCX` operation list, and its qROM load terms coherently control on both little-endian address bits and the sign bit. The address, sign, zero-digit, and external-enable labels remain unchanged, while the effective-enable derivation correctly implements `external_enable AND NOT zero_digit`.

The arithmetic action is nevertheless wrong on a complete declared basis. `_table` creates one row per address/sign pair, while the arithmetic emitter loops over every row but controls the translation only on the loaded payload. On the order-seven control curve, distinct rows have identical payloads:

- `(address=2, sign=0)` and `(address=3, sign=1)` select the same signed point.
- `(address=2, sign=1)` and `(address=3, sign=0)` select the other duplicated signed point.

Because the same payload-controlled translation is emitted once for each table key, each duplicated payload activates two identical translation networks. Those four enabled, nonzero-digit rows therefore apply the translation twice rather than once.

The uniform exhaustive check found:

- `4,096` total clean-work basis states checked;
- `224` valid-point states and `3,872` invalid-code states;
- `28` semantic failures, all among valid points;
- `0` invalid-code changes;
- `0` label-preservation failures;
- `0` final cleanup failures.

The 28 failures are exactly all seven valid accumulator points in each of the four duplicated-payload address/sign rows, with `external_enable=1` and `zero_digit=0`. Disabled and zero-digit branches remain identity as required.

## Finding J1-2 — exceptional action is incomplete and its trace metadata is not faithful

The same check evaluated `O`, `A`, `-A`, and `-2A` for every one of the eight address/sign rows under enabled, nonzero-digit control. Of the 32 required exceptional actions:

- all 16 cases for addresses 0 and 1, under both signs, matched the signed translation;
- all 16 cases for addresses 2 and 3, under both signs, failed because of the duplicated-payload double application.

There is a second conformance defect in the exceptional-mask representation. `_point_payload` appends `(1, 1, 1, 1)` for every table row, so the four named qROM mask wires are constant handler-availability controls rather than the frozen packet's exceptional-case masks. The task-local `circuit-spec.yaml` silently weakens their semantics to “handler-availability bits,” but no amendment authorizes that change. Moreover, every emitted arithmetic gate has branch metadata `O`: the emitter classifies the fixed cycle origin once and attaches that label to all swaps, rather than tracing the runtime `O/A/-A/-2A` case. The correct action on the 16 unique-payload exceptional cases comes from an enumerated whole-point permutation, not from four faithfully represented exceptional mask paths.

## Finding J1-3 — load/use/unload cleanup holds; the archived inverse-equality failure is a verifier defect

The qROM coordinates and all four mask wires are loaded before arithmetic, remain controls throughout arithmetic, and return to zero after the reverse pass. The effective-enable bit is also uncomputed. The exhaustive check found every declared work/qROM target clean on all 4,096 producer basis states.

The actual unload operation list is the exact reverse of the load list after restoring phase/tag metadata and preserving each gate's logical-access field. The archived `inverse_unload_exact=false` result is caused by the liveness verifier setting `logical_access="load"` on every reversed unload operation, including the negative-control X-sandwich gates whose original value was `None`. That metadata-normalization error makes structurally identical load/unload gates compare unequal. This corrects the interpretation of that one operational check only; it does not repair or supersede the immutable run, and the independent complete-basis action failure still breaks J1.

## Finding J1-4 — pinned patch applicability holds, upstream integration does not

The patch has SHA-256 `ba41596c4723e2a93ae9f733f053e28e7c71509890f2acfb125a9b28d1e0ff8d` and size `28,650` bytes. In a fresh temporary detached checkout:

- observed upstream HEAD: `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`;
- observed upstream tree: `38fe0708f2d7256f490e4685670dad3eed6bb9a2`;
- `git apply --check`: pass.

The diff only creates `/coherent_signed_qrom_backend.py`; it modifies no existing upstream module, import, package surface, caller, or test. Exact-commit applicability is therefore established, but integration of the backend into the pinned upstream program is not. A standalone new root file does not satisfy the J1 integration obligation.

## Known-false controls

The same acceptance rubric rejected all six frozen objects. Full details are in `known-false-results.json`. The declared structural failure was observable for each object. However, the archived control harness is weaker than its summary suggests: it uses variant-specific `detect_known_false` predicates, and then counts any `verify_basis_domain` exception as semantic detection even though the producer already fails that verifier.

In particular, `KF-PREMAP-FLAG-CLEANUP` has exactly the producer's 28 semantic failures and adds no new semantic failure. Its injected mask-target MCX gates omit the original negative-control X sandwiches, so the attempted early cleanup is ineffective on this truth table. A uniform liveness audit still rejects the object because mask-target operations appear between load and arithmetic, but the archived assertion that this object independently demonstrates exceptional-control semantic failure is not established.

## Limitations and required disposition

- This review does not repair the implementation, rerun the producer command, reproduce resource accounting, or inspect any sibling report.
- This review does not perform the separate blind re-derivation.
- The operational finding is bounded to the archived deterministic circuit IR and exact pinned patch.
- The Coordinator must compose this joint result with the other independently assigned joints. This report cannot authorize archival, transition, or any broader conclusion.

## Procedure deviation

During exact-ID path discovery, a filename-only `rg --files` filter unintentionally returned the path of one prohibited sibling handoff. The handoff content, sibling artifacts, messages, and status were not opened or read, and the sibling task ID was already present in the authorized review plan. This path-listing violated the explicit no-list constraint and is disclosed here. Mutual blindness of report content remained intact.

```yaml
review_attestation:
  schema: crypto.autoresearch.review_attestation.v1
  task_id: TASK-20260824-7a6b70
  plan_id: REVIEW-PLAN-QEC-COHERENT-QROM-aca034
  role: reviewer
  independent_session: true
  requested_policy: review-adversarial
  reasoning_effort: xhigh
  runtime: native_codex
  resolved_model_id: gpt-5
  model_verified_by_repository_probe: false
  fallback_used: false
  degraded_requirements: []
  bedrock_used: false
  joints_owned:
    - J1-coherent-semantic-action-and-integration
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - docs/task-lifecycle.md
    - plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/SKILL.md
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/packet.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/review-plan.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/dispatch_queue.json#TASK-20260824-7a6b70-only-and-nontask-metadata
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/archives/TASK-20260824-74edc9/snapshot-receipt.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/circuit-spec.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/src/coherent_signed_qrom_backend.py
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/tests/test_coherent_signed_qrom_backend.py
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/integration/upstream-b5e4c664de212bdb0981d93d70964a1dca1a0ec9.patch
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/run-manifest.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/command.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/stdout.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/stderr.txt
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/run/results.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/resource-accounting.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/source-provenance.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/control-matrix.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/tasks/TASK-20260824-aca034/receipt.json
    - upstream:b5e4c664de212bdb0981d93d70964a1dca1a0ec9#tree-and-patch-application-only
  read_sibling_reports: false
  contacted_sibling_reviewers: false
  sibling_messages_read: false
  blind_rederivation_performed: false
  procedure_deviations:
    - filename-only discovery listed one prohibited sibling handoff path; no sibling content or status was read
  verdict: breaks
  whole_claim_verdict: not_issued
```
