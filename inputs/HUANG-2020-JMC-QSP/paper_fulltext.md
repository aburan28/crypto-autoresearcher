<!--
Extracted from inputs/HUANG-2020-JMC-QSP/huang-et-al-jmc-2020-qsp.pdf (sha256 in the .sha256
sidecar) on 2026-09-16 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
detect_vertical=False). Derivative text extraction vendored under
the paper's CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/), stated on the publisher's first page and on the Birmingham repository cover sheet,
with attribution to Ming-Deh Huang, Michiel Kosters, Christophe Petit, Sze Ling Yeo and Yang Yun.

NOT hand-cleaned. Ligatures, superscripts flattened onto the baseline, displayed
formulas broken across lines, and (cid:NN) glyph placeholders are left exactly as
the extractor produced them. Section, lemma, proposition, theorem and remark
numbers are the paper's own and are the citable anchors.
-->

University of Birmingham

Quasi-subfield polynomials and the elliptic curve
discrete logarithm problem

Huang, Ming-Deh; Kosters, Michiel ; Petit, Christophe; Yeo, Sze Ling ; Yun, Yang

DOI:
10.1515/jmc-2015-0049

License:
Creative Commons: Attribution (CC BY)

Document Version
Publisher's PDF, also known as Version of record

Citation for published version (Harvard):
Huang, M-D, Kosters, M, Petit, C, Yeo, SL & Yun, Y 2020, 'Quasi-subfield polynomials and the elliptic curve
discrete logarithm problem', Journal of Mathematical Cryptology, vol. 14, no. 1, pp. 25-38.
https://doi.org/10.1515/jmc-2015-0049

Link to publication on Research at Birmingham portal

General rights
Unless a licence is specified above, all rights (including copyright and moral rights) in this document are retained by the authors and/or the
copyright holders. The express permission of the copyright holder must be obtained for any use of this material other than for purposes
permitted by law.

•Users may freely distribute the URL that is used to identify this publication.
•Users may download and/or print one copy of the publication from the University of Birmingham research portal for the purpose of private
study or non-commercial research.
•User may use extracts from the document in line with the concept of ‘fair dealing’ under the Copyright, Designs and Patents Act 1988 (?)
•Users may not further distribute the material nor use it for the purposes of commercial gain.

Where a licence is displayed above, please note the terms and conditions of the licence govern your use of this document.

When citing, please reference the published version.

Take down policy
While the University of Birmingham exercises care and attention in making items available there are rare occasions when an item has been
uploaded in error or has been deemed to be commercially or otherwise sensitive.

If you believe that this is the case for this document, please contact UBIRA@lists.bham.ac.uk providing details and we will remove access to
the work immediately and investigate.

Download date: 16. Sep. 2026

  J. Math. Cryptol. 2020; 14:25–38

Research Article

Ming-Deh Huang*, Michiel Kosters, Christophe Petit, Sze Ling Yeo, and Yang Yun

Quasi-subfield Polynomials and the Elliptic
Curve Discrete Logarithm Problem

https://doi.org/10.1515/jmc-2015-0049

Received Feb 05, 2020; accepted Feb 06, 2020

Abstract: We initiate the study of a new class of polynomials which we call quasi-subfield polynomials. First,

we show that this class of polynomials could lead to more efficient attacks for the elliptic curve discrete log-

arithm problem via the index calculus approach. Specifically, we use these polynomials to construct factor

bases for the index calculus approach and we provide explicit complexity bounds. Next, we investigate the

existence of quasi-subfield polynomials.

Keywords: Elliptic Curve Discrete Logarithm Problem, Cryptanalysis, Finite Fields

2010 Mathematics Subject Classification: 94A60, 11T06, 11T71

1 Introduction

The hardness of the discrete logarithm problem (DLP) in cyclic groups has been one of the key mathematical

problems underlying many public key cryptosystems in use today. In its most general form, given a generator

g of a cyclic group G = ⟨g⟩ of order N, and an arbitrary element h ∈ G, DLP seeks for the smallest integer
k such that h = gk (or h = kg in the additive notation). For the purposes of cryptographic applications, the

most common cyclic groups used are multiplicative subgroups of finite fields as well as subgroups of rational

points on elliptic curves over finite fields.

The discrete logarithm problem in multiplicative groups of finite fields was the basis for one of the earliest

public-key protocols, namely the Diffie-Hellman key exchange protocol [5]. Since then, remarkable progress

has been made to improve the complexity of solving this problem. First, in [1], index calculus methods were

proposed to solve DLP over finite fields in sub-exponential time. More impressive results were obtained in

recent years with heuristic quasi-polynomial time bounds in the case of finite field of small characteristics

[2].

By contrast, the elliptic curve discrete logarithm problem (ECDLP) has so far been more resistant to ef-

ficient attacks and the best attacks for groups of N rational points are generic algorithms such as Pollard’s

rho and Baby-Step-Giant-Step algorithms with a number of group operations proportional to

N. In this pa-

√

per, we refer to the complexity bounds from these generic algorithms as generic bounds. In 2004, Semaev

proposed an index calculus approach to solve ECDLP [23]. This inspired several subsequent works leading to

sub-exponential attacks for some families of elliptic curves [4].

*Corresponding Author: Ming-Deh Huang: University of Southern California, United States of America;

Email: mdhuang@usc.edu

Michiel Kosters: University of California, Irvine, United States of America; Email: kosters@gmail.com

Christophe Petit: University of Birmingham, United Kingdom of Great Britain and Northern Ireland;

Email: christophe.f.petit@gmail.com

Sze Ling Yeo: Institute for Infocomm Research (I2R) and Nanyang Technical University, Singapore;

Email: slyeo@i2r.a-star.edu.sg

Yang Yun: School of science, Jinling Institute of Technology, China; Email: YANG0379@e.ntu.edu.sg

Open Access. © 2020 M.-D. Huang et al., published by De Gruyter.

Attribution 4.0 License

This work is licensed under the Creative Commons

26 | M.-D. Huang et al.

Essentially, the index calculus method seeks for a good factor basis that gives rise to an efficient relation

search. Semaev’s work converts this relation search into a problem of solving polynomial equations over finite

fields. Factor bases that have been proposed include sets of elliptic curve points with the x-coordinates from

