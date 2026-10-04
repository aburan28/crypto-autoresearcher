<!--
Extracted from inputs/SEMAEV-2015-310/eprint-2015-310.pdf (sha256 in the
.sha256 sidecar) on 2026-09-13 by this directory's extract_text.py, using
pdfminer.six with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5).
Derivative text extraction, vendored under the paper's CC BY 4.0 license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Igor Semaev.

NOT hand-cleaned. Ligature and math artifacts from the PDF's Type-1 fonts are
left as the extractor produced them: `ﬁ`/`ﬀ`/`ﬂ` ligatures, `(cid:100)x(cid:101)`
for the ceiling brackets in k = ceil(n/m), `Gr¨obner`, and superscripts flattened
onto the baseline (so "2 c sqrt(n ln n)" appears broken across lines in the
abstract). Tables 1-3 are reflowed by column rather than by row; use
`tables.yaml` in this directory for the row-wise transcription.

Section and equation numbers below are the paper's own and are the citable
anchors: Assumption 1 (Section 4.5, d_F4 <= 4), Assumption 2 (Section 4.6,
d_F4 = o(sqrt(n/ln n))), the success-probability model (Section 4.3, eq. 11),
the chained S_3 system (eq. 5), and the two-stage cost balance (eqs. 15-17).
-->

New algorithm for the discrete logarithm problem on elliptic
curves

Igor Semaev
Department of Informatics
University of Bergen, Norway
e-mail: igor@ii.uib.no
phone: (+47)55584279
fax: (+47)55584199

April 10, 2015

Abstract

A new algorithms for computing discrete logarithms on elliptic curves deﬁned over
ﬁnite ﬁelds is suggested. It is based on a new method to ﬁnd zeroes of summation
polynomials. In binary elliptic curves one is to solve a cubic system of Boolean equa-
tions. Under a ﬁrst fall degree assumption the regularity degree of the system is at
most 4. Extensive experimental data which supports the assumption is provided. An
heuristic analysis suggests a new asymptotical complexity bound 2c
n ln n, c ≈ 1.69 for
computing discrete logarithms on an elliptic curve over a ﬁeld of size 2n. For several
binary elliptic curves recommended by FIPS the new method performs better than
Pollard’s. The asymptotical bound is correct under a weaker assumption that the reg-
ularity degree is bounded by o((cid:112) n
ln n ) though the conclusion on the security of FIPS
curves does not generally hold in this case.

√

Keywords: ﬁnite ﬁelds, elliptic curves, Gr¨obner basis algorithms, discrete loga-

rithms, asymptotical complexity

Mathematics Subject Classiﬁcation (2010): primary 94A60,11Y16, secondary

13P15, 14G50

1

Introduction

Let E be an elliptic curve deﬁned over a ﬁnite ﬁeld Fq with q elements. The discrete
logarithm problem is given P, Q ∈ E(Fq) compute an integer number z such that Q = zP
in the group E(Fq). That problem was independently introduced in [17, 14]. A number of
information security standards are now based on the hardness of the problem, see [7] for
instance. Two cases are of most importance: q = p is a large prime number and q = 2n,
where n is prime. For super-singular and anomalous elliptic curves the discrete logarithm

1

problem is easy, that was independently discovered by several authors, see [23, 25, 8]
and [26, 24, 29]. The more general are Pollard’s methods [18]. They are applicable to
compute discrete logarithms in any ﬁnite group. In elliptic curve case the time complexity
is proportional to q1/2 ﬁeld operations and the memory requirement is negligible. The
method was improved in [22, 9, 30] though the asymptotical complexity bound remained.
In [21] a method for eﬃcient parallelization of Pollard type algorithms was provided.

Summation polynomials for elliptic curves were introduced in [27]. It was there sug-
gested to construct an index calculus type algorithm for the elliptic curve discrete logarithm
problem by decomposing points via computing zeroes of these polynomials. In [10, 3, 12, 6]
Gr¨obner basis type algorithms were applied for computing zeroes of summations polyno-
mials or their generalisations over extension ﬁnite ﬁelds. For curves over some such ﬁelds
the problem was proved to be sub-exponential, [3]. However no improvement for elliptic
curves over prime ﬁelds or binary ﬁelds of prime extension degree was achieved in those
papers.

Based on observations in [6], it was shown in [19] that under a ﬁrst fall degree as-
sumption for Boolean equation systems coming from summation polynomials, the time
complexity for elliptic curves over F2n is sub-exponential and proportional to 2cn2/3 ln n,
where c = 2ω/3, and 2.376 ≤ ω ≤ 3 is the linear algebra constant. It was there found
that for n > 2000 the method is better than Pollard’s. The assumption was supported by
experiments with computer algebra package MAGMA in [19, 28].

In this work we suggest computing zeroes of summation polynomials by solving a much
simpler system of Boolean equations. The system incorporates more variables than previ-
ously but has algebraic degree only 3. The ﬁrst fall degree is proved to be 4. Then a ﬁrst
fall degree assumption says the regularity degree dF 4 of the Gr¨obner basis algorithm F 4 is
at most 4 as well. The assumption was endorsed by numerous experiments with MAGMA.
The new method overcomes strikingly what was achieved in the experiments of [19, 28].

The time and memory complexity of computing summation polynomial zeroes under
the assumption is polynomial in n. The overall time complexity of computing discrete
logarithms on elliptic curves over F2n becomes proportional to

√

2c

