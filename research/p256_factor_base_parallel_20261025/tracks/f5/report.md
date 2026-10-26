# F5 — explicit P-256 target representatives (2026-10-25)

This is implementation validation and an exact mathematical screen under TASK-20261025-7144c5, not an admitted performance trial or a scientific state transition. Four explicit maps were constructed over the actual P-256 field: one of degree 3, one of degree 5, and two of degree 11. Their complete kernels, endpoint coefficients, evaluators and dual evaluators are retained in `attempt02-kernel-screen-{3,5,11}.json`. All four pass symbolic curve-landing and dual-composition checks and seven deterministic point-recovery checks each. These are producer checks, pending independent review.

## Instance and certified invariants

The field and full source/endpoint representation identities are in `identities.json`; its source alias is `EC1P256Cp256hc59ede3f79de`, full UID `urn:ec-record:1:sha256:c59ede3f79defa1603280e26ca59b3057d13626874aac2e3d044763c9f17051c`. The manifest binds the published generator and prime order r, not merely the field size. Coefficients are canonical integers modulo p; a=−3. The field, b, r and generator are spelled out in executable source and metadata.

Sage 10.6 with `proof.all(True)` proves p and r prime, verifies nonzero G and [r]G=O, and checks nonsingularity. The full integer Hasse interval in `supplement-checks.json` contains exactly one multiple of r, namely r. Thus #E(Fp)=r and the full rational group is cyclic. This supplement uses floor(sqrt(4p)); the initial Sage receipt used the slightly narrower expression 2 floor(sqrt(p)). The exact interval supplement removes that rounding ambiguity.

Derived and checked:

- t = 89188191154553853111372247798585809583.
- Δπ = −455213823400003756884736869668539463648899917731097708475249543966132856781915.
- −Δπ = 3 · 5 · 456597257999 · 1428624589419343516204097 · 46523541035814968339936406074986559003387. Each factor is proven prime on replay, all exponents are one, and Δπ≡1 mod4.
- Therefore Δπ is fundamental: D_K=Δπ, fπ=1. The order inclusion Z[π]⊆End(E)⊆O_K forces f_E=1 for the source and every Fp-isogenous endpoint. The representative conductor is resolved here; it is not copied from an unverified Frobenius conductor.
- t mod p is nonzero, so the class is ordinary. Its point counts over every extension and its rational endomorphism algebra remain unchanged by these Fp-isogenies.

The factorization was retrieved from committed `research/endosweep_nist_20261006/nist.json` (`prior-p256.json`, with the full retrieved source in `nist-source.tmp`) and rechecked by exact product and primality routines here. This is provenance `internal`, not a novelty claim.

## Bounded catalogue

The exact Frobenius polynomial T²−tT+p was reduced modulo all 14 primes ≤43. The inert directions in that boundary are 2,7,19,31; ramified directions are 3 and 5; the remaining eight primes split. Distinct split eigenvalues give two stable cyclic kernel lines. At the repeated-root primes actual kernels were constructed, rather than inferring full rational torsion. The source cubic is irreducible, confirming that it has no rational degree-two quotient.

| Degree | Division-polynomial factor degrees | Validated maps | Kernel x-field / point-field degree | Direct affine model per map |
|---|---|---:|---|---|
| 3 | 1,3 | 1 | 1 / 2 | ≤14M+11A+2I |
| 5 | 1,1,5,5 | 1 (product of the two linear factors) | 1 / 2 | ≤24M+21A+2I |
| 11 | twelve factors of degree 5 | 2 | 5 / 10 | ≤54M+51A+2I |

M,A,I denote multiplication, addition and inversion in Fp. These are conservative dense Horner models for the serialized rational functions, not measurements or optimized bounds. They evaluate the four polynomials in x independently and then form x′ and y′; common powers of the kernel denominator can reduce the modeled work. `composition-checks.json` gives the degrees and the exact counting definition.

For the first map the kernel polynomial is

h₃(x)=x+7297273671128722501105690488737988060417332747327511973586927408428460908388.

Its x-map is N₃(x)/h₃(x)² of degrees 3/2 and its y-map is yM₃(x)/h₃(x)³. The receipt contains every coefficient. All four endpoints have distinct j from the source as recorded, so these are genuine isogenies, rather than coordinate changes. Each edge is separable, defined over Fp and horizontal because both endpoint conductors equal one.

