# ECDLP-IDEA-034 — Hasse-gap carry linearization

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation and preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; recovering toy carries or validating lifted addition identities is not an ECDLP break.

## Falsifiable hypothesis

For a prime-order curve `E/F_p` with `#E(F_p)=N=p+1-Delta` and
`|Delta|<=2 sqrt(p)`, canonical integer lifts of a fixed, target-independent family of
complete addition-law identities yield simultaneous congruences modulo `p` and modulo
`N`.  Their bounded discrepancy, or carry vector, determines the hidden scalar in
`Q=[x]P` using time and bit memory of exponent below `1/2` in `N`, after all lattice,
height, ambiguity, and verification costs are charged.

## Mechanism-new operation

The proposed operation is **two-modulus carry extraction**: couple coordinate identities
that vanish modulo the field modulus `p` with scalar identities that vanish modulo the
nearby group modulus `N`, then solve for the small integer discrepancies made possible by
`p-N=Delta-1`.  This is not merely a shorter global lift (idea 005).  It survives as a
separate mechanism only if the joint `p/N` carry lattice has provably smaller dimension or
height than either modulus alone; if eliminating the carries leaves the same Mordell–Weil
height problem, this record merges into idea 005 and is rejected.

## Assumptions

1. The scope is explicitly the cofactor-one, prime-order family; applicability outside it is not assumed.
2. Addition laws, integer representatives, monomial order, lattice scaling, and row selection are frozen without the hidden scalar or a scalar-indexed table.
3. Every denominator, exceptional addition branch, coefficient height, and carry bound is exact and charged.
4. The Hasse gap supplies an exploitable joint constraint rather than merely restating `N` and `p`.
5. Lattice output gives an explicitly based integer coordinate, not a relabeled group DLP.
6. All extrapolations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`prime_order_Hasse_gap | simultaneous_p_and_N_integer_lifts | bounded_addition_carry_lattice | hidden_scalar_reconstruction`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field relation baseline whose missing scalar coefficient must actually be exposed.
2. `ledger/H-REP-001.yaml` — distinguishes a new integer carry object from an ordinary coordinate rewrite.
3. `ledger/EV-REP-001.yaml` — requires every sign, denominator, and lift branch to be retained.
4. `ledger/H-FB-001.yaml` — supplies the factor-base and smoothness accounting boundary.
5. `ledger/SYNTHESIS-20260716.md` — requires complete target descent and matched rho/BSGS accounting.

## Closest primary literature

