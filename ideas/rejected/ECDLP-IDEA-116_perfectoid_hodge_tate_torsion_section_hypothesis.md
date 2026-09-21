# ECDLP-IDEA-116 — Perfectoid Hodge–Tate torsion section

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_prime_to_p_perfectoid_no_go`
- Top lane: `-`
- Evidence scale: semantic/theorem screen only; no run; any future period computation would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a perfectoid lift, Hodge–Tate period, torsion section, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Lift an ordinary `E/F_p` to a good-reduction elliptic curve over a perfectoid field and pass to its infinite `p`-power-level perfectoid cover. The hypothesis proposes a target-independent nonlogarithmic Hodge–Tate period section whose evaluation on prime-to-`p` subgroup points is additive, nonzero, and source-injective. Such a section would turn factor-base relations and a masked target into exact scalar equations with complete time and memory below rho and BSGS.

## Mechanism-new operation

For the claimed factor-base pipeline, the operation includes a public scalar-blind
inverse from each accepted period word to every exact signed factor-base tuple. A
source-injective period value without that atom-to-point inverse is only a coordinate
diagnostic and does not supply the stated relation/descent path.

The proposed operation is **use a perfectoid infinite-level section and Hodge–Tate period map, rather than a formal logarithm, to orient prime-to-`p` torsion sources**. The scoped formulation is rejected: the chosen perfectoid tower and Hodge–Tate/Tate-module data resolve `p`-power directions. The cryptographic subgroup has order `N` prime to `p`; an additive map from this finite group into a torsion-free `p`-adic period target kills it. Adding full `N`-level structure moves the orientation into an `N`-state torsion cover and restores the DLP/dictionary cost.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N!=p`, with target-independent `F` of size `B=N^beta` and fixed relation arity `m`.
2. A canonical good-reduction lift and perfectoid `p`-power-level cover are constructible without a hidden scalar, factor logs, or target-specific choices.
3. A public Hodge–Tate or period section evaluates on all lifted prime-to-`p` subgroup points and is additive modulo a target retaining order `N`.
4. The section is source-injective and has a complete inverse to signed factor-base indices without an `N`-level table.
5. Relation and blind-target evaluations use identical lifts, untilts, period normalizations, and ambiguity rules.
6. Field extensions, infinite-level truncation, period precision, section construction, output, rank, factor logs, descent, verification, and peak memory are charged.

## Semantic fingerprint

`good_reduction_perfectoid_lift | infinite_p_power_level_cover | Hodge_Tate_period_section | prime_to_p_source_orientation | public_period_word_source_inverse | blind_descent`

