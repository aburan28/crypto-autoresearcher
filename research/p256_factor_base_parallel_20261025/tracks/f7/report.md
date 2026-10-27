# F7 — explicit same-field covers of P-256 (2026-10-25)

This report records exact construction and implementation checks under TASK-20261025-7144c5. It supplies a smooth nonhyperelliptic genus-three plane quartic and a contrasting hyperelliptic genus-two curve, both over the actual P-256 field, with subgroup-compatible pullback/norm correspondences. It does not report a DLP trial, a faster solver, or a scientific state transition. `checks.json` and `elliptic-quotient-checks.json` retain the arithmetic outputs; producer checks await independent review.

## Source and fields

Use E: y²=x³−3x+b over Fp with the published p, b, prime r and generator in `source-identity.json` and executable sources. The exact source UID is `urn:ec-record:1:sha256:c59ede3f79defa1603280e26ca59b3057d13626874aac2e3d044763c9f17051c`, alias `EC1P256Cp256hc59ede3f79de`. F5's prime and Hasse certificates establish #E(Fp)=r and t=89188191154553853111372247798585809583. These are public parameters and deterministic synthetic multiples, with no private target.

Both cover maps and induced rational divisor-class maps are defined over **Fp**, without replacing it by a smaller field. The quadratic extension Fp[i]/(i²+1) is used only to display nonsplit fibre supports. Since p≡3 mod4, i^p=−i. Frobenius-stable pairs encode Fp-rational divisor classes even when their support points are individually nonrational.

## A nonhyperelliptic genus-three cover

Let C be the projective plane quartic

U⁴=X³Z−3XZ³+bZ⁴.

On Z=1, write x=X/Z and u=U/Z; then u⁴=x³−3x+b. Define π:C→E by (x,u)↦(x,u²). The unique point at infinity [1:0:0] maps to O. This is a separable degree-two cover over Fp, with deck involution u↦−u.

**Derived and exactly checked smoothness.** Affine singularities require u=0 and f(x)=f′(x)=0, excluded by the computed gcd(f,f′)=1. At infinity ∂H/∂Z=−1 at [1:0:0]. Thus C is a smooth plane quartic. Its genus is (4−1)(4−2)/2=3. Its plane embedding is canonical, so it is nonhyperelliptic; this assertion follows from smoothness, rather than from a name assigned to the equation.

The function defining the cover is u²=y on E. Its three simple zeros are the nonidentity geometric 2-torsion points; its pole at O has order three. All four odd valuations ramify. Their Frobenius orbit lengths are **3 and 1**, because the P-256 cubic is irreducible and O is rational. Riemann–Hurwitz gives 2g(C)−2=4. These branch orbits do not require rational order-two points on E.

For every P=(xP,yP)∈E(Fp) other than O, its pullback fibre has ideal

I_P=(x−xP, u²−yP).

Hence the subgroup map is the divisor class

ι(P)=π*([P−O])=[V(I_P)−2∞] ∈ J_C(Fp).

This is a map to a Jacobian, not a pointwise group embedding into the curve C. The two roots of u²=yP may lie in Fp², but the ideal coefficients are in Fp. The implementation verifies both roots lie on C, map to P and form a Frobenius-stable multiset, on scalars 1,2,3,17,257,65537,r−1. Three fibres split over Fp and four do not; all seven norms recover P as described below. This fixed constructed list is a correctness fixture, not a sampling study.

## Subgroup preservation and Frobenius constraints

For a finite separable degree-two cover, pullback and pushforward satisfy the universal divisor-class identity

π_* π*=[2] on J_E=E.

A local finite fibre pushes to 2P, including multiplicities; the ramified infinity fibre pushes to 2O. Extending these operations to divisors and principal divisors proves the identity on Pic⁰. Since r is prime and odd, multiplication by 2 is invertible on the target subgroup. Thus ι is injective there, and [2⁻¹ mod r]π_* is a recovery map. If Q=[n]G, a solver returning n from ι(Q)=[n]ι(G) gives the identical n modulo r, verified by [n]G=Q. No source scalar is used to construct I_P.

The exact Frobenius polynomial of E divides that of J_C over Fp. More can be derived without pretending to have a complete point count of J_C:

P_JC(T)=(T²−tT+p)(T⁴+A T²+p²), with A an unknown integer, |A|≤2p.

The automorphism σ:u↦i u over Fp² has square equal to the deck involution. On the two-dimensional Prym factor, σ²=−1. Frobenius conjugates σ to σ⁻¹=−σ on that factor, so its odd Frobenius coefficients vanish. Reciprocity gives the displayed constant coefficient p²; Weil bounds give |A|≤2p. These are derived constraints, not a computed value of A or a supersingularity assertion.

There is also a complete first-extension point-count identity: since gcd(4,p−1)=2, the numbers of fourth roots and square roots of each c∈Fp are equal. Summing over x and adding the unique infinity point gives **#C(Fp)=#E(Fp)=r**. This fixes trace(J_C)=t but does not determine its order. The constraints imply #J_C(Fp)=r(p²+A+1); the multiplicity of r in the Prym order is unresolved. The injected source subgroup exists regardless of that multiplicity.

