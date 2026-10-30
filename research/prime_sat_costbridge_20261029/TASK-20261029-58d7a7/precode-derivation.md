# TASK-20261029-58d7a7: independent derivation before code access

This document was written before reading or hashing reference.py,
check_reference.py, or test_reference.py. It is to remain unchanged after its
seal. Its actually observed seal clock and SHA256 are recorded in the final
attestation, outside this file. It is a symbolic derivation, with zero software
or scientific runs. The accepted local Hilbert series and raw regularities in
the brief are premises; this review independently derives their accounting
consequences. No new producer conclusions or sibling reports were read.

## Inputs, provenance, and scope

The phase-one sources actually read are the following literal paths/URLs:

- AGENTS.md
- coordination/prime_sat_costbridge_20261029/blind-brief.md
- coordination/prime_sat_costbridge_20261029/review-plan.yaml
- coordination/prime_sat_costbridge_20261029/runtime-attestation-policy.yaml
- coordination/prime_sat_costbridge_20261029/reference-contract.json
- coordination/prime_sat_costbridge_20261029/inference-amendment.yaml
- ledger/handoffs/TASK-20261029-58d7a7.yaml
- research/prime_sat_regularity_20261029/proof.md
- research/prime_sat_regularity_20261029/grouped-proof.md
- ledger/decisions/DEC-20261029-ce5c57.yaml
- ledger/decisions/DEC-20261029-0857a9.yaml
- docs/agent-contract-extended.md (sections Literature first, Observe first;
  interpret later, Scientific observation comes first, Review architecture,
  Inter-agent messaging, Knowledge retrieval policy, Intermediate-cost and
  asymmetric-access hypotheses; section headings inspected narrowly)
- docs/agent-contract-supplement.md (Name the obstruction and Research direction;
  section headings inspected narrowly)
- docs/lab-contract.md (sections 1-5; section headings inspected narrowly)
- docs/skill-routing.md (Choose by action and Choose by subject)
- /var/lib/spot-codex/home/skills/route/SKILL.md
- /var/lib/spot-codex/home/skills/review-evidence/SKILL.md
- https://arxiv.org/html/2304.13485 (Definitions 2.4-2.5,
  Propositions 3.10/3.13 and their proofs)
- https://www.rfc-editor.org/rfc/rfc9380.html (Appendices I.1/I.4 and F.2.1.1)

Repository records have internal provenance; public references were retrieved
and read in this session by /root/costbridge_blind_reviewer. No novelty search
outside the whitelist, knowledge-index search, memory lookup, Git inspection,
inbox scan, or protected-report access was performed. The repository route
skill path .claude/skills/route/SKILL.md was absent; the available installed
skill was read instead. Generic lifecycle merge, additional-report, experiment,
and execution steps do not apply to this restricted symbolic reviewer task;
the explicit handoff governs the three-file scope. Root owns archive and any
later decision or visual rendering. This task makes no official transition.

