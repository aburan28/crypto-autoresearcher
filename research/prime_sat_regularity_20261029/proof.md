# A strict leading-form regularity reduction for two-summand prime-field systems

Status: derived proof, submitted for independent adversarial review. This is
a theorem about the degree of regularity of specified polynomial generators.
It is not a solving-degree theorem, a running-time claim, a novelty claim,
or a general ECDLP algorithm. The full thread goal remains active.

Question: can the membership augmentation already implemented in
`research/prime_sat_followup_20261029/encoding.py` reduce an actual algebraic
regularity invariant, even though its measured algebraic work increased?
This note supplies a candidate all-parameter answer with explicit premises.
It changes no previous protocol, source, measurement or failed receipt.

## 1. Definitions and retrieved ingredients

For a finite generator list F in the standard graded polynomial ring R over
k, write F^top for its highest homogeneous parts. We use

    d_reg(F) = min { d >= 0 : (F^top)_d = R_d }.

This is Definition 1.4 of Caminata and Gorla, *Solving degree, last fall
degree, and related invariants*, arXiv:2112.05579v2, retrieved 2026-10-29:
https://arxiv.org/html/2112.05579v2 . The leading-form ideal here is Artinian
because it contains the squares of all variables. Thus d_reg is one plus
the last nonzero degree of its quotient, unless that quotient is zero.
It is not the regularity of the affine ideal viewed without its generators,
nor automatically the regularity of its homogenization or its solving degree.

The external algebraic input is Theorem 2.7 of Ho V. N. Phuong and Quang Hoa
Tran, *A new proof of Stanley's theorem on the strong Lefschetz property*,
arXiv:2211.13548, retrieved 2026-10-29:
https://arxiv.org/pdf/2211.13548 . For

    B_s = k[z_1,...,z_s] / (z_1^2,...,z_s^2),

characteristic zero or characteristic p > s, multiplication by a power of
L=z_1+...+z_s has maximal rank in every degree. A diagonal variable scaling
gives the same result for L=sum a_i z_i with every a_i nonzero. This scaling
is used in the homogeneous square-zero ring only; it is not asserted to
preserve the affine equations z_i^2-z_i.

Kosters and Yeo, *Notes on summation polynomials*, Proposition 2.1 and the
explicit S_3 formula, retrieved 2026-10-29:
https://arxiv.org/html/1503.08001 . Their general equivalence is over the
algebraic closure. Rationality for the present two-summand case is proved
below, not inferred from that general proposition.

Novelty remains unverified. These ingredients are established prior work;
the particular application below needs a wider prior-art audit before any
novelty statement. The knowledge-search MCP is unavailable in this session;
repository source search and primary papers were used instead.

## 2. A tensor-product calculation

Let m>=2, 1<=e<=s, and char(k)=0 or p>s. Form m disjoint copies B_i of B_s,
with nonzero-coefficient linear forms L_i. Let

    B = tensor_i B_i,       f = product_i L_i^e,
    c_j = binomial(s,j),    r_j = min(c_{j-e}, c_j),

where c_j=0 outside 0<=j<=s. In target multidegree (j_1,...,j_m), the image
of multiplication by f is the tensor product of the m multiplication images.
Its rank is product_i r_{j_i}; the ambient dimension is product_i c_{j_i}.
Consequently the exact ordinary Hilbert series is

    H_(B/(f))(T) = (1+T)^(m*s) - (sum_(j=0)^s r_j T^j)^m.       (1)

For 0<=j<=s, the one-block map is onto exactly when

    j >= q := ceil((s+e)/2).

Indeed maximal rank reduces this to c_{j-e}>=c_j; symmetry and strict
unimodality of the binomial coefficients give precisely that threshold.
For j<e the source is zero, consistently with the same criterion.

Put t=q-1. A multigraded quotient component is nonzero exactly when at
least one j_i<=t. Its maximum total degree is therefore

    D = (m-1)*s + t,

attained at (t,s,...,s). This proves the exact regularity of the polynomial
generator system whose top ideal is (all variable squares, f):

    d_reg = (m-1)*s + ceil((s+e)/2).                            (2)

