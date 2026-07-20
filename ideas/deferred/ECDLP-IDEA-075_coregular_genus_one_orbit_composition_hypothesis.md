# ECDLP-IDEA-075 — Coregular genus-one orbit composition

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `deferred_theorem_required`
- Evidence scale: `toy` invariant-theory identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; composing or reducing invariant-theory orbits is not an ECDLP break.

## Falsifiable hypothesis

There is a bounded-dimensional coregular representation whose rational orbits encode a marked genus-one curve and point, with an explicit orbit composition corresponding to elliptic addition. On a positive-density target-independent orbit factor base, a new smooth-orbit factorization plus canonical inverse returns the original point sources, enabling relation collection and blind target descent with all time and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **composition and factorization of coregular genus-one orbits with an exact point-source inverse**. Curve invariants, Selmer labels, minimization, or orbit reduction alone are controls. The mechanism must make additive point decomposition easier in orbit space and map every factor back to an actual factor-base point.

## Assumptions

1. Soluble public orbits for `(E,R)` can be constructed and normalized without the scalar of `R`.
2. Orbit composition is explicit, associative on the tested domain, and compatible with elliptic addition.
3. A smoothness notion factors a random target orbit over `B=N^beta` public orbit atoms with improved density.
4. Canonical inverse covariants recover every point, sign, and exceptional orbit branch.
5. Stabilizers, field extensions, minimization, coefficient growth, failed factorizations, rank, and descent are charged.
6. The orbit basis never embeds a scalar-labelled dictionary.

## Semantic fingerprint

`coregular_genus_one_orbit | explicit_orbit_composition | orbit_smoothness_atoms | invariant_covariant_source_inverse | relation_rank_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H396`, the nearest nonlinear representation-composition hypothesis.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H397`, which asks whether richer quotient/module invariants add usable constraints.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H465`, the closest request for a true quotient identity rather than another solver.
4. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-NR-009`, where a representation split leaves orientation unresolved.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-006`, where fixed-degree complementary objects give only constant multiplicity.

## Closest primary literature

- Bhargava and Ho, [Coregular spaces and genus one curves](https://intlpress.com/site/pub/files/_fulltext/journals/cjm/2016/0004/0001/CJM-2016-0004-0001-a001.pdf), parametrizes genus-one data by orbits but does not give the claimed smooth factorization.
- Fisher, [Invariant theory for the elliptic normal quintic II: the covering map](https://arxiv.org/abs/1303.2550), constructs covariants and covering maps, not a sub-rho source decomposition.
- Fisher, [The invariants of a genus one curve](https://arxiv.org/abs/math/0610318), computes Jacobian invariants but supplies no ECDLP orientation.

## Complete factor-base-to-target-descent path

1. Freeze the representation, group action, invariant/covariant formulas, normalization, and map between point and soluble orbit.
2. Encode every factor-base point as a source-labelled normalized orbit and prove addition/composition on exhaustive tiny curves.
3. Define orbit primes/atoms and factor randomized relation targets, returning every constituent orbit with stabilizer data.
4. Invert covariants to exact factor-base points and verify each elliptic relation.
5. Collect `B+sigma` independent rows, solve and verify factor logs.
6. Factor masked blind target orbits, combine calibrated logs, unmask, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho and BSGS have exponent `1/2`; BSGS also uses memory exponent `1/2`. Let orbit setup/normalization exponent be `s`, factor-base exponent `beta`, inverse relation/target densities `delta,delta_t`, per-factorization exponent `k`, inverse-covariant/output exponent `u`, linear algebra `ell>=2beta` absent proved structure, coefficient-height exponent `h`, and memory `mu`. Then `lambda=max(s,h,beta+delta+k+u,ell,delta_t+k+u,beta)`. Stabilizer enumeration or an orbit table of size `N^r` contributes exponent `r` without amortization.

## Likely fatal obstruction

Coregular invariants deliberately quotient the group action and can forget the point orientation needed for a ledger row. Orbit minimization/factorization may be an arithmetic reduction problem unrelated to group addition, while making it canonical can require solving the original torsor/Selmer class or enumerating a stabilizer of size `N`. Fixed-dimensional invariant theory can therefore change notation without changing relation density.

## Proof track

Give the point-orbit functor, explicit composition, atom factorization, and inverse-covariant theorem; prove positive-density source recovery and bound height, stabilizers, rank, descent, output, and memory below rho.

## Disproof track

Find two point sources with the same normalized orbit data, show composition cannot be evaluated without choosing a DLP orientation, or establish factorization/density/height exponent at least `1/2`.

## Positive and negative controls

- Published invariant/covariant identities on soluble genus-one models.
- Planted orbit products with known point sources.
- Nonsoluble/twisted orbits with identical coarse invariants.
- Random coordinate encodings matched for dimension and coefficient size.
- Blind point sources and stabilizer-complete output.
- Measured rho/BSGS and direct elliptic decomposition baselines.

## Quantitative promotion and falsification gates

The theorem gate requires a biconditional orbit-composition law, canonical source inverse, and nontrivial smoothness prediction. Experimental promotion would require zero orbit/source errors, at least 1,000 independent relations and 100 blind descents at each of two largest sizes, and upper 95% `lambda,mu<=0.45`. Falsify the scoped mechanism if any legal orbit has unresolved source multiplicity `>=N^(1/2)`, relation yield matches the direct control within confidence, or lower 95% complete exponent is at least `0.50`.

## Artifact plan

- Theorem: `ideas/artifacts/ECDLP-IDEA-075/orbit_composition.md`
- Models: `ideas/artifacts/ECDLP-IDEA-075/coregular_models.sage`
- Source inverse: `ideas/artifacts/ECDLP-IDEA-075/invert_covariants.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-075/verify_orbits.py`
- Runs: `ideas/artifacts/ECDLP-IDEA-075/runs/<run-id>/`

## Interpretation boundary

This deferred representation change is toy, heuristic, model-bound, and novelty-unverified. Correct invariants, orbit composition, or a soluble covering does not establish a faster discrete logarithm.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-075/orbit_composition.md` with one explicit bounded-dimensional point-orbit composition and a complete source-inverse proof on exhaustive tiny fields.
