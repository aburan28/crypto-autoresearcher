# ECDLP-IDEA-148 — Isolation-weight lowest-monomial source extractor

## Status and claim labels

- Class: `algebraic-algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `rejected_isolation_requires_source_generating_polynomial`
- Cohort: `20260718-a`
- Evidence scale: paper mechanism audit only; no experiment ran
- Contract posture: rejected archival record; no execution contract
- Scale labels: every prospective finite test is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an isolated monomial, exact tuple, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

For every public target `R`, compact elliptic equations admit a target-local arithmetic circuit whose nonzero multilinear monomials are biconditional with exact signed factor-base decompositions of `R`. Random isolation weights would select a unique lowest monomial with constant probability, and black-box valuation plus logarithmic derivatives would recover its source indices below rho without expanding the relation polynomial.

## Mechanism-new operation

The proposed operation is **pre-expansion isolation of a source-generating polynomial followed by lowest-valuation source inversion**. Public random weights are assigned to factor-base variables, the circuit is evaluated over a weighted truncated series ring, and the unique minimum monomial is recovered from its valuation and derivatives. Isolation itself is not the mechanism unless the source-generating circuit is constructed from `(E,F,R)` before source enumeration.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and public factor base `F` of size `B=N^beta`.
2. A compact target-local circuit `G_R(z_1,...,z_B)` has one noncancelling multilinear monomial for each exact signed five-source tuple and no false monomials.
3. The circuit is built without enumerating tuples, materializing a `B^2` or larger coefficient object, or using scalar-labelled variables.
4. Isolation weights are public and independent; all collisions, zero coefficients, characteristic-dependent cancellation, and retries are retained.
5. Lowest valuation and logarithmic-derivative data recover exact source indices and multiplicities, not only an aggregate weight or relation count.
6. Circuit construction, precision, failed seeds, output, rank, factor logs, blind descent, verification, and peak bit memory are charged.

## Semantic fingerprint

`endpoint_conditioned_source_generating_polynomial | pre_expansion_random_isolation_weights | black_box_lowest_valuation_monomial | logarithmic_derivative_source_inverse | blind_target_reuse`

The removal test is a public compact circuit plus an exact pre-expansion source inverse. Applying isolation to an enumerated monomial list, dense resultant, supplied quotient, or relation table is a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, whose missing public source-fiber generator is precisely the required circuit constructor.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H662`, which tests transposed exact factor-membership evaluations across pair states and target batches.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact value matrices retain full source-state rank.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`, the exact cubic source-generation and target-batch baseline.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where a logarithmic one-transition norm is exact but source-complete composition becomes dense quadratic.

## Closest primary literature

- Mulmuley, Vazirani, and Vazirani, [Matching is as easy as matrix inversion](https://doi.org/10.1145/28395.383347), introduces the isolation mechanism in a represented combinatorial family but does not construct an elliptic source polynomial or its source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation equations but no compact source-generating circuit.

No checked primary source gives this constructor and complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, source-variable encoding, circuit grammar, weight distribution, precision, masks, and verifier.
2. Construct `G_R` from public compact equations for a known endpoint `R` without enumerating source tuples or coefficient support.
3. Assign preregistered isolation weights, evaluate the lowest nonzero valuation, and recover every index of the selected monomial through typed derivative data.
4. Verify the emitted signed tuple by factor-base membership and direct elliptic addition; retain cancellations, ties, misses, retries, and false outputs.
5. Repeat the identical recipe on known `R_j=[r_j]P` until `B+sigma` verified rows have rank `B`, charging all failed seeds and outputs.
6. Solve and independently verify every factor-base logarithm.
7. Apply the frozen circuit/weight procedure to fresh `Q+[t]P`, substitute logs, subtract `t`, and enumerate all ambiguity.
8. Accept only `[x]P=Q` and preserve complete circuit, precision, output, time, rank, and memory receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; circuit derivation cost `N^a,N^a_m`; reciprocal relation and target densities `N^delta,N^delta_t` including isolation retries; one valuation/source query `N^q,N^q_m`; source output and ambiguity `N^o,N^u`; and factor-log linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

For `beta=0.20` and constant densities/output, promotion requires `q<=0.25`. A `B^2` circuit, coefficient array, or derivative pass per target makes the relation campaign `N^0.60`; a `B^5` monomial family is `N` before extraction.

## Likely fatal obstruction

The isolation lemma selects a unique member only after the combinatorial family is represented. Constructing or evaluating `G_R` is the original P1434 source-fiber problem; generic elimination exposes dense `B^m` coefficients, and compact one-transition identities densify on composition. Lowest degree or a derivative can also reveal only an aggregate weight unless source-labelled variables and all coefficient provenance were already retained.

## Proof track

Give an explicit target-local circuit with a monomial/source biconditional, prove cancellation-free isolation and exact derivative-to-index inversion, and bound its construction, precision, retries, complete relation campaign, factor-log solve, and blind descent by `lambda,mu<=0.45`.

## Disproof track

Reduce circuit construction or valuation to the P1434 generator, prove `Omega(B^2)` represented traffic per target, exhibit characteristic cancellation or equal-weight source ambiguity, or show that exact derivative recovery requires the full labelled coefficient support.

## Positive and negative controls

- Planted sparse multilinear polynomials with a known unique minimum source monomial.
- The same polynomials with collisions, cancellation, repeated variables, and zero coefficients.
- Enumerated elliptic source polynomials as inadmissible supplied-input controls.
- P1478 one-transition and dense-composition controls plus the P1435 cubic generator baseline.
- Known-log and blind unknown-log targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

This mechanism is rejected at the missing source-polynomial boundary. A fresh ID requires a public circuit of sub-`B^1.25` complete query cost at `beta=0.20`, isolation success at least `1/2` per independent seed, `100%` exact-source recovery and `0` false outputs on exhaustive fixtures, and complete `lambda,mu<=0.45`. Falsify on one false or missed source, a supplied source list, any `B^2` per-target circuit/traffic stage, uncharged precision or retries, or complete time or memory exponent at least `0.50`.

## Artifact plan

- Source-polynomial isolation audit: `ideas/artifacts/ECDLP-IDEA-148/isolation_source_polynomial_gate.md`
- Circuit grammar: `ideas/artifacts/ECDLP-IDEA-148/circuit_spec.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-148/fixtures.json`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-148/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-148/cost_analysis.md`

All paths are prospective; no run or experiment artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified algebraic-algorithm evidence. Any finite test would be toy, and all scaling claims remain heuristic and model-bound. Isolation or a correct tuple would prove only scoped functionality, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-148/isolation_source_polynomial_gate.md` proving whether the public circuit can be constructed and source-inverted before coefficient or tuple expansion, without implementing a solver.
