# ECDLP-IDEA-139 — Middle-convolution source rank drop

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_aggregate_sheaf_transform`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: every prospective finite test is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a rank drop, rigid local system, trace identity, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Encode factor-base source punctures in a target-indexed lisse sheaf, apply Katz middle convolution to reduce the sheaf rank while retaining each puncture's source identity in local monodromy, and invert transformed local factors to all signed five-source tuples. A bounded-rank transformed sheaf then supplies relations and blind descent below rho.

## Mechanism-new operation

The proposed operation is **source-labelled middle convolution with exact local-factor inversion**. The sheaf is to be constructed from compact elliptic addition and target data, convolved with a frozen Kummer sheaf, rigidified, and decoded pointwise.

After audit this is merged/rejected. Middle convolution transforms already supplied monodromy representations and preserves aggregate local conjugacy data; it does not attach arbitrary factor-base point labels to an endpoint or invert a trace/local factor to those labels. A source-labelled input sheaf is the full source dictionary, while an unlabeled sheaf loses ancestry. This repeats the aggregate sheaf/trace boundary of IDEA-019, IDEA-080, IDEA-110, IDEA-123, IDEA-127, and IDEA-132.

## Assumptions

1. Public `E,<P>,N,Q,F`, `B=N^beta`, and complete signed relation semantics are fixed.
2. A target-independent bounded-complexity sheaf encodes every factor point without a rank-`B` skyscraper direct sum or scalar orientation.
3. Middle convolution reduces rank and preserves a biconditional local invariant for every ordered source tuple.
4. Construction and inverse work directly from public equations, not enumerated sources or relation rows.
5. Sheaf construction, fields, conductors, local factors, output, rank, factor logs, blind descent, and memory are charged.

## Semantic fingerprint

`target_relation_sheaf | Kummer_middle_convolution | rigid_rank_drop | source_puncture_local_monodromy | exact_local_factor_to_point_inverse | blind_descent`

Only a direct endpoint-to-labelled-sheaf construction plus exact inverse would be new. Aggregate trace/rank manipulation is the rejected duplicate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the missing source-fiber generator that a source-labelled sheaf cannot assume.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, where complete additive-character phases are correctness controls and do not provide a source generator.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, showing complete public value representations remain full rank.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact compact transition invariant loses its advantage on source-complete composition.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where bounded public feature spaces do not contain the factor-log orientation.

## Closest primary literature

- Katz, [Rigid Local Systems](https://doi.org/10.1515/9781400882595), develops middle convolution and rigidity from supplied local systems; it does not encode arbitrary ECDLP sources.
- Dettweiler and Reiter, [Middle convolution of Fuchsian systems and the construction of rigid differential systems](https://doi.org/10.1016/j.jalgebra.2007.08.029), give constructive rank/monodromy transformations, not finite-field point-source inversion.
- Katz, [Exponential Sums and Differential Equations](https://doi.org/10.1515/9781400882434), relates sheaves and trace functions while retaining the aggregate nature of traces.

No checked source supplies the missing source-labelled sheaf or inverse. Novelty remains unverified, but the specified transform is semantically occupied.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, punctures, coefficient field, sheaf construction, convolution character, exceptional cases, and independent source verifier.
2. Construct the source sheaf directly from compact equations, record rank/conductor/field/bit costs, and apply middle convolution.
3. For known-log targets, derive transformed local factors, invert them to every signed tuple, and verify elliptic addition.
4. Collect `B+sigma` rank-`B` rows, solve and verify factor logs.
5. Repeat unchanged on fresh masked targets, enumerate all decoded candidates, and accept only `[x]P=Q`.
6. Charge construction, convolution, local factors, inverse output, rank, linear algebra, descent, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let sheaf construction/memory be `N^a,N^a_m`, transformed rank/conductor payload `N^c`, target local-factor/inverse time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, source output `o`, ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
All source-labelled stalks and coefficient extensions are charged. Toy rank drops are model-bound.

## Likely fatal obstruction

Middle convolution preserves and reorganizes monodromy data; it does not recover arbitrary labelled rational points from one endpoint. A direct sum of `B` labelled punctures already pays the dictionary, while quotienting labels yields traces and conjugacy classes shared by many source tuples. Exact inversion restores the discarded rank or enumerates the fiber.

## Proof track

Construct a bounded-rank sheaf directly from `(E,F,R)`, prove local-factor/source biconditionality through convolution, and derive complete `lambda,mu<=0.45` without a source dictionary.

## Disproof track

Show the input sheaf contains point-labelled stalks, the output is only an aggregate trace/conjugacy class, or exact inversion restores rank/output at least rho. The current specification is rejected by this reduction.

## Positive and negative controls

- **Positive control:** classical rigid local systems with independently supplied monodromy tuples and verified rank change.
- **Positive control:** tiny elliptic source sheaves built explicitly from enumerated points, clearly labelled as supplied-source controls.
- **Negative control:** shuffled point labels with identical local conjugacy data, trace-only sheaves, and random lisse sheaves matched by rank/conductor.
- **Negative control:** source-labelled skyscraper direct sums and full transposed value matrices.
- **End-to-end control:** rho/BSGS and blind targets with sheaf construction charged.

## Quantitative promotion and falsification gates

This record is rejected at the supplied/aggregate sheaf scope. A new ID requires a public endpoint-to-sheaf identity and exact inverse with `lambda,mu<=0.45`. Falsify on one source collision, rank-`B` labelled input, trace-only output, post-hoc labels, or complete exponent at least `0.5`.

## Artifact plan

- Aggregate-transform reduction: `ideas/artifacts/ECDLP-IDEA-139/middle_convolution_reduction.md`
- Prospective source-sheaf theorem: `ideas/artifacts/ECDLP-IDEA-139/source_sheaf_identity.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-139/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-139/cost_analysis.md`

No artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified evidence. Future tests would be toy and costs heuristic/model-bound. Rank or rigidity is not source recovery, an ECDLP speedup, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-139/middle_convolution_reduction.md` proving that the specified source labels are either supplied as sheaf rank/dictionary or lost under aggregate local monodromy.
