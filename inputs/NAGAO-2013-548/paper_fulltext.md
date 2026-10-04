<!--
Extracted from inputs/NAGAO-2013-548/eprint-2013-548.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao. NOT hand-cleaned; arrow accents and displayed formulas break across lines
as the extractor produced them.

WHY THIS PAPER IS FROZEN, AND THE ONE QUESTION IT IS FROZEN TO ANSWER. Section 7
of Nagao 2015/984 opens by crediting the DISJOINT (coset) factor base to this
paper -- its reference [10] -- and says Galbraith and Gebregiyorgis ePrint
2014/806 "recently re-discovered" it. This program's own mechanism-lane
hypothesis H-SEMBIN-c59e50 was built on 2014/806, so the priority sentence bears
directly on what that lane may claim as new. IDEA-20260913-352163 recorded the
priority question as NOT settled by 2015/984 asserting it, and left the pointer
unread. This freeze is the step that lets an agent check the sentence against the
cited text rather than against the citing author's summary of it.

Read the priority question against what this paper is actually about: its own
title and abstract are a decomposition formula for the Jacobian group of a plane
curve, and its revision note records that Proposition 3 of the first version "is
not true and this technique can not be used", forcing Section 4 to be rewritten.
Whether a disjoint/coset factor base for the elliptic case appears here at all,
and if so where, is the reading task -- not something this header decides.

Landing-page metadata, transcribed 2026-09-13 (see provenance.json):
  title      Decomposition formula of the Jacobian group of plane curve
  category   Foundations;  Publication info: Preprint. MINOR revision.
  keywords   Decomposition Attack, ECDLP
  history    2013-12-13: last of 3 revisions;  2013-09-04: received
  licence    CC BY;  short URL https://ia.cr/2013/548

The served PDF is the LAST of three revisions, so it is not necessarily the text
2015/984 read in 2015; the versions ePrint retains are listed on the landing page
and none of the earlier ones is frozen here.
-->

Decomposition formula of the Jacobian group of plane
curve (Draft)

Koh-ichi Nagao (nagao@kanto-gakuin.ac.jp)

Fac. of Engineering, Kanto Gakuin Univ.,

Joint-work with Kazuto Matsuo(Kanagawa Univ.,) and Tsuyoshi Takagi(Kyushu Univ.))

Abstract. In this article, we give an algorithm for decomposing given element of
Jacobian gruop into the sum of the decomposed factor, which consists of certain subset
of the points of curve.

Keywords Decomposition Attack, ECDLP
revise 6 Nov First version of this manuscript, we use Weil descent like techinique and
the decomposition problem of Jacobian reduces to solving exact g number equations system.
However, Proposition 3 is not true and this thechnique can not be used. So, we re-write §4 and
show that the decomposition problem of Jacobian reduces to solving some equations system
(however, the number of the equations is quite large).

1 Introduction

In this article, we give an algorithm for decomposing given element of Jacobian gruop into the
sum of the decomposed factor, which consists of the points of curve. This is the generalization
of the Semaev’s formula [9] and by leading this formuls, we use the Riemann-Roch space
technique similar as [6]. Recently, French researchers [3], [8], propose the algorithm for solving
ECDLP over binary extension ﬁeld by subexponential complexities of extension degree n.
This algorithm uses the fact that the system of the equations obtained by decomposing given
element of elliptic curve into decomposed fatcor contains many hidden equations and the
complexity for decomposing a point of elliptic curve into d = nc (0 < c < 1/2 is a constant 1 )
elements of decomposed factor, is subexponential. These arguments seems to have some gaps,
but, any way, there is some posibility that ECDLP is subexponential. By using thier argument
to the Jacobian of plane curve, we similarly get that the DLP of the Jacobian of plane curve
of small genus over binaly extension ﬁeld /or its generalization to small characterristic ﬁeld
also subexponential.

2 Notations

In this article, let C : f (x, y) = 0 be a plane curve of small genus g over Fpn, ∞ be a ﬁxed
point at inﬁnity, D0 = Q1 + Q2 + ... + Qg − g∞ be a ﬁxed element of Jac(C/Fpn). We also
put dy := degy f (x, y) and φ1(x) :=

i=1 x − x(Qi).

(cid:81)g

3 Riemann-Roch Space

Proposition 1 (Riemann-Roch). Let D be a divisor such that deg D ≥ 2g − 1. Then
dimL(D) = deg D − g + 1.

