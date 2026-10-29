# Additive structural leads outside the sealed proof

Status: theory-only derivations by root, not independently reviewed. These notes
are outside producer snapshot81957e6eda and must not enter its blind review.
No numerical trial, solver speedup, novelty claim or goal completion is asserted.

## A. Grouped indicator encoding: a larger regularity reduction

This changes the coordinate parameterization instead of adding dense membership
polynomials. It applies to arbitrary Boolean polynomial systems and does not
use a lattice or a special elliptic curve.

For a pair of bits (b0,b1), introduce three variables u1,u2,u3, constrained by

    u_j^2-u_j = 0  (j=1,2,3),
    u1*u2 = u1*u3 = u2*u3 = 0.

The four solutions are the all-zero vector and the three unit vectors. The
bijection is

    b0 = u1+u3,          b1 = u2+u3,
    u1 = b0*(1-b1),      u2 = (1-b0)*b1,      u3=b0*b1.

Thus a two-bit coordinate digit b0+2*b1 becomes u1+2*u2+3*u3, still linear.
For arbitrary nonzero original weights a,b it becomes a*u1+b*u2+(a+b)*u3;
zero resulting weights do not affect the following regularity upper bound.
Replace every two-bit group in each of two s-bit coordinates this way and
substitute the resulting affine coordinates into the same S3 polynomial.
For even s the new generator list has 3s variables, 6s local quadratic
equations, and the S3 quartic. It has a bijection with the original Boolean
solutions, with no membership table or full-domain enumeration.

Its highest-part ideal contains every degree-two monomial supported within
one indicator group, including the squares. A monomial of total degree s+1
in the s groups repeats a group, so it belongs to this ideal. Therefore

    d_reg(F_grouped) <= s+1.

For the raw, unreduced S3 quartic this bound is exact. Write each local top
quotient as A_j=k plus V_j, where V_j has dimension3 in degree1 and all its
products vanish. The quartic top is L1^2*L2^2, where each L_i is the sum of
its group's local coordinate linear forms ell_j. Quotient every A_j further
by ell_j. Each remaining degree1 space has dimension at least2. The global
quartic maps to zero, so A/(L1^2*L2^2) surjects onto the tensor product of
these smaller local rings. Its degree-s component is nonzero. Together with
the upper bound, this proves

    d_reg(F_grouped_raw_S3) = s+1.

Do not assert the same equality after reducing the quartic by local affine
equations or adding other generators: those presentations retain the upper
bound but can have smaller regularity.

For the original two-summand bit encoding the separately derived exact value
is s+ceil((s+2)/2). With even s this means a reduction of at least s/2, while
the variable count increases from 2s to 3s. This comparison uses the same
highest-homogeneous-part definition; it is not merely a quadratic input-degree
claim. The projection/inverse identities prove exact model equivalence.

General w-bit groups use q-1=2^w-1 indicators, all-zero representing digit0.
Use Boolean equations for each indicator and all pairwise products. There are
q(q-1)/2 local quadratics. The bit map is a linear sum of indicators with the
corresponding binary digit set. An inverse is the Boolean assignment indicator
product. For G groups in total, every monomial of degree G+1 repeats a group:

    d_reg(F_grouped) <= G+1.

Partial final groups use their true smaller widths. Hence two s-bit coordinates
give G=2*ceil(s/w), but their variable count must be summed using those actual
group sizes. For fixed w, construction and representation overhead are linear
in s apart from constructing the original substituted constraint. If the quartic
is fully expanded, term growth must also be charged; retain its arithmetic
circuit when evaluating constraints. No auxiliary circuit encoding inherits
this algebraic bound automatically.

The local quotient after taking highest parts has Hilbert series

    product_over_groups (1+(2^w_group-1)*T).

For even s and w=2 this is (1+3T)^s. Its total vector-space dimension is 4^s,
exactly the 2^(2s) assignments represented originally. Lower degree has not
removed combinatorial information. Graded-component widths, matrix rows,
fill-in, bit cost and SAT certificate work can all outweigh the reduction.
This is a candidate for a new controlled implementation, not an end-to-end
advantage.

A concrete SAT interface uses the three pairwise negative clauses per group;
all-zero is permitted, so no at-least-one clause is needed. The same coordinate
and point witnesses must be projected and independently verified. Compare
complete projected model sets, construction, solver, reconstruction and proof
checking on the original fixed fixtures. This is a structural encoding change,
not scaling the earlier two-bit backdoor search.

