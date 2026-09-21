# ECDLP-IDEA-094 — Equivariant Hilbert fixed-point atomization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_localization_aggregation`
- Evidence scale: `toy` fixed-point/localization preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: equivariant localization returns aggregate fixed-point classes;
  a generic elliptic curve has no useful torus action, and source annotations restore the
  full incidence table.
- Breakthrough claim: **none**; a fixed-point formula, Hilbert-scheme class, or verified
  relation is not an ECDLP break.

## Falsifiable hypothesis

Map a target-independent elliptic factor base to torus-fixed ideals in an auxiliary
surface Hilbert scheme. Realize the target-conditioned addition incidence as an
equivariant Hilbert-scheme class whose localization has only `N^(r+o(1))`, `r<1/2`,
nonzero fixed branches. Invert each branch to exact factor-base atoms, push their class
through Abel addition, collect `B+sigma` independent rows, and perform blind masked-target
descent with complete time and memory below rho/BSGS.

## Mechanism-new operation

The proposed operation is **equivariant fixed-point localization followed by a canonical
fixed-branch-to-source inverse**. Factor atoms become fixed monomial ideals, the target
incidence class is localized, and each nonzero contribution is claimed to identify a
complete source tuple before Abel pushdown.

The operation is rejected. A generic ordinary elliptic curve has only finite
automorphisms, not the positive-dimensional torus action needed for an isolated fixed-
ideal basis. Moving to an auxiliary toric surface loses elliptic target orientation.
Localization computes a sum of contributions in equivariant cohomology; it does not
unrank the underlying point sources. Decorating fixed branches with exact point labels
materializes the original target/source incidence object.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order
   `N=p^(1+o(1))`, with `Q=[x]P`.
2. A target-independent factor base `F={F_1,...,F_B}` has `B=N^beta`, complete
   point/sign labels, and a scalar-blind embedding into a fixed-ideal Hilbert model.
3. A public torus action preserves the auxiliary target-incidence class and has a
   sub-rho set of isolated fixed branches on every generic input in scope.
4. Localization is exact over the stated coefficient ring, including zero weights,
   repeated points, nonreduced subschemes, poles, and exceptional addition charts.
5. Fixed-branch inversion returns exact curve points without an explicit point-to-ideal
   or target/source table.
6. Model construction, localization denominators, coefficient growth, branch output,
   relation rank, factor-log solving, descent, verification, and peak memory are charged.

## Semantic fingerprint

`factor_atoms_to_torus_fixed_ideals | target_incidence_Hilbert_scheme | equivariant_localization_source_classes | fixed_branch_inverse | Abel_pushdown | blind_descent`