Let d be an integer such that d > 2g − 1. Put D := d∞ − D0 = (d + g)∞ − Q1 − Q2 − ... − Qg.
Then form Riemann-Roch theorem(Proposition 1), there are independent elements of function
ﬁeld fi(x, y) ∈ Fpn(C) (i = 0, 1, .., d − g) such that fi(x, y) = 0 at all Q1, .., Qg, fi(x, y) does

1 Taking d = O(n1/3) is best possible for the complexity

not has a pole except ∞, ord∞fi(x, y) < −d−g for i = 1, 2, .., d−g and ord∞f0(x, y) = −d−g.
Moreover, form Riemann-Roch Theorem, the element h(x, y) of function ﬁeld Fpn(C) such
that h(x, y) = 0 at all Q1, .., Qg, h(x, y) does not has a pole except ∞, and ord∞h(x, y) =
−d − g, is written by h(x, y) = f0(x, y) + a1f1(x, y) + .... + ad−gfd−g(x, y) (ai ∈ Fpn) up to
constant multiplication.

Let us denote

H(x, y) := f0(x, y) + A1f1(x, y) + .... + Ad−gfd−g(x, y)

where Ai are variables and let S(x) := resultanty(f (x, y), H(x, y)).

Lemma 1. 1. degx S(x) = d + g.
2. φ1(x) | S(x)
3. Put g(x) := S(x)/φ1(x) and we have degx g(x) = d.
4. Put Ci be the i-th coeﬃcients of g(x) (i.e. g(x) =
polynomial of A1, ..., Ad−g with total degree ≤ dy.

4 System of equations

From the discussion of §3, we have the following lemma;

(cid:80)d

i=0 Cixi). Then we have Ci is a

(cid:81)d

Lemma 2. Let Pi = (xi, yi) ∈ C(Fp) (i = 1, 2, .., d) and Put si by the xi coeﬃcient of
the polynomial
i=1(x − xi). When D0 + P1 + ... + Pd − d∞ ∼ 0, there are some ai ∈ Fp
(i = 1, 2, .., d − g) satisfying the following:
1. h(x, y) = Constant × H(x, y)|Ai=ai,
2. si · Cd|Ai=ai = Ci|Ai=ai (i = 0, 1, .., d − 1).

Further let Xi (i = 1, .., d) be variables and put Si = Si(X1, .., Xd) ∈ Fpn [X1, .., Xd] by

xi-th coeﬃcient of

i=1(X − Xi). Put

(cid:81)d

gi(A1, .., Ad−g; X1, .., Xd) := Si(X1, .., Xd)Cd(A1, .., Ad−g)−Ci(A1, .., Ad−g),

(i = 0, .., d−1)

and consider the equation system

EQS1 : {gi(A1, .., Ad−g; X1, .., Xd) = 0|i = 0, .., d − 1}.

Lemma 3. When EQS1 has a solution (a1, ..ad−g; x1, .., xd) ∈ A2d−g(Fp), there are some
Pi ∈ C(Fp) (i = 1, .., d) such that D0 + P1 + ... + Pd − d∞ ∼ 0 and x(Pi) = xi (i = 1, .., d).

i=1 aifi(x, y), and let Pi’s be the points on C(Fp) which
Proof. Put h(x, y) = f0(x, y) +
meet h(x, y) = 0 except Q1, .., Qg. So, we have {x(Pi)|i = 1, .., d} = {x1, .., xd} and ﬁnish the
proof.

(cid:80)d−g

From Lemma 2, and Lemma 3, we have the following;

Proposition 2. The following (1) (2) are equivalent;
1) EQS1 has solution (a1, .., ad−g; x1, .., xd) ∈ A2d−g(Fp)
2) There are some Pi ∈ C(Fp) (i = 1, .., d) satisfying x(Pi) = xi (i = 1, .., d) and D0 + P1 +
... + Pd ∼ 0.

Let T1, ..., Tg be new variables and put

hi(A1, .., Ad−g; X1, .., Xd; T1, .., Tg) := gi(A1, .., Ad−g; X1, .., Xd),
hd−g(A1, .., Ad−g; X1, .., Xd; T1, .., Tg) :=
sider the equation system

(cid:80)g

i=1 Ti · gi+d−g−1(A1, .., Ad−g; X1, .., Xd), and con-

(i = 0, .., d − g − 1),

EQS2 : {hi(A1, .., Ad−g; X1, .., Xd; T1, .., Tg) = 0|i = 0, .., d − g}.

5 Absolute resultant

