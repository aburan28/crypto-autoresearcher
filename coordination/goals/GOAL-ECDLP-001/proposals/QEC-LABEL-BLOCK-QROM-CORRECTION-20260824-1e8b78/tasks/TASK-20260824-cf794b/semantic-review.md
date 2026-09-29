# J1 semantic and alias-control review

- Task: `TASK-20260824-cf794b`
- Review plan: `REVIEW-PLAN-QEC-LABEL-BLOCK-QROM-1e8b78`
- Joint owned: `J1-label-block-semantics-exceptions-and-alias-controls`
- Joint verdict: **BREAKS**, narrowly on the packet's literal generic-core-versus-exceptional-mux dispatch requirement.
- Whole-claim verdict: not issued.
- Scientific meaning: none. This is one deterministic finite implementation/control review with zero scientific experiments.

## Outcome

The emitted circuit does realize the finite direct-sum basis permutation

`U = sum_l |l><l| tensor T_A(l)`

on the stated `p=5`, `n=3`, `w=3` code space. The two required equal-payload alias superpositions retain their distinct address/sign labels, exact coefficients `3/5` and `-4/7`, and relative sign; each branch receives one signed translation; and all declared work registers return to zero. The single selected record is loaded from the unchanged label, remains unchanged through the translation layer, and is unloaded by the exact reversed gate sequence. The payload-row-iterated known-false emits two translation blocks for every aliased key and visibly applies `2A` rather than `A`.

J1 nevertheless breaks as a structural joint. The input comparisons compute five one-hot flags (`O`, `A`, `-A`, `-2A`, and `generic`), but the IR immediately XOR-collapses every flag into the same one-bit `route_enable`. Every arithmetic MCX is controlled by `route_enable`, the label, the checked record, and accumulator bits; no arithmetic gate is controlled by a particular branch flag. Consequently, the implementation runs one monolithic complete truth-table permutation for every routed input. It does not literally dispatch one generic core or one exceptional mux as required by `packet.yaml`. The finite output action and cleanup hold; the claimed branch-specific dispatch does not.

This is a verdict on J1 only. It does not decide archive integrity or exhaustive-domain reproduction (J2), decomposition or scalable liveness (J3), the blind rederivation, or the packet's whole claim.

## Binding and preflight

The opening worktree was clean. `HEAD` and the configured upstream branch were both `1c1f475fbd30be5ac2714b5bb3af91d61e30fc53` on `codex/qec-exact-add-preadmission-20260824`.

The raw bytes of `dispatch_queue.json` hash to `b17a6c143ded670bc6da4d55f71c9dcf051fff3b6028cbd4ffeece65763c77d0`. The initial pause that compared this raw digest with the expected canonical dispatcher digest was resolved by the Coordinator: the frozen value is the dispatcher's normalized `source_queue_sha256`, not the raw file digest. A fresh out-of-repository render then produced exactly:

- `source_queue_sha256 = 56b2ec2ae50c76158be407e4a63115396928dafa84f70544aec7a107c18ee2e1`
- `plan_sha256 = b9666a2ece41096bc5e37a8e1387c37b08025364f8590388a8d970dfa37a656f`
- all ten dispatcher gates `true`
- `TASK-20260824-cf794b` selected with completed producer and snapshot dependencies

The canonical Codex preflight returned `READY`: generated runtime bindings, runtime authority bindings, and harness doctor all passed. No backend probe was performed. The shared worktree later acquired an untracked sibling task directory while this review ran; no sibling file was opened, listed internally, or contacted, and the opening cleanliness fact is preserved rather than rewritten.

The declared read-scope path `docs/research-lifecycle.md` is absent at this HEAD. The harness-mandated current lifecycle files `docs/task-lifecycle.md` and `docs/dynamic-subagent-dispatch.md` had already been read before selection. This substitution is disclosed as a non-scientific procedure deviation and was not used as evidence for the J1 verdict.

## Direct-sum and selected-record trace

The selected-record path is concrete:

1. The load copies the two address bits and sign bit into `qrom_address` and `qrom_sign`, then sets `qrom_valid` and four check bits. The eight-bit record is a checked label-derived handle; point coordinates remain compiled constants.
2. Input comparisons are controlled by effective enable, all three unchanged label bits, seven checked-record bits, and the seven accumulator bits. Exactly one of the five flags is set on an enabled valid point.
3. Five CX gates XOR the one-hot flags into `route_enable`.
4. The central translation MCXs use `route_enable`, all three label bits, all eight record bits, and six non-target accumulator bits. The correct circuit emits one 34-MCX translation block per key. Negative-control X gates are reversible polarity sandwiches around these central MCXs; they are not uncontrolled translations.
5. `route_enable` is unselected, output comparisons clean the flags using `R+A`, the eight load gates are appended in exact reverse as unload gates, and effective enable is uncomputed.