The no-go key is `no generic elliptic torus action + localization aggregates classes +
source annotations restore incidence enumeration`. A Hilbert-scheme restatement, fixed-
point count, or post-hoc labelling of localized branches is a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate
   barrier that an auxiliary fixed-point basis must actually remove.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H686`, the nearest coordinate
   expansion/local-reconstruction theorem gap.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1447`, where raw coordinate-energy
   diagnostics do not become a source-generating mechanism.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1449`, the frozen primary
   coordinate-expansion negative control.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the m-ary membership exponent
   boundary that all localization construction and branch output must beat.

## Closest primary literature

- Białynicki-Birula, [Some theorems on actions of algebraic groups](https://doi.org/10.2307/1970840),
  supplies the fixed-point cell-decomposition framework for algebraic group actions,
  not a source-separating torus action on a generic elliptic curve.
- Ellingsrud and Strømme, [On the homology of the Hilbert scheme of points in the
  plane](https://doi.org/10.1007/BF01389419), supplies the torus-fixed/affine-cell setting
  for plane Hilbert schemes, not a generic elliptic target encoding.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the comparison relation fiber whose sources must be recovered.
- Shoup, [Lower bounds for discrete logarithms](https://www.shoup.net/papers/dlbounds1.pdf),
  supplies the generic square-root boundary.

These sources establish nearby primitives only. None provides a positive-dimensional
torus action on a generic elliptic curve or an exact fixed-branch source decoder.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the auxiliary surface, Hilbert component, torus action,
   incidence class, Abel pushdown, localization convention, and exhaustive reference
   enumerator.
2. Embed every labelled factor atom into a fixed ideal and prove that the target
   incidence class represents exactly the tuples whose elliptic sum is the supplied
   point, including repeats and exceptional charts.
3. For known targets `R=[a]P`, compute the complete localization formula, retain every
   zero/pole/cancelled branch, invert each surviving branch to exact point sources, and
   independently verify the elliptic sum.
4. Collect at least `B+sigma` independently verified rows with their known target
   scalars; retain duplicates and dependencies rather than silently resampling.
5. Solve the factor-base logarithms modulo `N` and independently verify every recovered
   log by checking its scalar multiple on `E`.
6. Freeze the setup, evaluate the same class for masked blind targets `Q+[t]P`, recover a
   complete source-labelled decomposition, and substitute the factor logs.
7. Unmask every scalar candidate, retain the complete ambiguity list, and accept only
   after verifying `[x]P=Q`.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, auxiliary-model and localization setup
be `N^a`, per-target fixed-point evaluation be `N^q`, retained fixed branches and exact
source output be `N^o`, reciprocal relation and target success densities be
`N^delta,N^delta_t`, factor-log linear algebra be `N^ell` with `ell>=2beta` absent a
proved structure, and peak memory be `N^mu`.

The full time exponent is

`lambda=max(a, beta+delta+q+o, ell, delta_t+q+o)`,

with `mu>=max(beta, fixed_basis, localization_state, o)`. Every fixed ideal, tangent
weight, denominator, cancellation certificate, failed target, and emitted branch is
charged. A compact aggregate class with an `N^(1/2)` source-unranking output does not
beat either baseline.

## Likely fatal obstruction

An elliptic curve is not a toric variety: a generic elliptic curve admits no
positive-dimensional algebraic torus action with isolated fixed points. An auxiliary
toric Hilbert scheme can localize its own equivariant classes, but the map back to
`E(F_p)` forgets the point labels and Abel orientation. Localization is additive, so
many source subschemes can contribute to the same fixed class. Making the contribution
source-specific requires annotations or fixed ideals indexed by the original tuples,
whose construction/output is the full relation table.

## Proof track

Construct a target-independent auxiliary torus action and incidence class, prove a
bijection between its nonzero fixed branches and exact elliptic factor-base tuples, and
prove sub-rho bounds for model size, localization, inversion, output, relation rank,
factor logs, blind descent, verification, and memory.

## Disproof track

Prove the generic curve has no admissible torus action, exhibit two distinct source tuples
with the same localized class, show the auxiliary pushdown loses point labels, show fixed-
branch annotation enumerates the incidence table, or establish `lambda>=1/2` after all
branches and output are charged.

## Positive and negative controls

- Positive localization control: `Hilb^m(A^2)` with its standard torus action and known
  partition-indexed fixed ideals.
- Positive source control: a planted toric addition model with an explicit fixed-branch
  inverse.
- Negative geometry control: generic ordinary elliptic curves with only finite
  automorphisms.
- Aggregation control: two source subschemes with equal equivariant pushdown but distinct
  point labels.
- Mechanism control: an explicitly annotated fixed-ideal table and ordinary tuple
  enumeration, both charged at full size.
- Baseline control: matched Pollard-rho and BSGS runs.

## Quantitative promotion and falsification gates

This formulation is rejected and has no active promotion gate. A versioned successor
would require an explicit scalar-blind torus/incidence construction, zero fixed-branch or
source errors on exhaustive curves through 18 bits, at least `1,000` independent rows and
`100` blind descents at each of the two largest sizes, and upper 95% bounds
`a,q+o,lambda,mu<=0.45`. Falsify immediately if no admissible generic torus action exists,
one localized class has two unresolvable source fibers, annotation count has lower 95%
exponent `>=0.50`, or every complete arm has `lambda>=0.50`.

## Artifact plan

- No-go derivation: `ideas/artifacts/ECDLP-IDEA-094/localization_aggregation_no_go.md`
- Model specification: `ideas/artifacts/ECDLP-IDEA-094/hilbert_model.yaml`
- Toy localizer: `ideas/artifacts/ECDLP-IDEA-094/fixed_point_atomization.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-094/verify_fixed_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-094/analysis.md`
- Any future runs: `ideas/artifacts/ECDLP-IDEA-094/runs/<run-id>/`

## Interpretation boundary

This record is toy, heuristic, model-bound, and novelty-unverified. A correct Hilbert
scheme, fixed ideal, localization identity, equivariant class, Abel pushdown, valid
relation, or recovered toy scalar is not evidence of a better-than-rho algorithm or a
cryptanalytic breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-094/localization_aggregation_no_go.md` proving that a generic elliptic target has no source-separating torus-fixed Hilbert localization without an explicit source-indexed incidence object.