and from Stirling formula, which

In this section, we study the absolute resultant of EQS2 (cf [1] §3). Here, we consider {Ai}
as variables and {Xi} ∪ {Ti} as constants and eliminate {Ai} from EQS2. For the precise
discussion, we must use the homogenious polynomial system. However, it is complicated and
we continue the discussion using non-homogenious polynomial system.

Let Di := deg{Xi} hi(≤ dy) (i = 0, .., d − g) and D =

i=0 Di − (d − g)(≤ (d − g)dy). Let
Mall be the set of monomials ofA1, .., Ad−g of degree ≤ D. The number of such momomial

(cid:80)d−g

(cid:182)

#Mall is estimated by

states N ! ∼

√

(cid:179)

d − g + D
d − g

(cid:180)

(cid:181)

≤

(d − g)(dy − 1)
d − g

(cid:113)

2πN N N exp(−N ), we have #Mall ≤

dy+1
2π(d−g)dy

{ (dy+1)dy +1

dy
y

d

}d−g. Let

S0 := {m ∈ Mall | deg{Ai} m ≤ D − D0},
S1 := {m ∈ Mall | deg{Ai} m > D − D0, AD1
S2 := {m ∈ Mall | deg{Ai} m > D − D0, AD1

1

1 |m},

(cid:54) |m, AD2

2 |m},

· · · · · ·

Sd−g := {m ∈ Mall | deg{Ai} m > D − D0, AD1
Note that it is well known that #Sd−g = D0D1...Dd−g−1 and Mall = ∪d−g
of Mall).

(cid:54) |m, · · · , ADd−g−1

d−g−1 (cid:54) |m, ADd−g

1

d−g |m},

i=0 Si (disjoint division

Put Mall = {

−→
M 1, ...,

−→
M #Mall} and ∪d−g

i=0 {him | m ∈ Si} = {G1, ..., G#Mall }. Let Gij ∈

Fp[{Xi} ∪ {Ti}] be the polymomials such that Gi =

(cid:80)#Mall

j=1 Gij

−→
M j and

Res(X1, .., Xd; T1, .., Tg) = determinant of the matrix[Gij]1≤i,j≤#Mall ∈ Fp[{Xi} ∪ {Ti}].

Res is known as absolute resultant and we have the following; 2

Lemma 4. Let (x1, ..., xd) ∈ Ad(Fp). The follwoing (1) (2) are (essentially) equivalent;
1) Res(x1, .., xd; T1, .., Tg) = 0 (Ti’s are still variables).
2) There are some (a1, ..., ad−g) ∈ Ad−g(Fp) satisfying (a1, .., ad−g; x1, .., xg) is a solution of
EQS1.

Lemma 5. 1) deg{Ti} Res(X1, .., Xd; T1, .., Tg) ≤ dd−g
.
(cid:113)

y

2) deg{Xi} Res(X1, .., Xd; T1, .., Tg) ≤ d · #Mall ≤ d ·

dy+1
2π(d−g)dy

{ (dy+1)dy +1

dy
y

d

}d−g.

Proof. The number of the row that Ti appears equals to #Sd−g = D0D1...Dd−g−1 ≤ dd−g
and the degree of {Ti} of each element of the the matrix is 1. So, we have 1). The degree of
{Xi} of each element of the the matrix is ≤ d and the size of the matrix is #Mall. So, we
have 2).

y

Let {m1, ..., mN } be the set of monomial of {T1, .., Tg} which divide some monomial of

Res(X1, .., Xd; T1, .., Tg) and put
Res(X1, .., Xd; T1, .., Tg) =

(cid:80)N

(cid:181)

dd−g

y

and N =

deg{Ti} Res + g
g

i=1 Hi(X1, .., Xd) · mi. From Lemma 5, we have deg{Ti} Res ≤

(cid:182)

≤

(dd−g

y +g)g

g!

(cid:113)

. From Lemma 5,

we also have deg{Xi} Hi(X1, .., Xd) ≤ d

dy+1
2π(d−g)dy

{ (dy+1)dy +1

dy
y

d

}d−g (i = 1, .., N ).

From Lemma 4 and Proposition 2, we have the following;

Proposition 3. Let (x1, ..., xd) ∈ Ad(Fp). The follwoing (1) (2) are (essentially) equivalent;
1) Hi(x1, .., xd) = 0 (i = 1, .., N ).
2) There are some Pi ∈ C(Fp) (i = 1, .., d) satisfying x(Pi) = xi (i = 1, .., d) and D0 + P1 +
... + Pd ∼ 0.

