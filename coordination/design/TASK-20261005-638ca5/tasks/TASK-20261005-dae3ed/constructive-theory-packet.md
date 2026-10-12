# Bounded constructive packet: TASK-20261005-dae3ed

This replacement session supplies three failed definitions, not a surviving
novel PKE. A fails correctness; B exposes its decoder; C has injective message
encoding but no established efficient EndRing-only inversion. These statements
concern the specified definitions. No experiment or security result is reported.

| Route | Tracked object / mechanism | Public Enc | Actual message Dec | Blocking gate |
|---|---|---|---|---|
| A | Endpoint fiber of a coprime isogeny diamond | Defined | Two messages give the same ciphertext | Correctness fails |
| B | Additive coset of a rank-four quaternion lattice | Defined | Defined, also publicly computable | No secret decoding advantage |
| C | Bounded-degree map determined by its full coprime torsion action | Defined | Exhaustive decoder defined; efficient decoder unresolved | EndRing-to-Hom compiler and nonduplication unresolved |

## Shared domains, encoding and key-generation specification

Let p>5 be prime. Public Setup receives a certified supersingular reference
E*/F_(p²), scalar p²-Frobenius, and a public evaluable basis O*=End(E*).
There is no secret setup datum. Specify L, a, 1<=k<a, D=2^a and N=5^b with
N²>4D. Use a fixed finite extension F of F_(p²) containing the required
torsion. Its degree and all reference certificates are public and charged.
Finding short certificates, extension degree and efficiency are unresolved K0.

KeyGen uses uniform independent choices among the four cyclic order-3
subgroups at each of L steps to construct tau:E*->E of degree t=3^L.
It forms R=Z·1+tau O* dual(tau) inside End(E). Compute the trace-dual R#;
enumerate intermediate lattices R<=O'<=R# closed under multiplication with
trace-form discriminant p². For a basis element beta, choose a denominator
n with n beta in R, evaluate n beta, test that it kills E[n], and divide the
map through [n] when it does. The denominator can be prime to p because R is
already maximal locally at p. Keep the order whose basis maps pass these
integrality tests. This is a finite saturation specification, not a polynomial
algorithm claim; no GRH conversion is invoked. The actual End(E) occurs in this
enumeration. It is the maximal integral order in this fixed map embedding.
Output sk=(four evaluable basis maps, multiplication table, coordinate data).
Erase tau and its transcript; retaining them would add a distinct secret path.
K0 includes bounds on this enumeration and compact evaluation representations.

For A/C publish E and deterministic bases U,V of E[D] and P,Q of E[N], found
by finite point enumeration and independence checks. The choice rule is public
and has no hidden orientation. D_curve is the resulting length-L walk law on
canonical curve models, not an asserted uniform supersingular law. The public
level structures give a separate augmented distribution D_level. The bare
EndRing-eval(D_curve) output is an evaluable Z-basis modulo GL_4(Z), with
explicit model-isomorphism transport; no claimed reduction erases D_level.

Encode field elements in a fixed polynomial basis and points in affine
coordinates with an infinity tag. Canonicalize a curve model by the least
encoding in its finite F-isomorphism orbit and transport point images by the
least isomorphism; ties are deterministic. Ciphertext equality is exact byte
equality after this normalization. Reject noncanonical encodings, wrong
domains or failed validation with bottom (⊥); candidate-list output is forbidden.

## A: endpoint-only coprime diamond

Messages are m in {0,1}; randomness is the singleton {0}; ciphertexts are
canonical supersingular curve models. Set H_0=<2^(a-1)U>, H_1=<2^(a-1)V>.
Encrypt computes alpha_m:E->E/H_m of degree 2, then its dual back to E,
and emits only the endpoint c=E. The length is exactly two, not variable.
All computations use pk alone. The map is phi_m=dual(alpha_m) alpha_m=[2].
Decrypt(sk,c) compares the two defined encryptions; return their sole message
if exactly one matches, otherwise ⊥. Thus for every generated key and both m,
Dec(sk,Enc(pk,m;0))=⊥, contradicting the required equality to m.

The intended ring advantage was to complete a coprime diamond
phi_m tau=tau' eta_m with deg(eta_m)=4, deg(tau')=t. Here eta_m=[2] and
tau'=tau complete it for both messages. Even disclosure of the exact tau,
all Hom modules and every endomorphism cannot distinguish the factorizations.
The discarded first-edge choice is precisely the message; it is absent even
from the composite map. This is an exact collision for this encoding, not a
claim about fixed-length nonbacktracking or cyclic-kernel encodings.

Low-rank gate: solving any quaternion norm equation for [2] supplies the same
element for both branches. Torsion gate: every finite representation of the
composite is rho_N([2])=2I for both m. Additional diamond-completion assumptions
cannot repair this information loss. Closest boundary is the known walk/diagram
families; an endpoint fiber test adds no construction novelty.

## B: exposed rank-four order-lattice cosets

Use the same ring sampler. In a fixed rational quaternion coordinate space
V=Q^4 with public positive reduced-norm Gram matrix G, take Lambda=q O for
public integer q>=2. Publish a rational full-rank basis matrix B of Lambda.
Set v=B(1/2,0,0,0)^T. Then v is not in Lambda. Let
delta=min_(z in Z^4)||v-Bz||_G>0 and choose public rational 0<epsilon<delta/2.
Setup also specifies finite integer box [-Z,Z]^4 and a rational error grid
E_epsilon={e on that grid: ||e||_G<=epsilon}. Publish their exact bounds.
KeyGen outputs pk=(B,G,v,epsilon,Z,grid); sk additionally holds O's maps.

