# ECDLP-IDEA-328 — Sum-of-squares pseudoexpectation source rounding

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_duplicate_of_idea_133_target_local_moment_flat_extension`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a feasible relaxation, flat moment matrix, valid relation, or toy rounding is not an ECDLP break.

## Falsifiable hypothesis

A bounded-degree sum-of-squares pseudoexpectation for the endpoint relation ideal becomes flat at target-local degree, and its representing atoms can be rounded to all exact signed factor tuples inside the P1553 work and memory rectangle.

## Mechanism-new operation

The screened operation is **solve a target-local moment/SOS relaxation, detect rank-flatness, extract the finitely atomic representing measure, and decode its atoms to factor points**. This is precisely the moment-matrix and flat-extension operation owned by theorem-deferred `ECDLP-IDEA-133`, with IDEAs 053, 098, 191, 259, and 279 as moment/atomization controls. Calling the moments a pseudoexpectation changes the optimization interface, not the mathematical source inverse.

## Assumptions

1. Endpoint-only constraints generate a bounded-degree positive moment functional over the finite-field relation scheme.
2. A characteristic-compatible flatness theorem yields every signed source atom, including nonreduced strata.
3. Moment construction and SDP/linear-algebra state remain below `B^(9/4)` without supplied source moments.
4. Atom extraction, output, rank, factor logs, blind descent, verification, and bit complexity are charged.
5. The identical degree rule applies to fresh masked targets.

## Semantic fingerprint

`endpoint_relation_ideal | bounded_degree_SOS_pseudoexpectation | flat_moment_extension | exact_atomic_factor_rounding | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-P1427-EXACT-RIEMANN-ROCH-COMPILER-CONTROL`, the exact coefficient and transposed-moment control.
2. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed pair/four-sum generator hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transposed state boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`, the compact endpoint object versus source output boundary.

## Closest primary literature

- Lasserre, [Global optimization with polynomials and the problem of moments](https://doi.org/10.1137/S1052623400366802), constructs a hierarchy of moment/LMI relaxations from supplied polynomial constraints.
- Curto and Fialkow, [Flat extensions of positive moment matrices](https://doi.org/10.1090/memo/0648), characterizes finitely atomic representing measures under positivity and flat-extension hypotheses.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint polynomials but not low-degree flatness or signed source atoms.

No checked source supplies a direct finite-field analogue of the cited ordered PSD moment model, bounded degree, or the complete ECDLP route; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, `B=N^(1/5)`, factor decks, moment monomials, degree rule, positivity surrogate, atom decoder, masks, and verifier.
2. Build endpoint-only pseudoexpectations for known-log targets, prove flatness, extract all atoms, map them to signed points, and verify relations.
3. Collect at least `B` independent rows, solve and verify the complete factor-log system.
4. Apply the identical relaxation and rounding to fresh scalar-blind masked targets without source moments or target-trained degrees.
5. Substitute logs, remove masks, preserve all ambiguity, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let setup and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, moment construction/solve excluding atom output `N^q,N^q_m`, verified rank credit `N^r`, atom output `N^o`, ambiguity `N^u`, and factor-log work/memory `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Moment dimension, coefficient construction, field-to-ordered surrogate, SDP precision, flat extension, atom extraction, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and at least `B` independent verified rows. Pollard rho has time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The cited SOS and flat-extension machinery consumes a supplied moment functional with ordered real PSD/positivity structure. Endpoint equations do not supply source moments, and that ordered structure has no direct `F_p` analogue in the cited theorems. Constructing a source-faithful moment matrix or a high enough Macaulay surrogate is exactly IDEA-133's unresolved dense-state/source-atom obstruction.

## Proof track

Prove a characteristic-compatible endpoint-only moment construction, bounded flat degree, exact all-strata atom extraction, full relation rank, factor logs, blind descent, and complete `lambda,mu<=0.45`.

## Disproof track

Reduce the proposed matrix to IDEA-133, show that positivity/flatness requires supplied moments or dense degree, or exhibit equal truncated moments with different signed source fibres.

## Positive and negative controls

- Positive: supplied finitely atomic real moment problems satisfying flatness must recover all planted atoms.
- Negative: nonflat and equal-truncated-moment/different-support instances must not return preferred elliptic sources.
- Baselines: IDEA-133 directly; IDEAs 053/098/191/259/279; dense Macaulay; rho; and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only flatness and atom theorems, exact recall, 1,000 verified rows and 100 blind descents per large size, complete `lambda,mu<=0.45`, and the P1553 rectangles.
- Falsify if the proposed finite-field surrogate lacks the ordered PSD property used by the proof, the moment state reaches `B^3`, a source moment is supplied, or either exponent reaches `0.50`.
- Successful rounding of planted moments is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-328/idea133_sos_merge_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-328/finite_field_flatness_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-328/moment_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-328/cost_analysis.md`

## Interpretation boundary

This merges the stated SOS route into IDEA-133 and does not reject all nonlinear moment representations. A flat toy matrix or exact planted atom is not a full ECDLP path or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-328/idea133_sos_merge_receipt.md` matching the pseudoexpectation, flatness, and atom extraction objects to IDEA-133 and identifying the first unsupplied source moment.