2 We do not use homogenious polynomial system and projective variety. So, there is some gap.

However, it seems to negligible and continue the discussion.

Thus, the decomposition problem of Jacobian of a plane curve reduced to solve some the
equations system.

6 Hyper elliptic curve case

In this section, we consider the hyper elliptic curve case. Let C : f (x, y) = y2 + b(cid:48)
1xy + .. −
x2g+1 − b2gx2g − ... − a0 = 0 be a hyper elliptic curve of small genus g over Fpn, ∞ be a unique
point at inﬁnity, D0 = Q1+Q2+...+Qg−g∞ be a ﬁxed element of Jac(C/Fpn). From Munford
representation, D0 is also represented by using two polynomials φ1(x) :=
i=1 x − x(Qi) and
φ2(x) which has the properties deg φ2(x) ≤ g − 1 and y(Qi) = φ2(x(Qi)).

(cid:81)g

Let d be an integer such that d > 2g−1. Put D := d∞−D0 = (d+g)∞−Q1 −Q2 −...−Qg.

Then form Riemann-Roch theorem(Proposition 1), the base of the vector space
L(D) := {h ∈ C(Fpn)|h has zero at all Q1, .., Qg and has pole only at ∞, ord∞h ≤ −d − g}
is written by

{φ1(x), φ1(x)x, ..., φ1(x)xM1, (y − φ2(x)), (y − φ2(x))x, ..., (y − φ2(x))xM 2

}

where M1 = (cid:98)(d−g)/2(cid:99) and M2 = (cid:98)(d−g −1)/2(cid:99). Note that when 2|(d−g), ord∞φ1(x)xM1 =
g + d and when 2 (cid:54) |(d − g), ord∞(y − φ2(x))xM2 = g + d.

So put f0(x, y) :=

(cid:189)

φ1(x)xM1
(y − φ2(x))xM2

2|(d − g)
2 (cid:54) |(d − g)

and putfi(x, y) (1 ≤ i ≤ d − g) by other

bases of L(D) and exceeds the simailar argument of Section 2. Let us denote

H(x, y) := f0(x, y) + A1f1(x, y) + .... + Anfn(x, y)

where Ai are variables and let S(x) := ±resultanty(f (x, y), H(x, y)).

Lemma 6. 1. S(x) is monic polynomial of x and degx S(x) = d + g.
2. φ1(x) | S(x)
3. Put g(x) := S(x)/φ1(x). g(x) is a monic polynomial of x and degx g(x) = d.
4. Put Ci be the i-th coeﬃcients of g(x) (i.e. g(x) = xd +
polynomial of A1, ..., Ad−g with total degree 2. (Note that Cd = 1 form g(x) being monic.)

i=0 Cixi). Then we have Ci is a

(cid:80)d−1

Similarly let Xi (i = 1, 2, .., d) be variables and put Si = Si(X1, .., Xd) by the X i coeﬃcient
of the polynomial

(cid:81)d

i=1(X − Xi).

Consider the system of the equations

EQS3 : {Si(X1, ..., Xd) = Ci(A1, .., Ad−g) |

i = 0, 1, .., d − 1}

(1)

Proposition 4. Let (x1, .., xd) ∈ Ad(Fp). The condition that there are some Pi = (xi, yi)
(i = 1, 2, .., d) such that D0 + P1 + ... + Pd − d∞ ∼ 0 and x(Pi) = xi (i = 1, .., d) is equivalent
to the condition that the equations system EQS3 of the variables{Ai} and {Xi} has some
solution satisfying Xi = xi.

Note that the variables {Ai} can be eliminated by the technique of previous section.

7 Decomposed factor

In 2009, Diem [2] proposes the way of taking decomposed factor, called Diem-variant, and
shows ECDLP of elliptic curves over Fpn satisfying log p = O(n2) has subexponential complex-
ity when input size n log p goes to inﬁnity. In 2005 or 2006, soon after the Semaev’s formula is
discoverd, Matsuo also found the simmilar and more general way of taking decomposed factor
(for exapmle distinct or non-equal size decomposed factor). Matsuo tries to decompose an
element of elliptic curve over around 120-bit size binary ﬁeld, but, huge memory workstation

does not returns the reply and it it not presented and only the researchers around him knows
this.