finite subfields [4, 14] or more generally, vector spaces [11, 21]. The corresponding polynomial systems are

typically solved via Weil descent, that is, transformed into polynomial systems over the base field and then

solved using one of the existing polynomial solving methods such as Rojas’ algorithm [22], Gröbner basis
algorithms [8, 9] or resultants. Thus far, this approach works well for finite fields Fqn with q being large. For q
small and n a prime, heuristic sub-exponential results were proposed in [21]. However, experimental results

in [16] gave some evidence against the heuristic assumption used. In other words, the best proven attack for
the important class of elliptic curves over F2n for n prime are the generic attacks.

One therefore wonders if there exist factor bases that directly give rise to a more efficient polynomial

solving technique. In this paper, we propose factor bases constructed from roots of polynomials of the form

Xqn′

− λ(X) which split completely in Fqn . When deg(λ) is small enough, we call Xqn′

− λ(X) a quasi-subfield

polynomial, by extension of the subfield case which has λ(X) = X. Using these polynomials, we construct a
polynomial system over the field Fqn such that the zero set gives a relation for the index calculus method. By
employing Rojas’s algorithm to solve this polynomial system, we give precise complexity results for our index

calculus algorithm.

The next interesting question is to ask for the existence of the quasi-subfield polynomials. Apart from the

above mentioned links to efficient attacks on the elliptic curve discrete logarithm problem, this problem is an

interesting mathematical problem in its own right. What we are able to prove so far is that there exists a class

of quasi-subfield polynomials such that our algorithm yields a time complexity that beats exhaustive search

(exhaustive search runs in O(N) steps). In addition, we investigate this problem by considering additive and

multiplicative subgroups of fields. Statistical arguments suggest that for arbitrary q and n in general these

groups are unlikely to give rise to quasi-subfield polynomials to achieve a time complexity better than generic
bounds for ECDLP over Fqn . An interesting question is whether special families of {q, n} can be identified
where these groups do give rise to quasi-subfield polynomials. The search of quasi-subfield polynomials in

general remains an open problem.

In Section 2 we recall previous ECDLP algorithms for elliptic curves defined over extension fields. In Sec-

tion 3 we describe our new algorithm and we analyze its complexity depending on its various parameters. In

Section 4 we discuss the existence of suitable parameters for our approach. We finally conclude the paper in

Section 5.

2 Index Calculus Algorithms for ECDLP over Extension Fields

For the remainder of this paper, let q be a prime, K = Fqn be a finite field with qn elements, and let E be an
elliptic curve defined over K. Let P be a rational point on E, and let Q be randomly chosen in the subgroup

generated by P. As this is standard in cryptographic contexts, we assume that P generates a subgroup of

large prime order N. We are interested in algorithms to compute the discrete logarithm of Q with respect to

P, namely an integer s such that Q = [s]P. We are particularly interested in the case where q is a very small

prime.

2.1 Existing Algorithms

Here we focus on algorithms specific to elliptic curves, and particularly index calculus algorithms [4, 11, 14,

21, 23].

Given q, n, E, P, Q, we first choose parameters m, n′ and a vector space V of dimension n′ over Fq. We

then define a factor basis

F := {(x, y) ∈ E(K) | x ∈ V}.

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 27

Following standard index calculus algorithms for the discrete logarithm problem over finite fields, we then

collect sufficiently many relations of the form

ai P + bi Q =

m
∑︁

j=1

Pij

with ai , bi randomly chosen and Pij ∈ F.

Finally, we perform linear algebra operations modulo N on the relations to obtain a new relation of the

form aP + bQ = 0 from which one (almost always) deduces the discrete logarithm value s = −a/b mod N.

In this algorithm, for every index i, we need to solve an instance of the following problem:

Problem 1 (Point Decomposition Problem). Fix a positive integer m. Given a point R ∈ E(K), find, if any, m
points P1, ..., Pm ∈ F, such that R = P1 + ... + Pm.

This is typically done using Semaev’s summation polynomials [23], a Weil descent strategy, and an algorithm

to solve systems of multivariate polynomial equations.

For every index r ≥ 2, the summation polynomial Sr ∈ K[X1, X2, . . . , Xr] is a polynomial depending on E
such that Sr(x1, x2, . . . , xr) = 0 if and only if there exist yi ∈ K and (xi , yi) ∈ E(K) with (x1, y1) + (x2, y2) +
. . . + (xr , yr) = 0 on E(K). This is a symmetric polynomial with degree 2r−2 in each variable.

In order to solve the point decomposition problem above, we can solve

Sm+1(x1, x2, . . . , xm , xR) = 0,

xi ∈ V ,

(1)

where xR is the X coordinate of R, and for each of these solutions x1, . . . , xm, one checks whether all the yi
are in K.

This problem is further reduced to a polynomial system as follows. We fix a basis {θ1, . . . , θn} of K over
Fq and a basis {v1, . . . , vn′ } of V over Fq. We then introduce mn′ variables xij over Fq, with 1 ≤ i ≤ m
and 1 ≤ j ≤ n′ such that xi = ∑︀n′
j=1 xij vj. Substituting in Equation 1 and projecting the equation over each
component of the basis {θ1, . . . , θn} of K over Fq, we obtain a system of n equations in the mn′ variables xij.
When q is reasonably large compared to n, one can take V := Fq. The system is then solved using resul-
tants or a Groebner basis algorithm [4, 14]. On the other hand when q is small, one adds the so-called field
equations xq

ij − xij = 0 to the system, and solves it using a Groebner basis algorithm [11, 21].

2.2 Complexity Analysis

The analysis of these algorithms has so far required several heuristic assumptions.

Fix a positive integer m. Heuristically, one can expect that roughly half of the values in V are the x-

coordinates of exactly two points on the curve, and hence we approximate |F| ≈ qn′
. Moreover, assuming
that most (unordered) tuples of m points in F produce a distinct sum, the probability that the randomly cho-
sen point Ri := ai P + bi Q can be split as a sum of m points in F is heuristically estimated by

|F|m
m! · qn ≈

qn′m−n
m!

.

These heuristic assumptions appear reasonable, and they are common in the literature. Furthermore, we need
about |F| decompositions to solve the discrete logarithm problem.

If we let C(q, n, m, n′) be the expected cost of Solving Problem 1, the relation search phase of the algorithm

