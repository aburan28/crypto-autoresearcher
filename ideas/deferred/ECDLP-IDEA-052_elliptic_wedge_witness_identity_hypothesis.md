# ECDLP-IDEA-052 — Elliptic wedge-witness identity

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `deferred_missing_identity`
- Evidence scale: `toy` symbolic derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a vanishing wedge or relation certificate is not a break.

## Falsifiable hypothesis

Complete elliptic addition admits a curve-specific exterior-algebra identity whose
antisymmetrized evaluation annihilates all nondecompositions while encoding the source
indices of every factor-base decomposition in `N^(r+o(1))` exterior coordinates with
`r<1/2`. Exact coefficient extraction then recovers witnesses without materializing the
`B^2` pair surface.

## Mechanism-new operation

The proposed operation is an **elliptic addition-law wedge identity with source
coefficients**. It must be derived from the curve law, not generic color coding, and must
return indices rather than a determinant/nonzero certificate. Generic exterior
algebra, solver substitution, Pluecker restatement, or relation-only certificates are controls.

## Assumptions

1. `E(F_p)` has prime subgroup `<P>` of order `N=p^(1+o(1))` with `Q=[x]P`.
2. `F` is deterministic and target-independent with `B=N^beta`.
3. The identity covers all addition charts and repeated/exceptional points.
4. Exterior dimension, coefficient height, and source decoding are fully charged.
5. Random colors are used only as a controlled implementation aid, never a success selector.
6. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_addition_syzygy | antisymmetric_wedge_filter | nonwitness_annihilation | source_index_coefficients | subquadratic_pair_state`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — blocks algebraic reformulations with unchanged complexity.
2. `ledger/EV-REP-002.yaml` — supplies rank/scaling controls.
3. `ledger/FINDING-PF-IC-001.md` — fixes the membership cost to remove.
4. `ledger/H-FB-001.yaml` — prevents factor-base structure from carrying the claim.
5. `ledger/SYNTHESIS-20260716.md` — requires source recovery and target descent.

## Closest primary literature

- Koutis, [Faster algebraic algorithms for path and packing problems](https://doi.org/10.1007/978-3-540-70575-8_47), introduces exterior/group-algebra sieving for witness structures.
- Williams, [Finding paths of length k in O*(2^k) time](https://arxiv.org/abs/0807.3026), gives the nearby algebraic cancellation technique.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the elliptic relation predicate.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies chart completeness.

These do not give the required curve-specific source-resolving wedge identity.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,m,beta,F` and complete addition-law evaluation vectors.
2. Derive and verify the antisymmetric identity without enumerating factor-base pairs.
3. Evaluate it for known `R=[a]P` and extract source-index coefficients.
4. Verify recovered points lie in `F` and sum to `R`; retain all misses and collisions.
5. Collect relations, solve factor-base logarithms, and charge exterior storage.
6. Apply unchanged to `Q+[t]P`, remove `t`, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let exterior state exponent `r`, build/storage
`a,s`, coefficient extraction `e`, reciprocal densities `delta,delta_t`, and
`B=N^beta`. Then query exponent `q=max(r,e)`,
`lambda=max(a,beta+delta+q,2beta,delta_t+q)`, and
`mu=max(s,beta,r)`. Every color repetition, coefficient, and witness branch is charged.

## Likely fatal obstruction

The wedge space may require dimension `Omega(B^2)` or annihilate valid repeated-source
relations. A nonzero determinant can certify existence while coefficient extraction
still enumerates all pairs; then the recorded membership obstruction remains.

## Proof track

Give the exact elliptic identity, prove nonwitness cancellation, completeness, source
decoding, dimension and height bounds, and full `lambda,mu<1/2`.

## Disproof track

Show the identity is only a generic Pluecker certificate, requires `B^2` state, loses
valid witnesses, or yields `lambda>=1/2` after extraction and density.

## Positive and negative controls

- Positive control: a planted set-packing tensor with known exterior witness recovery.
- Positive correctness control: exhaustive tiny-curve decompositions.
- Negative control: matched random evaluation vectors.
- Mechanism control: generic color coding and explicit pair enumeration.
- Leakage control: forbid post-hoc colors, target-specific bases, scalar advice, and count-only outputs.

## Quantitative promotion and falsification gates

Deferral lifts only after a symbolic generic identity returns source coefficients and a
proved state bound `r<1/2`. A later study requires zero false/missed exhaustive
witnesses, 20 curves per size, at least 1,000 relations and 100 descents at largest sizes,
and upper 95% `lambda,mu<=0.45`. Reject if a generic counterexample exists, exterior
state is `Omega(B^2)`, or lower 95% `lambda>=0.50`.

## Artifact plan

- Derivation: `ideas/artifacts/ECDLP-IDEA-052/wedge_identity.md`
- Checker: `ideas/artifacts/ECDLP-IDEA-052/check_wedge_identity.sage`
- Analysis: `ideas/artifacts/ECDLP-IDEA-052/analysis.md`
- Retain symbolic identities, dimensions, coefficients, witnesses, counterexamples, commands, environment, and commit.

## Interpretation boundary

The deferred claim is toy, heuristic, model-bound, and novelty-unverified. Wedge
cancellation, a nonzero coefficient, or a valid relation cannot establish an ECDLP speedup.

## Exactly one next executable action

1. Derive the complete two-addition wedge identity and test it symbolically against exhaustive source-labelled relations and nonrelations.
