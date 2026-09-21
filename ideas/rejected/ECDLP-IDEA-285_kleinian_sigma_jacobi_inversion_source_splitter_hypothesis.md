# ECDLP-IDEA-285 — Kleinian-sigma Jacobi-inversion source splitter

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_jacobi_inverse_recovers_reduced_divisors_not_factor_tuples`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid sigma identity, Jacobi inversion, relation, recovered divisor, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform hyperelliptic representation of each ECDLP source fiber admits compact Abel–Jacobi coordinates whose Kleinian sigma derivatives canonically split the endpoint into the exact factor-base points.  Jacobi inversion would then supply relations and fresh-target descent with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the source equations into a hyperelliptic Jacobian, map the endpoint to Abel–Jacobi coordinates, and use Kleinian sigma-function Jacobi inversion to recover labelled source points**.  This is a representation-changing inversion, not a replacement equation solver.  Kleinian functions can encode reduced divisors and explicit Kummer/Jacobian data after a curve, period or algebraic sigma data, and Abelian argument are supplied.  For source length above the genus, the Abel map has positive-dimensional or combinatorial fibers; choosing a genus or curve that makes every tuple a unique reduced divisor expands the representation with the source alphabet.  Thus the operation merges with reduced-divisor, materialized-product, and full-rank inverse controls after compiler, sigma data, branches, and exact return are charged.

## Assumptions

1. Public source equations and endpoint canonically determine a hyperelliptic curve and Abel–Jacobi state without a known factor tuple.
2. The state retains enough information to distinguish every relevant ordered or signed source tuple despite divisor reduction and permutation.
3. Kleinian sigma derivatives and Jacobi inversion are exact and sub-rho over the required finite-field or algebraic model and return factor-base points.
4. Curve construction, genus, sigma/theta data, extension arithmetic, branch output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | hyperelliptic_source_embedding | kleinian_sigma_jacobi_inversion | reduced_divisor_source_split | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the invertible representation change without source inversion.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the source-product materialization control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the compressed invariant without exact source output.
5. `inputs/ledger_inventory.json` — imported `P1477`, the representation-changing exact-return boundary.

## Closest primary literature

- Buchstaber, Enolskii, and Leykin, [Hyperelliptic Kleinian functions and applications](https://arxiv.org/abs/solv-int/9603005), develops Kleinian functions and explicit hyperelliptic Kummer and spectral constructions; it assumes the hyperelliptic representation and does not invert an unrelated finite-field source fiber.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the multivariate finite-field source equations whose bounded solutions would have to survive the representation and be returned exactly.

No checked primary source gives a compact tuple-injective compilation from Semaev fibers to Kleinian Jacobi inversion; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source equations, hyperelliptic compiler, Abel map, sigma normalization, inversion convention, masks, and verifier.
2. For random known-log endpoints, build the auxiliary curve and compact Abel–Jacobi state without enumerating source tuples.
3. Evaluate sigma derivatives, invert every accepted state to exact signed factor points, and verify each resulting relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen compiler and inversion to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode every surviving Jacobi branch to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging curve/genus construction, sigma data, inversion arithmetic, branch ambiguity, source output, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one compile/sigma/inversion attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned divisor/source output be `N^o`, unresolved Abel-fiber ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every auxiliary coefficient, genus unit, period or algebraic sigma datum, derivative, extension element, Jacobi branch, reduced divisor, failed inversion, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Jacobi inversion returns a reduced divisor for a point of a chosen Jacobian; it does not recover an arbitrary longer decomposition that mapped to that point.  Divisor reduction, permutation, and Abel-map fibers erase source labels.  Raising the genus or enriching the sigma state until all source tuples are distinct makes the curve/state size or branch output track the source alphabet, while forming the Abelian argument from a desired tuple imports the witness.  The representation therefore reorganizes a supplied decomposition but supplies no compact endpoint-selected section.

## Proof track

Give a witness-free compiler, prove tuple injectivity through divisor reduction on all strata, prove exact sigma inversion into original factor points, and certify complete `lambda,mu<=0.45` including genus and output.

## Disproof track

Exhibit distinct source tuples with the same Abel–Jacobi state, prove required genus/state or branch output at least `N^0.50`, show the compiler or Abelian argument imports the tuple, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy hyperelliptic curve, a generic degree-`g` reduced divisor, its Abelian state, and an independently checked sigma inversion.
- Negative controls: degree above genus, linearly equivalent distinct effective divisors, permuted factor labels, compressed sigma jets, explicit tuple-built Abel states, materialized products, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires witness-free tuple-injective compilation, exact all-strata factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  An Abel-fiber collision, divisor-label loss, source-built input, genus/state/output exponent at least `0.50`, missing factor return, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-285/kleinian_source_split_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-285/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-285/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-285/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite sigma/Jacobi check would be toy and projections heuristic and model-bound.  A correct Kleinian identity, reduced divisor, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-285/kleinian_source_split_theorem.md` proving tuple-injective Jacobi inversion or the Abel-fiber/genus-growth obstruction.