then has an expected cost of

qn′ m!

qn′m−n C(q, n, m, n′) = m! · qn−n′m+n′

C(q, n, m, n′).

In practice m will be small compared to qn′

, so a sparse linear algebra algorithm will be used for the linear
algebra phase of the algorithm [25]. The expected cost of this phase can therefore be approximated by mq2n′

.

We then have:

28 | M.-D. Huang et al.

Theorem 2.1. Under plausible heuristic assumptions, the total cost of solving a discrete logarithm problem for

a curve defined over K can be approximated by

where C is as above.

m! · qn−n′m+n′

C(q, n, m, n′) + mq2n′

Evaluating the cost C(q, n, m, n′) of solving Problem 1 has proven to be very difficult. The polynomial systems

obtained after the Weil descent procedure are solved with Groebner basis or multivariate resultant algorithms.

These algorithms reduce polynomial system solving to linear algebra. The main issue in estimating the cost

of Problem 1 is estimating the size of this linear algebra problem.

Existing upper bounds seem to provide a good approximation for the cost of solving generic systems of

polynomial equations, but have often been of little value for systems with special structure, and in particular

those coming from cryptography [10, 16, 19].

For some ranges of the parameters n and q, these bounds suffice to show that the algorithm above with
V = Fq outperforms generic algorithms [4, 14] and in the best case the algorithm has subexponential com-
plexity. In the important case q = 2 and n prime, the bounds lead to an overall cost above the cost of generic

algorithms [11], but studies of the polynomial systems suggest that the actual complexity of solving them may

be lower [12, 17, 21, 24]. In [21] it was shown that under the first fall degree assumption, a heuristic previously

used in other cryptanalysis work [6, 7, 10, 15], the overall cost of ECDLP over characteristic 2 fields would

be subexponential. Since then Huang et al. [16] have provided some evidence against the first fall degree

assumption, and the actual cost of the algorithm remains unknown.

2.3 Current Challenges

There are two main challenges related to the family of index calculus algorithm sketched in this section:

– Complexity estimates: the complexity of these algorithms is hard to analyze.

– Practical efficiency: solving ECDLP for curves used in cryptography is still very hard in practice.

This is in contrast to the particular case V = Fq where for some range of parameters, improvements over

generic algorithms have been demonstrated both in theory and in practice [4, 14].

3 A new ECDLP Algorithm

The particular vector space V = Fq can be equivalently described as the set of elements x ∈ K such that xq = x.
Let m := n in this case. From the problem

we easily derive n equations

Sn+1(x1, x2, . . . , xn , xR) = 0,

xi ∈ V ,

S(i)(X1, X2, . . . , Xn) := Sqi

n+1 (X1, X2, . . . , Xn , xR) mod Xq

1 − X1, . . . , Xq

n − Xn .

Clearly, all the equations above can be chosen to have the same degree. We thus have a system of n equa-

tions (letting i = 0, 1, . . . , n − 1) in n variables. The system can be solved using resultants or Groebner basis

algorithms, leading to the good complexity results mentioned above.

Motivated by these ideas, we consider factor bases whose elements are roots of some “nice” polynomials.

Concretely, our main idea in this paper is to replace the vector space V by the set of points satisfying an

equation of the form xqn′

= λ(x) where λ is a polynomial of small degree.

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 29

3.1 Our Algorithm

Let q, n, E, P, Q as above, and suppose we want to solve the corresponding discrete logarithm problem. Fur-
thermore, fix λ(x) ∈ K[X] and positive integers n′ and m.

Let M be the set of monomials in K[X1, . . . , Xm]. For a positive integer i and f = ∑︀

M∈M aM M ∈
M M, that is, we raise the

M aqi

K[X1, . . . , Xm], we define the polynomial Fi(f ) as the polynomial Fi(f ) = ∑︀
coefficients of f to the power qi. Let

φ : K[X1, . . . , Xm] →K[X1, . . . , Xm]

f (X1, . . . , Xm) →Fn′

(f )(λ(X1), . . . , λ(Xm)).

Observe that we have

f qn′

≡ φ(f )

Our algorithm has three steps:

1. Choice of a “factor basis”: Set

and a “factor basis”

(mod Xqn′

1 − λ(X1), . . . , Xqn′

m − λ(Xm)).

{︂

x ∈ K |xqn′

V :=

}︂

− λ(x) = 0

F := {(x, y) ∈ E(K) | x ∈ V}.

2. Relation search: let ∆ be a small integer. For i = 1, 2, . . . , |F| + ∆, we generate random ai , bi ∈
{0, . . . , N−1} and we compute Ri := ai P+bi Q. We let S(0)(X1, X2, . . . , Xm) := Sm+1(X1, X2, . . . , Xm , xRi )
and for k = 1, . . . , m − 1, we let

S(k)(X1, X2, . . . , Xm) := φ

(︁

S(k−1)(X1, X2, . . . , Xm)

)︁

.

We solve the polynomial system S = {S(k)}m−1

k=0 using Rojas’ sparse resultant algorithm [22] and a uni-
variate polynomial root finding algorithm. Given a solution (x1, . . . , xm), we check whether all the x
values correspond to points in the factor basis in two steps:

– Check if for each j = 1, 2, . . . , m, xj ∈ V, that is, xqn′

j

= λ(xj).

– Check if for each j = 1, 2, . . . , m there exists yj ∈ K such that (xj , yj) ∈ E(K).

We then find signs such that the relation Ri = ∑︀m

j=1 ±(xj , yj) holds.

Once a solution is found, we store the corresponding relation.

3. Linear algebra: as in previous algorithms, we perform linear algebra operations on the relations to

derive a relation of the form aP + bQ = 0, from which we deduce the discrete logarithm value.

Our goal in the relation search step is to solve the equation Sm+1(x1, . . . , xm , xR) = 0 with xi ∈ V,

i = 1, . . . , m. This is equivalent to finding the zeros of the system T = {Sm+1(X1, . . . , Xm , xR), Xqn′
λ(X1), . . . , Xqn′

1 −
m − λ(Xm)}. In this paper we consider the system S, which might have more solutions than
the system T. We make the assumption that S is zero-dimensional. We refer to Appendix B for an argument

in support of this assumption.

We observe that a randomly chosen polynomial λ with small degree will usually result in a very small

