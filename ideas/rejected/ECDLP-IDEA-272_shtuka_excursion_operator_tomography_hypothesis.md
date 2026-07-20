# ECDLP-IDEA-272 — Shtuka excursion-operator tomography

## Status and claim labels

- Class: `automorphic_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_global_shtuka_realization_and_source_labelled_legs_unsupplied`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an excursion eigenvalue, Langlands parameter, valid relation, recovered factor, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A canonical global-function-field and shtuka realization of the marked finite-field ECDLP produces commuting excursion operators whose joint spectrum separates the unknown source point or its factor tuple.  Tomography of that spectrum would return exact factors and complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **globalize the marked subgroup into a multi-leg shtuka, evaluate excursion operators indexed by leg permutations and dual-group functions, and invert their joint spectrum to a source point**.  This is more than a Fourier or ordinary character substitution.  Excursion operators recover global Langlands parameters from automorphic data; they do not canonically factor a supplied elliptic-curve endpoint.  Building a global shtuka whose legs distinguish every `[x]P`, or a vector on which the spectrum is source-faithful, requires the missing globalization, point labels, and automorphic state.  Once those are charged, the proposal merges with representation/character tomography and transfer-return negatives.

## Assumptions

1. Public `E/F_p,P,Q,N` canonically determines a global curve, reductive group, level structure, shtuka stack, and automorphic state without `x`.
2. A compact family of excursion operators has a joint spectrum injective on the ECDLP source fiber.
3. The spectrum admits an exact sub-rho inverse to signed factor points rather than only a Langlands parameter.
4. Globalization, cohomology/state construction, operator evaluation, spectrum output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | global_shtuka_realization | excursion_operator_joint_spectrum | source_tomography | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H008`, the automorphic/global-transfer hypothesis.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-030`, the globalization and source-compatibility negative.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the transfer-output and return-map negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transform without source inversion control.
5. `inputs/ledger_inventory.json` — imported `P1479`, the transformed-spectrum source-return frontier.

## Closest primary literature

- V. Lafforgue, [Chtoucas pour les groupes reductifs et parametrisation de Langlands globale](https://doi.org/10.1090/jams/897), constructs excursion operators and global Langlands parameters over function fields.
- Mirkovic and Vilonen, [Geometric Langlands duality and representations of algebraic groups over commutative rings](https://arxiv.org/abs/math/0401222), supplies the geometric Satake representation machinery behind multi-leg constructions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations and factor-base baseline.

No checked source gives a canonical ECDLP-to-shtuka globalization or a joint-spectrum inverse to source factors; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the ECDLP instance, globalization, group/level/leg data, automorphic state, excursion family, factor base, masks, and verifier.
2. Construct the shtuka cohomology/state and commuting excursion operators without source enumeration or target advice.
3. On known-log endpoints, evaluate the joint spectrum and map every accepted spectral branch to exact signed factor points.
4. Verify relations, collect independent rows, solve all factor logs, and verify them on `E(F_p)`.
5. Globalize fresh masked targets `Q+[t]P` with the identical frozen rule and evaluate the same operator family.
6. Invert every surviving joint eigenpacket to a complete factorization or scalar residue, remove the mask, and verify exact endpoint equality.
7. Accept only `[x]P=Q`, charging global-model search, cohomology, operators, eigenpackets, ambiguity, factor logs, descent, and live state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one globalization/operator/tomography/return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, eigenpacket output be `N^o`, inverse ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every global curve and level candidate, shtuka leg, cohomology class, operator matrix, eigenpacket, failed inverse, source branch, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Excursion spectra canonically encode a semisimple global Langlands parameter of an automorphic representation, not a chosen point in an unrelated finite cyclic source fiber.  There is no public target-uniform globalization preserving `Q=[x]P`.  Adding marked legs or a vector until eigenvalues distinguish all source points supplies a source-labelled state whose dimension, construction, or output carries the missing deck.  Even a valid parameter therefore lacks the exact return map demanded by descent.

## Proof track

Construct the canonical compact globalization and source-faithful excursion family, prove exact spectral inversion to factor points, and certify complete time and memory exponents at most `0.45`.

## Disproof track

Show globalization is noncanonical or scalar-dependent, exhibit spectral collisions, prove source-faithful legs/state materialize `N^0.50` or larger data, show no exact return, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied global shtuka and automorphic eigenstate with a known Langlands parameter.
- Negative controls: distinct source labels with the same unmarked globalization, permuted legs, random automorphic states, abelian character tables, point-faithful regular representations, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a target-uniform compact globalization, injective excursion spectrum, exact all-strata factor return, blind descent, and complete `lambda,mu<=0.45`.  Noncanonical globalization, spectral collisions, source-labelled state, missing return, output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-272/shtuka_excursion_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-272/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-272/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-272/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative automorphic-transfer proposal.  Every finite surrogate would be toy and projections heuristic and model-bound.  A correct eigenpacket or Langlands parameter does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-272/shtuka_excursion_source_theorem.md` proving canonical globalization and spectral source return or the globalization/state/return obstruction.
