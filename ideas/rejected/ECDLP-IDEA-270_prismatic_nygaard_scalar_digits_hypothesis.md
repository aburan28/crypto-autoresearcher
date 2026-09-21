# ECDLP-IDEA-270 — Prismatic Nygaard scalar digits

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_p_primary_prismatic_invariants_do_not_orient_prime_to_p_scalar`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Frobenius eigenvalue, Nygaard jump, valid relation, recovered digit, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform prismatic lift of the finite-field elliptic curve and marked pair `P,Q` has Frobenius and Nygaard-filtered observables whose graded jumps encode digits of the unknown prime-to-characteristic scalar `x` in `Q=[x]P`.  Reading and recombining those observables would return exact factor points or `x` with total time and memory below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the marked ECDLP instance to a prism, take Frobenius/Nygaard-filtered prismatic or Dieudonne data, and decode scalar digits from graded jumps before returning to the finite subgroup**.  This is not a same-field isogeny, a solver substitution, or a parameter change.  The obstruction is structural: prismatic Dieudonne theory naturally controls `p`-divisible or `p`-primary data in characteristic `p`, whereas the benchmark subgroup has prime order `N` coprime to `p`.  Functorial invariants of the unmarked curve and its subgroup are generator-invariant; marking enough of a section or comparison isomorphism to orient the `N`-torsion reimports the discrete-log coordinate.  It therefore merges with p-adic lift, formal-group, and transfer negatives once the prime-to-`p` orientation and return map are charged.

## Assumptions

1. Public `E/F_p,P,Q,N` admits a canonical target-uniform prism and comparison data computable without `x`.
2. Frobenius, Nygaard filtration, and any prismatic Dieudonne realization retain nontrivial information about the prime-to-`p` relation `Q=[x]P`.
3. Scalar digits or exact source factors can be decoded from compressed graded data and returned to `E(F_p)` without a source-labelled basis.
4. Prism construction, precision, filtration, matrices, comparison maps, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | prismatic_lift | Frobenius_Nygaard_graded_digits | prime_to_p_scalar_orientation | exact_source_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `OFQ-autolab-05`, the p-adic and ordinary-formal lifting boundary.
2. `inputs/ledger_inventory.json` — imported `ISO-SP-001`, the isogeny and subgroup-orientation control.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the arithmetic-transfer compatibility hypothesis.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the local-to-global return-map hypothesis.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the transfer-state and target-return negative.

## Closest primary literature

- Bhatt and Scholze, [Prisms and prismatic cohomology](https://doi.org/10.4007/annals.2022.196.3.5), defines prismatic cohomology and the Nygaard/Frobenius structures used by the proposed lift.
- Anschutz and Le Bras, [Prismatic Dieudonne theory](https://arxiv.org/abs/1907.10525), relates prismatic objects to `p`-divisible groups, exposing the p-primary scope.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field factor-base baseline and source equations.

No checked source supplies a prime-to-`p` scalar decoder or sub-rho return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the prime-field instance, prism/lift rule, precision schedule, Nygaard grades, observables, factor base, masks, and verifier.
2. Build the prism and Frobenius/Nygaard data for the curve and marked public points without using scalar labels or a source basis.
3. On known-log endpoints, decode proposed graded digits and map every accepted output to exact signed factor points in `E(F_p)`.
4. Verify relations, collect independent rows, solve every factor log, and verify each recovered log on the curve.
5. Apply the identical frozen construction to fresh masked targets `Q+[t]P`; retain every filtration branch and precision lift.
6. Decode a complete factor decomposition or scalar residue, remove the mask, and reject any output not satisfying the exact group equation.
7. Accept only an exact `x` with `[x]P=Q`, charging all precision, comparison, ambiguity, relation, descent, and memory receipts.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one prism/filtration/decode/return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, output multiplicity be `N^o`, surviving filtration ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every Witt/prismatic coefficient, precision digit, Frobenius matrix, Nygaard grade, comparison map, failed lift, source branch, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

The available prismatic and Dieudonne structures are tuned to characteristic-`p` infinitesimal and `p`-divisible information.  The ECDLP lives in a cyclic group of order `N` coprime to `p`, so multiplication by `N` is etale and carries no Nygaard digit filtration analogous to the proposed scalar expansion.  Functorial unmarked data are invariant under changing the generator, while a marked comparison basis capable of distinguishing `[x]P` from `[y]P` is precisely an oriented source coordinate.  Thus the observable either forgets `x` or its input already contains it.

## Proof track

Construct a canonical prime-to-`p` prismatic observable, prove target-uniform scalar sensitivity and exact source return, and certify complete exponents at most `0.45` without a source-labelled comparison basis.

## Disproof track

Prove the observable factors through p-primary/unmarked data, demonstrate invariance under prime-to-`p` generator changes, show the comparison input determines the scalar, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied `p`-power torsion example with known Dieudonne coordinates and known scalar digits.
- Negative controls: prime-to-`p` cyclic subgroups with changed generators, unmarked isomorphic curves, random Nygaard grades, ordinary p-adic/formal lifts, same-field isogenies, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires scalar-sensitive prime-to-`p` prismatic data, exact all-strata source return, full factor-log rank, blind masked-target descent, and complete `lambda,mu<=0.45`.  Generator invariance, p-primary-only information, source-labelled comparison data, output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-270/prismatic_nygaard_scalar_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-270/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-270/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-270/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative arithmetic-transfer proposal.  Every finite check would be toy and projections heuristic and model-bound.  A valid prism, comparison, filtration jump, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-270/prismatic_nygaard_scalar_theorem.md` proving prime-to-`p` scalar sensitivity and source return or the p-primary/orientation obstruction.
