# ECDLP-IDEA-096 — Borcherds-product divisor factorization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected`
- Evidence scale: `toy` divisor/product derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: the vector-valued modular-form principal part prescribes the
  special divisor before the Borcherds lift; supplying an arbitrary target relation there
  already supplies the witness, while pullback/factorization merges with S-unit and modular
  quotient descent.
- Breakthrough claim: **none**; a convergent product, correct special divisor, valid
  principal relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Lift point-marked factor-base data to a vector-valued weakly holomorphic modular form whose
regularized theta lift is a Borcherds product. Its divisor should specialize to a sparse
sum of source-labelled Heegner atoms whose Abel image is a supplied elliptic target. The
infinite product is claimed to factor those atoms without enumerating the source fiber,
support `B+sigma` independent relations and factor-log calibration, and give a separate
masked-target descent with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **regularized theta lifting followed by Borcherds-product
divisor factorization and finite-field source specialization**. A point-marked principal
part would specify modular input data, the infinite product would expose Heegner divisor
atoms, and specialization plus Abel projection would return exact factor-base sources.

The operation is rejected as a merge. In Borcherds theory the negative Fourier
coefficients of the input principal part prescribe the special divisor. Encoding the
desired arbitrary factor-base/target divisor in that principal part therefore encodes the
relation before the lift. Without that encoding, Borcherds products produce only their
special-cycle support, not arbitrary factor-base atoms. Pulling such a product back to an
elliptic or modular quotient and factoring its principal divisor is the occupied
Miller/S-unit or modular-quotient source search.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order
   `N=p^(1+o(1))`, with `Q=[x]P`.
2. A deterministic target-independent factor base `F={F_1,...,F_B}` has
   `B=N^beta` and complete point/sign labels.
3. A scalar-blind marked modular construction maps arbitrary factor-base atoms and target
   classes to an admissible vector-valued principal part without first knowing a source
   relation.
4. The regularized theta lift, product expansion, divisor, integral model, reduction, and
   specialization are exact and cover every point/sign/exceptional branch.
5. Special divisor components invert canonically to exact finite-field source points,
   rather than only cycle classes or multiplicities.
6. Input construction, coefficient height, product truncation/certification, field
   extensions, divisor factoring, output, rank, factor logs, descent, verification, and
   peak memory are fully charged.

## Semantic fingerprint

`point_marked_vector_modular_form | regularized_theta_lift | borcherds_infinite_product | heegner_divisor_atoms | finite_field_source_specialization | blind_descent`