factor basis F (and in an impractically large m), while a randomly chosen set of around qn′
K will lead to a polynomial λ of large degree. The existence and construction of suitable parameters will be

elements from

further discussed in Section 4.

3.2 Complexity Analysis

The next lemma (proved in Appendix A.1) evaluates the cost of Rojas’ algorithm:

30 | M.-D. Huang et al.

Lemma 3.1. Let d = deg(λ). Consider the set S = {S(k)

: k = 0, 1, . . . , m − 1}. Suppose that S is zero-

dimensional. By applying Rojas’s method [22], one can construct univariate polynomials h(X), h1(X), . . . , hm(X) ∈
K[X] such that the zero set of S on (K
these polynomials can be found in ˜O(m5.188 · (3d)4.876m2
K.

)m is given by {(h1(θ), h2(θ), . . . , hm(θ)) ∈ (K

) arithmetic steps over (a small degree extension of)

)m | h(θ) = 0}. Moreover,

*

*

As in previous algorithms, we heuristically approximate |F| ≈ |V| and we assume |V| ≈ qn′

.

Under the assumptions recalled above, we can therefore evaluate the cost of our algorithm as follows:

Theorem 3.2. Let d := deg λ. Under the assumptions listed in this section, the complexity of our algorithm is

m! · qn−n′m+n′

· ˜O

(︁

m5.188 · (3d)4.876m2 )︁

+ mq2n′

arithmetic operations.

An ideal polynomial λ in our attack will have a small degree d. The case V = Fq is used in Diem and Gaudry’s
algorithms [4, 14], and it corresponds to d = n′ = 1. Concretely, we have m = n and |V| = q. Theorem 3.2 gives
the time complexity of n! · q · ˜O
+ nq2 arithmetic steps. By letting n and q vary in a particular

n5.18834.876n2 )︁

(︁

way, one can get a sub-exponential complexity (see [4]).

Remark 3.1. Recall that generic algorithms use O(qn/2) group operations, whereas brute force ap-
proaches require O(qn) group operations.

– Assume d > q0.102 n

m2 . Then Theorem 3.2 has a term which is at least O(qn/2), suggesting that our algorithm

does not beat generic algoritms.

– Fix an integer m and real number α with 0 < α < 1. Assume that m ≈ αn/n′ and furthermore that

d ≈ qn′2/n. Then our complexity reduces to

(︁

˜O

qn−n′m+n′

· d4.876m2

+ q2n′ )︁

= ˜O

(︁

qn(1−α+4.876α2)+αn/m + q2αn/m)︁

For m large enough this gives a complexity of approximately ˜O

(︁

qn(1−α+4.876α2+ϵ))︁

. The minimum value of

1 − α + 4.876α2 is approximately 0.95. Hence when α is chosen properly (for example α = 0.1), the com-
plexity is ˜O(q0.95n) which beats brute force algorithms. Note that one can get better complexity estimates
if d ≈ qβn′2/n where β < 1.

Definition 3.1. In view of Remark 3.1, we call polynomials Xqn′
logq(deg(λ)) < n′2/n quasi-subfield polynomials.

− λ(X) ∈ K[X] dividing Xqn

− X with logq(d) =

4 Finding Suitable Parameters and constructions

We now discuss the existence and computation of suitable parameters for our attack. We first give a general

existential result. Then we focus on the case of additive subgroups of the finite field. We give a probabilistic

argument in that context, followed by an explicit construction. In Appendix C we further study additive sub-

groups for Mersenne prime extensions of characteristic 2 fields, and we investigate multiplicative subgroups

of the finite field.

4.1 Lower Bounds on deg λ

Let q, n, n′, m, d and λ be as above, and suppose that deg λ > 1. Assume that L(X) = Xqn′
so that |V| = qn′

. The following lemma (proved in Appendix A.2) shows that deg λ cannot be too small.

− λ(X) splits over K,

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 31

Lemma 4.1. Suppose that L(X) = Xqn′

− λ(X) ∈ K[X] divides Xqn

− X and that ℓ := logq d = logq deg λ > 0.

Then we have

⌋︁

⌊︁ n
n′

ℓ + (n mod n′) ≥ n′.

One can prove a similar result when L(X) splits almost completely over K (see Lemma C.2). Remark that the

above lemma does not apply when λ is linear.

The above constraints on ℓ = logq deg λ are more strict when n mod n′ is smaller. When n mod n′ is too

small, we see that our algorithm is often worse than generic algorithms by Remark 3.1.

We remark that random polynomials dividing Xqn

− X are unlikely to be such that ℓ is small. On the

other hand, a random polynomial of the shape of L with ℓ small is unlikely to have many roots in K. We will

therefore need ad hoc constructions to build these polynomials. Perhaps, the most natural constructions are

to consider additive and multiplicative subgroups of K. In what follows, we argue that these constructions

may not provide us with the sparse polynomials we seek.

4.2 Additive Subgroups

In the remaining of this section we focus on polynomials L such that the corresponding set V :=

x ∈ K |xqn′
= λ(x)}︀ is a vector space over Fq. The factor bases considered are therefore a subset of the factor bases con-