This argument computes full homogeneous components, not a restricted
Macaulay window or a degree observed in a bounded solver.

## 3. Nonzero block predicates remove the block's top monomial

Let h_i be any nonzero homogeneous squarefree polynomial in block i, of
degree d_i between 1 and s. Choose a support monomial z_S with coefficient
a_S != 0. In B_i,

    h_i * z_(complement S) = a_S * Omega_i,
    Omega_i = product_(j=1)^s z_(i,j).                         (3)

Every different support monomial of the same degree repeats at least one
variable in complement S and hence vanishes modulo the squares. Thus
Omega_i belongs to (h_i) in B_i. A nonzero constant predicate instead
makes the whole quotient zero and needs no argument.

It follows that B/(f,h_1,...,h_m) is a quotient of

    Q = B/(f,Omega_1,...,Omega_m).

In Q each block degree is at most s-1. Multiplication ranks in these retained
block degrees are unchanged, since their source degrees j-e are also below s.
Therefore

    H_Q(T) = ((1+T)^s-T^s)^m
             - (sum_(j=0)^s r_j T^j-T^s)^m.                   (4)

Because e<=s, t<=s-1. The last nonzero degree of Q is
(m-1)*(s-1)+t, attained at (t,s-1,...,s-1). Hence adding a nonzero
block-local predicate in every block gives

    d_reg(augmented) <= (m-1)*(s-1)+ceil((s+e)/2)
                      = d_reg(baseline) - (m-1).              (5)

If every h_i is a nonzero multiple of Omega_i, equality holds in (5).
For other predicates it is an upper bound; no exact augmented value is
asserted without computing the remaining homogeneous ideal.

## 4. Application to two-summand point decomposition

Assume p>3 is prime, E/F_p is nonsingular and given by

    y^2 = x^3 + a*x + b,

and R=(r,v) is a rational target with v!=0. Let s>=2, 2^s<=p. Each of the
two coordinate domains is given by an injective affine bit map

    x_i = h_i + sum_(j=0)^(s-1) a_(i,j) z_(i,j),
    z_(i,j) in {0,1},   a_(i,j)!=0.

Ordinary interval windows use a_(i,j)=2^j; modular wrap does not impair
injectivity when 2^s<=p. Equal coordinate values between the two summands
are allowed. The variables in different blocks are distinct.

Let F_0 consist of the 2s Boolean equations z^2-z and the S_3 quartic
S_3(x_1,x_2,r). Its highest degree-four part, modulo the variable squares,
is L_1^2 L_2^2. No other term has total degree four in the bit variables.
The same statement holds if the quartic is first reduced modulo z^2-z:
terms with repeated variables drop degree, and the degree-four part differs
from L_1^2 L_2^2 only by elements of the square ideal. Since s>=2 and p>3,
this degree-four part is nonzero. Also 2^s<=p implies p>s.

Equation (2), with m=2 and e=2, gives the exact baseline value

    d_reg(F_0) = s + ceil((s+2)/2)
               = 1+s+floor((s+1)/2).                         (6)

For each block construct the unique multilinear polynomial M_i whose
Boolean values are 1 when x_i^3+a*x_i+b is a nonzero nonsquare, and 0
otherwise. Assume each domain contains at least one rejected coordinate,
so M_i!=0. Let F_1=F_0 union {M_1,M_2}. Applying (3)-(5) to the highest
nonzero homogeneous parts of M_i proves

    d_reg(F_1) <= s+floor((s+1)/2) = d_reg(F_0)-1.              (7)

If M_i=1 in either block, F_1 contains 1 and d_reg(F_1)=0; (7) still holds.
If either M_i is identically zero, this strict-reduction theorem is not
applicable. Such an input is reported explicitly, not silently shifted.

## 5. The augmentation preserves the actual solutions and affine ideal

Define

    N = x_1*x_2-r*(x_1+x_2)-2*r^2-a.

The polynomial identity

    S_3(x_1,x_2,r) = N^2-4*v^2*(x_1+x_2+r)                  (8)