n ln n,

(1)

2

where c =

(2 ln 2)1/2 ≈ 1.69. The asymptotical bound is still correct if dF 4 = o((cid:112) n

ln n ). The
analysis in this case does not rely on any ﬁrst fall degree assumption in contrast with [19].
Our analysis suggests a number of FIPS binary elliptic curves in [7] are theoretically
broken (in case dF 4 ≤ 4) as the new method starts to perform better than Pollard’s for
n > 310. The estimate is obviously extendable to elliptic curves over Fpn for ﬁxed p > 2
and growing n, by using ﬁrst fall degree bounds from [11]. The time complexity is then
pc

n ln n, where c =

√

2

(2 ln p)1/2 .

After the ﬁrst version of this paper appeared at the IACR e-Print Archive 2015/310
the author got messages from Michiel Kosters, Koray Karabina and Cristophe Petit with

2

Tsuyoshi Takagi and Yung-Ju Huang who claimed the idea of splitting one summation
polynomial equation into several ones and therefore simplifying the problem was in their
I got those contributions [15, 13, 20] and acknowledge that
unpublished works as well.
is correct. However non of them provides asymptotical analysis of any index calculus
algorithm and derives any bound like (1).

The author is grateful to Michiel Kosters for a discussion on the ﬁrst fall degree as-

sumptions.

2 Summation polynomials and index calculus on elliptic curves

Let E be an elliptic curve over a ﬁeld K in Weierstrass form

Y 2 + a1XY + a3Y = X 3 + a2X 2 + a4X + a6,

(2)

For an integer m ≥ 2 the m-th summation polynomial is the polynomial Sm in m variables
deﬁned by the following property. Let x1, x2, . . . , xm be any elements from ¯K, the algebraic
closure of K, then Sm(x1, x2, . . . , xm) = 0 if and only if there exist y1, y2, . . . , ym ∈ ¯K such
that the points (xi, yi) are on E and

(x1, y1) + (x2, y2) + . . . + (xn, yn) = ∞

in the group E( ¯K), see [27]. It is enough to ﬁnd S3(x1, x2, x3) then for m ≥ 4 in any case

