# F1 exact derivations (2026-10-25)

All identities are in characteristic greater than three. Here p is the published
P-256 prime, and E is y²=x³−3x+b with the committed published b and prime order r.
Sources: committed plan/baseline and read-only prior `dickson-inspection/proofs.txt`
(provenance: internal, retrieved by this implementation session). New derivations
below are checked by the delivered source, not claimed as independently reviewed.

## Symmetric quadratic circuit

For three input coordinates x₁,x₂,x₃ let (u,v,w) be their elementary symmetric
coordinates. The elementary symmetric coordinates of xᵢ²−2 are

```
Φ₁ = u² − 2v − 6
Φ₂ = v² − 2uw − 4u² + 8v + 12
Φ₃ = w² − 2v² + 4uw + 4u² − 8v − 8.
```

These follow by elementary symmetric expansion; `identity_checks()` obtains them
independently using SymPy symmetrization. With S=2ᵏ, all three coordinates satisfy
D_S(xᵢ)=c exactly when Φᵏ(u,v,w)=(3c,3c²,c³). The equivalence holds over the
algebraic closure, including repeated coordinates: the terminal cubic is (Z−c)³.

For xᵢ=αtᵢ+β, α≠0, transform the input symmetric coordinates by

```
s₁ = αu + 3β
s₂ = α²v + 2αβu + 3β²
s₃ = α³w + α²βv + αβ²u + β³.
```

Thus the joint relation system is the terminal circuit and the committed
quartic S4(s₁,s₂,s₃,x(Q))=0. The delivered numerical determinant identity checks
S4 against the resultant of two S3 polynomials on 40 deterministic field tuples.
S4 roots must still be lifted and checked on E. P-256 has cofactor one; delivered
finite bases additionally check rP=O for every retained point.

## Generic cosets and scalar ramification

Because p≡3 mod 4, use Fp[i]/(i²+1). Set z(t)=(t+i)/(t−i), equivalently
((t²−1)/(t²+1), 2t/(t²+1)). Its norm is one. Let ω have exact order S in the
norm-one group (ω is obtained by exponentiation and certified by ω^S=1 and
ω^(S/2)≠1). Choose c=Tr(z₀^S), where c≠±2. The roots of D_S(X)−c are precisely

```
{ Tr(z₀ ωʲ) : 0≤j<S }.
```

Indeed D_S(z+z⁻¹)=z^S+z⁻S. A trace collision has either equal z or inverse z;
an inverse collision between this coset and itself would imply z₀²∈<ω>, hence
z₀^S=±1 and c=±2. The generic fibre therefore has S distinct rational roots.
The delivered verifier checks the complete polynomial factor identity.

For c=2 the scalar polynomial D_S−2 is ramified and has S/2+1 distinct roots
for k≥1, all rational when S divides p+1. Its squarefree radical is checked
against the supplied factorization. For P-256, v₂(p+1)=96. Exact circuit and
torus witnesses reach k=96; full domains are enumerated only through k=8.

## The symmetric diagonal remains ramified

A generic scalar fibre does **not** make this symmetric membership ideal radical.
The terminal is the triple (c,c,c) in root coordinates, a diagonal point of the
permutation quotient. For an unramified scalar fibre of size S there are exactly
C(S+2,3) distinct symmetric preimages, but the scheme length is S³.

One justification of length: the highest homogeneous components of Φ vanish
simultaneously only at zero. The first forces u=0, the second then v=0, the third
then w=0. This finite polynomial morphism has degree 2³, and its iterates have
degree S³. Equivalently, Bezout has no points at infinity; its three equations
form a zero-dimensional complete intersection of length S³. Flatness here follows
from the finite map between equal-dimensional polynomial rings and the regular
sequence, so special fibre length is constant.

At an unramified scalar preimage, the multiplicity attached to a multiset of
three roots is 1 when all are equal, 3 when exactly two are equal, and 6 when all
are distinct. The local scalar maps are invertible; these factors are the indices
of the input stabilizers in S₃ at the fully equal terminal. Summing gives

```
S + 3 S(S−1) + 6 C(S,3) = S³.
```

The implemented Groebner adapter observes length 8 versus 4 distinct points at
S=2, and length 64 versus 20 at S=4. Joint S4 examples also retain multiplicity.
An extraction method requiring a squarefree characteristic polynomial of the
unradicalized multiplication algebra cannot simply be assumed to apply. This is
a representation issue; it is not a proof that implicit solving is impossible.

## Two actual solving formulations

1. **Forward algebraic elimination.** Expand Φᵏ in three variables; adjoin the
   S4 quartic; compute a grevlex Groebner basis; recursively eliminate in lex
   order, taking all Fp roots at each univariate branch using FLINT. Joint
   cases k=1 and k=2 complete and match exhaustive inverse-state zero sets.
   k=3 stopped at its declared resource watchdog during basis construction.
   Basis ideal-membership witnesses are not exported, so these are adapter
   outputs validated against an exhaustive finite-domain reference, not a
   peer-certified Groebner implementation.
2. **Inverse symmetric recursion.** Store a state as the sorted three roots of
   its split cubic. Starting at (c,c,c), replace each y by every square root of
   y+2, then deduplicate by sorting. Each reverse step has at most eight raw
   branches. Induction proves that every domain multiset occurs and no other
   state occurs. At depth k there are exactly C(N+2,3) states, where N is the
   number of distinct domain roots. Test S4 at the leaves, recover all signed
   curve lifts, and check sums exactly. This is algebraic backward recursion,
   but it enumerates the whole symmetric domain and does not prune globally.

Neither formulation creates one dense pair polynomial per factor-base point.
The inverse implementation replaces that architecture with a complete triple
state enumeration; no asymptotic or measured advantage follows.

## Representation and operation accounting

With u²,v²,w²,uw shared, a written Φ stage uses three field squarings, one general
multiplication, eight small-constant scalings, and eleven additions/subtractions.
Small-constant scalings are counted separately, without implementation-specific
weighting. An unexpanded chain uses 3k quadratic equations in 3(k+1) variables,
plus three terminal equations and S4. This is a short input representation, not a
bound on Groebner work or solving degree.

The expanded outputs have degree 2ᵏ. Exact nonzero monomial counts at k=1…5 are
(3,5,6), (7,16,19), (24,71,85), (111,408,489), (648,2735,3281).
These are exact symbolic counts for terminal c=7 over the actual field. The dense
three-variable cap is 3 C(2ᵏ+3,3) coefficient slots. Neither cap nor finite counts
prove a lower bound for compressed elimination. Inverse recursion stores
C(N+2,3) root triples; its exact branch and square-root-request counts are in each
case bundle. Precomputing the S4 coefficients, point lifts, failed branches, and
base/coset matching are retained as separate operations rather than timed away.