uses v^2=r^3+a*r+b. On S_3=0 set lambda=N/(2v). Then
lambda^2=x_1+x_2+r and

    x^3+a*x+b - (lambda*(x-r)-v)^2
       = (x-r)*(x-x_1)*(x-x_2).                             (9)

Thus P_i=(x_i,lambda*(x_i-r)-v) are rational curve points. The line contains
P_1,P_2,-R with intersection multiplicities, so P_1+P_2=R. This includes
tangent and coincident-x cases; v!=0 is essential. Conversely, rational
points summing to R give S_3=0. Therefore every Boolean solution of F_0
already satisfies M_1=M_2=0, and F_0,F_1 have exactly the same solutions.

There is also equality of the affine ideals. The Boolean quotient
F_p[z]/(z^2-z for all z) is the product of copies of F_p indexed by Boolean
assignments. In this ring a polynomial lies in (S_3) exactly when it vanishes
on the zero set of S_3. More explicitly, for each M_i,

    M_i = M_i*S_3^(p-1) = (M_i*S_3^(p-2))*S_3.              (10)

At a nonzero S_3 evaluation this is Fermat's identity; at a zero evaluation
both sides vanish. Equality of evaluations is equality in the Boolean
quotient. This proves ideal equality, without claiming the displayed
high-degree multiplier is a cheap certificate for a solver.

The degree-of-regularity change is therefore a change in the leading-form
ideal of an equivalent generator presentation. It does not lower an
invariant attached only to the common affine ideal.

## 6. Applicability and charged construction

For a fixed domain, test the explicit nonzero-predicate premise. If it fails,
the domain is not changed under the guise of an equivalent transformation.
For a newly selected base on a curve whose rational group has odd prime
order, there is a simple way to ensure it. There are no rational points of
order two. If N_E=#E(F_p), the number U of x with nonsquare right-hand side is

    U = p-(N_E-1)/2 >= p/2-sqrt(p) > 0,

using Hasse's bound and p>3. The bound is Theorem 7.3 of Andrew Sutherland's
MIT 18.783 Lecture 7 notes (2023), retrieved 2026-10-29:
https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf . Sampling an x until one is rejected has expected
at most 1/(1/2-1/sqrt(p)) field samples. Use that x as a window's offset h;
the zero bit string then guarantees M(0)=1. This is a prospective base
construction, not a repair of the fixed-input premise. A rejected-only window
has no useful relation and must not be treated as a useful ECDLP factor base.

Building M_i evaluates 2^s quadratic-character tests and performs an
O(s*2^s) multilinear interpolation transform. With ordinary exponentiation,
the character tests take O(2^s*log p) field multiplications; storage is
O(2^s) coefficients per distinct domain. Identical domains can share a table.
This is exponential in the digit width s, and must be charged. The proof
neither changes relation yield nor establishes that added polynomials make
a practical solver faster. The PNEXT observations in fact record greater
algebraic search work for membership augmentation on the retained fixtures.

## 7. Limits, controls and the next proof obligation

- Equations (6)-(7) are about the exact leading-form d_reg convention in
  Section 1. They are not bounds on last fall degree or observed SAT degree.
- The symbolic family is not a finite-sample extrapolation. Its external
  input is the cited Lefschetz theorem under p>s; that hypothesis is not
  dropped in small characteristic.
- Two-summand rationality is essential to the equivalence proof. For more
  summands, nonrational points over a quadratic extension can cancel among
  themselves. The tensor lemma alone does not justify adding rational-point
  predicates to an arbitrary Semaev system without changing its solutions.
- The reduction is at least one degree at arity two; it leaves the same
  linear growth in s. No improved complexity exponent follows.
- No claim that this transformation is new is made. No native run is
  relaunched, no new numerical experiment is claimed, and no official
  hypothesis status is changed by this note.
- The next substantive obligation is a larger-arity presentation with
  proved rational model equivalence, a strict regularity bound in a fixed
  convention, and charged construction/yield/solution extraction. That
  remains part of the original broad objective, not a replaced objective.
