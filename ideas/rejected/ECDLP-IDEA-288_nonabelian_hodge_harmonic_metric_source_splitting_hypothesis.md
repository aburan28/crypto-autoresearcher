# ECDLP-IDEA-288 — Nonabelian-Hodge harmonic-metric source splitting

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_harmonic_metric_correspondence_preserves_representation_not_source_labels`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid harmonic metric, Higgs decomposition, relation, recovered eigenline, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform complex or lifted representation of each ECDLP source fiber admits a canonical harmonic metric under nonabelian Hodge correspondence, and the resulting Higgs-field spectral splitting separates the exact factor tuple.  Decoding those components would yield relations and fresh-target descent with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile source equations into a semisimple local system, solve for its harmonic metric, pass to the corresponding Higgs bundle, and decode spectral/eigenline components as exact source factors**.  This is a representation-changing analytic splitting rather than an equation-solver substitution.  Simpson's correspondence relates already supplied semisimple local systems and polystable Higgs bundles on complex projective/Kähler spaces; it does not turn an endpoint into a labelled basis of hidden finite-field preimages.  A local system with one eigensummand per tuple imports a source-sized representation, while a compact representation merges tuples and the harmonic metric is unique only up to the relevant gauge data.  The operation merges with spectral-basis, full-rank-transform, and missing-section negatives.

## Assumptions

1. Public finite-field source equations and endpoint canonically lift to a compact complex geometric space and semisimple local system without knowing a source tuple.
2. The associated harmonic metric and Higgs spectral data preserve tuple labels through lifting, gauge equivalence, and descent back to the finite field.
3. Spectral splitting canonically returns exact signed factor-base points rather than aggregate monodromy or eigenvalue data.
4. Lifting, rank, local-system matrices, PDE/metric solution, Higgs conversion, spectral branches, precision certification, output, factor logs, descent, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | source_local_system_lift | nonabelian_hodge_harmonic_metric | higgs_spectral_source_split | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank basis change without source inversion.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the compressed invariant without exact source output.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the endpoint-selected representative boundary.
5. `inputs/ledger_inventory.json` — imported `P1477`, the geometric representation exact-return boundary.

## Closest primary literature

- Simpson, [Higgs bundles and local systems](http://www.numdam.org/item/PMIHES_1992__75__5_0/), develops the correspondence between suitable local systems and Higgs bundles using harmonic metrics in the complex geometric setting; it assumes the representation and does not decode finite-field source preimages.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field multivariate source equations whose bounded solutions the lifted correspondence would have to preserve and return exactly.

No checked primary source gives a target-uniform, complexity-preserving nonabelian-Hodge lift that splits an ECDLP source fiber; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source equations, characteristic-zero lift, geometric base, local-system compiler, metric/Higgs conventions, masks, and verifier.
2. For random known-log endpoints, construct the compact local system and certify its harmonic metric without enumerating source tuples.
3. Form the Higgs/spectral splitting, decode every accepted component to exact signed factor points, and verify each resulting relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen lift, metric construction, and splitting to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode all surviving spectral components to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging lift construction, representation rank, harmonic-metric solve, certification, spectral ambiguity, source output, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one lift/metric/Higgs/decode attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned spectral/source output be `N^o`, unresolved gauge/eigenline ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every lift coefficient, local-system matrix, representation dimension, metric iterate, precision bit, gauge transform, Higgs coefficient, spectral branch, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Nonabelian Hodge theory transports a supplied semisimple representation to equivalent differential-geometric data; it does not refine a many-to-one endpoint into its hidden source representatives.  Harmonic metrics and Higgs spectra are invariant under gauge and retain representation-level information, so tuple labels absent from the local system cannot reappear.  Encoding one subrepresentation or eigenline per tuple makes rank/state source-sized, and constructing that decomposition from a chosen tuple imports the witness.  Moreover, the analytic complex correspondence has no free exact finite-field descent.

## Proof track

Construct a witness-free exact lift, prove tuple injectivity modulo gauge and reduction, prove certified harmonic/Higgs splitting into original factor points on all strata, and certify complete `lambda,mu<=0.45` including precision and rank.

## Disproof track

Exhibit source tuples giving gauge-equivalent local systems or identical spectra, prove lift/rank/precision/output at least `N^0.50`, show the local-system compiler imports tuple labels, show exact finite-field descent fails, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy semisimple complex local system with a known harmonic metric and labelled Higgs eigensplitting.
- Negative controls: gauge-conjugate representations, repeated eigenvalues, reducible systems with permuted summands, lossy characteristic-zero lifts, source-indexed block matrices, numerical-only metrics, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires witness-free exact lifting, gauge-invariant tuple injectivity, certified all-strata factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  A gauge/spectral collision, source-labelled representation, lift/rank/precision/output exponent at least `0.50`, missing exact descent, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-288/nonabelian_hodge_split_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-288/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-288/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-288/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite lifted metric check would be toy and projections heuristic and model-bound.  A correct correspondence, harmonic metric, Higgs splitting, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-288/nonabelian_hodge_split_theorem.md` proving exact tuple-injective harmonic splitting or the gauge/rank/lift obstruction.
