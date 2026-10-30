# Grouped indicators for prime-field Boolean polynomial systems

Producer TASK-20261029-e95503. Theory only; independent review pending.
No scientific trials, formal verification, novelty conclusion or runtime result.
This is a separate package from the earlier membership theorem. It finalizes
Section A of next-leads.md under the prospective grouped review contract;
the three-summand and forbidden-word proposals are outside this package.

## 1. Invariant and generating lists

For an explicitly supplied polynomial list F in a standard graded polynomial
ring R over a field k, let F^top contain the highest homogeneous part of each
nonzero listed polynomial. Use

    d_reg(F) = min { d >= 0 : (F^top)_d = R_d }.

This is the convention in Caminata–Gorla, Definition 1.4,
https://arxiv.org/html/2112.05579v2 . It depends on the generator presentation.
An equality of affine ideals, or an isomorphism of affine quotient rings,
does not identify these graded quantities. The zero polynomial is omitted;
a listed nonzero constant gives d_reg=0. Every bound below specifies the
ambient ring and the actual generators whose highest parts are used.

Start with Boolean bits b_j, their equations b_j^2-b_j, and additional
polynomials f_1,...,f_t. Partition the bits into G nonempty groups of actual
widths w_g>=1. For group g let q_g=2^w_g, and introduce u_(g,a) for every
nonzero word a in {0,1}^w_g. There is no indicator for the zero word. Impose

    u_(g,a)^2-u_(g,a) = 0,
    u_(g,a) u_(g,c) = 0       for distinct nonzero a,c.

Let J be the ideal of these local equations. Set

    B_(g,j)(u) = sum_(a:a_j=1) u_(g,a).

The grouped list consists of the local equations and the raw substitutions
f_i(B(u)). The substituted original Boolean equations may be included too;
they are consequences of J and their highest quadratic parts belong to J^top.
No auxiliary circuit variables or normalization equation are included.

## 2. Exact models and quotient-ring isomorphism

Over any field, u^2-u=0 forces u in {0,1}. Pairwise product equations allow
at most one indicator to be 1 in each group. Thus the local models are the
all-zero vector and the q_g-1 unit vectors, in bijection with every bit word.
The all-zero vector represents the zero word. No field characteristic
restriction is needed for this local statement.

The inverse map is the Boolean assignment indicator

    D_(g,a)(b) = product_(j:a_j=1) b_(g,j)
                product_(j:a_j=0) (1-b_(g,j))     (a nonzero).

This is a ring statement as well as a set statement. The local Boolean
quotient is a product of q_g copies of k. In k[u_g]/J_g every polynomial
reduces to a linear combination of 1 and the q_g-1 indicators: repeated
powers reduce, and products of different indicators vanish. Those q_g
classes are independent by evaluation at the zero and unit vectors.
Consequently this quotient also is the function algebra on the q_g states.
The B and D maps induce inverse ring homomorphisms. Tensoring over groups
and adjoining f_i versus f_i(B) gives

    k[b]/( b_j^2-b_j, f_i )  ~=  k[u]/( J, f_i(B) ).

The ideals live in different polynomial rings; they are not claimed equal.
Every grouped model has exactly one original bit model and conversely.
Every coordinate obtained as an affine function of the bits is preserved.
If the original coordinate map is injective, this also preserves distinct
coordinate models; injectivity is not necessary for the bit-level bijection.

For a two-bit group one may order nonzero words as 10,01,11. Then

    b0=u1+u3, b1=u2+u3,
    u1=b0(1-b1), u2=(1-b0)b1, u3=b0*b1.

An original weighted digit alpha*b0+beta*b1 becomes
alpha*u1+beta*u2+(alpha+beta)*u3. Some resulting weights may vanish;
this does not affect the local representation or its degree upper bound.

## 3. Counts and the local highest-part quotient

There are N=sum_g(q_g-1) variables and

    Q=sum_g [ (q_g-1) + binom(q_g-1,2) ]
     =sum_g q_g(q_g-1)/2

local quadratic equations. Both counts use actual widths of shortened groups.
For two s-bit coordinates grouped separately into pairs with even s>=2,
G=s, N=3s, Q=6s. With odd s, G=2*ceil(s/2); the two final one-bit groups
each contribute one variable and one quadratic, not the two-bit counts.

The homogeneous ideal of the listed local highest parts consists of every
degree-two monomial supported in a single group. Hence

    A = k[u]/J^top = tensor_g (k + V_g),
    dim_k V_g=q_g-1, deg V_g=1, V_g^2=0.

Its monomial basis consists of choosing either no variable or one variable
from each group. Thus

    H_A(T)=product_g(1+(q_g-1)T),
    dim_k A=product_g q_g=2^(sum_g w_g).

The degree-G component is nonzero and degree G+1 is zero. This proves
d_reg(local list)=G+1. Adding substituted equations can only shrink this
highest-part quotient, so every full grouped list satisfies

    d_reg(full grouped list) <= G+1.

That statement alone is an upper bound, not an equality for arbitrary added
generators. A constant1 generator, for example, makes it zero. The inequality
also holds if a substituted polynomial is reduced using the affine local
equations before being listed, provided every local equation remains present.
Such reduction need not preserve equality or the same highest-part ideal.

## 4. Prime-field S3 comparison and exact raw grouped value

Let p>max(3,s), s>=2, and work over F_p. Let E:y^2=x^3+a*x+b be nonsingular,
and fix a finite rational target R=(r,t) with t!=0. Use two disjoint s-bit
blocks with affine abscissa maps x_i=h_i+sum_j alpha_(i,j)b_(i,j), all original
weights nonzero. When an injective coordinate domain is intended, require
injectivity separately (the usual power-of-two weights with 2^s<=p suffice).