{︁

sidered in [11, 21] and follow-up works, though of course our algorithm computes relations in a different way.
α∈V (X − α) is a monic
linearized polynomial, namely its only non-zero coefficients are coefficients of power of q terms [3, Ch. 11]. Any

We recall that for any vector space V over Fq, the associated polynomial L(X) = ∏︀

two distinct vector spaces correspond to distinct linearized polynomials, but not every linearized polynomial

corresponds to a vector space. In fact, as shown in Appendix A.3, we have:

Lemma 4.2. Let N(q, n, n′) be the number of distinct vector spaces over Fq of dimension n′ that are contained
in K. Assume n ≥ n′ ≥ 1. Then:

qn′(n−n′) · (1 − n′q−(n−n′+1)) ≤ N(q, n, n′) ≤ qn′(n−n′+1).

If n is large in comparison to n′, the previous lemma essentially tells us that there are about qn′(n−n′) subspaces
of K of dimension n′. There are exactly qnn′
over K, and there are
qnℓ such polynomials with deg λ ≤ qℓ. Heuristically, we may expect that linearized polynomials associated to

monic linearized polynomials of degree qn′

vector spaces are as likely to have small d than other polynomials. We would therefore expect that the number
of vector spaces of dimension n′ such that deg λ ≤ qℓ is about

qn′(n−n′)qn(ℓ−n′) = qnℓ−n′2

.

In particular, we would expect no such polynomial to exist whenever ℓ << n′2

n .

On the other hand, as in Remark 3.1 parameters with ℓ > n′2

n will result in a time complexity worse than
brute force. Hence this approach might only work well for exceptional families of parameters. Indeed an
exceptional family where the heuristic analysis does fail is where n′|n and λ(x) = x, thus ℓ = 0 < n′2
n , and the
subspace is none other than the subfield of degree n′ over Fq. The work of Diem [4] shows that there is an
infinite family of such n and q where the ECDLP can be solved in subexponential time in that case.

In the next section we provide an explicit infinite family of parameters giving quasi-subfield polynomials.

In Appendix C.1, we further study the case of parameters where n is a Mersenne prime.

4.3 A Particular Family

Let F be a field of characteristic p. We recall that to any polynomial f = ∑︀ℓ
a linearized polynomial Lf (X) = ∑︀ℓ

i=0 fi Xqi

∈ F[X]. Moreover this association is such that given any two

i=0 fi Xi ∈ F[X], one can associate

32 | M.-D. Huang et al.

polynomials f1, f2 ∈ F[x], we have

Lf1f2 (X) = Lf1 ∘ Lf2 (X)

where ∘ denotes the polynomial composition [3, Ch. 11]. The polynomial f ∈ F[X] divides Xn − 1 if and only if
Lf (X) divides Xqn

− X.

Lemma 4.3. Let q′ be powers of p. For l ≥ 0 let pi = ∑︀l

i=0 q′i. Then in F[X], where F is any field of characteristic

p, one has for k ≥ 0:

(1 +

k
∑︁

i=0

Xpi )|(Xpk+1 − 1) and hence (X +

Xqpi )|(Xqpk+1 − X).

k
∑︁

i=0

Proof. One has pk+1 = q′pk + 1. Let f = 1 + ∑︀k

i=0 Xpi . Modulo f we find:

0 ≡ Xf q′

= X +

k
∑︁

i=0

X(Xpi )q′

= Xp0 +

k
∑︁

i=0

Xpi+1 = Xpk+1 + f − 1 ≡ Xpk+1 − 1.

We apply the construction in the above lemma to the case F = K = Fqn with n = pk+1. Note that deg(X +
∑︀k
i=0 Xqpi . Note

i=0 Xqpi ) = qpk and that n′ = pk. Furthermore, note that ℓ = pk−1 = logq(deg(λ)) where λ = − ∑︀k−1

that

ℓ = pk−1 =

pk−1pk+1
pk+1

=

pk−1(q′pk + 1)
pk+1

=

(q′pk−1 + 1)pk − (pk − pk−1)
pk+1

=

k

p2
pk+1

−

(pk − pk−1)
pk+1

<

n′2
n

.

Hence our construction gives rise to quasi-subfield polynomials. By picking the right parameters, Remark
3.1 implies that our algorithm will run faster than brute force search. Note that since n ≡ 1 (mod n′), we are

in the worst case scenario of Lemma 4.1. We hope that there are better constructions giving rise to better

complexity estimates.

5 Conclusion and Open Problems

In this paper we introduced quasi-subfield polynomials, which are polynomials over a finite field Fqn of the
form Xqn′

− λ(X) which are nearly split and where λ has small degree. We showed that such polynomials

could lead to faster algorithms for the elliptic curve discrete logarithm problem (ECDLP) over composite fields

when deg λ is small enough. Finally, we investigated the existence of these polynomials, and provided one

particular family leading to an ECDLP algorithm more efficient than exhaustive search.

It remains an open problem to find (or rule out) the existence of quasi-subfield polynomials where deg λ

is small enough to improve on the best (generic) algorithms for ECDLP. A question of particular interest is
whether the bound on deg λ provided by Lemma 4.1 is tight: in fact removing the term n mod n′ in this bound

would show that our approach cannot beat generic algorithms. Besides the construction of better families of

quasi-subfield polynomials, one may hope to beat generic algorithms by generalizing our approach in various

directions: such generalizations could include using a rational function for λ, using an isogeny map for L (as

in [20]), or adapting various tricks also used in other index calculus algorithms such as double large prime,

unsymmetrized and unbalanced variations [12, 13, 18]. We hope that our paper will motivate further work in

these directions.

References

[1]

Leonard M. Adleman, A Subexponential Algorithm for the Discrete Logarithm Prob- lem with Applications to Cryptography

(Abstract), in: FOCS, pp. 55–60, IEEE, 1979.

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 33

[2]

Razvan Barbulescu, Pierrick Gaudry, Antoine Joux and Emmanuel Thomé, A Heuristic Quasi-Polynomial Algorithm for Discrete

Logarithm in Finite Fields of Small Characteristic, in: Advances in Cryptology - EUROCRYPT 2014 - 33rd Annual Interna-

tional Conference on the Theory and Applications of Cryptographic Tech- niques, Copenhagen, Denmark, May 11-15, 2014.
Proceedings, pp. 1–16, 2014.
E. R. Berlekamp, Algebraic coding theory, Aegean Park Press, Laguna Hills, CA, USA, 1984.

[3]

[4] Claus Diem, On the discrete logarithm problem in elliptic curves, Compositio Math- ematica 147 (2011), 75–104.
[5] Whitfield Difle and Martin E. Hellman, New Directions in Cryptography, IT-22 (1976), 644–654.
[6]

Jintai Ding and Timothy J. Hodges, Inverting HFE Systems Is Quasi-Polynomial for All Fields, in: CRYPTO (Phillip Rogaway, ed.),
Lecture Notes in Computer Science 6841, pp. 724–742, Springer, 2011.

[7]

[8]

[9]

Vivien Dubois and Nicolas Gama, The Degree of Regularity of HFE Systems, in: ASIACRYPT (Masayuki Abe, ed.), Lecture Notes
in Computer Science 6477, pp. 557–576, Springer, 2010.

Jean-Charles Faugère, A new eflcient algorithm for computing Gröbner bases (F4)., Journal of Pure and Applied Algebra 139
(1999), 61–88.

Jean-Charles Faugère, A new eflcient algorithm for computing Gröbner bases with- out reduction to zero (F5), in: Proceedings
of the 2002 international symposium on Symbolic and algebraic computation, ISSAC ‘02, pp. 75–83, ACM, New York, NY, USA,
2002.

[10]

Jean-Charles Faugère and Antoine Joux, Algebraic Cryptanalysis of Hidden Field Equation (HFE) Cryptosystems Using Gröbner

Bases, in: CRYPTO (Dan Boneh, ed.), Lecture Notes in Computer Science 2729, pp. 44–60, Springer, 2003.
Jean-Charles Faugère, Ludovic Perret, Christophe Petit and Guénaël Renault, Improving the Complexity of Index Calculus

[11]

Algorithms in Elliptic Curves over Binary Fields, in: EUROCRYPT (David Pointcheval and Thomas Johansson, eds.), Lecture
Notes in Computer Science 7237, pp. 27–44, Springer, 2012.

[12] Steven D. Galbraith and Shishay W. Gebregiyorgis, Summation Polynomial Algo- rithms for Elliptic Curves in Characteristic

Two, in: Progress in Cryptology -IN- DOCRYPT 2014 - 15th International Conference on Cryptology in India, New Delhi, India,
December 14-17, 2014, Proceedings (Willi Meier and Debdeep Mukhopad- hyay, eds.), Lecture Notes in Computer Science
8885, pp. 409–427, Springer, 2014.

[13] P. Gaudry, E. Thomé, N. Thériault and C. Diem, A double large prime variation for small genus hyperelliptic index calculus,

Math. Comp. 76 (2007), 475–492 (elec- tronic).

[14] Pierrick Gaudry, Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem, J.

Symb. Comput. 44 (2009), 1690–1702.

[15] Louis Granboulan, Antoine Joux and Jacques Stern, Inverting HFE Is Quasipolynomial, in: CRYPTO (Cynthia Dwork, ed.), Lecture

Notes in Computer Science 4117, pp. 345–356, Springer, 2006.

[16] Ming-Deh A. Huang, Michiel Kosters and Sze Ling Yeo, Last Fall Degree, HFE, and Weil Descent Attacks on ECDLP, in: Advances
in Cryptology - CRYPTO 2015 - 35th Annual Cryptology Conference, Santa Barbara, CA, USA, August 16-20, 2015, Proceedings,
Part I, pp. 581–600, 2015.

[17] Yun-Ju Huang, Christophe Petit, Naoyuki Shinohara and Tsuyoshi Takagi, Improvement of Faugère et al.’s Method to Solve

ECDLP, in: IWSEC (Kazuo Sakiyama and Masayuki Terada, eds.), Lecture Notes in Computer Science 8231, pp. 115–132,
Springer, 2013.

[18] Antoine Joux and Vanessa Vitse, Elliptic Curve Discrete Logarithm Problem over Small Degree Extension Fields. Application to
q5 ), Cryptology ePrint Archive, Report 2010/157. To appear in Journal of Cryptology.,