Sm(x1, . . . , xm) = ResX (Sm−r(x1, . . . , xm−r−1, X), Sr+2(xm−r, . . . , xm, X)

(3)

where 1 ≤ r ≤ m − 3. The polynomial Sm is symmetric for m ≥ 3 and has degree
2m−2 in each its variable. S3 was explicitly constructed in [27] for characteristic ≥ 5 and
characteristic 2, the latter in case of a so called Koblitz curve. In characteristic ≥ 5 we can
assume a1 = a3 = a2 = 0 and denote A = a4, B = a6. So

S3(x1, x2, x3) = (x1 − x2)2x2

3 − 2[(x1 + x2)(x1x2 + A) + 2B]x3 + (x1x2 − A)2 − 4B(x1 + x2).

We are mostly concern with characteristic 2 case and the curves recommended by [7]. So
we can assume a1 = 1, a3 = 0, a4 = 0 and denote B = a6. Then

S3(x1, x2, x3) = (x1x2 + x1x3 + x2x3)2 + x1x2x3 + B,

see [27, 3].

It was suggested in [27] to construct an index calculus type algorithm for the discrete
logarithm problem in E(Fq) via ﬁnding zeroes of summation polynomials. For random
integer u, v compute an aﬃne point R = uP + vQ = (RX , RY ). Then solve the equation

Sm+1(x1, . . . , xm, RX ) = 0.

(4)

3

for xi ∈ V , where V is a subset of Fq. Each solution provides with a linear rela-
tion(decomposition) which incorporates R and at most m point from a relatively small
set of points in E(Fq), whose X-coordinate belongs to V and possibly an order 2 point in
E(Fq). Then linear algebra step ﬁnds the unknown logarithm. Two cases were considered
in [27]. First, q is a prime number, then V is a set of residues modulo q bounded by q1/n+δ
for a small δ. Second, q = 2n, and f (X) be an irreducible polynomial of degree n over F2,
and F2n = F2[X]/(f (X)). Then V is a set of all degree < n/m + δ polynomials modulo
f (X). However no algorithm to ﬁnd the zeros in V of summation polynomials was sug-
gested in [27]. In the next Section 3 we suggest producing the decomposition by solving a
diﬀerent equation system. The new system is essentially equivalent to (4). In case q = pn,
where n is large, after reducing the equations over Fq to coordinate equations over Fp(Weil
descent) the solution method is a Gr¨obner basis algorithm. In Section 4 for p = 2 we show
under a ﬁrst fall degree assumption that the complexity of a Gr¨obner basis algorithm on
such instances is polynomial. The assumption was proved correct in numerous experiments
with computer algebra package MAGMA. A similar assumption looks correct for odd p too
but the computations are tedious already for p = 5.

3 New algorithm

Let P be a point of order r in the group E(Fq), where E is an elliptic curve deﬁned over Fq.
Then Q = zP belongs to the subgroup generated by P . The discrete logarithm problem is
given Q and P , ﬁnd z mod r. In this section an algorithm for computing z is described.

1. Deﬁne parameter m and a subset V of Fq of size around q1/m.

2. For random integer u, v compute R = uP + vQ. If R = ∞, then compute z from
the equation bz + a ≡ 0 mod r. Otherwise, R has aﬃne coordinates (RX , RY ). If
RX = x1 ∈ V , then we have a relation (7) for t = 1. Otherwise

3. for t = 2, . . . , m try to compute x1, . . . , xt ∈ V and u1, . . . , ut−2 ∈ Fq until the ﬁrst

system of the following t − 1 equations is satisﬁed

S3(u1, x1, x2)
S3(ui, ui+1, xi+2) = 0, 1 ≤ i ≤ t − 3
S3(ut−2, xt, RX ) = 0.

= 0,

(5)

For t = 2 the system consists of only one equation S3(x1, x2, RX ) = 0. If non of the
systems is satisﬁed repeat the step with a new R. The solutions to (5) are solutions
to

St+1(x1, x2, . . . , xt, RX ) = 0.

(6)

The reverse statement is true as well if the systems (5) with lower t are not satisﬁable,
see Lemma 2. In practical terms it is enough to solve only one system (5) for t = m.

4

The experiments in characteristic 2 presented below demonstrate that for t < m
the solving running time with a Gr¨obner basis algorithm drops dramatically and the
probability of solving is relatively lower. So it may be more eﬃcient to solve a lot
of the systems with t < m for diﬀerent R instead of one system for t = m with one
R. One can probably win in eﬃciency and lose in probability. Though the trade oﬀ
may be positive, we won’t pursue this approach in the present work as this does not
aﬀect the asymptotical running time estimates.

Compute y1, . . . , yt ∈ Fq2 such that

(x1, y1) + (x2, y2) + . . . + (xt, yt) + uP + vQ = ∞.

(7)

If there are yi ∈ Fq2 \ Fq, then the sum of all points (xi, yi) in (7), where yi ∈ Fq2 \ Fq,
is a point in E(Fq) of order exactly 2, see Lemma 2. So that is a useful relation
anyway. At most |V | relations (7) are necessary on the average.

4. Solve the linear equations (7) and get z mod r.

4 Analysis

We will show in Lemma 2 that the system (5) is essentially equivalent to (6). Despite the
number of variables in (5) is signiﬁcantly larger, each equation on its own is much simpler.
In particular, the algebraic degree of equations (5) in each of the variables is only 2 in
contrast to 2t−1 for (6).

4.1 Lemmas

Lemma 1 Let the elliptic curve E be deﬁned over a ﬁeld Fq. Let x1, . . . , xt ∈ V be a
solution to (6). Then there exist y1, . . . , yt ∈ Fq2 such that

(x1, y1) + (x2, y2) + . . . + (xt, yt) + R = ∞.

(8)

Lemma 2 Let RX /∈ V . Assume the equations

Si+1(x1, . . . , xi, RX ) = 0, x1, . . . , xi ∈ V

are not satisﬁable for 2 ≤ i < t and x1, . . . , xt ∈ V is a solution to St+1(x1, . . . , xt, RX ) = 0.
Then

1. in (8) assume y1, . . . , ys ∈ Fq2 \ Fq and ys+1, . . . , yt ∈ Fq. Then

H = (x1, y1) + . . . + (xs, ys)

is a point in E(Fq) of order exactly 2. So s = 0 or s ≥ 2.

5

2. There exist u1, . . . , ut−2 ∈ Fq such that

S3(u1, x1, x2)
S3(ui, ui+1, xi+2) = 0, 1 ≤ i ≤ t − 3
S3(ut−2, xt, RX ) = 0.

= 0,

(9)

Proof Let’s prove the ﬁrst statement of the lemma. Assume s > 0 and let

G = (xs+1, ys+1) + . . . + (xt, yt) ∈ E(Fq).

Then H = −R − G ∈ E(Fq) as well. Let φ be a non-trivial automorphism of Fq2 over Fq,
then

φ(H) + H = ∞, φ(H) = H,

and so 2H = ∞. If H = ∞, then G + R = ∞ and so St−s+1(xs+1, . . . , xt, RX ) = 0. That
contradicts the assumption. Therefore H is a point in E(Fq) of order exactly 2 and s ≥ 2.
Let’s prove the second statement. Assume y1, . . . , ys ∈ Fq2 \ Fq and ys+1, . . . , yt ∈ Fq,

where s = 0 or s ≥ 2. There are points P1, . . . , Pt−2 such that

(x1, y1) +(x2, y2)
Pi
Pt−2

+(xi+2, yi+2) +Pi+1 = ∞, 1 ≤ i ≤ t − 3
+(xt, yt)

= ∞.

+R

+P1

= ∞,

(10)

By the lemma assumption and the previous statement P1, . . . , Pt−2 (cid:54)= ∞. So Pi = (ui, vi),
where ui ∈ Fq. Therefore (10) implies (9). The lemma is proved.

A variation of the ﬁrst statement of Lemma 2 has already appeared in [27].

4.2 General discussion on complexity

The complexity of solving a linear system of equations (7) is taken O(|V |ω(cid:48)), where ω(cid:48) = 2
as the system is very sparse for any ﬁnite ﬁeld Fq, see [31].

It is not quite clear how the system (5 may be resolved in case q is a large prime
number. However, for q = pn, where n is large, a Gr¨obner basis algorithm is applicable.
The approach was already used in [10, 3] for solving (4) after it was reduced to a system of
n multivariate polynomial equations in about n variables over Fp by so called Weil descent,
where V may be taken any vector space of dimension k = (cid:100)n/m(cid:101) over Fp. The problem of
generating such a system and keeping it in computer memory before solving is diﬃcult by
itself for m ≥ 4 and the diﬃculties increase rapidly for larger m. In [19] it was shown that
the complexity of solving (4) is sub-exponential in n under a ﬁrst fall degree assumption,
see Section 4.4 below. That assumption was supporter by a number of experiments in
[19, 28], where the parameter m was taken at most 3.

In this paper we suggest using a Gr¨obner basis algorithm to solve (5) rather than (4).
The system (5) for t = m is equivalent to a system of (m − 1)n multivariate equations in

6

(m − 2)n + km ≈ (m − 1)n variables in Fp. Under a ﬁrst fall degree assumption, see Section
4.4 and Assumption 1, we show its complexity is O[(n(m − 1))4ω], where 2.376 ≤ ω ≤ 3,
that is polynomial in n. The assumption was proved correct in numerous experiments with
MAGMA, see Section 4.5.1. We were able to solve (5) for t = m and therefore (4) for m
as 5, 6 and some n on a common computer. For n, m as in [19, 28], the solution is up to 50
times faster and takes up to 10 times less memory in comparison with [19, 28]. Similar to
[19], one can take the advantage of a block structure of the Boolean system resulted from
(5), though that does not aﬀect the asymptotical estimates. By extrapolating running
time estimates we ﬁnd that four binary curves recommended by FIPS PUB 186-4 [7] for
n = 409, 571 become theoretically broken as the new method is faster than Pollard’s for
n > 310, see Section 4.5.2. If the block structure of the system is not exploited and we
extrapolate the complexity of the default Gr¨obner basis algorithm F4, then only two FIPS
curves for n = 571 are broken.

In practical terms an additional eﬀort is required in order to accelerate the decomposi-
tion stage by solving (5) and to break the rest of the binary curves in [7]. As the collecting
stage still signiﬁcantly dominates the method running time, see Table 3, one can use almost
unbounded parallelisation to get more eﬃciency. In asymptotical analysis the complexity
of generating summation polynomials and computing their zeros to get point decomposi-
tion may be neglected as it is polynomial. That signiﬁcantly improves the asymptotical
complexity bound in [19], see Section 4.5.2.

4.3 Success probability

We estimate the probability that

St+1(x1, . . . , xt, RX ) = 0, x1, . . . , xt ∈ V,

where 2 ≤ t ≤ m, is satisﬁable. We adopt the following model. For random z the mapping
x1, . . . , xt → St+1(x1, . . . , xt, z) is a symmetric random mapping from V t to Fq. Let K be
the number of classes of tuples (x1, . . . , xt) under permuting the entries. Then K ≈ |V |t
t! .
The probability of a solution is the probability P (q, m, t, |V |) that the mapping hits 0 ∈ Fq
at least once. So

P (q, m, t, |V |) = 1 − (1 − 1/q)K

≈ 1 − (1 − 1/q)

|V |t

t! ≈ 1 − e− |V |t

q t!

(11)

q t! = o(1), then P (q, m, t, |V |) ≈ |V |t

If |V |t
It is obvious the probability of
solving at least one of the ﬁrst t − 1 systems (5) is at least P (q, m, t, |V |). On the other
hand, the latter is larger than the probability of solving (5). Therefore, we can assume
that the probability of solving (5) is approximately P (q, m, t, |V |).

q t! as in [3, 19].

In case q = pn we denote the probability P (q, m, t, |V |) by P (n, m, t, k), where |V | = pk

and p should be clear from the context.

7

4.4 Solving polynomial equations and ﬁrst fall degree assumption

Let

f1(x1, . . . , xn) = 0,

f2(x1, . . . , xn) = 0,

. . .

fm(x1, . . . , xn) = 0,

(12)

be a system of polynomial equations over a ﬁeld K. The system (12) may be solved by ﬁrst
ﬁnding a Gr¨obner basis g1, g2, . . . , gs for the ideal generated by polynomials f1, f2, . . . , fm.
If the ground ﬁeld K = Fq is a ﬁnite ﬁeld of q elements and we want the solutions with
entries in Fq, then the basis is computed for the ideal generated by

f1, f2, . . . , fm, xq

1 − x1, . . . , xq

n − xn.

d

The solutions to gi(x1, . . . , xn) = 0, (1 ≤ i ≤ s) are solutions to (12) and they are relatively
easy to ﬁnd due to the properties of the Gr¨obner basis. Several algorithms were designed
to construct a Gr¨obner basis. Let deg g denote the total degree of the polynomial g =
g(x1, . . . , xn). The ﬁrst algorithm [2] was based on reducing pairwise combinations(S-
polynomials) of the polynomials from the current basis and augmenting the current basis
with their remainders. Equivalently [16], one can triangulate a Macaulay matrix Md whose
rows are coeﬃcients of the polynomials mifj, where mi are monomials and deg(mi) +
deg(fi) ≤ d for a parameter d. That produces a Gr¨obner basis for some large enough
(cid:1) < nd columns. So the complexity is
d = d0. The matrix incorporates at most (cid:0)n+d−1
O(nωd0) of the ground ﬁeld operations, where 2.376 ≤ ω ≤ 3 is the linear algebra constant.
Also one may solve a system of linear equations which comes from mifj = 0, deg(mi) +
deg(fi) ≤ d after linearisation to get the solutions to (12) without computing a Gr¨obner
basis. The method is called extended linearisation(XL). The matrix of the system is es-
sentially Md. For large enough d = d1 the rank of the matrix is close to the number of
variables after linearisation [32]. The complexity is O(nω(cid:48)d1) of the ground ﬁeld operations,
where 2 ≤ ω(cid:48) ≤ 3 is a linear algebra constant, which depends on the sparsity of the matrix.
It may be that ω(cid:48) = 2 for a very sparse matrix in case of solving by extended linearisation.
Numerous experiments with solving the equations (5) by computer algebra package
MAGMA were done in this work. MAGMA implements an eﬃcient Gr¨obner basis algorithm
F4[4]. The algorithm successively constructs Macaulay type matrices of increasing sizes,
compute row echelon forms of them, produce some new polynomials and use them in the
next step of the construction as well. At some point no new polynomials are generated.
Then the current set of polynomials is a Gr¨obner basis. The complexity is characterised
by dF 4, the maximal total degree of the polynomials occurring before a Gr¨obner basis is
computed. The overall complexity is the sum of the complexities of some steps, where the

8

largest step complexity is bounded by

O(nω dF 4).

(13)

We assume the complexity of the computation is determined by the complexity of the
largest step.
In the experiments in Section 4.5.1 the ratio between the overall running
time and the largest step running time was bounded by ≈ 3 for the number of variables
n ≈ 50. So in the asymptotical analysis below we accept (13) as the complexity of F4. An-
other Gr¨obner basis algorithm F5[5] with the maximal total degree dF 5 has the complexity
O(nωdF 5), see [1]. It was implicitly assumed in [19, 28] that dF 5 = dF 4.

We will use the following deﬁnition found in [19]. The ﬁrst fall degree for (12) is the
smallest total degree df f such that there exist polynomials gi = gi(x1, . . . , xn), (1 ≤ i ≤ m)
with

maxi(deg gi + deg fi) = df f ,

deg

gifi < df f

(cid:88)

and (cid:80)
i gifi (cid:54)= 0. A ﬁrst fall degree assumption says dF 4 ≤ df f and that is a basis for
asymptotical complexity estimates in [19]. Although not generally correct, the assumption
appears correct for the polynomial systems coming from (4) and was supported by extensive
experiments for relatively small parameters in [19, 28]. This is very likely correct for (5)
as well, see sections below.

i

4.5 Characteristic 2

Let E be determined by

A, B ∈ F2n. Therefore,

Y 2 + XY = X 3 + AX 2 + B,

S3(x1, x2, x3) = (x1x2 + x1x3 + x2x3)2 + x1x2x3 + B,

(14)

see Section 2. Let f (x) be an irreducible polynomial of degree n over F2 and α its root
in F2n. Then 1, α, . . . , αn−1 is a basis of F2n over F2. Elements of F2n are represented as
polynomials in α of degree at most n − 1. Let V be a set of all polynomials in α of degree
< k = (cid:100)n/m(cid:101). Obviously, that is a vector space over F2 of dimension k. Following [3],
one can deﬁne V as any subspace of F2n of dimension k. However it seems that using the
subspace of low degree polynomials signiﬁcantly reduces the time and space complexity in
comparison with a randomly generated subspace and is therefore preferable. We attribute
the phenomena to the fact that the set of polynomials to compute a Gr¨obner basis is
simpler in the former case.

According to [10, 3] the equation (4), where xi ∈ V , is reducible, by taking coordi-
nates(so called Weil descent), to a system of n Boolean equations in mk variables. A
Gr¨obner basis algorithm is applicable to ﬁnd its solutions. The maximal total degree of

9

the Boolean equations is at most m(m − 1). Also it was observed in [19] and proved in [11]
that the ﬁrst fall degree of the Boolean equations coming from

Sm+1(x1, . . . , xm, RX ) = 0

is at most m2 + 1.

We consider the case m = 2 in more detail now. First we take the polynomial (14),
where all x1, x2, x3 are variables in V or F2n. Following an idea in [19] it is easy to prove
that the ﬁrst fall degree is 4 in this case. Really, coordinate Boolean functions which
represent S3(x1, x2, x3) are of total degree 3. We denote that fact

However

again because

degF2 S3(x1, x2, x3) = 3.

degF2 x1S3(x1, x2, x3) = 3

x1S3(x1, x2, x3) = x1[(x1x2 + x1x3 + x2x3)2 + x1x2x3 + B]
1x2

1x2x3 + Bx1

3 + x1x2

3 + x2

2 + x3

= x3

1x2

2x2

despite degF2 x1 + degF2 S3(x1, x2, x3) = 4. This argument does not work for S3(x1, x2, z),
where z is a constant from F2n. We have

degF2 S3(x1, x2, z) = 2,
degF2 x1S3(x1, x2, z) = 3,

and degF2 x1 + degF2 S3(x1, x2, z) = 3. The ﬁrst fall degree for such polynomials was
bounded by 5 in [11]. The experiments show it is always 4 again. Anyway at least t − 2
of the equations in (5) have the ﬁrst fall degree 4. So we come up with the following
assumption.

Assumption 1 Let q = 2n and 2 ≤ m < n, k = (cid:100) n
m (cid:101). Also let V be a subspace of
dimension k in F2n. Then dF 4 ≤ 4 for a Boolean equation system equivalent to (5) for any
2 ≤ t ≤ m.

4.5.1 Experiments

In this section we check Assumption 1 by experiments with MAGMA. The package im-
plements the Gr¨obner basis type algorithm F4 due to Faug`ere [4]. We run the algorithm
to construct solutions for the system of Boolean equations resulted from (5). The system
consists of n(t − 1) coordinate equations in n(t − 2) + kt variables and n(t − 2) + kt ﬁeld
equations are added. To simplify computations the X-coordinate RX of a random R was

10

substituted by a random element z from F2n. We take the parameters n, t ≤ m, k = (cid:100)n/m(cid:101)
from a range of values and solve the system for 100 random z.

The results, where B = 1 in (14), are presented in Table 1. The results, where B is
In the columns of
a randomly generated element from F2n, are presented in Table 2 .
the tables the following parameters are shown: n, m, t, k = (cid:100) n
m (cid:101), the experimental success
probability, theoretical success probability P (n, m, t, k), maximal degree dF 4 of the poly-
nomials generated by F4 before a Gr¨obner basis is computed, average time in seconds for
solving one system and overall amount of memory in MB used for solving 100 systems (5).
A computer with 2.6GHz Intel Core i7 processor and 16GB 1600MHZ DDR3 of memory
was used. The most important of all the parameters is dF 4. We use the verbosity imple-
mented in MAGMA for Faug`ere’s F4. The computation by F4 is split into a number of
steps, where ”step degree” is the maximal total degree of the polynomials for which a row
echelon form is computed. The parameter is available for every step of the algorithm. If
the ideal generated by the polynomials is unit, then ”step degree” was always bounded by
4. If not, that is there is a solution, then ”step degree” was bounded by 4 for all the steps
before the basis is computed. They were followed by at most three more steps, where ”step
degree” was 5, 6, 7 with the message ”No pairs to reduce”. At this point the computation
stops. To ﬁll the tables 2300 Boolean systems each of total degree 3 coming from (5), where

Table 1: Max. degree of polynomials by MAGMA and other parameters, B = 1.

n
12
13
13
14
14
15
15
16
17
17
17*
17*

t = m k = (cid:100)n/m(cid:101)

6
4
5
4
5
4
5
4
3
3
3
3

2
4
3
4
3
4
3
4
6*
6
6
6*

exp. prob. P (n, m, t, k)
0.0013
0.2834
0.0327
0.1535
0.0165
0.0799
0.0082
0.0408
0.2834
0.2834
0.2834
0.2834

0.00
0.41
0.05
0.10
0.02
0.11
0.05
0.09
0.32
0.30
0.36
0.25

dF 4
4
4
4
4
4
4
4
4
4
4
4
4

av. sec.
2.30
81.64
84.65
79.57
23.47
136.70
300.48
175.72
27.08
11.41
12.09
34.32

MB
257.8
739.8
1597.8
879.7
960.2
1457.3
3286.9
1657.7
378.1
364.1
355.1
693.2

t = m, were solved. For all of them the maximal total degree attained by F4 to compute
a Gr¨obner basis was exactly 4. For t < m the maximal total degree was smaller or equal
to 4. We conclude that for all values of n, m and t ≤ m in the tables Assumption 1 was
correct for randomly chosen z ∈ F2n. So the assumption is very likely to be correct for any

11

values of n, m, t ≤ m.

The method signiﬁcantly overcomes what was experimentally achieved in [19, 28]. For
instance, n = 21, m = 3, k = 7 the solution in [28] of (4) took 6910 seconds on the average
with 27235 MB maximum memory used. With the new method the solution of (5) for
t = m, and therefore (4) as well, takes 133.5 seconds on the average and 2437.8 MB
maximum memory on an inferior computer, see Table 2.

Table 2: Max. degree of polynomials by MAGMA and other parameters, random B.

n m t
6
6
12

k = (cid:100)n/m(cid:101)
2

exp. prob. P (n, m, t, k)
0.0013

0.01

dF 4
4

av. sec.
2.52

13
13

14
14

15
15
15
15
15
15
15

16
16
16

17

19
19

21
21

40

4
5

4
5

4
4
4
5
5
5
5

4
4
4

3

3
3

3
3

2

4
5

4
5

4
3
2
5
4
3
2

4
3
2

3

3
2

3
2

2

4
3

4
3

4
4
4
3
3
3
3

4
4
4

6

7
7

7
7

20

0.31
0.09

0.16
0.03

0.06
0.02
0.00
0.03
0.01
0.00
0.00

0.04
0.01
0.00

0.21

0.47
0.01

0.12
0.01

0.28

0.2834
0.0327

0.1535
0.0165

0.0799
0.0206
0.0038
0.0082
0.0051
0.0026
0.0009

0.0408
0.0103
0.0019

0.2834

0.4865
0.0155

0.1535
0.0038

0.3934

4
4

4
4

4
4
4
4
4
4
4

4
4
4

4

4
4

4
4

4

MB
289.9

981.8
1633.0

1056.7
1154.2

1177.5
64.1
32.1
2635.4
424.9
32.1
32.1

1145.2
64.1
32.1

85.30
98.81

93.48
41.15

102.85
0.4765
0.0013
174.47
12.95
0.0339
0.0006

160.87
0.4984
0.0014

15.80

375.8

137.32
0.0092

133.54
0.0095

1812.8
32.1

2437.8
32.1

139.43

3913.3

In the last 4 lines of Table 1 we also take into account the inﬂuence of the choice of
generating polynomial for F2n and the vector space V . The line with 17∗ means a random
irreducible polynomial f (X) of degree 17 for constructing F217 was used in the computa-
tions. Otherwise a default generating polynomial of MAGMA or a sparse polynomial were
used. The line with 6∗ means a random subspace of dimension 6 in F217 was used in the
computations. Otherwise a subspace of all degree < 6 polynomials modulo f (X) was used.

12

We realise the latter is preferable.

To conclude the section we should mention that the maximal degree(regularity degree)

generally exceeds 4 when k > (cid:100) n

m (cid:101) though the ﬁrst fall degree is still 4.

4.5.2 Asymptotical Complexity

In this section an asymptotical complexity estimate for the discrete logarithm problem in
E(F2n) based on Assumption 1 is derived. The algorithm complexity is the sum of the
complexity of two stages. First collecting a system of ≤ 2k, k = (cid:100)n/m(cid:101) linear relations (7)
and then solving them. The probability of producing one linear relation by solving at least
one system of multivariate Boolean equations (5) for 2 ≤ t ≤ m is at least P (n, m, m, k) ≈
2mk−n/m!, see Section 4.3. The complexity of solving by the Gr¨obner basis algorithm
F4 is [n(m − 1)]4ω. The estimate in [19] was based on using a block structured Gr¨obner
basis algorithm, where the block size was k, rather than the standard F4. That reduced
the asymptotical complexity of solving (4). We think the same approach is applicable
to solve the equations coming from (5) as well, with the block size n. That reduces the
complexity of ﬁnding the relation to n4ω. We remark that does not aﬀect the asymptotical
complexity of the present method anyway as the both estimates are polynomial. Therefore
the complexity of the ﬁrst stage is

2kn4ω

P (n, m, m, k)

≈

m!

2mk−n 2kn4ω

(15)

operations, where 2.376 ≤ ω ≤ 3 is the linear algebra constant. For ω = 3 that is at most
m!2

m n12. The complexity of the second stage is

n

2kω(cid:48)

,

(16)

where ω(cid:48) = 2 is the sparse linear algebra constant. One equates (15) and (16) to determine

for large n. The overall complexity is

2kω(cid:48)

≈ 2

nω(cid:48)

√

m = 2c

n ln n,

(17)

(cid:113) (2 ln 2)n

ln n

the optimal value m ≈

where c =

2

(2 ln 2)1/2 .

We now compare the values of (15) and (16) for a range of n ≤ 571 in Table 3. The
ﬁrst stage complexity dominates. For each n in the range one ﬁnds m, where the ﬁrst stage
complexity m!2

m n12 is minimal. The table presents the values of

n

n, 2n/2, m, m! 2

n

m n12, 22n/m.

The new method starts performing better than Pollard’s for n > 310. Therefore four curves
deﬁned over F2n for n = 409, 571 and recommended by FIPS PUB 186-4 [7] are theoretically

13

broken. If only the default Gr¨obner basis algorithm F4 is used with complexity [n(m−1)]4ω,
then two FIPS curves for n = 571 are broken.

The ﬁrst stage of the algorithm is easy to accomplish with several processors working
in parallel. As the ﬁrst stage complexity is dominating that signiﬁcantly improves the
running time of the method in practical terms.

Table 3: Complexity estimates in characteristic 2.

n

m n12

2n
m

2

n
100
150
200
250
300
310
350
400
409
450
500
571

2n/2
1.12 × 1015
3.77 × 1022
1.26 × 1030
4.25 × 1037
1.42 × 1045
4.56 × 1046
4.78 × 1052
1.60 × 1060
3.63 × 1061
5.39 × 1067
1.80 × 1075
8.79 × 1085

m m!2
6
7
8
9
10
10
10
11
11
11
12
12

7.49 × 1031
1.84 × 1036
5.54 × 1039
4.97 × 1042
2.07 × 1045
6.13 × 1045
4.21 × 1047
5.92 × 1049
1.36 × 1050
5.68 × 1051
4.08 × 1053
1.21 × 1056

1.08 × 1010
7.96 × 1012
1.12 × 1015
5.29 × 1016
1.15 × 1018
4.61 × 1018
1.18 × 1021
7.81 × 1021
2.43 × 1022
4.26 × 1024
1.21 × 1025
4.44 × 1028

4.6 Another assumption

In this section we come up with a diﬀerent weaker assumption.

Assumption 2 Let q = 2n and m = O((cid:112) n
a subspace of dimension k in F2n. Then dF 4 = o((cid:112) n

ln n ) for large n, k = (cid:100) n

m (cid:101). Also let V be
ln n ) for a Boolean equation system

equivalent to (5) for any 2 ≤ t ≤ m.

Under Assumption 2 the asymptotical bound (17) remains intact. Really, for m ≈
the complexity of the ﬁrst stage of the algorithm is

(cid:113) (2 ln 2)n

ln n

2kn4ω

P (n, m, m, k)

≈

m!

2mk−n 2k(n(m − 1))dF 4ω ≈ m!2k

for large n as the complexity of F4 is

(n(m − 1))dF 4ω ≈ 2o(

√

n ln n).

14

The complexity of the second stage is again 22k. That implies the bound (17) is true under
the Assumption 2 as well. Therefore the asymptotical bound does not depend on any ﬁrst
fall degree assumption. However the complexity estimates in Table 3 will change.

References

[1] M. Bardet, J.-C.Faug´ere, and B. Salvy, Complexity of Gr¨obner basis computation for
semi-regular overdetermined sequences over F2 with solutions in F2, Research report
RR–5049, INRIA 2003.

[2] B. Buchberger, Theoretical Basis for the Reduction of Polynomials to Canonical Forms,

SIGSAM Bull. 39(1976), pp. 19–24.

[3] C. Diem, On the discrete logarithm problem in elliptic curves, Compos. Math.,

147(2011), pp. 75–104.

[4] J.-C. Faug`ere, A new eﬃcient algorithm for computing Gr¨obner bases (F4), J.Pure

Appl. Algebra, 139 (1999), pp. 61–88.

[5] J.-C. Faug`ere, A new eﬃcient algorithm for computing Gr¨obner bases without reduction

to zero (F5), in ISSAC’2002, pp. 75 – 83, ACM Press 2002.

[6] J.-Ch. Faug`ere, L. Perret, Ch. Petit, and G. Renault, Improving the complexity of index
calculus algorithms in elliptic curves over binary ﬁelds, in EUROCRYPT’2012, LNCS
7237, pp. 27–44, Springer 2012.

[7] Federal

Information
Standard(DSS),

Processing

Standards
PUB 186-4,

Publication,
July,

2013,

Digital
available

Sig-
at

nature
FIPS
http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf.

[8] G. Frey and H.-G. Ruck, A remark concerning m-divisibility and the discrete logarithm

in the divisor class group of curves, Math. Comp. 62 (1994), pp. 865–874.

[9] R. Gallant, R. Lambert,and S. Vanstone, Improving the parallelized Pollard lambda

search on anomalous binary curves, Math. Comp. 69 (2000), pp. 1699–1705.

[10] P. Gaudry, Index calculus for abelian varieties of small dimension and the elliptic

curve discrete logarithm problem, J. Symbolic Comput., 44(2009), 1690–1702.

[11] T. Hodges, C. Petit, and J. Schlather, First fall degree and Weil descent,Finite Fields

Appl., 30(2014), pp. 155–177.

[12] A. Joux and V. Vitse, Cover and decomposition index calculus on elliptic curves made
practical-application to a previously unreachable curve over Fp6, in EROCRYPT’2012,
LNCS 7237, pp. 9–26, Springer 2012.

15

[13] K. Karabina, Point decomposition problem in binary elliptic curves, preprint, 2015.

[14] N. Koblitz, Elliptic curve cryptosystems, Math. Comp. 48(1987), pp. 203–209.

[15] M. Kosters, Solving ECDLP without a factor base, presentation slides, 2014.

[16] D. Lazard, Gr¨obner-bases, Gaussian elimination and resolution of systems of algebraic

equations, in EUROCAL’1983, pp. 146–156.

[17] V. Miller, Use of elliptic curves in cryptography, in CRYPTO’85, LNCS 218, pp.

417–426, Springer 1986.

[18] J. Pollard, Monte-Carlo methods for index computation mod p, Math.Comp. 32

(1978), pp. 918–924.

[19] C. Petit and J. Quisquater, On polynomial systems arising from a Weil descent, in

ASIACRYPT 2012, LNCS 7658, pp. 451–466, Springer 2012.

[20] C. Petit, T. Takagi and Y.J. Huang, On generalised ﬁrst fall degree assumptions,

preprint, 2014.

[21] P.van Oorschot and M.Wiener, Parallel collision search with cryptanalytic applica-

tions, J. Cryptology, 12 (1999), pp. 1–28.

[22] M.Wiener and R.Zuccherato, Faster attacks on elliptic curve cryptosystems, LNCS

1556, pp. 190–200, Springer 1999.

[23] A. Menezes, S. Vanstone, and T. Okamoto, Reducing elliptic curve logarithms to loga-
rithms in a ﬁnite ﬁeld, Proc. 23rd ACM Symp. Theory of Computing, 1991, pp. 80–89.

[24] T. Satoh and K. Araki, Fermat quotients and the polynomial time discrete log algo-
rithm for anomalous elliptic curves, Comment. Math. Helv., 47 (1998), pp. 81–92.

[25] I. Semaev, Fast algorithm for computing Weil pairing on an elliptic curve(in Russian),
Int. Conf. ”Modern Problems in Number Theory”, Russia, Tula, 1993, Abstracts of
papers.

[26] I. Semaev, Evaluation of discrete logarithms in a group of p-torsion points in char-

acteristic p, Math. Comp., 67(1998), pp. 353–356.

[27] I. Semaev, Summation polynomials and the discrete logarithm problem on elliptic

curves, Cryptology ePrint Archive 2004/031, 2004.

[28] M. Shantz and E. Teske, Solving the elliptic curve discrete logarithm problem using
Semaev polynomials, Weil descent and Gr¨obner basis methods - an experimental study,
LNCS 8260, pp. 94–107, Springer 2013.

16

[29] N. Smart, The discrete logarithm problem on elliptic curves of trace one, J. Cryptol-

ogy, 12 (1999), pp. 193–196.

[30] E. Teske, On Random Walks for Pollard’s Rho Method, Math. Comp. 70 (2001), pp.

809–825.

[31] D. H. Wiedemann, Solving sparse linear equations over ﬁnite ﬁelds, IEEE Trans.

Inform. Theory, 32( 1986), pp. 54–62.

[32] B.-Y. Yang, J-M. Chen, and N.Courtois, On asymptotic security estimates in XL and
Gr¨obner bases-related algebraic cryptanalysis, LNCS 3269, pp. 401–413, Springer 2004.

17

