# J3 Red-Team Report: Proves-Too-Much, Scope, and End-to-End Cost

- Task: `TASK-20260824-01b12b`
- Packet: `QEC-COHERENT-QROM-PREADMISSION-20260824-aca034`
- Joint owned: `J3-proves-too-much-scope-and-end-to-end-cost`
- Joint verdict: **breaks**
- Whole-claim verdict: **not issued**
- Method: static review of the committed packet, review plan, content-first snapshot receipt, and the 13 archived producer artifacts; no producer rerun and no scientific experiment

## Outcome

J3 breaks for two independent reasons. First, the acceptance evidence is not a discriminating six-object proves-too-much control: the producer itself fails the complete basis-domain oracle, several structural detectors are specimen-aware checks of mutation labels or metadata, and the partial-arithmetic mutant removes a whole table row rather than one of the declared `O/A/-A/-2A` exceptional paths. Second, the recorded costs are exact only for an unsuccessful `p=5`, `w=3` abstract `X/MCX` IR. They omit a physical decomposition and its scratch space, do not supply accepted liveness, and implement arithmetic by exhaustive point-permutation synthesis rather than by the pinned upstream arithmetic primitives. They cannot support an end-to-end coefficient or performance transfer.

This is a verdict on J3 only. It does not compose the mutually blind round and changes no hypothesis, goal, packet, queue, evidence, decision, P1553, or B71 state.

## Load-bearing findings

### J3-F1 — The sparse pass is selected away from the full-domain failure

The sparse enabled/nonzero cases cover only addresses 0 and 1. Its only address-2 branch is disabled, and its only address-3 branch has `zero_digit=1`. The complete basis check is the first control that requires enabled, nonzero action for all four addresses, and it fails.

The source exposes a concrete separator without rerunning it. The frozen curve says the base has order 7 and the table uses magnitude `address+1`. Hence

- table keys `(2,0)` and `(3,1)` both load `3A`, because `-4A = 3A` in the order-7 subgroup;
- table keys `(2,1)` and `(3,0)` both load `4A`, because `-3A = 4A`.

Arithmetic controls include `effective_enable` and the qROM payload, but not address/sign. Nevertheless the code emits a complete translation once for every table key. Each aliased payload therefore enables two copies of the same translation. On those rows the implementation applies the selected translation twice, which the sparse subset does not exercise. This is a source-level derivation tied to the observed full-basis failure, not a new run.

The sparse pass consequently establishes only the 18 enumerated branches. It cannot be transferred to the declared 224 basis blocks or to arbitrary coherent tables.

### J3-F2 — The inverse-unload structural failure is a control false negative

The implementation constructs `qrom_unload` by reversing every emitted load operation, and the underlying `X` and `MCX` gates are self-inverse. The liveness comparator then maps every reversed unload operation back with `logical_access="load"`. Original negative-control sandwich `X` operations had `logical_access=None`, so those reconstructed dataclass values cannot equal the original load operations. The comparator therefore returns false even for the sequence produced as the exact reverse.

This does not cure J3-F1. It means the two reported failures have different meanings: the basis-domain failure is semantic, whereas the inverse structural failure is caused by the acceptance comparator. The archived phase/count record does include both 53-term load and 53-term unload passes, but there is no accepted liveness certificate.

### J3-F3 — The six known-false results are not six independent semantic separators

The common semantic check in test 05 is `verify_basis_domain(broken)`. The unmutated producer already fails that oracle. A generic `basis-domain translation mismatch` therefore does not attribute failure to a mutation unless the first mutation-specific witness is recorded before the producer's address-alias failure. The archived control matrix records no witness state and no failing stage for five of the six semantic mismatches.

The structural classifier is also passed the expected variant ID. Four checks execute only inside `if variant == ...` branches, and the classical-loop check trusts a producer-controlled metadata flag. This is not an unchanged, blind acceptance predicate over an unknown backend.

The exact-object assessments are:

| Known-false object | Exact archived mutant | Declared failure signature | J3 assessment |
|---|---|---|---|
| `KF-NOOP-PROTOCOL` | Empty operation list | empty IR and identity on enabled/nonzero input | Exact mutant is rejected. Non-emptiness plus the full-domain oracle is adequate for this exact empty object, although the generic semantic message is not a mutation-local witness. |
| `KF-CLASSICAL-ADDRESS-LOOP` | Address-controlled operations removed and metadata set to runtime branching | no coherent address controls | **Breaks as a control.** Detection trusts `run_time_address_branching=true`; it does not inspect or model host runtime branching. A classically selected backend that self-reports false is outside the test's observation. |
| `KF-MISSING-UNLOAD` | All operations tagged `qrom_unload` removed | absent inverse phase and dirty qROM target | Exact mutant is rejected by phase absence and cleanup. This is the strongest recorded known-false control, despite the separate false-negative equality comparator in J3-F2. |
| `KF-PREMAP-FLAG-CLEANUP` | Selected mask toggles inserted under an artificial `premature_mask_cleanup` phase | flag lifetime/exception use failure | **Breaks as a discriminating control.** The detector recognizes the injected phase name. The archived semantic message reaches the producer's generic basis mismatch rather than recording a pre-use flag or dirty-mask witness. Equivalent early cleanup under ordinary tags can evade the structural check. |
| `KF-ZERO-DIGIT-OMISSION` | Effective enable changed to a direct external-enable `CX` and zero sandwiches removed | negative control absent and zero branch changes | Exact mutant is rejected, and the exhaustive oracle contains an early zero-digit witness. The tag test alone is insufficient—a dummy sandwich could remain—but the semantic condition is appropriate for this exact object. |
| `KF-PARTIAL-ARITHMETIC` | Every arithmetic operation with table key `(0,0)` removed | one exceptional `O/A/-A/-2A` path missing | **Breaks specification correspondence.** This removes the entire `+A` row, not one exceptional path. The four qROM masks are constant-one payload bits, and the emitted permutation has no independently mutable exceptional handlers. Thus the test does not instantiate the declared known-false object. |