The collision key is `principal part already prescribes divisor + special-cycle support
is not arbitrary factor-base support + pullback factorization is S-unit/modular descent`.
A formal automorphic product or relation-only divisor certificate is a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P001`, the nearest exact native
   principal-divisor relation with public source recovery.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P048`, the closest exact balanced
   cover relation whose correct principal divisor does not by itself improve full cost.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-044`, where ordinary closed-point
   smoothness on a cover supplies no hidden factor-base advantage.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-002`, where target-coupled sparse
   divisor relations fail after rank and descent are charged.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H004`, the closest nonhomomorphic
   cover-label lane closed after exact pushforward and source accounting.

## Closest primary literature

- Borcherds, [Automorphic forms with singularities on Grassmannians](https://arxiv.org/abs/alg-geom/9609022),
  constructs regularized theta lifts and automorphic products whose special divisors are
  controlled by the modular input.
- Bruinier, [Borcherds products with prescribed divisor](https://arxiv.org/abs/1607.08713),
  makes the prescribed-divisor boundary explicit; it does not encode arbitrary elliptic
  factor-base relations for free.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the comparison decomposition relation and source obligation.

No checked source supplies a scalar-blind principal-part constructor for an arbitrary
finite-field elliptic target or a sub-rho source-specialization algorithm.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the orthogonal lattice/modular variety, vector-valued form
   space, principal-part grammar, theta-lift normalization, integral model, specialization
   map, and exhaustive tiny-curve source truth.
2. Map every labelled factor atom to admissible special-divisor data and prove that the
   construction uses neither its hidden scalar nor a preselected source relation.
3. For known random targets `R=[a]P`, build the point-marked modular input, compute and
   certify the Borcherds product/divisor, specialize all components, lift them to exact
   factor-base points, and independently verify their elliptic sum.
4. Retain every absent component, multiplicity, pole, failed specialization, duplicate,
   and dependency; collect at least `B+sigma` independently verified rows and their known
   target scalars.
5. Solve factor-base logarithms modulo `N` and independently verify each calibrated log
   on the original curve.
6. Freeze all target-independent data, construct the same input for masked blind targets
   `Q+[t]P`, factor and specialize a complete source-labelled divisor, and substitute the
   factor logs.
7. Unmask every scalar candidate, retain the complete ambiguity list, and accept only
   after verifying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, modular/lattice and product setup exponent
be `a`, per-target input/lift/product/divisor computation be `q`, divisor-factor/source-
specialization output be `o`, reciprocal relation and target densities be
`N^delta,N^delta_t`, factor-log linear algebra be `N^ell` with `ell>=2beta` absent
proved structure, coefficient/field-size exponent be `h`, and peak memory be `N^mu`.

The fully charged time exponent is

`lambda=max(a, h, beta+delta+q+o, ell, delta_t+q+o)`,

with `mu>=max(beta, product_state, divisor_support, h, o)`. Principal-part construction,
all Fourier coefficients needed for certification, product precision, special components,
field extensions, failed targets, and emitted sources are included. A correct divisor
whose input already lists its atoms receives no algorithmic credit.

## Likely fatal obstruction

The Borcherds lift does not discover a divisor independently of its input: the principal
part prescribes the special-cycle multiplicities. Arbitrary factor-base points on a
generic finite-field elliptic curve need not be Heegner/special divisors on the chosen
orthogonal modular variety. Writing the desired atoms into the principal part is circular;
omitting them yields an unrelated special divisor. Pullback and finite-field
specialization can also lose components or require factoring a principal function over
the full source space, reproducing the Miller S-unit/modular-quotient obstruction.

## Proof track

Construct a target-only, scalar-blind modular input whose Borcherds divisor has a proved
bijection with exact factor-base decompositions; prove certified product computation and
finite-field source specialization with sub-rho support/output; then prove relation rank,
factor-log calibration, blind descent, verification, and `lambda,mu<1/2`.

## Disproof track

Show the required principal part must contain the source divisor, show generic factor
atoms are not special cycles, show specialization/pullback loses point labels, reduce the
factorization to the occupied principal-divisor/S-unit search, or establish complete time,
height, output, or memory exponent at least `1/2`.

## Positive and negative controls

- Positive Borcherds control: published products with prescribed special divisors and
  independently checked product/divisor identities.
- Positive source control: a planted modular example whose special components are known
  and map injectively to toy curve points.
- Circularity control: one input principal part explicitly listing the desired atoms,
  charged as source advice.
- Negative support control: random factor-base points not lying on the available special
  divisor family.
- Mechanism controls: Miller S-unit principal-divisor search and modular-quotient
  factorization with identical source/output accounting.
- Baseline control: matched Pollard-rho and BSGS runs.

## Quantitative promotion and falsification gates

No active promotion gate remains for this merged formulation. A versioned successor
would require a noncircular target-to-principal-part theorem, zero divisor/source/
specialization errors on exhaustive ordinary curves through 18 bits, at least `1,000`
independent verified rows and `100` blind descents at each of the two largest sizes, and
upper 95% bounds `a,h,q+o,lambda,mu<=0.45`. Falsify if the principal part must name any
accepted source atom, generic factor-base support misses the special-divisor family,
specialization/source output has lower 95% exponent `>=0.50`, or every complete arm has
`lambda>=0.50`.

## Artifact plan

- Merge proof: `ideas/artifacts/ECDLP-IDEA-096/borcherds_sunit_merge.md`
- Modular input specification: `ideas/artifacts/ECDLP-IDEA-096/principal_part_spec.yaml`
- Toy product checker: `ideas/artifacts/ECDLP-IDEA-096/borcherds_factorization.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-096/verify_specialized_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-096/analysis.md`
- Any future runs: `ideas/artifacts/ECDLP-IDEA-096/runs/<run-id>/`

## Interpretation boundary

This record is toy, heuristic, model-bound, and novelty-unverified. A valid modular form,
regularized lift, automorphic product, special divisor, principal relation, finite-field
specialization, or recovered toy scalar is not evidence of a better-than-rho algorithm or
a cryptanalytic breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-096/borcherds_sunit_merge.md` proving that prescribing the accepted Borcherds divisor requires source advice and that target-only pullback factorization reduces to the occupied principal-divisor/S-unit or modular-quotient search.