The mechanism is related to established indicator/one-hot CSP encodings. A
retrieved primary reference is the One-hot subsection of
https://drops.dagstuhl.de/storage/00lipics/lipics-vol374-icalp2026/html/LIPIcs.ICALP.2026.120/LIPIcs.ICALP.2026.120.html .
No novelty conclusion follows from the current search. The regularity proof
above is elementary and self-contained; independent review remains required.

### A precise bridge to one solving-degree convention

Salizzoni, *An upper bound for the solving degree in terms of the degree of
regularity*, arXiv:2304.13485, Definition2.5 and Proposition3.10, retrieved
2026-10-29 from https://arxiv.org/html/2304.13485 , proves

    sd_sigma(F) <= max(d_reg(F)+1, maximum input degree).

Here sd_sigma is the least D for which the full degree-D multiplication-closed
space V_(F,D) contains a Groebner basis for a degree-compatible order. The
paper identifies the algorithm family with mutant-style algorithms. This is
not automatically the largest step degree of any particular F4/F5 software,
a SAT decision degree, or a wall-clock estimate.

For the even-width grouped S3 list above, the input degree is at most4, so

    sd_sigma(F_grouped) <= max(s+2,4) = s+2  for s>=2.

This is a rigorous upper-bound corollary if the grouped-encoding proof passes
review. It is not a proof that the actual solving degree is smaller than the
actual solving degree of the original list; the original could already solve
below both upper bounds. It also does not remove the variable-count or linear
algebra cost. No finite solver trajectory is substituted for the full space.

## B. Three summands with disjoint coordinate domains

Assume an odd-characteristic nonsingular elliptic curve with no nonzero rational
2-torsion, a finite rational target R with R!=-R, and three pairwise disjoint
coordinate domains. Any point with abscissa in F_p has ordinate in F_(p^2).
It is either rational, or Frobenius sends it to its negative.

If three such points sum to R, let U be the sum of their nonrational members,
and A the sum of their rational members. Then A+U=R and A-U=R, hence 2U=O.
Also U=R-A is rational; the 2-torsion hypothesis forces U=O. There cannot be
one nonrational point summing to O. Two nonrational points summing to O have
the same abscissa, excluded by disjoint domains. Three nonrational points
would give R=U=O, excluded. Thus all three points are rational.

By the Semaev zero-set property over the algebraic closure, S4=0 therefore
admits rational lifts on this restricted domain. Flip all signs if necessary
to make their sum R. Exact rational-membership predicates are redundant on
Boolean solutions, and Boolean function-ring ideal equivalence follows as
in the two-summand proof. Pairwise disjointness is a domain premise, not an
extra saturation polynomial or uncharged auxiliary-variable encoding.

The leading part of S4(x1,x2,x3,r), with r fixed and xi scaled together, is
(x1*x2*x3)^4. To derive it, write the defining resultant of
S3(x1,x2,t) and S3(x3,r,t). Scale t=T*u and xi=T*Xi. Their leading terms have
scaling degree4; the second is X3^2*u^2. The resultant in u has leading term
X3^4*(X1^2*X2^2)^2 at degree16. Rescaling the eliminated variable contributes
T^4, leaving degree12 and the asserted product. Its coefficient is nonzero.

For s>=4, p>s, injective affine bit maps with nonzero weights, and nonzero
membership predicates in all three domains, the tensor lemma therefore gives

    d_reg(baseline) = 2*s+ceil((s+4)/2),
    d_reg(augmented) <= 2*(s-1)+ceil((s+4)/2).

This is a proposed two-degree improvement at arity three. Domain disjointness,
nonzero predicates and sufficiently many usable points must all be verified.
It is not an unconditional construction of useful bases of any chosen size.
The higher-arity obstruction returns at four summands, where three nonrational
points can sum to O while the remaining rational point is R. The two-degree
formula is not independently reviewed and must not be promoted with the
separate two-summand verdict.

Primary definition: Kosters and Yeo, Section2 and Proposition2.1,
https://arxiv.org/html/1503.08001 .

## Priority and unresolved obligation

The grouped-indicator encoding is the more useful implementation candidate:
its premises do not require finding special windows and its representation
cost is linear for fixed group width. First independently audit its theorem
and projection map. Then freeze a controlled comparison before changing the
certified implementation or running data. The original requirement remains:
a lower stated invariant is only one step toward a matched general ECDLP
algorithm with setup, solve, reconstruction, verification and memory charged.

## C. Replace a dense membership table by one certified forbidden word

Additional unreviewed corollary, discovered after the grouped lead was frozen
at5c163305b4. It is outside both the current membership proof snapshot and the
future grouped-only review scope; it inherits no review verdict automatically.

