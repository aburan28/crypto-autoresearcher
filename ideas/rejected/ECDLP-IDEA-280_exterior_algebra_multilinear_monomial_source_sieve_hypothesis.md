# ECDLP-IDEA-280 — Exterior-algebra multilinear-monomial source sieve

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_multilinear_detection_is_relation_only_and_witness_extraction_materializes_sources`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a detected multilinear monomial, nonzero wedge, valid relation, recovered witness, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

An arithmetic circuit compiled from the ECDLP summation/source equations has a distinguished multilinear monomial exactly when the endpoint has a factor-base decomposition.  Random exterior- or group-algebra evaluation would cancel repeated-factor paths while retaining squarefree solution monomials, and a compact witness decoder would return exact factor points for rows and fresh-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile source branches into monomials, substitute exterior/group-algebra labels so repeated variables annihilate, detect surviving multilinear support, and decode a surviving monomial to an exact source tuple**.  The cancellation sieve is algorithmically distinct from a dense resultant or a mere parameter change.  Koutis-style multilinear detection is fundamentally an existence test for a bounded-degree monomial in a supplied circuit; it does not return the endpoint-selected factor tuple, and its exponential dependence on degree is hidden only when degree is treated as fixed.  Self-reduction needs repeated restricted evaluations and a source-addressable variable universe, while a circuit with one monomial per factor tuple can already materialize the dense source deck.  The idea therefore merges with relation-only certificates, selector-free row tests, and source enumeration once witness, density, rank, and descent are included.

## Assumptions

1. Public source equations and an endpoint compile to an arithmetic circuit of sub-rho size whose multilinear monomials correspond exactly to valid signed factor tuples.
2. Exterior/group-algebra evaluations avoid characteristic, sign, and cancellation failures across every relevant source stratum.
3. A surviving monomial can be decoded to exact factor points with sub-rho calls, output, and ambiguity rather than merely certifying existence.
4. Circuit construction, algebra dimension, random labels and repetitions, self-reduction, witnesses, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | source_circuit_monomial_encoding | exterior_algebra_repetition_annihilation | multilinear_support_detection | exact_witness_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator and witness decoder.
2. `inputs/ledger_inventory.json` — imported `P1477`, the decision-to-exact-source return boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the circuit/product source-materialization control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the relation-level nonzero test without source output.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the witness extraction and fresh-target descent requirement.

## Closest primary literature

- Koutis, [Faster algebraic algorithms for path and packing problems](https://doi.org/10.1007/978-3-540-70575-8_47), introduces algebraic cancellation techniques for detecting multilinear monomials in circuits, motivating the proposed source sieve.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the source equations whose solution tuples would have to be represented as decodable monomials.

No checked source supplies a compact ECDLP source circuit together with all-strata exact witness extraction and complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, circuit compiler, monomial degree and variable encoding, algebra substitution distribution, factor base, masks, and verifier.
2. Compile known-log relation endpoints into circuits and evaluate the complete exterior/group-algebra sieve with preregistered repetitions and no source-tuple advice.
3. For every positive detection, perform the frozen witness decoder, retain all cancellation branches, and map each recovered monomial to exact signed factor points.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen compilation, sieve, and decoder to fresh masked targets `Q+[t]P` without post-hoc selectors or target-specific tuning.
6. Retain every surviving witness, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging circuit size, algebra dimension, repetitions, false negatives, self-reduction calls, witness output, rows, factor logs, fresh-target descent, verification, and live state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one compile/sieve/witness-return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, witness output be `N^o`, cancellation or decoding ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every circuit gate and edge, monomial degree, algebra basis element, random vector, repetition, cancellation event, restricted self-reduction, witness branch, failed return, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Multilinear-monomial sieves decide whether some support survives; they do not expose the support label carried through a compressed algebra evaluation.  A self-reduction can seek a witness only if variables individually address candidate factors and repeated oracle calls preserve success, which charges the factor-base/source universe and still pays the original relation density.  Encoding complete elliptic-curve compatibility in monomial support either makes the circuit enumerate source combinations or permits false multilinear monomials.  Thus a nonzero exterior element is a relation-only certificate unless the missing source-output operation is separately supplied.

## Proof track

Construct a sub-rho-size endpoint circuit with exact solution-monomial correspondence, prove characteristic-safe detection and witness decoding of exponent at most `0.45`, and certify both complete exponents at most `0.45`.

## Disproof track

Exhibit false or cancelling solution monomials, prove circuit/algebra/witness state at least `N^0.50`, show self-reduction materializes the source universe or preserves only existence, demonstrate fresh-target failure, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small circuit with one labelled multilinear monomial and a known witness under a characteristic-safe substitution.
- Negative controls: circuits containing only repeated-variable monomials, cancelling multilinear pairs, positive existential tests with hidden supports, relation-only certificates, materialized source products, random row selectors, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an exact compact circuit and all-strata witness decoder of exponent at most `0.45`, independently verified source tuples, full row rank and factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Existence-only output, false/cancelled monomials, source-materialized circuits, circuit/algebra/witness state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-280/exterior_multilinear_witness_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-280/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-280/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-280/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative conservative algorithm proposal.  Every finite circuit evaluation would be toy and projections heuristic and model-bound.  A nonzero wedge, detected monomial, valid relation, or toy witness does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-280/exterior_multilinear_witness_theorem.md` proving compact exact witness extraction or the existence-only/circuit-size/source-materialization obstruction.
