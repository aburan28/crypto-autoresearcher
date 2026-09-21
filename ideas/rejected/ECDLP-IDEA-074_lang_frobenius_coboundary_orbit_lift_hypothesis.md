# ECDLP-IDEA-074 — Lang–Frobenius coboundary orbit lift

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_orbit_degree_no_go`
- Evidence scale: `toy` orbit identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Lang preimage or Frobenius identity is not an ECDLP break.

## Falsifiable hypothesis

Choose a Lang preimage `S` with `Frob_p(S)-S=P`. Then a source-resolving compressed representation of the Frobenius orbit satisfies `Frob_p^x(S)-S=[x]P` (with the exact geometric-series correction when required), and a low-degree orbit factor base plus public refinement recovers `x` with extension degree, setup, output, and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **lifting scalar multiplication to indexed Frobenius coboundaries and compressing the resulting orbit with exact source lift**. Lang surjectivity or a computed preimage alone is a correctness control. The mechanism must avoid an extension/orbit of length `N`, provide factor-base-to-target descent, and not relabel the scalar as a Frobenius index.

## Assumptions

1. A public Lang preimage and its field of definition are constructible without knowing target scalars.
2. The coboundary identity is exact for the chosen `S,P` and normalization.
3. The relevant orbit admits a sub-sqrt compressed action and inverse index refinement.
4. Orbit-factor atoms map back to exact elliptic factor-base points.
5. Extension arithmetic, Frobenius powering, orbit ambiguity, relation rank, target descent, and memory are charged.
6. No table indexed by all scalar/Frobenius powers is allowed.

## Semantic fingerprint

`Lang_Frobenius_minus_identity_preimage | scalar_to_Frobenius_orbit_index | compressed_coboundary_action | orbit_atom_to_point_source_lift | blind_scalar_refinement`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H003`, the closest Frobenius/trace-fiber representation boundary.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-005`, where trace-kernel multiplicity gives no useful rank gain.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where Frobenius/state polynomials become dense.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, the closest compact transition primitive.
5. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-NR-009`, where an auxiliary orbit representation retains orientation.

## Closest primary literature

- Lang, [Algebraic groups over finite fields](https://doi.org/10.2307/2372673), proves the surjectivity theorem underlying the coboundary but no ECDLP compression.
- Narayanan, [Fast computation of isomorphisms between finite fields using elliptic curves](https://arxiv.org/abs/1604.03072), formulates elliptic Lang-preimage computation as the key bottleneck rather than providing generic scalar-orbit decoding.
- Gaudry, Hess, and Smart, [Constructive and destructive facets of Weil descent](https://doi.org/10.1007/s00145-001-0011-x), supplies the extension-field descent boundary.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, the Lang equation, preimage selection, extension representation, and point factor base.
2. Construct `S`, prove the exact iterated coboundary formula, and enumerate all correction terms on tiny fields.
3. Build compressed orbit atoms and a source lift to factor-base points; compare against the full orbit.
4. Generate and verify randomized source-labelled relations in the original subgroup and solve factor logs.
5. Lift `Q+[t]P` to its orbit/coboundary representation, refine its compressed index, map any decomposition back to calibrated points, and recover `x+t`.
6. Unmask and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS time exponents are `1/2`; BSGS memory exponent is `1/2`. Let extension-degree exponent be `d`, preimage/setup `s`, compressed orbit size `c`, factor-base exponent `beta`, relation/target density exponents `delta,delta_t`, orbit evaluation/lift `k`, residual index list `r`, linear algebra `ell`, and memory `mu`. Then `lambda=max(d,s,c,beta+delta+k,ell,delta_t+k,r)`. A generic degree-`N` orbit or index table sets `d,c`, or `mu` to `1`.

## Likely fatal obstruction

Iterating `F(S)-S=P` gives `F^d(S)-S=[d]P`. If `S` has Frobenius period `d`, then `[d]P=0`; for prime-order `P`, `N` divides `d`. Thus every faithful Lang preimage orbit and field of definition has degree at least `N`. Frobenius-invariant compression forgets the index, while faithful orbit indexing is the original DLP with `N` states or an order-`N` minimal polynomial.

## Proof track

Construct a family with bounded preimage degree and faithful compressed orbit action; prove source lift and scalar refinement and bound every relation/descent cost below rho.

## Disproof track

Prove generic orbit degree/state complexity at least `N^(1/2)`, show compression loses scalar index, or reduce index refinement to generic DLP.

## Positive and negative controls

- Exhaustive Lang preimages and Frobenius orbits on tiny curves.
- Planted short Frobenius orbits.
- Random extension points matched for degree.
- Trace/norm and torsor-orbit controls.
- Full-orbit enumeration as a forbidden-cost reference.
- Blind masked targets and complete candidate lists.

## Quantitative promotion and falsification gates

The theorem gate requires exact coboundary identity, sub-sqrt orbit degree/state, and source-resolving inverse. A future promotion gate requires 100 blind descents per largest size and upper 95% `d,c,r,lambda,mu<=0.45`. Falsify if generic tested families have lower 95% orbit/state exponent at least `0.50` or any faithful decoder is equivalent to orbit-index DLP.

## Artifact plan

- Identity: `ideas/artifacts/ECDLP-IDEA-074/lang_coboundary.md`
- Orbit schema: `ideas/artifacts/ECDLP-IDEA-074/frobenius_orbit.yaml`
- Prototype: `ideas/artifacts/ECDLP-IDEA-074/lang_orbit.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-074/verify_coboundary.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-074/analysis.md`

## Interpretation boundary

This deferred representation is toy, heuristic, model-bound, and novelty-unverified. Lang surjectivity, a correct preimage, or a short exceptional orbit is not a generic ECDLP improvement.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-074/lang_orbit_degree_no_go.md` proving `F^d(S)-S=[d]P` and the consequent `N|d` lower bound for every faithful prime-order Lang orbit.