Messages are bits; randomness r=(z,e) is uniform on the displayed finite sets;
Encrypt emits x=Bz+m v+e in Q^4, with reduced rational-coordinate encoding.
Decrypt computes d_i=min_z||x-i v-Bz||_G, i=0,1. Return the unique i with
d_i<=epsilon, else ⊥. Exact comparisons can use squared rational norms.
For every key,m,z,e, d_m<=epsilon and d_(1-m)>=delta-epsilon>epsilon.
Consequently Dec(sk,Enc(pk,m;(z,e)))=m with zero valid-input failure.

The exact same decoder uses only pk: closest-vector search in fixed dimension
four with the supplied rational positive metric is computable in polynomial
bit complexity by fixed-dimension integer optimization. It needs neither a
short secret basis nor evaluation of End(E). This route's purported ring
operation is therefore absent. No lattice hardness exponent is claimed.
Endpoint/coset ambiguity is avoided by the strict distance bound, which also
lets the public decoder work. Publishing a torsion representation instead of
B is a different definition: its coefficient constraints are a four-column
linear system modulo N, invertible when that matrix has rank four. A rank
defect would require a new encoding and ambiguity analysis, not establish a
trapdoor for the exposed-B definition. This is an additive lattice control,
not an asserted new ideal-action or SÉTA construction.

## C: cyclic-kernel encoding with a finite-torsion lift

Messages are k-bit integers 0<=m<2^k; randomness is 0<=r<2^(a-k), uniform.
Set s=m+2^k r in Z/DZ and K_s=<U+sV>. Encrypt computes the cyclic degree-D
quotient phi_s:E->C_s as a chain of a degree-2 isogenies and emits
c=(C_s,phi_s(P),phi_s(Q)), normalized together. This uses only public points,
m and r. Validate the two images as an N-torsion basis with pairing
e_N(P',Q')=e_N(P,Q)^D; this necessary check alone does not prove membership.

An actual finite decoder enumerates s=0,...,D-1, reenacts Enc, compares the
entire ciphertext and returns s mod 2^k for a unique match; else ⊥.
It is publicly executable and exponential in a. It proves a functional
encoding, not efficient secret inversion. Its correctness is quantified over
every generated key, all messages and all allowed randomness, with no failure.

To prove uniqueness, identify equal normalized codomains. Two degree-D maps
phi,psi agreeing on P,Q agree on E[N]. Thus phi-psi factors through [N]. If
nonzero its degree is at least N². Positive definiteness of the Hom degree
form gives deg(phi-psi)<=(sqrt(D)+sqrt(D))²=4D<N², a contradiction.
Hence phi=psi. Their cyclic kernels agree, and coefficient 1 on U forces
s=s' mod D, so the decoder returns the actual m, not a path or branch label.

The proposed efficient secret Dec has a missing operation C1: from sk=End(E)
and c compute an evaluable Z-basis h_1,...,h_4 of Hom(E,C), its positive
degree form and its restriction to E[N], in polynomial input/output size.
End(E) acts on Hom(E,C) on the right but does not by its type supply this
connecting module. Calling this operation Lift(sk,c) would not define it.
Given C1, express the public image pair and h_i(P),h_i(Q) in a target
N-torsion basis using smooth-N discrete logs. Solve the four-coordinate
linear congruences for the affine lattice of all compatible Hom maps.
Degree-D phi_s is its unique shortest element: any other element of norm
at most D would contradict the same N²>4D bound. Fixed-rank exact closest
vector optimization then recovers phi_s. Evaluate it on U,V. The point
phi_s(V) has order D because <V> meets K_s trivially; use the smooth-order
discrete log -phi_s(U)=s phi_s(V) to recover s and output s mod 2^k.

Public finite-level linear algebra determines residues once a Hom basis is
known; it neither supplies that basis nor proves secret-only recovery. The
low-rank lattice gate has therefore moved to obtaining Hom, not vanished.
If Hom and its evaluation are public, the same algorithm decrypts publicly.
The source ring may help construct it, but this is unresolved C1, separate
from efficient key generation K0, public recovery/leakage C2, and normalized
nonduplication C3. The full-torsion interface is close to SÉTA and the historical
SSI-T attack boundary in the committed notes. No withholding-ring security
argument, current attack transfer, or novelty claim follows from this packet.

## One next obligation and ceiling

Prioritize C1: write a polynomial-size, explicit EndRing-eval-to-evaluable-Hom
compiler for exactly C's distribution and ciphertexts, or identify its missing
connecting-ideal information. Run its derivation against the same public-Hom
control to determine what really requires the ring. This is a mathematical
obligation, not authorization for a run. A remains a collision diagnosis; B
remains a public-decoder control. No open-ended fourth mechanism is proposed.
Heuristic distributions are not used; all remaining efficiency, leakage and
comparison statements are unresolved. Time/memory exponent improvement is 0
claimed. C's fallback costs D encryptions and streaming storage; no asymptotic
advantage over published PKE is asserted. Independent review must precede any
later claim or implementation contract.
