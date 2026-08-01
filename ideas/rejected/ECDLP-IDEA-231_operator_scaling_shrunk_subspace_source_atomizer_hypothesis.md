# ECDLP-IDEA-231 — Operator-scaling shrunk-subspace source atomizer

## Status and claim labels

- Class: `algorithm`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_operator_tuple_materializes_source_tensor_and_span_not_atoms`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired `review_required` theorem preflight; unapproved and zero-run
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; positive capacity, a null-cone certificate, or a shrunk subspace is not an ECDLP break.

## Falsifiable hypothesis

The endpoint-conditioned elliptic addition tensor admits a compact tuple of linear maps whose
operator-scaling limit or minimum shrunk subspace canonically exposes the exact signed factor-base
source coordinates.  The scaled marginals and rounded subspace would support independent relation
rows, full factor logs, and masked target descent with complete time and memory below rho and BSGS.

## Mechanism-new operation

The claimed operation is **compile the endpoint relation fiber into an implicit completely positive
operator, scale it to canonical marginals, and round its minimal shrunk subspace into exact point
sources**.  It earns credit only if the operator tuple is built without expanding the relation tensor
and the rounded subspace has a canonical all-source inverse.  Using operator scaling merely as a
rank, feasibility, invariant-theory, or solver backend is a control.

## Assumptions

1. The map tuple is target-independent apart from the public endpoint and is derived from public curve and factor-base data without hidden scalar or source advice.
2. Tuple description, scaling precision, iteration count, rounding, and peak state have exponents below `1/2` and do not materialize `B^m` tensor entries.
3. The minimum shrunk subspace determines every exact signed source, including multiplicities and boundary strata, rather than only a span or null-cone witness.
4. Setup, arithmetic bit complexity, output, relation density, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`implicit_elliptic_relation_operator | capacity_and_operator_scaling | minimum_shrunk_subspace | canonical_coordinate_to_point_atoms | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing compact source-fiber generator and transposed-target join.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate compression barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the measured transposed matrix/tensor-rank boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full phase-feature rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact sparse norm/resultant composition whose dense payload remains charged.

## Closest primary literature

- Garg, Gurvits, Oliveira, and Wigderson, [Operator scaling: theory and applications](https://arxiv.org/abs/1511.03730), gives polynomial-time capacity and noncommutative-rank algorithms for a supplied operator tuple.
- Franks, Soma, and Goemans, [Shrunk subspaces via operator Sinkhorn iteration](https://arxiv.org/abs/2207.08311), derives and rounds minimum shrunk subspaces for supplied linear maps over the complex field.

Neither paper constructs the implicit finite-field elliptic operator or turns a shrunk subspace into
exact point-labelled relation sources.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, operator compiler, scaling normalization, precision, rounding, and verifier.
2. Construct the endpoint operator tuple implicitly, with random-access products and adjoints, without enumerating source tuples.
3. Run scaling, certify capacity or a minimal shrunk subspace, round it, recover every exact signed source, and verify every elliptic sum.
4. Collect independent relation rows and solve and independently verify the complete factor-log system.
5. Apply the identical operator construction and source atomizer to fresh `Q+[t]P`, retain all ambiguity, and subtract `t`.
6. Accept only scalars satisfying `[x]P=Q`, charging arithmetic precision, output, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let operator setup time/memory be `N^a,N^a_m`, reciprocal relation and target densities
`N^delta,N^delta_t`, one scale/round/source inverse `N^q,N^q_m`, independent-rank gain
`N^r`, source output/ambiguity `N^o,N^u`, and factor-log completion
`N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Tuple dimensions, matvecs, precision, condition numbers, iterations, rounding, source output,
rank loss, factor logs, masked descent, and verification enter the exponents.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

Operator scaling consumes an explicit tuple of linear maps and returns marginal normalization,
capacity, or a subspace certificate.  Encoding the nonlinear elliptic source incidence in those maps
appears to materialize the same relation tensor or transition deck that the operation is supposed to
avoid.  Even with a compact matvec, a shrunk subspace identifies a linear span and is basis-covariant;
it does not canonically split into individual point-labelled source atoms.  Choosing such a basis or
rounding dictionary restores the source labels, while dense tuple dimension reaches the source-fiber
payload.

## Proof track

Give an implicit finite-field operator compiler with sub-rho dimensions and matvecs, prove a unique
source-labelled minimum shrunk subspace on every stratum, and bound scaling, rounding, output, rank,
descent, and memory so `lambda,mu<=0.45`.

## Disproof track

Reduce any faithful operator tuple to the explicit source tensor or show two source fibers related by a
basis action have the same capacity and shrunk-subspace dimensions but different point labels;
alternatively prove a dimension, condition, output, or complete-cost exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied small operator tuples with known noncommutative rank and independently verified minimum shrunk subspaces.
- Negative controls: basis-conjugated tuples, source-label permutations, random tensors with matched dimensions, IDEA-001/056/135/142/159, P1421/P1423, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a tuple description and matvec exponent at most `0.45`, exact all-source recall,
zero false sources, no explicit relation tensor, full factor-log rank, 100 blind descents at each of two
largest future toy sizes, and complete `lambda,mu<=0.45`.  Basis-dependent atoms, omitted precision,
source-tensor traffic, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-231/implicit_operator_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-231/operator_scaling_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-231/independent_shrunk_subspace_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-231/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative algorithm hypothesis.  Capacity convergence,
noncommutative rank, a null-cone witness, a rounded toy subspace, a valid relation, or a recovered toy
scalar is not crypto-scale validation, a complete ECDLP algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-231/implicit_operator_source_theorem.md` deriving a compact endpoint operator with a canonical exact-source inverse or proving that every faithful tuple factors through the explicit source tensor.