the static Difle-Hellman problem on E(F
2010, http://eprint.iacr.org/.

[19] Christophe Petit, Bounding HFE with SRA, https://www.cs.bham.ac.uk/~petitcz/files/SRA_GB.pdf.
[20] Christophe Petit, Michiel Kosters and Ange Messeng, Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem

over Prime Fields, in: Public-Key Cryptography - PKC 2016 - 19th IACR International Conference on Practice and Theory in
Public-Key Cryptography, Taipei, Taiwan, March 6-9, 2016, Proceedings, Part II (Chen-Mou Cheng, Kai-Min Chung, Giuseppe
Persiano and Bo-Yin Yang, eds.), Lecture Notes in Computer Science 9615, pp. 3–18, Springer, 2016

[21] Christophe Petit and Jean-Jacques Quisquater, On Polynomial Systems Arising from a Weil Descent, in: Asiacrypt (Xiaoyun

Wang and Kazue Sako, eds.), Lecture Notes in Computer Science 7658, pp. 451–466, Springer, 2012.

[22] Maurice Rojas, Solving Degenerate Sparse Polynomial Systems Faster, Journal of Symbolic Computation 28 (1999), 155–186.
Igor Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves, Cryptology ePrint Archive, Report
[23]
2004/031, 2004, http://eprint.iacr.org/.

[24] Michael Shantz and Edlyn Teske, Solving the Elliptic Curve Discrete Logarithm Problem Using Semaev Polynomials, Weil

Descent and Gr¨bner Basis Methods - An Experimental Study, in: Number Theory and Cryptography - Papers in Honor of
Johannes Buchmann on the Occasion of His 60th Birthday, pp. 94–107, 2013.

[25] Douglas H. Wiedemann, Solving sparse linear equations over finite fields, IEEE Trans. Information Theory 32 (1986), 54–62.

34 | M.-D. Huang et al.

A Omitted Proofs

A.1 Proof of Lemma 3.1

Proof. The polynomial system has m equations S(k) = 0 in m variables. The summation polynomial Sm+1 has
degree 2m−1 in each variable, and each application of φ increases the degree by a factor d in each variable,
so the polynomial S(k) has degree dk−12m−1 in each variable.

We compute the quantities M(E), R(¯E) and S(¯E) in Theorem 2.1 of [22]. Following the notations of [22]
paper, Ek is the fundamental hypercube of dimension m and length dk−12m, and Em+1 = △ is the pyramid
whose edges are all fundamental vectors. For k = 1, . . . , m, let λk = dk−12m−1, and let λm+1 = (m!)−1. We have

M(E) = Vol(E1, . . . , Em) =

m
∏︁

k=1

λk = 2m(m−1)d

m(m−1)
2

.

R(¯E) =

m+1
∏︁

λk

m+1
∑︁

k=1

k=1

λ−1

k ≤ M(E) +

m
2m−1m!

M(E) ≤ 2M(E) = 2m2−m+1d

m(m−1)
2

.

Mave

¯E =

)︃m

