# ECDLP-IDEA-095 — Geometric-Satake MV-cycle factorization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected`
- Evidence scale: `toy` convolution/basis preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: geometric Satake and MV cycles encode convolution
  multiplicities, not the original elliptic point sources; an exact Littelmann-path-to-
  source annotation restores the occupied Hall/Hecke enumeration.
- Breakthrough claim: **none**; a canonical-basis identity, MV cycle, or valid projected
  relation is not an ECDLP break.

## Falsifiable hypothesis

Associate every point in a target-independent elliptic factor base with a labelled
convolution object on an affine Grassmannian. Under geometric Satake, the target
convolution decomposes into a sparse MV-cycle/canonical basis whose Littelmann paths
factor uniquely into the original point atoms. Exact path inversion, Abel target
projection, `B+sigma` independent relation collection, factor-log calibration, and
masked-target descent all have complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **canonical MV-cycle factorization with an exact
Littelmann-path-to-elliptic-source inverse**. Convolution would turn factor atoms into a
Satake tensor product; MV cycles would provide a canonical basis, path factorization would
recover every labelled atom, and Abel projection would certify the elliptic sum.

This operation is rejected as a merge. Geometric Satake controls representation
multiplicities indexed by coweights. Those weights do not encode arbitrary
`E(F_p)` point labels. MV cycles and Littelmann paths can refine multiplicity spaces, but
they do not reconstruct which factor-base points produced a determinant/Abel class.
Adding exact point labels to every path recreates the extension/path table already
occupied by Hall, Hecke, and source-labelled convolution proposals.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order
   `N=p^(1+o(1))`, with `Q=[x]P`.
2. A target-independent factor base `F={F_1,...,F_B}` has `B=N^beta` and complete
   point/sign labels.
3. A scalar-blind functor maps each point atom to a Satake convolution object and maps
   tensor/convolution determinant to elliptic Abel addition on complete charts.
4. The relevant MV-cycle basis is finite, computable, target-independent, and has an
   exact inverse from each accepted path to the original point atoms.
5. Basis conversion, multiplicities, path branching, source output, relation rank,
   factor-log solving, target descent, verification, and peak memory are fully charged.
6. Coweights or path labels may not contain hidden factor logs, target-selected source
   tuples, or an explicit point-indexed convolution table.

## Semantic fingerprint

`factor_base_convolution_object | geometric_Satake_transform | MV_cycle_canonical_basis | Littelmann_path_atom_factors | exact_path_to_sources | Abel_target_descent`

The collision key is `canonical multiplicity basis without point support + exact path
annotation restores Hall/Hecke enumeration`. A basis conversion, tensor decomposition,
or determinant-only certificate is a control unless it creates point-source information
before aggregation.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the nearest hidden
   indecomposable block whose internal canonical representation still needs a point-source
   inverse.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-054`, where a representation/
   polarization descent fails to create the required source realization.
3. `ledger/FINDING-PF-IC-001.md` — imported `PO96`, the closest explicit saturation and
   decomposition question for a represented transfer object.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate
   barrier that canonical-basis vocabulary does not by itself remove.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where public feature coordinates do
   not contain factor-log orientation.

## Closest primary literature

- Mirković and Vilonen, [Geometric Langlands duality and representations of algebraic
  groups over commutative rings](https://arxiv.org/abs/math/0401222), establishes the
  geometric Satake equivalence and MV-cycle setting, not an elliptic point-source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the nearby exact factor-base decomposition relation.
- Shoup, [Lower bounds for discrete logarithms](https://www.shoup.net/papers/dlbounds1.pdf),
  supplies the generic square-root boundary.

No checked primary source attaches arbitrary finite-field elliptic point labels to MV
cycles in a way that survives convolution and admits sub-rho inverse factorization.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the reductive group, affine Grassmannian, atom functor,
   convolution order, MV-cycle basis, path convention, Abel projection, and exhaustive
   reference tuples.
2. Map every labelled factor atom to its convolution object and prove that Abel
   projection of a complete convolution equals the elliptic sum, including repeats,
   signs, stabilizers, and exceptional charts.
3. For known random targets `R=[a]P`, construct target convolution data without source
   advice, perform Satake/MV decomposition, invert every accepted Littelmann path to exact
   factor-base points, and independently verify the sum.
4. Retain all zero coefficients, multiplicities, duplicate paths, and failed inverses;
   collect at least `B+sigma` independently verified rows and their known target scalars.
5. Solve the factor-base logarithm system modulo `N` and independently verify every
   calibrated log on `E`.
6. Freeze the setup and apply the identical transform to masked blind targets
   `Q+[t]P`; obtain a complete source-labelled path factorization and substitute the
   factor logs.
7. Unmask every scalar candidate, retain all ambiguity, and accept only after verifying
   `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time `N^(1/2+o(1))` and constant state; BSGS has
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, functor/basis setup exponent be `a`,
per-target convolution and basis conversion exponent be `q`, MV-cycle/path branching and
source-output exponent be `o`, reciprocal relation and target densities be
`N^delta,N^delta_t`, factor-log linear algebra be `N^ell` with `ell>=2beta` absent
proved structure, and peak memory be `N^mu`.