Every emitted gate is X, CX, or MCX. The circuit is therefore a phase-free basis permutation. Since address/sign labels are restored and remain distinct, arbitrary input coefficients are transported without amplitude mixing or relative-phase change; the chosen rational coefficients provide an explicit signed control.

## Independent alias controls

One authorized deterministic reproduction imported the archived backend at SHA-256 `369692b8dfec765aca793bf432dd916e89ade7ef845919510afcc8ef27013172` and used an independently written phase-by-phase state tracer. It did not invoke the producer test runner and did not write or modify producer artifacts.

For the positive alias pair `(2,0)` and `(3,1)`, both records select `+3A = (3,3)`. The two output branches retained coefficients `3/5` and `-4/7`, retained both labels, reached `(3,3)` exactly once from `O`, cleaned all five comparison flags and `route_enable`, and unloaded the selected record.

For the mirror-negative pair `(2,1)` and `(3,0)`, both records select `-3A = (3,2)`. The same checks passed, with both output branches reaching `(3,2)` exactly once from `O`.

The records remained label-specific even when their payloads were equal:

- `(2,0)` loaded `[0,1,0,1,1,1,1,1]`; `(3,1)` loaded `[1,1,1,1,1,1,1,1]`.
- `(2,1)` loaded `[0,1,1,1,1,1,1,1]`; `(3,0)` loaded `[1,1,0,1,1,1,1,1]`.

Thus equality of selected point payloads does not merge labels or cause a second application in the correct backend.

## Generic and exceptional paths

The reproduction traced all 32 required exceptional basis cases: eight each for `O`, `A`, `-A`, and `-2A`. In every case the expected one-hot input flag was set, `route_enable` selected one translation layer, the accumulator reached `R+A`, the route and flag registers cleaned, the record unloaded, and the label was unchanged. Eight representative generic cases, one per address/sign key, also reached `R+A` and cleaned.

These observations establish finite action and cleanup. They do not cure the structural dispatch break: the five flags are not individually consumed by a generic core or exception mux; they only generate a shared Boolean enable for the same complete permutation.

## Payload-row known-false and other controls

For aliased payloads, the payload-row-iterated backend emits 68 central arithmetic MCXs per key instead of 34. Starting from `O`:

- the positive pair reaches `2(+3A) = (0,4)`, not `+3A = (3,3)`;
- the mirror-negative pair reaches `2(-3A) = (0,1)`, not `-3A = (3,2)`.

Labels and coefficients remain distinct, but the wrong second translation is explicit. The output-comparison cleanup, which is constructed for one translation, leaves both the original `O` flag and an `A` flag dirty. The producer alias helper therefore records two failure conditions per branch—wrong output and dirty work—for four markers per pair. The frozen producer runner expected two markers, stopped after observing four on the positive pair, and never reached its mirror-negative assertion. The independent trace reached both pairs and confirmed the required double-translation failure signature. It does not retroactively turn the archived `failed_implementation` run into a valid run.

The remaining known-false objects were rejected for their preregistered structural reason: an empty operation list fails a nonzero translation; runtime classical label branching violates coherent direct-sum structure; omission of unload leaves the record dirty; label canonicalization changes the address; and deleting the `(0,0)` arithmetic block fails its translation.

## Upstream patch

The patch SHA-256 `74e61d6c4158f547e3912b6f7f86f5a92e9fd27ffd7ad6b64ab5f998102c4086` applies with exit code zero to upstream commit `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`, tree `38fe0708f2d7256f490e4685670dad3eed6bb9a2`. After application it modifies `README.md`, adds `label_block_qrom_backend.py`, and adds `test_label_block_qrom_backend.py`; the installed backend is byte-identical to the archived source. `git apply` reports one trailing-blank-line whitespace warning in the new test file, which does not affect application or semantics.

The patch is additive and standalone. It does not connect the finite control to the upstream repository's existing arithmetic implementation; its README explicitly says it is separate from the existing Fig. 14 estimates. The review therefore treats it only as a pinned finite integration control, matching the packet ceiling.

## Limits and handoff

- The producer package remains terminal `failed_implementation`; this review does not repair or supersede it.
- The direct-sum and alias observations are confined to the frozen `p=5`, `n=3`, `w=3` implementation control.
- No exhaustive J2 reproduction, J3 cost/liveness inference, blind rederivation, general-curve transfer, P1553/B71 admission, scientific transition, speedup, attack, novelty, support, or breakthrough claim is made.
- The Coordinator must compose J1 with the independently blinded joints and decide any successor. This report changes no queue, ledger, goal, hypothesis, experiment, or official state.