(︃

1
m + 1

m+1
∑︁

k=1

λk

≤ λm

m = (2d)m(m−1),

S(¯E) = O

(︁√

mem(2d)m(m−1))︁

.

We have

We finally have

hence

Applying [22, Theorem 2.1], we obtain that Rojas’ algorithm requires

(︁

m5.18827.376m2−3.948m+2d4.876m2−4.876m)︁

˜O

= ˜O

(︁

m5.188(3d)4.876m2 )︁

arithmetic steps.

The univariate polynomials produced by Rojas’ algorithm are of degree bounded by M(E). Over finite fields,

root-finding is quasi-linear in this degree, and its cost can be neglected in the overall complexity estimation.

A.2 Proof of Lemma 4.1

Proof. To simplify notations, let us assume that λ is defined over Fq (the general proof follows the same lines).
One has

Xq2n′

≡ (Xqn′

)qn′

≡ λ(X)qn′

≡ λ(Xqn′

) = λ(λ(X)) mod L(X).

Recursively, we have

Xqn′ k

≡ λ ∘ λ ∘ . . . ∘ λ(X) mod L(X)

where λ is composed k times with itself in this formula. We then have

Xqn

≡ (λ ∘ λ ∘ . . . ∘ λ(X))qn mod n′

mod L(X)

where λ is composed ⌊ n

n′ ⌋ times with itself in this formula. Since Xqn

≡ X mod L(X), we deduce the result.

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 35

A.3 Proof of Lemma 4.2

Proof. We have N(q, n, n′) = N1(q,n,n′)
q that are
linearly independent over Fq, and N2 is the number of such choices defining the same vector space. One has
qn − q2)︁

N2(q,n,n′) , where N1 is the number of choices of n′ elements over Fn

N1 = (︀qn − 1)︀ (︀qn − q)︀ (︁

qn − qn′−1)︁

≤ qnn′

. . .

(︁

.

Also, one finds, using that for 0 ≤ ϵ ≤ 1 one has (1 − ϵ)n ≥ 1 − nϵ:

N1 ≥ qnn′

(1 − qn′−1−n)n′

≥ qnn′

· (1 − n′q(n′−1)/n).

Furthermore, one finds

q(n′−1)n′

≤ N2 =

(︁

qn′

)︁ (︁

qn′

− q

)︁ (︁

qn′

− q2)︁

− 1

. . .

(︁

qn′

− qn′−1)︁

< qn′2

.

Since N = N1/N2, the result follows.

B On the dimension of our polynomial systems

Throughout this section we let K = Fqn , K the algebraic closure of K, and A = K[X1, . . . , Xm]. If S is a set of
|F(P) = 0 for all F ∈ S}. If I is an ideal of A, then
polynomials in A, then Z(S) denotes the zero set {P ∈ K

m

V(I) ⊂ SpecA denotes the set of all prime ideals which contain I. Note that Z(S) is finite if dim ℘ = 0 for all

prime ideal ℘ ∈ V(I) where I is the ideal generated by S.

In our algorithm, finding a relation is reduced to solving a polynomial system S = {S(i), i = 0, . . . , m − 1}.
Here S(0)(X1, X2, . . . , Xm) = Sm+1(X1, X2, . . . , Xm , ξR) where ξR is the x-coordinate of a point R which is a
random linear combination of the points P and Q, and inductively S(i+1) = φ(S(i)) for i ≥ 0, where φ : A → A :
f (X1, X2, . . . , Xm) → Fn′

(f )(λ(X1), λ(X2), . . . , λ(Xm)), which is a ring morphism. Here F raises the coefficients
of a polynomial to the power q, and λ is a polynomial. In the main text we make the heuristic assumption

that for random R, Z(S) is likely finite. The goal of this section is to provide theoretical analysis in support of

this heuristic assumption.

If I be an ideal of A, then Iφ denotes the ideal generated by φ(I). Let I(0) = I and inductively I(i+1) =
(I(i))φ for i ≥ 0. Let Ji be the ideal generated by I(0) ∪ . . . ∪ I(i) for i ≥ 0. Our goal is to characterize when
dim Z(Jm−1) is 0. The situation considered in our algorithm is a special case where I is the ideal generated by
Sm+1(X1, X2, . . . , Xm , ξR).

φ
→ v if dim u = dim v and vφ ⊂ u. We will show that for every u ∈ SpecA,

For u, v ∈ SpecA, we write u
φ

there is a unique v such that u

→ v. In fact v = φ−1(u).

. . .

φ

We say that a sequence of prime ideals u0, ..., ui in SpecA is a φ-chain of length i led by u0 if u0
→ ui. We will show that for i ≥ 0, V(Ji) is the set ℘ ∈ V(I) such that ℘ leads a φ-chain of length i in V(I).
There are only finitely many minimal primes in V(I). In general it is likely the case that there are no

→ u1

φ

φ
→

minimal primes u and v in V(I) such that u

→ v, in which case dim J1 < dim I. Inductively there are finitely
many minimal prime ideals in V(Ji), each leading a φ-chain of length i. It is likely that there are no minimal
primes u and v in V(Ji) such that u
→ v, in which case no minimal prime in V(Ji) leads a φ-chain of length
i + 1, hence dim Ji+1 < dim Ji. Consequently Jm−1 is likely of dimension 0.

φ

In our situation I is the ideal generated by Sm+1(X1, X2, . . . , Xm , ξR), and the heuristic assumption is
that for R being a random combination of P and Q the ideal I is likely in the good case hence Jm−1 is likely of
dimension 0.

The rest of this section is devoted to proving the above-mentioned property of φ-chains and characteri-

zation of Ji in terms of φ-chains in V(I).

It is easy to see that φ : A → A is an integral ring morphism, that is A is integral over φ(A). Therefore if

u ∈ SpecA, φ−1(u) ∈ SpecA and dim u = dim φ−1(u). Let v = φ−1(u). Then φ(v) ⊂ u, so vφ ⊂ u, so u

Let w ∈ SpecA. If dim w = dim u and wφ ⊂ u. Then φ(w) ⊂ u. So w ⊂ φ−1u = v. Since dim w = dim u =

dim v, we must have w = v. We have proved the following:

φ
→ v.

φ

36 | M.-D. Huang et al.

Lemma B.1. Let u ∈ SpecA. Then there is a unique v ∈ SpecA such that u

φ

→ v. In fact v = φ−1(u).

Theorem B.2. Suppose I is an ideal of A. Let J be the ideal generated by I and Iφ. Then V(J) = {℘|℘

φ
→ u and

℘, u ∈ V(I)}.

To prove the theorem, observe that for ℘ ∈ SpecA, ℘ ∈ V(J) if and only ℘ ∈ V(I) and ℘ ∈ V(Iφ).

It is straightforward to verify that for ℘ ∈ SpecA,

From Lemma B.1 it follows that

Iφ ⊂ ℘ ⇔ φ(I) ⊂ ℘ ⇔ I ⊂ φ−1(℘).

V(J) = {℘|℘

φ
→ u and ℘, u ∈ V(I)}.

The theorem is proved.

The main result of this section is the next theorem.

Theorem B.3. The set V(Ji) consists of primes ℘ ∈ V(I) that leads a φ-chain of length i in V(I). In particular,
dim Jm−1 = 0 if and only if every φ-chain of length m − 1 in V(I) is of dimension 0.

Proof of Theorem B.3 The case i = 1 follows directly from Theorem B.2. For i > 1, since V(Ji) = V(Ji−1 ∪
→ u1 with u1 ∈ V(Ji−1).
(Ji−1)φ), Theorem B.2 implies that V(Ji) consists of primes ℘ ∈ V(Ji−1) such that ℘

φ

By induction since u1 ∈ V(Ji−1), u1 leads a φ-chain of length i − 1 in V(I). That is, u1
u2, . . . , ui ∈ V(I). So ℘

→ ui. That is ℘ leads a φ-chain of length i in V(I).

→ u2 . . .

→ u1

φ

φ

φ

φ

→ u2 . . .

→ ui with

φ

φ

φ

φ

For the converse suppose ℘ leads a φ-chain of length i in V(I). Thus ℘

→ ui with
℘, u1, . . . , ui ∈ V(I). Applying induction to ℘, u1, ..., ui−1 we conclude that ℘ ∈ V(Ji−1). Similarly apply-
ing induction to u1, ..., ui we conclude that u1 ∈ V(Ji−1). Since ℘
→ u1, Theorem B.2 implies that ℘ ∈ V(Ji).
This completes the proof of the theorem.

→ u2 . . .

→ u1

φ

C Further comments on the existence of quasi-subfield

polynomials

In this section we further develop our analysis of additive subgroups of Fqn , specializing to the case of
Mersenne prime degree extensions when q = 2.

We also investigate the case of multiplicative subgroups of F*

qn .

C.1 Mersenne Prime Degree Extensions over F2

We first expand on the construction of Section 4.2.

A plausible attempt for finding good parameters is to seek for parameters such that the polynomial Xn − 1
has many small degree factors over Fq. This polynomial is then a priori more likely to have a large number of
(non necessarily irreducible) factors of degree n′, maximizing the chance that one of these factors is sparse

enough. We would then take L as the linearized polynomial corresponding to that factor.

Mersenne prime degree extensions of F2 look particularly promising in that respect. Indeed when n =

2k − 1 is prime, the polynomial (Xn − 1)/(X − 1) has (n − 1)/k irreducible factors of degree k over F2.

In the following, let N(k, n′) be the number of distinct polynomials of degree n′ that divide Xn −1 ∈ F2[X].

We have:

Lemma C.1. Let k such that n = 2k − 1 is prime. Then N(k, n′) = (︀ ⌊n/k⌋
otherwise.

⌊n′/k⌋

)︀ if n′ mod k ∈ {0, 1}, and N(k, n′) = 0

Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem | 37

Note that we have

)︃