The original list F0 consists of its 2s Boolean equations and the raw quartic

    S3(x1,x2,r) = (x1-x2)^2*r^2
                 -2*((x1+x2)*(x1*x2+a)+2*b)*r
                 +(x1*x2-a)^2-4*b*(x1+x2).

Its highest part modulo bit squares is L1^2*L2^2, where each L_i is the
weighted sum of its own s variables. This degree-four class is nonzero:
s>=2, p>3, and nonzero weights leave a nonzero product of two squarefree
quadratics. No other term of the raw S3 polynomial has total degree four.

For completeness, the original degree can be derived independently. In each
square-zero s-variable block C, dim C_j=c_j=binom(s,j), with c_j=0 outside
0<=j<=s. Strong Lefschetz for the sum of variables holds in characteristic
zero or p>s by Phuong–Tran, Theorem 2.7,
https://arxiv.org/html/2211.13548 . Scaling variables handles the nonzero
weights. Multiplication by L_i^2 into degree j therefore has rank

    r_j=min(c_(j-2),c_j).

It is surjective precisely for j>=q within 0<=j<=s, where
q=ceil((s+2)/2). This follows from the symmetry and unimodality of binomial
coefficients, retaining their central ties. In bidegree (j,k), multiplication
by L1^2*L2^2 has rank r_j*r_k, because it is the tensor of the block maps.
The quotient component is zero exactly when both block maps are surjective.
Its largest nonzero total degree is (q-1)+s, witnessed at (q-1,s). Thus

    d_reg(F0)=s+ceil((s+2)/2).

Now assume s is even and group each block into pairs. For Fg use all local
indicator equations and the raw substituted S3, without affine reduction.
There are s groups in total, so the preceding upper bound is s+1.
Write the top local algebra as A=tensor_g(k+V_g), dim V_g=3. For each group
let ell_g in V_g be its contribution to the corresponding coordinate L_i.
Form A'=tensor_g(k+V_g/<ell_g>). Every factor has a nonzero degree-one
space (dimension at least two). Both coordinate forms L_i map to zero in A'.
Therefore L1^2*L2^2 maps to zero, and the full highest-part quotient surjects
onto A'. Its degree-s component is nonzero. Combining the two directions,

    d_reg(Fg)=s+1    (even s>=2, raw S3 list).

This lowers this specific invariant by s/2 from d_reg(F0)=1+3s/2, while
increasing the variable count from 2s to 3s. It preserves exact bit models
and the affine quotient through the explicit maps in Section2. It does not
require a membership table, favorable coordinate windows, or curve endomorphisms.
No equality for odd s or an affinely reduced S3 list is asserted here; both
retain the general G+1 upper bound. The exact equality proof just given is
for this raw S3 list, not a new theorem about arbitrary extra generators.

## 5. One precisely qualified solving-degree upper bound

Salizzoni, https://arxiv.org/html/2304.13485 , Definition2.5 and Proposition3.10
(retrieved2026-10-29), uses the smallest degree D for which V_(F,D) contains a
Groebner basis in a degree-compatible term order. V_(F,D) is the full linear
space closed under every multiplication that stays within the degree limit;
new low-degree consequences may themselves be multiplied. The proposition
gives sd_sigma(F)<=max(d_reg(F)+1,max_i deg f_i).

For the explicit even-s raw grouped list, max input degree is four, so

    sd_sigma(Fg) <= max(s+2,4)=s+2  for even s>=2.

The maximum input degree matters at s=2: d_reg=3 but the raw input has degree4.
This corollary addresses the mutant-closure convention in the cited source.
It does not certify the largest degree reached by any chosen F4/F5 software,
a restricted Macaulay window, or a SAT solver. Two upper bounds do not prove
a strict reduction of actual solving degrees. No actual solving-degree,
first/last-fall-degree comparison or runtime measurement is supplied here.

## 6. Construction, costs and known-false controls

For fixed group width, local domain construction has linear size in the
number of original bits. If width grows, q_g-1 and q_g(q_g-1)/2 must be charged;
encoding a whole coordinate in a single group is exponential. All-zero
represents digit0. Adding an at-least-one constraint without a zero indicator
would lose a valid original word. Omitting pairwise products would permit
simultaneous indicators and destroy both the bijection and the graded proof.

The coordinate linear forms can be assembled and evaluated in O(N) field
operations. Fully expanding the quartic can require O(N^4) terms; it is not
part of an unqualified linear-cost claim. Keeping an arithmetic circuit
avoids that expansion during evaluation, but adding circuit variables makes
a different polynomial presentation that needs its own graded analysis.

For pair groups, H_A(T)=(1+3T)^s and dim A=4^s, equal to the original
2^(2s) bit assignments. Degree has been redistributed into wider graded
components. Elimination rows, fill-in, memory, field bit costs and all witness
reconstruction/certificate checking remain real costs. The quotient used for
the lower-bound witness is a homogeneous proof device, not a scalar extractor.

In a Boolean SAT representation the local domain uses three pairwise negative
clauses per pair group; Booleanity is native to SAT. The field-polynomial
representation instead lists the six local quadratics per group. These are
different representations with the same local models. Any future SAT test
must verify complete projected models and separately charge construction,
search, witness reconstruction and certificate checking. The present package
does not implement or benchmark that comparison.

Additional controls: small characteristic or zero original bit weights lose
the stated original-baseline argument even though the indicator upper bound
remains sound; arbitrary circuit variables do not inherit it; and a nonzero
constant generator invalidates any claimed nonzero full-quotient witness.

This establishes a candidate generator-presentation regularity reduction and
a source-qualified upper bound, pending independent rederivation. Neither
novelty nor an end-to-end general prime-field ECDLP speedup is established.
The broader research goal remains active.
