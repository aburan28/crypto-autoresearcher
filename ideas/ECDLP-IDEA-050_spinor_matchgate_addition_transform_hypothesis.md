# ECDLP-IDEA-050 — Spinor-matchgate addition transform

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` identity preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Pfaffian identity or valid relation is not an ECDLP break.

## Falsifiable hypothesis

For a frozen arity `m` and factor base `F` of size `B=N^beta`, there is a public,
target-independent linear basis change on exact elliptic-addition signatures that maps
the balanced factor-base-to-target relation tensor to a spinor/matchgate signature.
The transformed signature has a planar Pfaffian realization of width `N^(w+o(1))`,
and exact self-reduction returns the source points, with complete time and memory
exponents below `1/2` for some fixed parameters.

## Mechanism-new operation

The new operation is an **exact spinor basis transform of the elliptic addition tensor**:
an explicit matrix sends each local rational-addition signature to the matchgate variety,
certified by Grassmann-Pluecker identities, so global contraction and source recovery use
Pfaffian minors. This changes the representation before solving. Merely calling a
Pfaffian solver, planarizing a dense graph, changing a Semaev parameter, or certifying a
relation does not qualify.

## Assumptions

1. `E(F_p)` has a known prime subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. The factor base is deterministic, target-independent, and has `B=N^beta` points.
3. Addition signatures include denominators, signs, repeated points, and exceptional fibers exactly.
4. The same public basis transform works for relations and target descent without scalar advice.
5. Pfaffian contraction returns actual factor-base witnesses by an exact self-reduction.
6. Scaling extrapolations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_addition_signature | public_spinor_basis_change | matchgate_identities | Pfaffian_contraction | exact_source_self_reduction`

The fingerprint excludes a generic tensor solver, a post-hoc planar subinstance, and the
already-tested exact ordinary-rank flattenings.

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — blocks coordinate rewrites that leave the solve cost unchanged.
2. `ledger/EV-REP-001.yaml` — supplies the matched representation-control evidence.
3. `ledger/FINDING-PF-IC-001.md` — records the measured prime-field membership bottleneck.
4. `ledger/H-FB-001.yaml` — prevents a factor-base shape change from carrying the claim.
5. `ledger/SYNTHESIS-20260716.md` — requires source recovery and end-to-end accounting.

## Closest primary literature

- Valiant, [Holographic Algorithms](https://doi.org/10.1137/070682575), establishes basis-transformed matchgate computation.
- Cai, Lu, and Xia, [Holographic algorithms by Fibonacci gates](https://arxiv.org/abs/1008.0683), develops matchgate realizability identities and tractable contractions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the nearby elliptic decomposition relation.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies exact addition-law coverage requirements.

None proves that generic prime-field elliptic signatures lie in one useful matchgate
orbit; that novelty and feasibility claim is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,m,beta` and a deterministic factor base `F`.
2. Compile exact local addition and factor-base membership signatures, including every exceptional chart.
3. Apply one public target-independent basis transform and verify all matchgate identities symbolically.
4. Contract the planar signature network to collect relations `[a]P=sum_i P_i` for known `a`.
5. Self-reduce Pfaffian minors to recover every `P_i in F` and independently verify the curve sum.
6. Collect `B+margin` independent rows and solve for factor-base logarithms.
7. Apply the identical transform to `Q+[t]P` until a verified decomposition is recovered.
8. Substitute factor-base logs, remove `t`, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let transform build and storage exponents be `a` and
`s`, Pfaffian width `W=N^w`, one contraction/self-reduction cost
`N^(q+o(1))` with the conservative dense bound `q=3w`, relation and target reciprocal
densities `N^delta` and `N^delta_t`, and sparse linear algebra `N^(2beta+o(1))`.
Then
`T_rel=N^(beta+delta+q+o(1))`,
`T_desc=N^(delta_t+q+o(1))`,
`lambda=max(a,beta+delta+q,2beta,delta_t+q)`, and
`mu=max(s,beta,2w)`. Promotion requires both `lambda<1/2` and `mu<1/2`; a low
ordinary tensor rank or a single fast contraction is insufficient.

## Likely fatal obstruction

Generic elliptic addition signatures may violate the matchgate identities in every
public basis, while planarization can require `W=N^(1/2-o(1))` or larger. Even if the
partition function is cheap, recovering sources may need quadratically many conditioned
Pfaffians. Any of these restores rho-scale time or memory.

## Proof track

Exhibit the basis matrix and planar realization; prove the Grassmann-Pluecker identities
over the working field, chart completeness, target independence, witness self-reduction,
and the stated build, density, solve, descent, and memory bounds.

## Disproof track

Derive a violated matchgate invariant on a generic symbolic curve, prove a
`N^(1/2-o(1))` width or self-reduction lower bound, or show every complete-cost parameter
choice has `lambda>=1/2` or `mu>=1/2`.

## Positive and negative controls

- Positive control: a known planar matchgate network transported through a random invertible basis.
- Positive correctness control: exhaustive decompositions on tiny curves.
- Negative control: matched random four-ary signatures with the same sparsity.
- Mechanism control: the untransformed Semaev/membership implementation on identical inputs.
- Leakage control: forbid target-selected bases, scalar coordinates, explicit tuple tables, and discarded misses.

## Quantitative promotion and falsification gates

On at least 20 ordinary curves per size from 11 through 22 bits, promotion requires
symbolic identity agreement in every chart, zero false witnesses, at least 1,000 verified
relations and 100 target descents at each of the two largest sizes, upper 95% bounds
`a<=0.45`, `q<=0.20`, `lambda<=0.45`, and `mu<=0.45`, plus a stable fit after
leaving out the largest size. Falsify the scoped mechanism on a generic symbolic
matchgate-invariant violation, any independently reproduced false witness, lower 95%
`q>=0.50`, or lower 95% `lambda>=0.50` for every frozen parameter arm. Crashes and
unsupported charts are implementation evidence only.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-050_matchgate_identity_preflight.yaml`
- Symbolic identities: `ideas/artifacts/ECDLP-IDEA-050/spinor_identities.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-050/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-050/analysis.md`
- Retain exact curves, bases, identities, witnesses, misses, operation counts, memory, seeds, environment, commit, stdout, and stderr.

## Interpretation boundary

All implications are toy, heuristic, model-bound, and novelty-unverified. A correct basis
change, Pfaffian value, or relation establishes neither source recovery nor a
better-than-rho ECDLP algorithm.

## Exactly one next executable action

1. After coordinator approval, run the frozen symbolic matchgate-identity preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-050_matchgate_identity_preflight.yaml`.