For each two-summand coordinate domain, suppose a single Boolean word c_i is
known whose coordinate has nonsquare curve right-hand side. Use the predicate

    D_i(z)= product_(j:c_ij=1) z_ij * product_(j:c_ij=0) (1-z_ij).

It equals1 exactly at this rejected coordinate word and0 everywhere else.
The two-summand rational-lifting theorem shows D_i vanishes on every baseline
solution. The same split Boolean function-ring argument proves equality of
affine ideals after adjoining D_1,D_2. Each highest part is a nonzero scalar
multiple of the full block monomial Omega_i, irrespective of the other table
entries. Therefore the exact tensor Hilbert calculation gives

    d_reg(F_0 union {D_1,D_2}) = d_reg(F_0)-1
                              = s+floor((s+1)/2).

Unlike a complete membership polynomial, these predicates do not need the
whole truth table. Their factored representation has sizeO(s). To retain a
sparse expanded polynomial, flip each bit with c_ij=0; then the rejected word
becomes the all-one word and D_i becomes the single monomial product_j z_ij.
The affine coordinate map updates its offset and signs of weights. This
bijection preserves the exact original coordinate domain, unlike shifting
a fixed interval. Its homogeneous action is diagonal with nonzero signs, so
the original regularity calculation is unchanged.

In SAT, D_i=0 is the single clause forbidding c_i, of length s. A certificate
that the coordinate is invalid consists of the evaluated cubic value and its
Euler-criterion computation; it is checked from the public coordinate/curve
and costsO(log p) field multiplications with ordinary exponentiation. Semantic
redundancy also relies on the separately reviewed rational S3 lift, not on the
residuosity computation alone. No enumeration of the other domain values is
needed to check the clause. Point/witness reconstruction remains charged.

Finding the word is a separate cost. For a fixed domain with an invalid word,
a deterministic search can require up to2^s character tests; no constant-time
bound for arbitrary fixed domains is asserted. For prospective new windows on
an odd-prime-order curve, choose an invalid global coordinate a_bad using the
Hasse-density argument, and set h=a_bad-sum_j weights so the all-one word maps
to it. Expected search is bounded by1/(1/2-1/sqrt(p)) global samples forp>3.
This chooses a new domain and is never presented as an equivalent change to
an existing one. Once a rejected word is known, extra construction isO(s),
with only two clause certificates for the two blocks.

This removes the exponential full-membership-table cost from the particular
one-degree reduction. It does not give the full membership predicate's pruning:
only one coordinate word per block is excluded. The difference between a
strict regularity change and actual solver work is particularly visible here.
It is an attractive cheap certified control arm, not an ECDLP speedup claim.

## D. Why the raw grouped regularity can be independent of the problem

Additional unreviewed algebraic observation, not part of the frozen grouped
review target. This is useful as a warning against treating the new degree
number by itself as an attack result.

Partition any Boolean variable list into G groups, each of width w>=2. Replace
that group's bits by linear projections of q-1=2^w-1 mutually exclusive
indicators as in SectionA, and include all local Boolean/pairwise equations.
Substitute the bit-linear projections into every original nonconstant
polynomial, without reducing the resulting polynomial by the local equations.
Assume there is no nonzero constant generator. Then the leading-form regularity
of this raw generating list is exactly G+1, regardless of the original system.

The upper bound is the same pigeonhole argument. For the lower bound, the
local top quotient is A_j=k plus V_j, with dim(V_j)=2^w-1 and V_j^2=0.
Quotient it further by all w bit-projection linear forms. Their rank is w:
the indicator columns indexed by the unit bit words give an identity matrix.
The remaining degree-one dimension is 2^w-1-w>=1. Linear substitution from
all original bits into the indicators is injective (the same identity columns
give a left inverse), so every nonconstant original polynomial keeps its
original degree and its highest part is the corresponding substituted highest
part. In the further quotient every original bit projection is zero; hence
all these homogeneous parts vanish. The top quotient of the full generating
list therefore surjects onto the tensor product of local rings with nonzero
degree-one spaces. Its degree-G component is nonzero. Thus d_reg=G+1.

This theorem includes inconsistent affine systems with no explicitly constant
generator; it is a statement about a chosen highest-part presentation, not
about hardness or the common affine ideal. A degree-reduced input list, a
constant generator, singleton groups, or a different auxiliary encoding needs
its own analysis. It does not guarantee a strict reduction relative to an
arbitrary original list whose regularity might already be small.

The concrete S3 comparison is informative because its original regularity is
computed exactly, so strict reduction follows there. Broader ECDLP claims
still need the full input-degree, variable/constraint, multiplication-closure,
model reconstruction and resource analysis. This general observation explains
why a regularity number alone cannot settle the user's algorithmic objective.