**Rational kernel versus rational kernel points:** #E(Fp)=prime r excludes nonidentity Fp-points of order 3,5,11. A kernel polynomial over Fp certifies a Frobenius-stable subgroup, not rationality of all its points. The eigenvalues are −1 mod3, −1 mod5 and {2,8} mod11; the last two each have order10 and first power equal to ±1 at degree5. `supplement.py` checks these exact minimal degrees. No kernel point was treated as an Fp-point.

## Universal transport certificate and finite checks

The kernel-polynomial constructor validates that each candidate is a finite subgroup. Ten other degree-five factors of ψ₁₁ fail that test and remain recorded as rejected candidate factors. Factoring a division polynomial is insufficient to identify a cyclic kernel.

A nonconstant curve morphism taking O to O is a group homomorphism. The exact maps satisfy the codomain equation modulo y²−(x³−3x+b). The serialized duals satisfy

hat(φ)∘φ=[ell]

as rational-function identities for both coordinates, checked independently of sampled points by `composition.sage.py`. Thus ker φ∩E(Fp)[r]={O}, since gcd(ell,r)=1. In fact φ is an isomorphism between the full order-r rational groups. Point recovery is [ell⁻¹ mod r]hat(φ); scalar recovery needs no such multiplication: if Q=[n]G then φ(Q)=[n]φ(G), so a destination logarithm is the same n modulo r and is verified on the source.

The scalar list 0,1,2,3,17,257,65537 supplies 28 constructed implementation checks. It estimates no success probability. O is explicitly included. Other rational subgroup inputs cannot meet a nontrivial kernel denominator zero. The universal argument, rather than the number of samples, supplies subgroup preservation.

## Bases and total-cost obligations

Two explicit families can now be inspected. A transported source base φ(B) preserves cardinality and all group relations because φ is injective on E(Fp). A destination x-domain D gives the pullback condition N(x)/h(x)²∈D together with denominator and point-lifting conditions; for an individual c∈D its equation is N(x)−c h(x)²=0. For a polynomial domain m(X)=0 of degree M, the naive cleared equation has degree at most ell M. This derivation supplies a concrete membership formulation, not a relation-solving advantage.

| Cost item | Status and scope |
|---|---|
| Discover kernel and endpoint | Actual factorization/construction completed at 3,5,11; no wall-time benchmark collected |
| Map G,Q | Two explicit evaluations; conservative field-operation model above |
| Build/lift a base and solve membership | Formula supplied; solver work, rejection rate and storage unmeasured |
| Relations, independent rank, linear algebra | Not implemented or measured in this track |
| Individual logarithm and verification | Destination algorithm unresolved; returned scalar must satisfy [n]G=Q |
| One target / many targets | Charge all setup for one target. Maps and φ(G) can be reused across targets; no measured amortized claim |

The next decisive implementation is a matched source/destination relation solver using these exact serialized maps, the same transported points, a coordinate-isomorphism control, identical symmetries and a fixed canonical base size. Its ledger must include map discovery, lifting, failed decompositions, rank, target attachment, memory and verification. No broad conclusion about untapped representatives or ECDLP speed follows from this screen.

## Receipts, limitations and provenance

Run `exact.sage.py`, `composition.sage.py`, then `supplement.py` in a fresh output directory with the input receipts copied as specified by `commands.json`. Sage containers were network-disabled, limited to 2GiB and one CPU. Only public curve parameters and synthetic multiples were used. The initial implementation accidentally placed the successful-map receipt block after an exception's `continue`; that attempt exited zero while omitting successful map records. Its exact source and outputs are preserved as `exact-attempt01.py`, `frobenius.json`, `kernel-screen-*.json`, and `attempt-01.*`. Attempt02 fixes the software issue; no negative mathematical conclusion is taken from attempt01. A metadata-helper invocation also used an incorrect relative directory; it wrote no artifact and is recorded in `commands.json`.

Audit/transfer/endomorphism profiles, their methodology and required KN-TECH-6a2ef9 were read. Sparse-checkout files were retrieved via `git show`; the initial sandboxed remote read and Docker socket diagnostic failed and were retried with the allowed tool permission. The handoff excludes official status, ledger and shared graph edits. The only affected graph is this track's `diagram.svg`; no canonical shared graph was changed. Root owns the aggregate PDF render and archival task TASK-20261025-466d20.