Here, we propose the way of taking decomposed factor of Jacobian of the curve, which is
the generalization of Matsuo’s decomposed factor. Fix [w1, ..., wn] be the base of Fpn/Fp. Let
n1, ..nd be the positive integers satisfying n1 + ... + nd ≈ ng. Put

B(cid:48)

i := {

nj(cid:88)

j=1

xi,jwj|xi,j ∈ Fp}

(i = 1, 2, ..., d).

Let r1, ..., rd be elements of Fpn

3 and take decomposed factor Bi by

Bi := {P −∞ ∈ Jac(C/Fpn)|P ∈ C(Fpn), ∃x ∈ B(cid:48)

i such that x(P ) = x+ri}

(i = 1, 2, ..., d),

and consider the decomposition (of D0)

D0 +

d(cid:88)

i=1

(Pi − ∞) = 0

(Pi − ∞) ∈ Bi

in Jacobian group.

Note that Bi’s are essentially disjoint, |Bi| ≈ pni, and the probability that the decompo-
sition success is O(pn1+...+nd−ng) ≈ 1. From the disjointness, it is improved that the term of
1/d! in the probability is omitted. (Remark that it is needed to compute gaussian elimination
of d-times size matrix in the last step.)

So, we have the following proposition, which is a generalization of Diem’s result:

Proposition 5. DLP of the Jacobian group of a plane curve of small genus g over extension
ﬁeld Fpn satisfying log p = O((ng)2) (since g is constant, it is equivalent to log p = O(n2))
has subexponential complexity when input size N = ng log p goes to inﬁnity. .

(cid:80)ng

Proof. We consider the case d = ng, n1 = n2 = ... = nd = 1 and compute the decomposi-
i=1(Pi − ∞) such
tion of given divissor D0. In this case, D0 is decomposed by the divisor
that x(Pi) = (xi,1w1 + ri) with xi,1 ∈ Fp. From Proposition ??, in order to ﬁnd such {xi,1},
it it suﬃcient to solve the 2ng equations Fj,k ∈ Fp[{xi,1}] obtained by Weil descent from
Fj(x1,1w1 + r1, ..., xng,1w1 + rng) = 0 (j = 1, 2, ..., g). (Note that put Fj,k be the polymo-
). From
nials obtained by Fj(x1,1w1 + r1, ..., xng,1w1 + rng) =
1 = Constng
Proposition ??,the degree of the equations obtained by Weil descent is ≤ Constd
1 .
So the upper bound of the cost of ﬁnding the value of {xi,1} by using Gr¨obner basis is es-
timated by (Constng
1 )ng×Const2 = exp(Const3 n2g2) = exp(N 2/3+o(1)). In order to solve the
DLP, we must have obtain dp = ngp decomposition and compute the Gaussian elimination
of the dp = ngp size matrix. Since ngp = exp(log(ng) + log p) = exp(N 2/3+o(1)), we also have
both of the costs of ngp decomposition and Gaussian elimination are exp(N 2/3+o(1)).

k=1 Fj,k(x1,1, ..., xng,1)wk

(cid:80)n

References

1. D. Cox, J.Little, D. O’Shea, Using Algebraic Geometry, Springer, 1997.
2. C. Diem, On the discrete logarithm problem in class groups II, preprint, 2011.
3. J-C. Faug´ere, L. Perret, C. Petit, and G. Renault, Improving the complexity of index calculus
algorithms in elliptic curves over binary ﬁelds, EUROCRYPTO 2012, LNCS 7237, pp.27-44.

4. F.S. Macaulay, The algebraic Theory of modular systems, 1916, Cambridge.
5. K. Nagao, Index calculus for Jacobian of hyperelliptic curve of small genus using two large primes,

Japan Journal of Industrial and Applied Mathematics, 24, no.3, 2007.

6. K. Nagao, Decomposition Attack for the Jacobian of a Hyperelliptic Curve over an Extension
Field, 9th International Symposium,ANTS-IX., Nancy, France, July 2010, Proceedings LNCS
6197,Springer, pp.285–300, 2010.

3 Take ri+1 ∈ Fpn \ ∪i

j=1B(cid:48)

j and disjoint decomposed factor is constracted

7. K. Nagao, Equations System coming from Weil descent and subexponential attack for algebraic

curve cryptosystem, draft, 2013.

8. C. Petit and J-J. Quisquater. On Polynomial Systems Arising from a Weil Descent, Asiacrypt

2012, Springer LNCS 7658, Springer, pp.451-466.

9. I. Semaev. Summation polynomials and the discrete logarithm problem on elliptic curves. Preprint,

2004.