[Salizzoni](https://arxiv.org/html/2304.13485) defines a degree-bounded closure
that may multiply newly obtained consequences, and a corresponding solving
degree. Proposition 3.10 bounds it by max(d_reg+1, maximum input degree).
Proposition 3.13 gives a field-operation upper bound under the additional
input-degree premise. These conventions do not name every F4/SAT implementation.
[RFC 9380](https://www.rfc-editor.org/rfc/rfc9380.html#appendix-I) supplies
prime-field square-root methods and a square-or-nonsquare-times-square output
interface; the costs and certificates below are derived explicitly.

## 1. Exact local inventory

Let s=2m, m>=1. Put C(n,k)=0 outside 0<=k<=n. For any integer D>=0,

    B_s(D) = sum_{k=0}^{min(D,2s)} C(2s,k),
    G_s(D) = sum_{k=0}^{min(D,s)} C(s,k) 3^k.

These count monomials of degree at most D in the LOCAL highest-part quotient:
squarefree subsets of the 2s bits, versus choosing at most one of three
indicators from each of s groups. Both total dimensions are 4^s. Write a sum
with negative upper limit as zero. Symmetry gives the exact table:

| presentation | preceding degree | regularity degree | mutant cap |
| --- | --- | --- | --- |
| bit degree | 3m | 3m+1 | 3m+2 |
| bit prefix | 4^s-sum_{j=0}^{m-1}C(4m,j) | 4^s-sum_{j=0}^{m-2}C(4m,j) | 4^s-sum_{j=0}^{m-3}C(4m,j) |
| group degree | 2m | 2m+1 | 2m+2 |
| group prefix | 4^s | 4^s | 4^s |

The regularities used here are d_b=3m+1 and d_g=2m+1. The raw quartic input
degree remains four: max(d_g+1,4)=s+2 even when s=2.

At respective preceding degrees, G is strictly larger than B for every s>=2.
At respective regularity degrees, equality holds only at s=2; G>B for s>=4.
At respective caps, equality holds at s=2,4; G>B for s>=6. Concretely:

| s | bit preceding | bit regularity | bit cap | group at all three degrees |
| --- | ---: | ---: | ---: | ---: |
| 2 | 15 | 16 | 16 | 16 |
| 4 | 247 | 255 | 256 | 256 |
| 6 | 4017 | 4083 | 4095 | 4096 |

These are direct binomial evaluations, not program output. At a COMMON
degree D=s+1, the grouped prefix has already saturated while the bit prefix
has not (s>=2). This is again an inventory comparison.

For a fixed offset j=0,1,2, Stirling's formula and the geometric tail ratio
near binomial degree s/2 imply

    4^s - B_s(3s/2+j)
      = Theta(s^(-1/2) * 2^(2s H_2(1/4))),  s -> infinity through even s,

where H_2(q)=-q log2(q)-(1-q)log2(1-q). Thus B_s/4^s ->1 exponentially
quickly and G_s/B_s ->1. The small-s zero tails above are retained. The
dimension 4^s is not reduced by grouping, and none of these identities
establishes the dimension of a full S3 quotient or a necessary solver cost.

## 2. Ambient capacities, full quotients, and algorithmic work

In a polynomial ring with n ordinary variables, the homogeneous degree-D
capacity is C(n+D-1,D), and the affine prefix capacity is

    A(n,D)=sum_{k=0}^D C(n+k-1,k)=C(n+D,D).

For the three respective degrees, the ambient bit prefixes are
C(7s/2,3s/2), C(7s/2+1,3s/2+1), C(7s/2+2,3s/2+2).
The group prefixes are C(4s,s), C(4s+1,s+1), C(4s+2,s+2).
At the same D>0, A(3s,D)>A(2s,D); at different D there is no such immediate
ordering. Small cases at the respective preceding/regularity/cap degrees:

| s | bit ambient triple | grouped ambient triple |
| --- | --- | --- |
| 2 | (35,70,126) | (28,84,210) |
| 4 | (3003,6435,12870) | (1820,6188,18564) |

For any fixed offset j, independently applying Stirling gives

    A(2s,3s/2+j)=Theta(s^(-1/2)*alpha_b^s),
    A(3s,s+j)=Theta(s^(-1/2)*alpha_g^s),
    alpha_b=(7/2)^(7/2)/(2^2*(3/2)^(3/2)),
    alpha_g=4^4/3^3,
    alpha_b^2=823543/6912 > (256/27)^2=alpha_g^2.

Thus the bit ambient capacity eventually exceeds the grouped capacity
exponentially at their respective offsets, despite the finite-s reversals.
This is an asymptotic statement about two capacity formulas only.

Four objects must stay distinct:

1. The local highest-part quotient has the monomial bases counted in Section 1.
2. The full highest-part quotient additionally imposes the highest part of S3.
   Its graded pieces can be smaller; the accepted d_reg says its degree d_reg
   piece vanishes. Local prefixes at that degree need not vanish.
3. The affine quotient uses Boolean/indicator equations with their lower terms
   and S3 itself. Its reduced function algebra dimension counts accepted bit
   assignments, subject to injective-coordinate qualifications. The accepted
   affine isomorphism does not preserve this standard degree filtration.
4. Actual elimination rows, columns, pivots, fill, consequences and search
   nodes depend on representation and algorithm, not just any one inventory.

Adding the constant equation 1 and adding no extra equation leave exactly
the same local inventory but yield a zero full quotient/trivial inconsistency
and a full local state space, respectively. Hence local inventory cannot be
a necessary solving-work lower bound. Sparse/mutant algorithms need not
construct every ambient row or column. Two solving-degree upper bounds do
not order the actual solving degrees.

Salizzoni's source-qualified closure bound gives caps d_b+1=3s/2+2 and
d_g+1=s+2. Proposition 3.13, as stated, needs max input degree<=d_reg:
it applies directly to bit s>=2 and grouped s>=4, but not grouped raw s=2
(4>3). Its O((n+1)^(4(d+1))) field-operation bound is an existence upper
bound with a specified closure algorithm. Its proof uses N=C(n+d+1,d+1),
which is capacity through d+1; a sentence labeling it through d is an
off-by-one description and does not alter the displayed formula. No such
upper bound is a measured comparison or necessary work. A direct finite
closure construction at a supplied cap D can in principle maintain at most
A(n,D) independent polynomials, queue at most A(n,D) monomial multiples per
new basis element, and do dense reduction, but remains an upper-bound
construction plus input/queue costs, never a prediction for chosen software.

## 3. S3 rationality and the independent second-coordinate roots

Assume p prime >3, nonsingular E:y^2=f(x)=x^3+ax+b, and R=(r,t) on E with
t!=0. Canonical D1,D2 have no repeated coordinate within each domain; they
may overlap each other. Infinity is excluded. Put x=x1,z=x2 and

    N=xz-r(x+z)-2r^2-a,
    S3=N^2-4t^2(x+z+r).

Expansion agrees with the accepted raw S3 using t^2=r^3+ar+b. If S3=0,
lambda=N/(2t) is rational and lambda^2=x+z+r. Direct coefficient expansion
then gives the monic identity in X:

    f(X)-(lambda*(X-r)-t)^2=(X-r)(X-x)(X-z).

Thus the rational line passes through -R and rational curve points
P=(x,lambda(x-r)-t), Q=(z,lambda(z-r)-t). Intersection multiplicities
give P+Q=R, also at tangencies or coincident abscissas. Conversely rational
finite P,Q summing to R supply this line and S3=0. Opposite summands cannot
sum to the finite nonzero-ordinate target. This proves rationality here,
without using algebraic-closure equivalence for arbitrary Semaev arity.

An independent root calculation does not require enumerating producer points.
Set h=x-r and c=-rx-2r^2-a. Then

    S3(x,z,r)=A z^2+B z+C,
    A=h^2, B=2hc-4t^2, C=c^2-4t^2(x+r).

Expanding its discriminant gives

    B^2-4AC=16t^2*(t^2-hc+h^2*(x+r))=16t^2*f(x).

Indeed h^2(x+r)=x^3-rx^2-r^2x+r^3 and
-hc=rx^2+r^2x+ax-2r^3-ar, so the bracket is f(x).
If h!=0 and y^2=f(x), its complete root set is

    z=(-B+4ty)/(2h^2), (-B-4ty)/(2h^2).

For y!=0 these are two distinct roots; for y=0 they are the same root once.
For a nonresidue f(x), the discriminant is a nonresidue, so there is no
rational root. The z associated to a particular lift P=(x,y) is

    z=(t+y)^2/h^2-r-x=(-hc+2t^2+2ty)/h^2.

If h=0, A=0 and B=-4t^2!=0, giving exactly one root

    z=C/(4t^2)=(3r^2+a)^2/(4t^2)-2r=x(2R).

At x=r the lifts are P=R and P=-R: P=R has Q=infinity and contributes no
affine solution; P=-R has Q=2R, finite since t!=0. If R has order three,
2R=-R and the retained root is r; it must not be removed as a coincident-x
case. For a general x!=r with f(x)=0, P=-P is its single rational lift;
the quadratic double root is still retained once. Cases Q=-P or inverse
addition are handled by complete group rules; no denominator with zero
ordinate may be inverted. The t=0 or composite-modulus cases lose premises
and are outside this theorem, rather than counterexamples to it.

The line formula determines a unique witness pair for each ordered coordinate
root pair because t!=0. For x!=r the two lift signs yield different z unless
y=0. For x=r only -R yields an affine complement. Thus projecting these
witnesses does not hide a second distinct witness of the same ordered pair
under these premises. Arbitrary noninjective bit maps can have several bit
models per coordinate pair; that multiplicity is a separate output cost.

## 4. Complementary enumeration and certificate design

Enumerate each D1 x in its declared order, compute f(x), classify it, and
extract one square root when it is a square. For f=0 visit P=(x,0) once;
for f nonzero square visit both signs; for a nonsquare visit no point.
For each P compute Q=R-P with complete group arithmetic, discard infinity,
and test x(Q) in D2. Emit an ordered projected coordinate pair and P,Q when
it qualifies. No y-field scan, D1*D2 pair scan, or D2 lift construction is
needed in the operational algorithm. Soundness follows from group arithmetic;
completeness follows either from the rational line correspondence or from
the complete second roots above.

All mode must exhaust D1 and carry exactly one lift-status record per x.
Root records contain checked roots and both signs, with zero once. A
nonroot row can carry either an Euler check f(x)^((p-1)/2)=-1 or the
following shared-nonsquare certificate. Certify 0!=Z and
Z^((p-1)/2)=-1 globally; per nonroot row require 0!=w and w^2=Z*f(x).
In a prime field, taking quadratic characters gives chi(Z)chi(f(x))=1,
so chi(f(x))=-1. Nonzero w excludes f=0. This proof does not follow for
a composite ring, an uncertified Z, or zero w. Producing w requires a
square root of Z*f(x) for EACH nonroot row; the certificate cannot hide
that cost. This certificate can move character-test work between producer
and checker; it is no automatic improvement.

An independent all-mode checker checks exact coverage and distinct canonical
coordinates, root/status certificates and both signs, derives quadratic roots
from the coefficients above (the x=r linear case separately), applies its
own D2 membership, and compares the complete deterministic projected output.
It separately verifies every supplied P,Q is on E, has the declared x values,
and sums to R using independent complete group arithmetic. It must import
no producer enumeration, arithmetic, or membership helpers. Root verification
requires squaring, not a new square-root extraction. All-mode set equality
and duplicate rejection are necessary in addition to witness checks.

First mode may stop on one valid witness and always has completeness=false,
even after an unsuccessful exhaustion. It does not acquire the all-mode
coverage certificate merely by returning an empty list. First-witness
validation must not be billed as complete enumeration, and complete output
must not be required from a successful first-witness query.

Fixed fixture challenges available before code: p=5,a=b=1,R=(0,1) has the
x=r root 4, since x(2R)=1/4=4. A mutation removing that root must fail;
x=1 has f=3 nonsquare, and x=2 has f=1 with both signs. For p=7,a=1,b=0,
R=(1,3), x=0 has f=0, and 2R=(0,0), so zero-root and x=r behavior are
both exercised. These are symbolic fixture checks, not executed trials.
The required p=5,7,13 and second p=7 fixtures test different root branches,
but finite tests alone cannot establish arbitrary-prime correctness.

## 5. Explicit resource expression

Let B_i=|D_i|, n_0,n_+,n_- count zero/square-nonzero/nonsquare radicands in
D1, so B1=n_0+n_++n_- and L=n_0+2n_+<=2B1 rational lifts. Let K be the
number of accepted ordered projected pairs. Then K<=L, and at most
L-1_{r in D1} complements are finite. These are bounds, not assumed yields.
Let M(ell), I(p), E(p), S(p), mu(D2) denote modular multiplication bit
cost, inversion, Euler test, square-root extraction excluding separately
counted setup/character tests, and membership cost; ell=ceil(log2 p).
Fermat exponentiation gives E,I=O(ell*M(ell)); arithmetic is not unit bit cost.

For p=3 mod4, a checked nonzero-square root is v^((p+1)/4), with
O(log p) field multiplications. For general prime p, write p-1=2^v*q,
q odd. Tonelli-Shanks needs a certified nonsquare and setup powers; standard
loop analysis gives an upper bound O(log p+v^2) field multiplications per
root plus setup and any separate Euler test. The loop invariant is that
the residual lies in a 2-power subgroup and each corrective multiplication
strictly reduces its order bound. All returned roots should be squared back.

Nonsquare discovery costs q_Z Euler probes plus generation/validation.
Uniform independent sampling in Fp* gives expected 2 probes since exactly
half the elements are nonsquares; sampling Fp gives 2p/(p-1). A deterministic
scan has no expected-constant guarantee from that argument; a safe trivial
upper bound is O(p) probes. A supplied Z still requires certification. A
p=3 mod4 root shortcut need not find Z, but the shared-nonroot certificate
option may require one anyway. Cold setup and reuse across targets must be
reported separately, and setup failures count.

A transparent all-mode producer expression using per-row Euler and optional
shared nonroot certificates is

    T_prod = T_prime_premise_or_certificate
           + T_domains + T_sqrt_setup + q_Z*E(p)
           + O(B1*M(ell)) + (n_++n_-)*E(p)
           + n_+*S(p)
           + [shared-certificate option: n_-*(S(p)+O(M(ell)))]
           + O(L*(I(p)+M(ell)+mu(D2)))
           + T_root_certificate_and_output_construction(B1,K).

The per-row Euler term can be altered by a separately proved sqrt-ratio
implementation, but not silently omitted. Zero radicands require no Euler
test or extraction. Affine addition needs at most one inversion and O(1)
field operations per nonexceptional lift; duplicated denominators may be
cached as an explicitly described refinement. Complete exceptional rules
remain necessary. No cost here includes extracting an unknown scalar.

Domain setup must charge representation and validation. A modular interval
0<=B<=p can use O(1) descriptor storage, O(B) generation, and membership
((x-h) mod p)<B; an implementation that materializes it uses O(B) words.
Explicit canonical lists require input reading and duplicate rejection;
hash indexing uses expected O(B2) construction/O(1) word lookup with hashing
assumptions and O(B2*ell) bits, or sorted lookup costs O(log B2) comparisons
after sorting. A linear scan costs O(B2) per lookup and would reintroduce a
product bound. These alternatives cannot be conflated. D1 order must be
declared and respected. D2 membership setup is not free even if no solution
is found. Validation and retained ordered lists may materialize both domains.

All-mode certificates use Omega(B1) records, O(B1*ell) bits for ordinary
field-element records; witnesses/projected output add O(K*ell) bits. A
streaming algorithm can lower working memory but cannot erase emitted output.
Deduplication and deterministic order construction must be charged if used;
arbitrary sorting costs O(K log K) comparisons. Input and serialization bit
costs are additional to field operations. Full all-mode output has unavoidable
output writing costs, not an invented solver lower bound beyond that output.

An independent checker has its own domain and instance validation costs,
one global Euler test when shared Z is used, O(B1) status/coverage/root checks,
O(B1*(I(p)+M(ell)+mu(D2))) second-root/membership work, and
O(K*(I(p)+M(ell))) curve/sum/witness checks, plus reading/comparing output.
Euler-only nonroot certificates additionally cost n_-*E(p); shared-w
certificates instead cost O(n_-*M(ell)) after global Z certification. It
uses no additional square-root extractions if the roots/w certificates
verify. Checker domain setup/duplicate detection/storage are separate from
producer setup, even when their asymptotic forms match.

For first mode replace B1 and L by the inspected prefix and visited lifts
for query work, retain the actual setup paid, and retain witness checking.
Worst-case unsuccessful search can still visit all B1 rows; it keeps
completeness=false by contract. No random-domain or success-rate assumption
licenses an expected early stopping improvement here.

## 6. Controls and decision boundary

The bridge rejects each of these overextensions: necessary matrix work from
local inventory (constant-one control); actual solving-degree ordering from
two upper bounds; rational completeness after omitting x=r, one nonzero
sign, or a zero root; a certificate after dropping a D1 record; an expected
constant deterministic nonsquare scan; duplicate coordinate labels without
multiplicity accounting; applying the prime-field theorem to a composite
modulus or t=0; and charging all-mode output as a first-witness obligation.

A future grouped-versus-bit solver comparison needs a fresh admitted protocol,
matched actual instance domains and encoding, common output mode, independent
projected/witness validation, and the complementary reference with setup,
preprocessing reuse, solver work, memory, reconstruction and checking all
counted. Grouped raw-generator regularity is an algebraic premise only;
arbitrary circuit/auxiliary/reduced encodings need their own proof. Even a
measured local improvement would leave relation/scalar extraction, general
unknown-scalar recovery and full ECDLP accounting unresolved. There is no
closure, novelty finding, measured performance inference, formal proof-assistant
verification, or general ECDLP advantage in this derivation.

The pre-code seal has no separate archival custody or independently
authenticated read-order timestamp. The reviewer records an observed clock
and content hash, with a truthful read-order attestation; these do not
mechanically prove the history. Runtime identity also remains as exposed:
canonical agent path /root/costbridge_blind_reviewer, native Codex tools;
requested gpt-6.1-sol/xhigh/fork_turns none is not provider authentication.