The exact mutants are all recorded as rejected, but the stronger statement “all six were rejected for independent declared structural and semantic reasons” is unsupported.

### J3-F4 — Exceptional masks and liveness do not transfer to upstream arithmetic

`_point_payload` appends `(1,1,1,1)` for every table point. The four named qROM masks therefore do not encode whether the current accumulator is `O`, `A`, `-A`, or `-2A`; they are constant availability controls held high. Arithmetic is synthesized as a complete permutation over every valid point code. The `branch` field is metadata derived from a cycle origin and does not control a distinct exceptional circuit path.

This can be a finite-domain permutation implementation, but it does not demonstrate or price the packet's scalable exception-aware controlled-addition path. The resource record counts storage and wide controls for four constant bits; it does not count predicate creation, case selection, exceptional formulas, or their cleanup in an upstream arithmetic implementation. `arithmetic_work=0` is a property of exhaustive permutation synthesis, not evidence that upstream field arithmetic needs no work qubits.

### J3-F5 — Abstract gate counts are internally bounded but not an end-to-end resource model

For the failed toy IR, the three MCX groups reconcile:

- 2 two-control MCXs derive and uncompute effective enable;
- 106 three-control MCXs are 53 qROM load plus 53 inverse-unload payload toggles;
- 272 eighteen-control MCXs implement adjacent Gray-state swaps;
- total: 380 MCXs, plus 4,860 `X` gates and zero `CX` gates.

These are exact emitted-IR observations at `p=5`, coordinate width 3, and window width 3. They are not exact Toffoli, Clifford+T, depth, or fault-tolerant costs:

1. No 18-control MCX decomposition is selected. Its elementary-gate cost and any clean/dirty scratch requirement are therefore unknown.
2. The reported 12 “peak clean ancilla” is the sum of `effective_enable`, qROM coordinate, `qrom_o`, and mask registers. During arithmetic all 12 are live controls or payload, so they are not simultaneously clean scratch available to decompose the 18-control MCXs.
3. Logical negative polarities are compiled into `X` sandwiches, but `negative_arity_0` is hard-coded for every MCX. The requested grouping by positive and negative control arity is absent. Total `X` happens to include the sandwiches, without a proof that they remain paired under composition.
4. A “qROM access” is defined as one payload-bit toggle term. It excludes the surrounding selector-polarity gates and is not a memory-access primitive. Scaling requires the number of rows, payload Hamming weights, selector polarities, and inverse pass.
5. The 272 “arithmetic primitive invocations” are exhaustive point-code Gray swaps, not invocations of a pinned upstream elliptic-curve addition primitive. Their construction enumerates `curve.points()` and translation cycles, so the toy count has no supplied linear-size transfer.
6. The only measured 0.90 seconds is host execution of the test harness on the toy object. It is not quantum runtime and has no Pollard-rho, BSGS, or specialized-baseline comparison.

The forward/inverse qROM pass was not omitted from the toy abstract count. What is missing is the decomposition, available-scratch, scalable exceptional-control, symbolic `n,w` relation, and composition needed for an end-to-end cost.

## Scope ceiling

The evidence supports at most this statement:

> At the frozen `p=5`, `w=3` deterministic control instance, the producer emitted a nonempty address/sign-controlled `X/MCX` IR with explicit qROM load and reverse-unload phases and recorded exact abstract operation counts. Eighteen selected sparse branches passed. The complete basis-domain control failed, so the artifact is not a validated exact signed-window correction even on its full declared toy domain.

No transfer is available to any of the following:

- exact 835, logarithmic, or Toffoli coefficient: no symbolic proof or MCX decomposition;
- leading `3n+O(log n)`: no accepted liveness/counting derivation and no composition with the pinned upstream primitive;
- practical speedup: no physical resource model, end-to-end runtime, or relevant baseline;
- ECDLP advance, P1553, or B71: zero scientific experiments, a `p=5` implementation control, and frozen pointers that are reference-only;
- novelty: no literature/retrieval result was produced or reviewed;
- supported or breakthrough status: no scientific transition is authorized, and this report is one joint in an uncomposed blind round.

## Cheapest successor falsification control

Add a two-branch exact sparse control named `CTRL-PAYLOAD-ALIAS-SEPARATOR`: put enabled, nonzero branches for `(address=2, sign=0)` and `(address=3, sign=1)`—which load the same `3A` payload—into one exact-amplitude superposition, with identical clean work inputs. Require each unchanged label block to apply exactly one `+3A` translation and to clean every payload/work register. Repeat only if needed for the conjugate alias `(2,1)` / `(3,0)`.

This is cheaper than another exhaustive pass, directly falsifies the observed sparse-to-full transfer, and distinguishes a payload-keyed translation emitted twice from either a unique-payload compilation or an address/sign-separated compilation. It is a proposed successor control, not a run performed by this task.

## Review attestation

- `joints_owned`: [`J3-proves-too-much-scope-and-end-to-end-cost`]
- `read_sibling_reports`: false
- `read_sibling_artifacts`: false
- `blind_rederivation_performed`: false
- `independent_session`: true
- `requested_policy`: `review-adversarial`
- `reasoning_effort`: `xhigh`
- `fallback_used`: false
- `degraded_requirements`: []
- `bedrock_used`: false
- `scientific_experiment_runs`: 0
- `deterministic_reproductions`: 0
- `deterministic_non_scientific_checks`: 1 (dispatcher authority/eligibility verification only)