## Hyperelliptic genus-two control and complete Frobenius factors

The second cover is C₂:w²=z⁶−3z²+b, with π₂(z,w)=(z²,w). Its sextic is squarefree, as checked, and it has two rational points at infinity. The function z²=x ramifies at the two geometric points of E above x=0, because b≠0; its pole at O has even order. Thus the different has degree two, 2g(C₂)−2=2, and C₂ is hyperelliptic of genus two. Both infinities map to O.

The source pullback fibre has Mumford congruence data U(z)=z²−xP, V(z)=yP, with U|(z⁶−3z²+b−V²). For the even-degree model the full divisor is the fibre minus ∞₊−∞₋; the polynomial congruence alone must not be confused with a chosen single-infinity normalization. The executable validates seven such fibres. The universal identity π₂,*π₂*=[2] gives the same subgroup preservation and recovery.

The other involution gives an elliptic quotient B:v²=s⁴−3s²+b s via s=z², v=z w. With X=b/s and Y=bv/s² its Weierstrass model is

B:Y²=X³−3X²+b².

The two elliptic quotient maps induce a degree-four split-Jacobian isogeny J_C₂→E×B; both factors and their Frobenius polynomials are over Fp. A separate Sage/PARI SEA computation gives

t_B=167631093631314538742209370567683050917,

#B(Fp)=115792089210356248762697446949407573529918512321658999656791421938299414803035.

Therefore P_JC₂(T)=(T²−tT+p)(T²−t_B T+p), with the complete coefficients and #J_C₂ in `elliptic-quotient-checks.json`. This exact point count is a software computation through PARI, with its Hasse check retained; it has not received an independent replay. Since 0<#B(Fp)<r, r does not divide #B(Fp): the rational r-component of this genus-two Jacobian comes from E and has multiplicity one.

## Cost ledger and algorithm obligations

| Stage | What is established | What is unmeasured or missing |
|---|---|---|
| Construct covers and branch data | Fixed explicit equations, smoothness gcds, maps and genus proofs | No moduli search or discovery benchmark |
| Pull back G,Q | Fp ideals with two generators; no square-root extraction needed to encode each fibre | Full plane-quartic divisor reduction/addition implementation |
| Norm and recovery | Universal degree-two identity; seven fibre support/recovery fixtures per cover | General optimized norm on arbitrary Jacobian divisor classes and measured costs |
| Locate target component | Source elliptic factor explicit; r-coprime degree proves injection | Quartic Prym order and possible extra r-primary multiplicity |
| Relations and logarithm | A destination solver must act on the image of this order-r subgroup | Factor base, useful rank, relation cost, memory, individual-log descent and actual solver |
| One target / many targets | Equations and fixed generator encoding reusable | All per-target attachment and source verification costs remain charged |

The represented subgroup retains order r≈p inside an ambient Jacobian of dimension three (or two). Appending the Prym or B factor does not make that subgroup larger or easier. A reported full-Jacobian plane-quartic algorithm with a different asymptotic regime cannot be substituted for a costed solver on this image. No matched source/destination trial, performance advantage or ECDLP cost bound is claimed here.

The repository literature records were retrieved and read as `kb` pointers. KN-LIT-b4a89c describes a cubic-extension E/F(q³) construction using Weil restriction to a genus-three Jacobian over Fq; its summary does not supply a smaller field for this prime-field source. KN-LIT-39d9ed describes explicit genus-three hyperelliptic-to-plane-quartic isogenies in specified tractable-kernel families; its existing claims do not establish a complete algorithm or advantage on our order-r elliptic factor. No novelty is asserted for the elementary covers derived here, and neither record was treated as a newly verified primary-paper theorem.

The precise next discriminating task is to implement arithmetic on the displayed plane quartic and π*,π_* on arbitrary classes, then define a relation mechanism that demonstrably handles the E component, complete rank modulo r, and both transported inputs. Compare the resulting total cost with the direct source algorithm on the same G,Q and success criterion, charging setup, failed relations, memory, individual logarithm and verification. The unknown Prym coefficient A can be computed independently, but matching its polynomial would still not resolve those solver obligations.

## Boundary, receipts and visual record

Within unramified connected covers of an elliptic curve, Riemann–Hurwitz forces genus one; thus higher genus requires ramification. Our two branched constructions meet that necessary condition exactly. They neither exhaust covers nor establish any impossibility outside their two equations.

`commands.json` records exact commands, source hashes, runtime and parameters. Containers used cached Sage 10.6 with no network, one CPU and 2GiB; all checks terminated successfully, with no failed cover attempt discarded. The figures are this track's editable `diagram.svg`; no existing canonical shared graph was altered. Root renders the aggregate PDF and owns archival task TASK-20261025-466d20. These results make no official state transition. The remaining solver obligation is explicit in `obligations.md`.