The complete time exponent is

`lambda=max(a, beta+delta+q+o, ell, delta_t+q+o)`,

with `mu>=max(beta, basis_state, convolution_support, o)`. Every convolution summand,
multiplicity, MV component, path, basis coefficient, failed target, and emitted source
branch is charged. A short multiplicity vector paired with an explicit point/path table
inherits the table's full cost.

## Likely fatal obstruction

Geometric Satake converts convolution of orbit sheaves into tensor-product
representation data; it does not remember arbitrary point labels on an unrelated
elliptic curve. MV cycles and Littelmann paths index weight multiplicities, so distinct
point-source tuples can share the same coweight, cycle, and determinant. A target Abel
class cannot construct the source-retaining convolution object. If every path is
decorated with the required point atoms, the decoration is the full Hall/Hecke extension
ancestry and source enumeration reappears.

## Proof track

Construct the scalar-blind point-to-Satake functor, prove a biconditional between target
MV paths and exact factor-base decompositions, prove canonical point-source inversion with
sub-rho branching/output, and then prove relation rank, factor-log solving, blind descent,
verification, and `lambda,mu<1/2`.

## Disproof track

Exhibit distinct elliptic source tuples with the same MV/path data, show target-only data
does not construct the required convolution object, prove point annotation enumerates the
Hall/Hecke path fiber, or establish complete time/output/memory exponent at least `1/2`.

## Positive and negative controls

- Positive Satake control: low-rank groups with exhaustively known tensor products, MV
  cycles, and Littelmann paths.
- Positive source control: planted labelled convolution categories whose atom labels are
  genuinely part of the public basis.
- Negative label control: permute elliptic point labels while fixing all coweight and
  tensor multiplicity data.
- Aggregation control: distinct factor tuples with identical determinant/Abel class.
- Mechanism controls: Hall/Hecke extension enumeration and an explicit path-to-source
  dictionary, both charged at full size.
- Baseline control: matched Pollard-rho and BSGS runs.

## Quantitative promotion and falsification gates

No active promotion gate remains for this merged formulation. A mechanism-new successor
would require a point-labelled Satake functor and exact source inverse with zero errors on
exhaustive ordinary curves through 18 bits, at least `1,000` independent verified rows
and `100` blind descents at each of the two largest sizes, fresh rank at least `0.8B`, and
upper 95% bounds `a,q+o,lambda,mu<=0.45`. Falsify if label permutation leaves all MV data
unchanged, one accepted path has unresolved source multiplicity, source annotation has
lower 95% exponent `>=0.50`, or every complete arm has `lambda>=0.50`.

## Artifact plan

- Merge proof: `ideas/artifacts/ECDLP-IDEA-095/satake_hall_merge.md`
- Functor specification: `ideas/artifacts/ECDLP-IDEA-095/satake_atom_functor.yaml`
- Toy decomposer: `ideas/artifacts/ECDLP-IDEA-095/mv_cycle_factorization.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-095/verify_mv_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-095/analysis.md`
- Any future runs: `ideas/artifacts/ECDLP-IDEA-095/runs/<run-id>/`

## Interpretation boundary

This record is toy, heuristic, model-bound, and novelty-unverified. A correct Satake
equivalence, MV cycle, canonical-basis coefficient, Littelmann path, determinant equality,
valid relation, or recovered toy scalar is not evidence of a better-than-rho algorithm or
a cryptanalytic breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-095/satake_hall_merge.md` proving that MV-cycle and Littelmann-path data retain representation multiplicities but not arbitrary elliptic point-source labels without an explicit Hall/Hecke ancestry table.