- Shparlinski and Stange, [Character sums with division polynomials](https://arxiv.org/abs/0912.5246), bounds arithmetic information in scalar-indexed division-polynomial sequences and is a nearby warning that useful signal may require long scalar ranges.
- Coppersmith, [Finding a small root of a univariate modular equation](https://doi.org/10.1007/3-540-68339-9_14), supplies the rigorous small-modular-root boundary for any claimed carry decoder.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), fixes the algebraic addition-law boundary and the need to account for a complete system rather than one exceptional formula.

No checked source gives a hidden-scalar algorithm from a simultaneous `p/N` carry
lattice.  The mechanism and any novelty claim are therefore novelty-unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is a frozen set of low-degree lifted addition identities
and their bounded carry coordinates.

- Build the target-independent identity base and certify that its complete addition-law cases cover every required step.
- Substitute public `P,Q,p,N` only after the base, lift convention, and lattice scaling are frozen.
- Derive the simultaneous congruences and exact intervals for every field and scalar carry.
- Reduce the resulting integer lattice, retaining every short vector and every exceptional branch.
- Reconstruct all scalar candidates from the based carry coordinates; do not use a scalar table in construction.
- Accept a candidate only after the original-curve check `[x]P=Q`.

## Full rho/BSGS cost model

Let reciprocal usable-instance density be `N^zeta`, identity-base construction be `N^c`,
base size and lattice dimension be `N^beta`, maximum lifted degree be `N^d`, coefficient
height be `N^h`, reciprocal usable-carry density be `N^delta`, per-row arithmetic be
`N^q`, exact lattice reduction be `N^(omega_L*beta+h)`, unresolved carry search be
`N^kappa`, candidate-list size be `N^u`, verification be `N^v`, and other bit memory be
`N^s`. Pollard rho costs `N^(1/2+o(1))` time and negligible group storage; BSGS costs
`N^(1/2+o(1))` time and `N^(1/2+o(1))` group-element memory. This proposal has time
exponent `lambda=max(zeta+c,beta+d+delta+q,omega_L*beta+h,kappa,u+v)` and bit-memory
exponent `mu=max(s,2*beta+h,kappa,u)`. Reading or emitting `N^beta` rows, enumerating
`N^kappa` carries, and storing their full coefficient bit lengths are included.

## Likely fatal obstruction

The Hasse bound constrains the two moduli but does not couple field-coordinate carries to
the unknown scalar.  Eliminating denominators can make division-polynomial degree and
height grow as the scalar circuit grows, while a fixed-degree system may be statistically
independent of `x`.  Any informative system may therefore have `beta+d+h>=1/2`, require
`N^kappa` carry enumeration, or collapse exactly to idea 005's height obstruction.

## Proof track

Prove a target-independent family of joint `p/N` identities, a sub-square-root bound on
dimension, degree, height, and carry ambiguity, and an injective based map from its short
carry vectors to `x mod N`.  Combine those bounds to establish `lambda,mu<1/2`.

## Disproof track

Prove that fixed-degree lifted identities have identical carry distributions across
scalars, that informative identities require square-root degree/height/dimension, or that
the joint lattice is algebraically equivalent to the occupied global-height channel.

## Positive and negative controls

- Positive control: an additive group modulo two nearby public moduli with a planted bounded carry.
- Positive instrumentation control: tiny prime-order elliptic curves with exhaustive hidden-scalar truth revealed only after the lattice is frozen.
- Negative control: random pairs of nearby moduli with matched gap and randomized coordinate encodings.
- Duplicate control: run the same lifted identities modulo `p` alone and classify any unchanged signal as idea 005.
- Leakage control: hash the identity base and lattice scaling before revealing scalar labels.

## Quantitative promotion and falsification gates

The toy gate uses deterministic prime-order curves at 8–20 bits, stratified by normalized
Hasse gap, and reports every exceptional branch. Promotion only to a scaling contract
requires zero wrong labels, blinded mutual information surviving randomized-encoding and
`p`-only controls, lower 95% information at least `0.25` bit per charged identity, and
upper 95% `beta+d<=0.25`, `h<=0.25`, `kappa<=0.20`, `lambda<=0.45`, and `mu<=0.45`.
Falsify if signal vanishes after blinding, any accepted label is wrong, the joint lattice
equals the `p`-only lattice, or any required exponent has lower 95% bound at least `0.50`.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-034/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-034/hasse_carry_lattice.sage`
- `ideas/artifacts/ECDLP-IDEA-034/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-034/runs/<run_id>/identities.jsonl`
- `ideas/artifacts/ECDLP-IDEA-034/runs/<run_id>/carry_vectors.jsonl`
- `ideas/artifacts/ECDLP-IDEA-034/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-034/analysis.md`

## Interpretation boundary

Every scaling statement is toy, heuristic, model-bound, and novelty-unverified. Exact
addition identities, short vectors, or correct toy labels are not a breakthrough; only a
complete original-target recovery below matched rho/BSGS accounting could support one.

## Exactly one next executable action

1. On the lexicographically first prime-order curve for each field bit size from 8 through 20, freeze the Bosma–Lenstra addition-law lifts before labels, exhaustively measure the minimum joint-`p/N` carry-lattice dimension and height needed to separate all scalars, and compare it with the `p`-only control.