(︃

n/k
n′/k

log

≈ (n′/k) log(n/k) − (n′/k) log(n′/k) ≈ (n′/k) log(n/n′) ≈ (n′/k) log m.

The number of monic polynomials of degree n′ over F2 is 2n′

, and there are 2ℓ such polynomials of the

form Xn′
+ s(X) with s(X) of degree at most ℓ. Heuristically assuming that the density of “sparse enough”
polynomials is identical for factors of Xn − 1 and for random polynomials, we expect that the number of
polynomials of degree n′ that divide Xn − 1 and are sparse enough can be approximated by

N(k, n′)2ℓ−n′

.

In particular, the existence of such polynomials a priori depends on whether ℓ is bigger or smaller than n′ −
(n′/k) log m.

To improve on generic algorithms, we want ℓ < 0.102 n

m2 as in Remark 3.1. Together with the above con-

straint on ℓ, this leads to a constraint

Using mn′ ≈ n and k = log n, this inequality implies

0.102n/m2 > n′ − (n′/k) log m.

log n′
n′

< 0.102

log n
n

but on the other hand we have log n/n < log n′/n′ since n′ < n. We conclude that this approach cannot lead

to interesting parameters for our attack, unless the above probabilistic argument fails significantly.

C.2 Multiplicative Subgroups

We now attempt to construct V as a multiplicative subgroup of K*. Such a subgroup can be characterized by

an equation of the form

Xr − 1 = 0

where r is a divisor of qn − 1. Let n′ ≥ logq r. The above equation implies

L(X) := Xqn′

− Xa = 0

where a := qn′
addition to the subgroup of order r.

mod r. Note that the set V corresponding to this polynomial L contains the element 0 in

In this context, we note the following generalization of Lemma 4.1:

Lemma C.2. Suppose that ℓ := logq d = logq deg λ > 0. Then we have

⌋︁

⌊︁ n
n′

ℓ + (n mod n′) ≥ logq |V|.

Proof. There exists a polynomial a(X) of degree 2n′
Following the same reasoning as for Lemma 4.1, we obtain an inequality

− |V| such that L(X) = Xqn′

+ λ(X) divides (Xqn

− X)a(X).

n

n′ q(n mod n′) + deg a ≥ qn′

d

from which we deduce the result.

It is a priori a good idea to choose q and n such that qn − 1 has many distinct small prime factors, as this will
give more options for r. The number of choices for r is maximal when qn − 1 has n log q/ log(n log q) distinct

prime factors bounded by log(n log q). In that case there are approximately

(︃

n log q/ log(n log q)
n′ log q/ log(n log q)

)︃

38 | M.-D. Huang et al.

options for r. In general, we expect far less options for r.

We observe the similarity of this formula with the value of N(k, n′) given by Lemma C.1 for the Mersenne

case. We similarly do not expect to improve on generic algorithms this way, except maybe for exceptional

parameters.

