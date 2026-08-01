# ECDLP-IDEA-049 — Bounded-root decomposition transducer

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `deferred_missing_height_theorem`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a small root on a toy lift is not an ECDLP break.

## Falsifiable hypothesis

There is a public integral lift of complete elliptic addition that transduces an
`m`-point factor-base decomposition of `R` into a polynomial system with an integer root
vector bounded by `N^eta`, while modulus and lattice determinant permit rigorous
multivariate small-root recovery in `N^(c+o(1))` time with `c<1/2`. The recovered root
must invert to the actual source points.

## Mechanism-new operation

The new operation would be an **operation-preserving bounded integral transducer**:
addition-law carries and denominator charts are encoded so the hidden decomposition,
not merely a bounded predicate value, becomes a certified small integer root.
Coppersmith lattice reduction is downstream. A coordinate bound, parameter change,
generic lattice solver, or relation certificate alone is a duplicate/control.

## Assumptions

1. `E(F_p)` has prime subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. A deterministic factor base `F` has `B=N^beta` and a target-independent integral encoding.
3. The lift covers modular wraparound, denominators, signs, and exceptional additions.
4. Root bounds and determinant inequalities are proved, not inferred from selected successes.
5. Every recovered integer root maps bijectively to factor-base source points.
6. All scaling claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`complete_addition_integral_lift | bounded_decomposition_root | carry_transducer | lattice_small_root_extraction | exact_source_inverse`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — fixes the membership-quotient baseline.
2. `ledger/H-REP-001.yaml` — blocks coordinate-only rewrites.
3. `ledger/EV-REP-001.yaml` — supplies representation controls.
4. `ledger/H-FB-001.yaml` — blocks factor-base retuning as the mechanism.
5. `ledger/SYNTHESIS-20260716.md` — requires complete target descent and cost accounting.

## Closest primary literature

- Coppersmith, [Finding a small root of a bivariate integer equation](https://doi.org/10.1007/3-540-68339-9_14), gives the small-root backend and determinant conditions.
- Howgrave-Graham, [Finding small roots of univariate modular equations revisited](https://doi.org/10.1007/BFb0054862), gives rigorous lattice small-root criteria.
- Jacobson, Koblitz, Silverman, Stein, and Teske, [Analysis of the Xedni calculus attack](https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf), gives the closest integral-lift height and coefficient-growth obstruction.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies the complete-chart requirement.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), is the nearby modular decomposition formulation.

No source proves the required bounded integral transducer; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,m,beta,F` and a complete integral addition atlas.
2. Transduce known `R=[a]P` decomposition constraints into bounded-root systems with audited carries.
3. Construct the lattice from preregistered monomials and recover all certified small roots.
4. Invert roots to points in `F` and independently verify their sum and every chart condition.
5. Collect independent relations and solve factor-base logarithms.
6. Apply the identical lift to `Q+[t]P`, recover sources, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho is `N^(1/2+o(1))` time with constant state; BSGS is
`N^(1/2+o(1))` time and memory. Let lattice construction/reduction exponent be `c`,
build and storage `a,s`, reciprocal relation and target densities `delta,delta_t`, and
`B=N^beta`. Then `lambda=max(a,beta+delta+c,2beta,delta_t+c)` and
`mu=max(s,beta,l)`, where `N^l` is the full lattice bit-size including coefficient
heights. Promotion requires `lambda,mu<1/2`; dimension, LLL/BKZ cost, failed roots, and
verification are charged.

## Likely fatal obstruction

Modular addition wraparound makes the informative carries as large as the modulus, while
eliminating them recreates the dense membership resultant. The lattice determinant/root
bound may therefore fail before source recovery, or lattice dimension may itself reach
`N^(1/2-o(1))`.

## Proof track

Construct the transducer, prove completeness and boundedness, verify the small-root
determinant inequality and source inverse, and derive full `lambda,mu<1/2`.

## Disproof track

Prove any complete lift needs modulus-sized carries or supercritical lattice dimension,
find a missing/false source, or show all full-cost arms have `lambda>=1/2`.

## Positive and negative controls

- Positive control: planted modular systems with certified small roots and identical lattice dimensions.
- Positive correctness control: exhaustive tiny-curve decompositions.
- Negative control: random modular systems and randomized carries of matched size.
- Mechanism control: ordinary Semaev plus generic Coppersmith preprocessing.
- Integral-lift control: the published Xedni-style lift with all coefficient and denominator growth charged.
- Leakage control: forbid target-selected bounds, known scalar coordinates, tuple tables, and post-hoc lattice bases.

## Quantitative promotion and falsification gates

Deferral can lift only after an exact complete two-addition transducer proves
`eta` within a rigorous small-root region and source inversion on every ordinary curve in
a symbolic generic family. A later toy study would require zero false/missed exhaustive
witnesses, at least 20 curves per size, and upper 95% `c,lambda,mu<=0.45`. Reject if
generic carries are modulus-sized, the determinant inequality fails asymptotically, or
lower 95% `lambda>=0.50`. Implementation failures are not mathematical falsification.

## Artifact plan

- Derivation: `ideas/artifacts/ECDLP-IDEA-049/integral_transducer.md`
- Symbolic checker: `ideas/artifacts/ECDLP-IDEA-049/check_transducer.sage`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-049/analysis.md`
- Retain equations, carry bounds, lattices, determinant calculations, witnesses, counterexamples, commands, environment, and commit.

## Interpretation boundary

This deferred hypothesis is toy, heuristic, model-bound, and novelty-unverified. Small
coordinates, lattice success, or a valid relation is not evidence of a generic
better-than-rho algorithm.

## Exactly one next executable action

1. Derive the complete two-addition integral transducer and either certify its root-height inequality symbolically or record the first generic obstruction.