The removal test is a nonzero additive source-injective prime-to-`p` section with a public exact period-word/source inverse derived from compact perfectoid data. A formal/jet logarithm, anomalous `N=p` attack, explicit `N`-level torsion basis, torsion-field table, chosen scalar-labelled lift, or period value without source inversion is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ISO-SP-001`, the closest verified pairing-based torsion-action lane, which still requires an oriented torsion structure.
2. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-003`, where exhaustive division lifts provide a verifier but not a scalable scalar coordinate.
3. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-004`, where one projected lift and pairing certify orientation only within the theorem-covered toy ascent.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H651`, the bounded curve-automorphism quotient lane whose constant symmetry does not expose the scalar.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H653`, the automorphism-weighted log-variable lane that retains hidden orientation.

## Closest primary literature

- Scholze, [Perfectoid spaces](https://arxiv.org/abs/1111.4914), constructs the perfectoid framework; it does not provide a prime-to-`p` elliptic discrete-log coordinate.
- Scholze and Weinstein, [Moduli of p-divisible groups](https://arxiv.org/abs/1211.6357), describes infinite-level `p`-divisible structures and period maps; its natural tower is `p`-primary.
- Bhatt, Morrow, and Scholze, [Integral p-adic Hodge theory](https://arxiv.org/abs/1602.03148), relates integral `p`-adic cohomologies but supplies no source-injective map on an arbitrary prime-to-`p` subgroup.
- Iovita, Morrow, and Zaharescu, [On p-adic uniformization of abelian varieties with good reduction](https://arxiv.org/abs/2107.09165), extend Fontaine integration to a perfectoid-like universal cover built from `p`-adic Tate-module data; they do not orient arbitrary prime-to-`p` sources.
- Bellovin, Cai, and Howe, with an appendix by He, [Characterizing perfectoid covers of abelian varieties](https://arxiv.org/abs/2501.03974), characterize perfectoid profinite étale covers using the Hodge–Tate filtration; they do not supply the proposed ECDLP source inverse.

No checked primary source gives the claimed nonlogarithmic prime-to-`p` source section. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, lift, untilt, perfectoid tower, finite truncation, period map, section normalization, precision, inverse, and exceptional-reduction policy.
2. Construct and independently verify the compact tower/section without factor logs or scalar-labelled torsion points.
3. For a public output `R`, evaluate the section, invert every returned atom to exact signed members of `F`, and independently verify the elliptic sum.
4. Apply the frozen operation to known `R_j=[r_j]P`; retain verified rows until exactly `B+sigma` have rank `B`.
5. Solve and independently verify all factor-base logarithms.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and use the identical lift, period section, inverse, and verification.
7. Substitute factor logs, subtract `t`, retain every precision/torsion ambiguity candidate, and accept only `[x]P=Q`.
8. Preserve lift failures, period-zero outputs, torsion collisions, extension/precision growth, duplicate rows, and rejected candidates.

## Full rho/BSGS cost model

Pollard rho has time `N^(1/2+o(1))` and constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; lift/tower/period plus factor-base construction time and memory be `N^a,N^a_m`; serialized level/precision and working state be `N^v,N^v_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; complete per-evaluation/source-inverse plus exact elliptic verification work be `N^k`; source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,v,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(a_m,v_m,beta+o,ell_m,u)`.

All tower levels, torsion coordinates, untilts, periods, precision limbs, failed evaluations, `B+sigma` rows, sources, and candidates are charged. Any explicit `N`-level structure enters `a`, `v`, or memory at its full size.

## Likely fatal obstruction

The perfectoid tower is built from `p`-power division and its Hodge–Tate period records a `p`-adic Tate-module line. The ECDLP subgroup has prime order `N` distinct from `p`. A homomorphism from that finite group into a torsion-free additive period space is zero. Retaining `N`-torsion instead requires a target with `N`-torsion and an orientation; constructing or indexing that level structure is the original DLP in another representation.

## Proof track

Construct a nonzero additive perfectoid-derived section on the prime-to-`p` subgroup, prove exact source inversion without `N`-level advice, and prove all complete exponents at most `0.45`.

## Disproof track

Prove the section factors through `p`-primary Tate data and kills `E[N]`, exhibit two distinct `N`-torsion points with identical period data, or show that any faithful refinement materializes `N`-level structure with exponent at least `1/2`. A scalar-labelled lift also disproves the mechanism.

## Positive and negative controls

- Published perfectoid towers for `p`-divisible groups with independently checkable period maps.
- Anomalous toy curves with `N=p` as a positive boundary, never mixed with ordinary `N!=p` curves.
- Ordinary prime-to-`p` torsion points expected to collide under `p`-primary period data.
- Explicit `N`-level torsion tables charged at full size.
- Formal-logarithm and torsion-pairing controls.
- Blind masked targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains. A versioned successor must prove a nonzero additive prime-to-`p` section, exact source inverse, and `a,a_m,v,v_m,k,o,u,lambda,mu<=0.45` without `N`-level advice. Any later toy preflight would require zero independent section/source/sum/factor-log/descent errors on 20 curves at four sizes, 1,000 rows and 100 blind descents at each of the two largest sizes. Falsify after one proved torsion-killing factorization, one source collision, or a lower 95% bound `>=0.50` for level state, complete time, or memory.

## Artifact plan

- Prime-to-p period no-go proof: `ideas/artifacts/ECDLP-IDEA-116/perfectoid_torsion_no_go.md`
- Frozen tower/period specification: `ideas/artifacts/ECDLP-IDEA-116/perfectoid_section_spec.yaml`
- Prospective toy period code: `ideas/artifacts/ECDLP-IDEA-116/perfectoid_section.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-116/verify_period_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-116/analysis.md`

## Interpretation boundary

This rejected high-risk record is toy, heuristic, model-bound, and novelty-unverified. The torsion-killing argument is scoped to the stated `p`-power perfectoid/Hodge–Tate section, not a generic ECDLP lower bound. A correct period map, tower, relation, or toy scalar is not a below-rho algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-116/perfectoid_torsion_no_go.md` proving whether every additive coordinate obtained from the stated `p`-power-level Hodge–Tate period data vanishes on the prime-to-`p` subgroup or requires explicit `N`-level orientation.
