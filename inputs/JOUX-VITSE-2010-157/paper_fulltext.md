<!-- Extracted 2026-09-20 from ePrint 2010/157 (Joux–Vitse). pdfminer.six. NOT hand-cleaned. -->

Elliptic Curve Discrete Logarithm Problem over Small Degree
Extension Fields
Application to the static Diﬃe-Hellman problem on E(Fq5)

Antoine Joux1 and Vanessa Vitse2

1 DGA and Universit´e de Versailles Saint-Quentin, Laboratoire PRISM, 45 avenue des ´Etats-Unis, F-78035
Versailles cedex, France
antoine.joux@m4x.org
2 Universit´e de Versailles Saint-Quentin, Laboratoire PRISM, 45 avenue des ´Etats-Unis, F-78035 Versailles cedex,
France
vanessa.vitse@prism.uvsq.fr

Abstract. In 2008 and 2009, Gaudry and Diem proposed an index calculus method for the resolution of
the discrete logarithm on the group of points of an elliptic curve deﬁned over a small degree extension
ﬁeld Fqn . In this paper, we study a variation of this index calculus method, improving the overall
asymptotic complexity when log q ≤ cn3. In particular, we are able to successfully obtain relations on
E(F
p5 ), whereas the more expensive computational complexity of Gaudry and Diem’s initial algorithm
makes it impractical in this case. An important ingredient of this result is a new variation of Faug`ere’s
Gr¨obner basis algorithm F4, which signiﬁcantly speeds up the relation computation and might be of
independent interest. As an application, we show how this index calculus leads to a practical example
of an oracle-assisted resolution of the elliptic curve static Diﬃe-Hellman problem over a ﬁnite ﬁeld on
130 bits, which is faster than birthday-based discrete logarithm computations on the same curve.

Key words: elliptic curve, discrete logarithm problem (DLP), index calculus, Gr¨obner basis compu-
tation, summation polynomials, static Diﬃe-Hellman problem (SDHP)

1 Introduction

Given a ﬁnite group G and two elements g, h ∈ G, the discrete logarithm problem (DLP) consists in computing
– when it exists – an integer x such that h = gx. The diﬃculty of this problem is at the heart of many existing
cryptosystems, such that the Diﬃe Hellman key exchange protocol [11], the Elgamal encryption and signature
scheme [13], DSA, or more recently in pairing-based cryptography. Historically, the DLP was ﬁrst studied
in the multiplicative group of ﬁnite ﬁelds. In such groups, now-standard index calculus methods allow to
solve the DLP with a subexponential complexity. Therefore, the key size necessary to achieve a given level
of security is rather large. For this reason, in 1985, Miller [26] and Koblitz [22] suggested using for G the
group of points of an algebraic curve, thus introducing elliptic curves to the cryptography community.

Up to now, very few algorithms exist that solve the DLP in the group of points of an elliptic curve
deﬁned over a ﬁnite ﬁeld (ECDLP). In most cases, only generic methods such as Baby-step Giant-step [33]
or Pollard’s rho and kangaroo algorithms [28, 29] are available. Their complexity is exponential in the size
of the largest prime factor of the group cardinality; more precisely, the running time is of the order of the
square root of this largest prime factor [27]. However, for some speciﬁc curves more powerful attacks can be
applied; they usually move the DLP to another, weaker group. The ﬁrst approach is to lift the ECDLP to
a characteristic zero ﬁeld, either global (i.e. Q) or local (i.e. p-adic numbers Qp): so far, this works only for
subgroups of E(Fpn ) of order pi [30, 32, 35]. The second approach is to transfer via the Weil or Tate pairing
the DLP on E(Fq) to F∗
qk : this includes the MOV [25] and FR [17] attacks for elliptic curves with small
embedding degree k. The last approach is to transfer via Weil descent the DLP on an elliptic curve deﬁned
over an extension ﬁeld Fqn to a second algebraic curve, deﬁned over Fq but of greater genus g; this is eﬃcient
when the resulting genus g is small, which occurs only with speciﬁc curves [8].

2

Antoine Joux and Vanessa Vitse

In [31], Semaev proposed for the ﬁrst time an index calculus method for the ECDLP, which unfortunately
turned out to be impracticable. However, combining Semaev’s ideas and Weil restriction tools, Gaudry and
Diem [10, 18] independently came up with an index calculus attack of subexponential complexity for elliptic
curves deﬁned over small degree extension ﬁelds. More precisely, the complexity of their algorithm over
E(Fqn ) for n ﬁxed is in ˜O(q2−2/n), but with a hidden constant in n that grows over-exponentially (in
O(n! 23n(n−1))). If one also allows n to go to inﬁnity, then the complexity remains subexponential as long as
n is upper bounded by O((cid:112)log(q)).

In this article, we investigate a variant of Gaudry and Diem’s attack and obtain the following result,
which implies that this new approach is better than generic methods like Pollard’s rho when n ≤ c log q, and
√
better than Gaudry and Diem’s when n ≥ c(cid:48) 3

log q for some constants c and c(cid:48).

Theorem 1 Let E be an elliptic curve deﬁned over Fqn and G a cyclic subgroup of its group of rational
points. Then there exists an algorithm to solve the DLP in G with asymptotic complexity

(cid:16)

˜O

(n − 1)!

(cid:16)

2(n−1)(n−2)en n−1/2(cid:17)ω

q2(cid:17)

where ω, 2 ≤ ω < 3, is the linear algebra constant of [2].

O(log q)

[Pollard]

[this work]

[Gaudry-Diem]

n

12
11
10
9
8
7
6
5
4
3
2
1

√
O( 3

log q)

log q

Fig. 1. Comparison of three attacks on the ECDLP over Fqn , n ≥ 1.

The paper is organized as follows. First, we give a summary of Gaudry and Diem’s index calculus; the
main ideas are the use of the Weil restriction to obtain a convenient factor base and of Semaev’s summation
polynomials to test decomposition. More precisely, Gaudry and Diem check whether a given point can be
decomposed as a sum of n points of this factor base, where n is the degree of the extension ﬁeld. This
amounts to solving a multivariate polynomial system of n equations in n variables of degree 2n−1, arising
from the (n + 1)-th summation polynomial. Next, we introduce our variant: we check if a point decomposes
as a sum of n − 1 points instead of n. This reduces the likelihood of ﬁnding a relation, but greatly speeds
up the decomposition process; as mentioned above, this trade-oﬀ is favorable when n is bigger than some
√
multiple of 3
log q. We then give a detailed analysis of the complexity of our variant, enabling us to prove
Theorem 1, and show that our trade-oﬀ is better than the one provided by the hybrid approach of [4].

The following sections are devoted to several optimizations of the decomposition process. As already
noted by Gaudry, the polynomial system that has to be solved is inherently symmetrical, so it pays oﬀ to
reduce its total degree by writing down the equations in terms of the elementary symmetric functions before
the resolution. A convenient way to do so is to use (partially) symmetrized summation polynomials instead
of Semaev’s; in section 3, we sketch two diﬀerent ways to directly compute these polynomials. More details
are given in appendix A. The second optimization concerns the resolution of the symmetrized system. The
fastest available method is to compute a Gr¨obner basis for an appropriate monomial order, using one of
Faug`ere’s algorithms [14, 15]. Since each relation search leads to a system with the same speciﬁc shape, we
propose an ad hoc variant of F4 which takes advantage of this particularity to remove all reductions to zero.

Title Suppressed Due to Excessive Length

3

Finally, in order to give a practical application of our idea on a problem of cryptographic interest, we
present a variation of our algorithm which solves the oracle-assisted static Diﬃe-Hellman problem (SDHP,
introduced in [6]) over E(Fqn ). As in the case of ﬁnite ﬁelds presented in [21], solving the SDHP, after some
oracle queries, is faster than solving the corresponding discrete logarithm problem. More precisely, we show
that an attacker is able, after (cid:39) q/2 well-suited oracle queries, to compute an arbitrary SDHP instance
reasonably quickly. To give a concrete example, we show that such an attack is currently achievable for a
random elliptic curve deﬁned over a ﬁnite ﬁeld Fq5 of size 130 bits and requires much less computing power
than a discrete logarithm computation using generic methods on the same group.

2 Index calculus attacks for elliptic curve over an extension ﬁeld

We begin by brieﬂy recalling the principle of index calculus methods. We consider a ﬁnite group G (for
simplicity, we assume G has prime order r) and two elements h, g ∈ G such that h = [x]g (in additive
notation), where x is the secret to recover. The basic outline of Dixon’s “precomputation-and-descent”
approach consists in four main steps:

1. Choice of a factor base, i.e. a family F = {g1, . . . , gN } of elements of G
2. Relation search: for “random” integers ai, decompose – if possible – [ai]g into the factor base, i.e. write

[ai]g =

N

(cid:88)

[ci,j]gj

(1)

j=1

3. Linear algebra: once k relations have been found where k is large enough, construct the vector A =
, and solve the linear system M X = A. It admits a unique

1≤i≤k and the matrix M = (ci,j) 1≤i≤k

(cid:0)ai

(cid:1)

1≤j≤N

solution that can be computed with elementary linear algebra as soon as k is greater than N and the
relations are linearly independent. The resulting vector X contains the logarithms w.r.t. g of the factor
base elements.

4. Descent step: ﬁnd an equation

[a]g + [b]h =

N

(cid:88)

[cj]gj,

(2)

j=1

with b (cid:54)= 0 and deduce the logarithm of h.
For example, if G is the multiplicative group of Fp, p prime, we can take for F the set of equivalence
classes of prime integers smaller than a ﬁxed bound B. An element is then decomposable in this factor base
if its representative in [1, p − 1] is B-smooth. There is obviously a compromise to be found: if B is large, then
most elements are decomposable, but many relations are necessary and the matrices involved in the linear
algebra step are comparatively large. On the other hand, if the factor base is small, the required number
of relations is small and the linear algebra step is fast, but ﬁnding a relation is much less probable. In any
case, the matrix M is usually very sparse and appropriate techniques are used to compute its kernel quickly.
Note that for discrete logarithm computations on ﬁnite ﬁelds, the descent step becomes quite involved (for
example, see [21]), but in our setting it will be no diﬀerent from a standard relation search. One major
obstruction to index calculus when G is a subgroup of rational points of an elliptic curve deﬁned over Fq,
is that there exist no obvious factor bases. The second, related diﬃculty is that decomposing an element
as in (1) or (2) is really not straightforward. In [31], Semaev proposes the ﬁrst eﬃcient way to ﬁnd such
decomposition, yet, his approach could not work for lack of an adequate factor base.

2.1 The versions of Gaudry and Diem

In [10, 18], Gaudry and Diem propose to apply an index calculus method in the group of rational points of
elliptic curves deﬁned over small degree extension ﬁelds. To do so, they combine ideas from Semaev’s index

4

Antoine Joux and Vanessa Vitse

calculus deﬁnition and Weil descent attack, to get a multivariate polynomial system that one can solve using
Gr¨obner basis techniques. More precisely, if E is an elliptic curve deﬁned over Fqn , their choice of factor base
is the set of points whose x-coordinate lies in the base ﬁeld: {P ∈ E(Fqn ) : P = (xP , yP ), xP ∈ Fq, yP ∈ Fqn }.
Actually, since this set is invariant under negation, it is possible to consider only one half of it; more precisely,
if E is given in reduced Weierstrass form in characteristic diﬀerent from 2 or 3, the factor base becomes:

F = {P ∈ E(Fqn ) : P = (xP , yP ), xP ∈ Fq, yP ∈ S}

where S is a subset of Fqn such that Fqn = S ∪ (−S) and S ∩ (−S) = {0} (for example, assuming that −1
is not a square in Fqn , we can choose for S the set of quadratic residues together with 0). The same kind of
twofold reduction can also be done for a general equation of E.

To compute the discrete logarithm of Q ∈ (cid:104)P (cid:105) with an index calculus algorithm, we ﬁrst need to ﬁnd
relations, i.e. to decompose combinations of the form R = [a]P or R = [a]P + [b]Q where a, b are random
integers, as sum of points in F. Following Semaev’s idea, Gaudry suggests to consider only relations of the
form:

R = ±P1 ± P2 ± . . . ± Pn

(3)

where n is the degree of the extension ﬁeld and Pi ∈ F (1 ≤ i ≤ n). Getting such relations can be
done by using a Weil restriction process. One considers Fqn as Fq[t]/(f (t)) where f (t) is an irreducible
polynomial of degree n over Fq, in order to represent points P = (xP , yP ) ∈ E(Fqn ) by 2n coordinates:
xP = x0,P + x1,P t + . . . + xn−1,P tn−1 and yP = y0,P + y1,P t + . . . + yn−1,P tn−1. Instead of writing down
an equation with (n + 1)n indeterminates from the decomposition (3), it is rather convenient to use the
Semaev’s summation polynomials to get rid of the yPi variables. We recall here the deﬁnition and properties
of such polynomials.

Proposition 2 Let E be an elliptic curve deﬁned over a ﬁeld K. The m-th Semaev summation polynomial
is an irreducible symmetric polynomial fm ∈ K[X1, . . . , Xm], of degree 2m−2 in each variable, such that given
P1 = (xP1 , yP1 ), . . . , Pm = (xPm , yPm ) ∈ E(K) \ {O}, we have

fm(xP1 , . . . , xPm) = 0 ⇔ ∃(cid:15)1, . . . , (cid:15)m ∈ {1, −1}, (cid:15)1P1 + . . . + (cid:15)mPm = O.

These summation polynomials can be eﬀectively computed by induction, see [31] or the appendix. At

this point, we replace (3) by the equivalent equation

fn+1(xP1, . . . , xPn , xR) = 0,

(4)

using the (n + 1)-th summation polynomial fn+1 ∈ Fqn [X1, . . . , Xn+1]. The unknowns xP1, . . . , xPn actually
lie in Fq, so if we sort (4) according to powers of t, we obtain (cid:80)n−1
i=0 ϕi(xP1, . . . , xPn ) ti = 0 where each
ϕi is a symmetric polynomial over Fq, of degree at most 2n−1 in each variable (and depending on xR, a
and b). This leads to a system of n symmetric polynomials. As advised by Gaudry, it can be written as a
system of polynomials of total degree 2n−1 in terms of the elementary symmetric functions e1, . . . , en of the
variables xP1, . . . , xPn . Given the (n + 1)-th summation polynomial, writing down such a system is almost
immediate, but solving it is much more complicated. An eﬃcient way to solve this multivariate polynomial
system is to compute a reduced Gr¨obner basis for the lexicographic order. This yields a univariate polynomial
whose degree is generically 2n(n−1) in this case. Unfortunately, even the best known algorithms [14–16] have
complexity at least polynomial in 2n(n−1), which renders this attack unfeasible for n ≥ 5 on current personal
computers.

Once we get enough equations like (3), we proceed to the linear algebra step. After collecting k > #F (cid:39)

q/2 distinct (independent) relations of the form:

[ai]P =

N

(cid:88)

j=1

[ci,j]Pj, where N = #F, ci,j ∈ {0; 1; −1} and

N

(cid:88)

j=1

|ci,j| = n,

we get a vector A = (ai)1≤i≤k and a matrix M = (ci,j) whose right-kernel is trivial and which is very sparse
since it has only n entries per row. The equation M X = A has thus a unique solution in Z/ord(P )Z, which
yields the discrete logarithms of the factor base elements. A single decomposition of [a]P + [b]Q with b (cid:54)= 0
then suﬃces to obtain the logarithm of Q.

Title Suppressed Due to Excessive Length

5

Complexity estimate of Gaudry and Diem’s algorithm

The ﬁrst main step of the algorithm consists of collecting around #F (cid:39) q/2 relations of the form (3) to build
the matrix M . The (n + 1)-th summation polynomial can be determined once for all using P oly(e(n+1)2
log q)
operations for a ﬁxed elliptic curve [10]. The representation of this summation polynomial in terms of
elementary symmetric functions can be done by using Gr¨obner elimination techniques for example, we refer
to section 3 for improvements of this computation. The probability of ﬁnding one decomposition of a point
R ∈ E(Fqn ) is approximately

#(F ∪ −F)n/Sn
#E(Fqn )

(cid:39)

qn

n!

1

qn =

1

n!

,

and the cost of checking if the point R is actually decomposable in the factor base, noted c(n, q), is the cost
of the resolution of a multivariate polynomial system of n equations deﬁned over Fq with n variables of total
degree 2n−1. As we need at least #F relations, the total complexity of the ﬁrst step is about n! c(n, q) q/2.

The estimation of the cost c(n, q) is not straightforward as it thoroughly depends on the algorithm used.
Following Diem’s analysis [10], the polynomial system considered is generically of dimension 0 since it has a
ﬁnite number of solutions over Fq, and using resultant techniques we get an upper bound for c(n, q):

c(n, q) ≤ P oly(n! 2n(n−1) log q).

The sparse linear algebra step can then be done in a time of ˜O(nq2) with Lanczos or Wiedemann’s
algorithm [8]. However, in order to improve the complexity of the algorithm, Gaudry suggests to rebalance
the matrix-building cost against the linear algebra cost using “large primes” techniques adapted from [19]
and [36] (see [18] for more details). By doing so, he needs to collect approximately q2−2/n relations instead
of q. The cost of the ﬁrst main step becomes thus n! c(n, q) q2−2/n. By contrast, the cost of the linear algebra
step is reduced to ˜O(n q2−2/n), which is negligible compared to the previous step. As a result, the elliptic
curve discrete logarithm problem over Fqn for ﬁxed n can be solved in an expected time of ˜O(q2−2/n), but
the hidden constant grows extremely fast with n. A complete complexity estimate using Diem’s bound is:

n! P oly(n! 2n(n−1) log q) q2−2/n.

2.2 Our version

The bad behaviour (over-exponential) in n occurring in the complexity of Gaudry and Diem’s algorithm
remains a serious drawback and makes their approach practical only for very small extension degrees, namely
n = 3 or 4. Since the cost of the multivariate system resolution heavily depends on the degree of the
summation polynomial, the complexity can be considerably improved by considering only decompositions
of combinations R = [a]P or R = [a]P + [b]Q as sum of (n − 1) points in F, instead of n points as in [10,
18]. Even though we are lowering the probability of getting such a decomposition when q grows, the gain is
suﬃcient to make this approach realistic for n = 5.

We can solve the equation:

[a]P + [b]Q = ±P1 ± . . . ± Pn−1,

(5)

6

Antoine Joux and Vanessa Vitse

where a and b are random integers and the Pi belong to F, in the same way as explained in the previous sec-
tion. The diﬀerences are that only the n-th summation polynomial is involved, and that the resulting system
of n polynomials is in (n − 1) variables and of total degree only 2n−2. Since this system is overdetermined,
its resolution is greatly sped up, as compared to the previous case. The trade-oﬀ is that it is less probable to
ﬁnd a decomposition. More precisely, the probability that a given point R decomposes into the factor base
is about

#(F ∪ −F)n−1/Sn−1
#E(Fqn )

= O

q→∞

(cid:18)

1

q(n − 1)!

(cid:19)

.

As mentioned, the cost of trying to ﬁnd this decomposition, noted ˜c(n, q), is reduced to the cost of the
resolution of an overdetermined multivariate polynomial system of n equations with (n − 1) variables of total
degree 2n−2. Consequently, the complexity of the relation search step becomes (n − 1)! ˜c(n, q) q2/2.

The value of ˜c(n, q) has to be compared to the cost c(n − 1, q): clearly we have ˜c(n, q) < c(n − 1, q).
Indeed, solving a system of n equations with (n − 1) variables of degree 2n−2 can be achieved by solving the
system consisting of the ﬁrst (n − 1) equations, and by checking the compability of the solutions with the
last equation. With such an upper bound of ˜c(n, q), we obtain the complexity for the ﬁrst collecting step of

(cid:16)

O

(n − 1)! q2P oly((n − 1)! 2(n−1)(n−2) log q)

(cid:17)

(6)

The linear algebra step has a complexity of ˜O(nq2), which is negligible compared to the ﬁrst step. Hence
the total complexity of the algorithm is given by (6). We emphasize that because of the q2 factor in the
complexity, Pollard’s rho or other generic methods remain faster than our variant for n ≤ 4. Thus our
approach is actually relevant only for n ≥ 5. On the other hand, with estimate (6) it is asymptotically faster
than generic methods as soon as n ≤ c log q for some constant c.

However, the resultant method yielding (6) is not optimal. A much faster way of solving the overde-
termined polynomial system is to compute a Gr¨obner basis of the corresponding zero-dimensional ideal.
Generically, this ideal is the whole polynomial ring and the corresponding set of solutions is empty. Ex-
ceptionally, i.e. when the decomposition exists, the set of solutions contains a very small number of points
(a single point in most cases), and this can be found directly by using a degree-reverse-lexicographic order
Gr¨obner basis. This is in stark contrast with the situation in Gaudry and Diem’s algorithm, where the solu-
tion set generically contains 2n(n−1) points although most of them lie in an extension of Fq. In their setting,
the computation of a degrevlex Gr¨obner basis is not suﬃcient to solve the system; an elimination order basis
is needed instead, whose computation (using for instance FGLM [16]) has a rather important cost.

In order to derive eﬀective upper bounds for the complexity of a Gr¨obner basis computation, it is necessary
to make some additional hypotheses on a zero-dimensional system {f1, . . . , fm}. For instance, one can assume
that the sequence {f1, . . . , fm} is semi-regular [2, 3] or that the set of solutions of the homogeneized system
has no positive dimension component at inﬁnity [24]. These properties hold generically and have been veriﬁed
in all our experiments with systems arising from (5). They imply that the maximum degree of polynomials
occurring during the computation of the Gr¨obner basis is bounded by the degree of regularity dreg of the
homogeneized system, which is itself smaller than the Macaulay bound (cid:80)m
i=1(deg fi − 1) + 1. Using the fact
that the system in our variant is composed of n polynomials of degree 2n−2 in n − 1 variables, we obtain that
dreg ≤ n2n−2 − n + 1. The standard algorithms for Gr¨obner bases (e.g. Buchberger [7], Faug`ere’s F4 and F5
[14, 15]) can be reduced to the computation of the row echelon form of the dreg-Macaulay matrix (cf [24]),

which has in our case at most

columns and a smaller number of lines. Using fast reduction

(cid:18)n − 1 + dreg
dreg

(cid:19)

techniques, we obtain the following bound:

˜c(n, q) = ˜O

(cid:18)(cid:18)n − 1 + dreg

(cid:19)ω(cid:19)

dreg

= ˜O

(cid:16)(cid:16)

2(n−1)(n−2)en n−1/2(cid:17)ω(cid:17)

,

where ω is the exponent in the complexity of matrix multiplication. This directly implies our main theorem:

Theorem 1 With the above assumptions, the complexity of our algorithm is

(cid:16)

˜O

(n − 1)!

(cid:16)

2(n−1)(n−2)en n−1/2(cid:17)ω

q2(cid:17)

(7)

Title Suppressed Due to Excessive Length

7

In the same spirit, we can also try to sharpen the estimate of the complexity of Gaudry and Diem’s
algorithm. However, since ω < 3, we ﬁnd that the cost of the degrevlex Gr¨obner basis computation is
dominated by the cost of the ordering change, whose complexity is in O (cid:0)(2n(n−1))3(cid:1). An easy computation
√
then shows that our approach is asymptotically faster, provided n ≥ c(cid:48) 3

log q for some constant c(cid:48).

2.3 Comparison with the hybrid approach

We have seen that the main diﬃculty in Gaudry and Diem’s algorithm is the resolution of the polynomial
system. Recently, Bettale et al. [4] have proposed a hybrid approach for solving such systems: the idea is
to ﬁnd a solution by exhaustive search on some variables and Gr¨obner basis computations of the modiﬁed
systems where the selected variables have been specialized (i.e. evaluated). It is thus a trade-oﬀ between
exhaustive search and Gr¨obner basis techniques. A natural choice here would be to specialize (or guess) one
variable. The exhaustive search multiplies by q the number of polynomial systems, but these systems now
consist of n equations in n − 1 variables. At ﬁrst sight, this seems quite similar to our version; however,
the total degree of the equations in this hybrid approach is 2n−1 whereas it is only 2n−2 in our case. The
following chart summarizes the number of multivariate systems to solve together with their parameters, in
order to ﬁnd one relation in E(Fqn). It shows that our version provides a better trade-oﬀ between the number
of systems to solve and their complexity than the hybrid approach.

method

average number
of systems

number of
equations

number of
variables

total degree

Gaudry-Diem
Gaudry-Diem with
hybrid approach

n!

n! q

this work

(n − 1)! q

n

n

n

n

n − 1

n − 1

2n−1

2n−1

2n−2

2.4 Application to Fq5

The approach of Gaudry and Diem, while theoretically interesting, turns out to be impracticable on Fqn
as soon as n ≥ 5. Not only is the computation of the 6-th summation polynomial problematic (cf. §3), but
also, the fact that the system arising from (4) has generically 25(5−1) (cid:39) 106 solutions in Fq5 renders its
resolution very cumbersome. Indeed, the complexity of the resolution (e.g. by using FGLM to obtain a lex
order Gr¨obner basis) depends of the degree of the ideal generated by the equations, which is generically
2n(n−1). A natural way of decreasing this degree would be to add the ﬁeld equations eq
i − ei, but clearly this
is not practical for large values of q. In particular, we have not been able to successfully run one complete
relation search with their method, as the requested memory exceeded the capacity of our personal computer.

Nonetheless, using our algorithm and our own implementation of the F4 variant, we are able to check
and if necessary compute a decomposition over Fp5 with |p|2 = 32 bits in about 8.5 sec on a 2.6 GHz Intel
Core 2 Duo processor. Needless to say, this is still much too slow to yield in a reasonable time the solution
of the ECDLP over ﬁelds of size compatible with current levels of security. However, our approach provides
an eﬃcient attack of non-standard problems such as the oracle-assisted static Diﬃe-Hellman problem, as
explained in section 5.

8

Antoine Joux and Vanessa Vitse

3 Computing symmetrized summation polynomials

The main diﬃculty of the previously investigated algorithms is the construction of relations of the form (3) or
(5). Semaev’s summation polynomials were ﬁrst proposed in [31] to solve, or at least, to palliate this diﬃculty,
allowing us to reduce this problem to the resolution of the polynomial equation fm(xP1 , . . . , xPm−1, xR) = 0,
where xP1 , . . . , xPm−1 are the unknowns. The m-th polynomial fm is computed only once and is evaluated
in xR for each relation search. As mentioned above, it is more eﬃcient to express this equation in terms of
the elementary symmetric functions of the unknowns before the resolution of the system. This symmetrizing
operation greatly reduces the total degree of the system, and improves a lot its resolution by e.g. Gr¨obner
techniques. It can be done once for all at the beginning of the relation search.

We propose two distinct improvements: both consider a direct computation of the symmetrized sum-
mation’s polynomials, instead of rewriting the equation fm(xP1, . . . , xPm−1 , xR) = 0 in terms of elementary
symmetric polynomials after the computation of Semaev’s polynomials, as in [18]. These improvements re-
duce the computation time by a factor 10. Since these developments are not central to this article, the details
will be given in appendix A; we only sketch here the main ideas.

Recall that Semaev’s summation polynomials are deﬁned recursively; each inductive step actually consists
of a resultant computation. Our ﬁrst improvement is to partially symmetrize after each step: it has the double
beneﬁt of reducing the size of the intermediate polynomials and the cost of the ﬁnal symmetrization, by
distributing it between the diﬀerent steps. In our second improvement, we show, using principal divisors and

Miller’s technique, that P1 + P2 + . . . + Pm = O if and only if the polynomial (cid:81)(X − xPi) has a speciﬁc shape.

This condition is algebraically equivalent to the vanishing of the m-th Semaev’s summation polynomial,
whose symmetrized expression can be directly recovered using elimination theory. Thus, the computation of
resultants and the symmetrization are replaced by an elimination order Gr¨obner basis computation.

4 An F4-like algorithm without reduction to zero

An eﬃcient way to solve the multivariate polynomial system coming from (3) or (5) is to use Gr¨obner basis
tools. The best known algorithms for constructing Gr¨obner bases are Faug`ere’s F4 and F5 [14, 15], which
are improvements of the classical Buchberger’s algorithm. The second one, F5, is considered as the most
eﬃcient, since it includes a criterion to eliminate a priori almost all critical pairs that eventually reduce
to zero. This criterion is based on the concept of “signature” of a polynomial; the main drawback is that
many reductions are forbidden because they do not respect signature compatibility conditions. Hence, the
polynomials considered in the course of the F5 algorithm are mostly “top-reduced” but their tails are left
almost unreduced; this increases signiﬁcantly the complexity of the remaining pairs’ reduction. Furthermore,
F5 generates many “redundant” polynomials, i.e. which are not members of a minimal Gr¨obner basis, but
cannot be discarded for signature reasons [12]. The total number of computed critical pairs thus remains
relatively important, at least compared to what could be expected from the F4 algorithm if all critical pairs
reducing to zero were removed. These drawbacks are especially signiﬁcant for overdetermined systems such
as those we are considering. As mentioned by Faug`ere in [15], this is a consequence of the incremental nature
of the F5 algorithm. Indeed, to determine a Gr¨obner basis of an ideal generated by m polynomials, F5 starts
by computing a basis of the ideal generated by the ﬁrst m − 1 polynomials. Clearly, the additional equation
of the overdetermined system cannot provide any speed-up at this point. Moreover, in our case, since the
systems considered during the relation search always have the same shape, it is possible to extract from
a precomputation the knowledge of the relevant critical pairs and to remove the pairs that lead to zero
reductions. When such a precomputation is accessible, there is no reason to use F5 instead of F4.

Recall that during the course of F4 algorithm, a queue of yet untreated critical pairs is maintained.
At each iteration of the main loop, some pairs are selected from this queue (according to some predeﬁned

Title Suppressed Due to Excessive Length

9

strategy, usually all pairs having the smallest lcm total degree) and treated, that is, their S-polynomials
are computed and reduced simultaneously using linear algebra tools and former computations. The queue is
then updated with the critical pairs involving the resulting new generators and satisfying the ﬁrst and the
second Buchberger’s criteria [7, 20]. Here is a quick outline of the method we used for our computations:

1. For precomputation purposes, run a standard F4 algorithm on the ﬁrst system, with the following

modiﬁcations:

– At each iteration, store the list of all selected critical pairs.
– Each time there is a reduction to zero, remove from the stored list the critical pair that leads to the

reduction.

2. For each subsequent system, run a F4 computation with the following modiﬁcations:

– Do not maintain nor update a queue of untreated pairs.
– At each iteration, instead of selecting pairs from the queue, pick directly from the previously stored

list the relevant pairs.

As an illustration of this approach we give some examples of the speed gain it provides on Fp5 , using the
equations generated from the ﬁfth summation polynomial. The system to solve is composed of 5 equations
deﬁned over Fp of total degree 8 in 4 variables. We run a degrevlex Gr¨obner basis computation of the
corresponding ideal over three prime ﬁelds of size 16, 25 and 32 bits. To be fair, we compare our variant F4’
with an implementation of F4 which uses the same primitives and structures (in language C), and also with
the proprietary software Magma (V2.15-15) whose implementation is probably the best publicly available
for the considered ﬁnite ﬁelds. All tests are performed on a 2.6 GHz Intel Core 2 Duo processor, the times
are given in seconds.

|p|2 = 16
|p|2 = 25
|p|2 = 32

F4 (Magma)
9.600
119.1
1046

F4
9.683
17.01
24.43

F4’
3.979
5.002
8.496

The F4’ algorithm requires a single precomputation of 11.31 sec to generate the list of relevant pairs. The
above timings show that this overhead is largely compensated as soon as there are more than two subsequent
computations. We emphasize that this precomputed list of relevant pairs is the same for the three cases
|p|2 = 16, 25 or 32 bits. In truth, for increased eﬃciency, this list was generated using an even smaller
characteristic (|p|2 = 8). We have also solved this system with our own implementation of the F5 algorithm3.
The size of the Gr¨obner basis computed by F5 at the last step (before minimalization) is surprisingly large:
it contains 17249 labeled polynomials whereas both versions of F4 never build more than 2789 polynomials
at once, and construct bases containing at most 329 generators. Note that these ﬁgures do not depend on the
implementation’s details. The large number of polynomials that F5 computes has obvious consequences on
its performances; in particular, the timings of F5 that we have obtained for this system are much worse than
those of F4 or its variants. This shows that F5 as described in [15] is unsuitable for these speciﬁc systems.

5 Application to a practical oracle-assisted static Diﬃe-Hellman algorithm

Semaev’s idea of decomposing points of E(Fqn ) into a well-suited factor base leads naturally to an oracle-
assisted resolution of the SDHP, similar to the ﬁnite ﬁeld SDHP algorithm presented in [21]. We ﬁrst recall
here the deﬁnition of oracle-assisted SDHP from [6]:

Deﬁnition 3 Let G be a ﬁnite group of order |G| and P, Q ∈ G such that Q = [d]P where d ∈ [1, |G| − 1] is
a secret integer. An algorithm A is said to solve the SDHP in G if, given P, Q, and a challenge X ∈ G, it

3 At the present time, we have found no public implementation of F5 which achieves the computation of the complete

Gr¨obner basis in a reasonable time.

10

Antoine Joux and Vanessa Vitse

outputs [d]X ∈ G.
The SDHP-solving algorithm A is said to be oracle-assisted if, during a learning phase, it can make any
number of queries X1, . . . , Xl to an oracle that outputs [d]X1, . . . , [d]Xl, after which A is given a previously
unseen challenge X and outputs [d]X.

Generally, the ability to decompose points into a factor base F = {P1, . . . , Pl} gives the following oracle-

assisted algorithm:

– learning phase: ask the oracle to compute Qi = [d]Pi for 1 ≤ i ≤ l,
– decompose a challenge X as X = (cid:80)

i[ci]Pi and answer Y = (cid:80)

i[ci]Qi.

This methodology directly applies to the case G = E(Fqn ) with the factor base F = {P ∈ E(Fqn) : P =
(xP , yP ), xP ∈ Fq, yP ∈ S}. The only minor diﬃculty is that a small fraction of points actually decompose
(1 in n! or q (n − 1)! depending of the details). However, we can use a simple variation of the descent step to
circumvent this diﬃculty:

1. learning phase: ask the oracle to compute Q = [d]P for each P ∈ F
2. modiﬁed descent: given a challenge X, pick a random integer r coprime to the order of G and compute

Xr = [r]X

i=1 (cid:15)iPi, with (cid:15)i ∈ {−1; 1}

3. check if Xr can be written as a sum of m points of F: Xr = (cid:80)m
4. if Xr is not decomposable, go back to step 2; else output Y = [s] ((cid:80)m

i=1 (cid:15)iQi) where s = r−1 mod |G|.
It should be noted that the same techniques can also be used to solve other variants of SDHP, such
as the “Delayed Target” Discrete Logarithm or Diﬃe-Hellman problem (DTDLP and DTDHP) described
in [23]. In practice, we have seen that, on a personal computer, we can only decompose a chosen point into
at most four points of the factor base. If we are working with a ﬁnite ﬁeld K whose size is approximately b
bits, then assuming K is a degree 4 extension ﬁeld, we obtain a complexity of O(2b/4) oracle calls plus the
decomposition cost of 4!c(4, 2b/4). On the other hand, assuming K is a degree 5 extension ﬁeld, the complexity
becomes O(2b/5) oracle calls plus the decomposition cost of 4!2b/5˜c(5, 2b/5). For practical applications, oracle
queries are usually the limiting factor. As a consequence, for a given ﬁeld size, the oracle-assisted elliptic
curve SDHP is less secure over degree 5 than over degree 4 extension ﬁelds.

To our knowledge, the only other known method of solving the SDHP over a general elliptic curve consists
in solving the underlying discrete logarithm problem, i.e. computing d given P and Q = [d]P . A state-of-the-
art attack of the Certicom ECC2K-130 challenge is currently underway [1] and is expected to solve the DLP
on a Koblitz elliptic curve deﬁned over F2131 in about one year with 3000 3GHz Core 2 CPUs. Since many
speciﬁc characteristic 2 speed-ups are not available for ﬁnite ﬁelds of the form Fq5 (with q a prime power),
generic discrete logarithm computations should be slightly slower on a random curve deﬁned over Fq5 where
|q5|2 ≈ 130, but still several orders of magnitude faster than with our approach. However, by using index
calculus to directly solve the SDHP on such a curve, we estimate the computation to a single month using
the same 3000 3GHz Core 2 CPUs. This computation requires approximately 225 (cid:39) 3.3 × 107 oracle queries.

6 Conclusion

In this article, we have shown that considering decomposition of points on E(Fqn ) as sums of n − 1 points
improves the index calculus proposed by [10, 18], when n ≥ 5 and log q ≤ O(n3). The key point of our
approach is that such decompositions lead to overdetermined polynomial systems, which are easier to solve
than the systems arising from Gaudry and Diem’s original version. This resolution can be greatly sped up
by using our modiﬁed Gr¨obner basis computation algorithm, which takes advantage of the common shape
of the systems and is therefore faster than F4 and F5. Note that our “F4-like” algorithm may be applied to
many other problems, as soon as one has to compute Gr¨obner bases of several same-shape systems.

The practicality of our algorithm is still too large to seriously threaten ECDLP-based cryptosystems with
the current cryptographic key sizes. However, we further illustrate the weakness of elliptic curves deﬁned over
small degree extension ﬁelds by providing an eﬃcient way of solving oracle-assisted Diﬃe-Hellman problems.

Title Suppressed Due to Excessive Length

11

References

1. D. V. Bailey, L. Batina, D. J. Bernstein, P. Birkner, J. W. Bos, H.-C. Chen, C.-M. Cheng, G. van Damme,
G. de Meulenaer, L. J. D. Perez, J. Fan, T. Gneysu, F. Gurkaynak, T. Kleinjung, T. Lange, N. Mentens, R. Nieder-
hagen, C. Paar, F. Regazzoni, P. Schwabe, L. Uhsadel, A. V. Herrewege, and B.-Y. Yang. Breaking ECC2K-130.
Cryptology ePrint Archive, Report 2009/541, 2009. http://eprint.iacr.org/.

2. M. Bardet. ´Etude des syst`emes alg´ebriques surd´etermin´es. Applications aux codes correcteurs et `a la cryptographie.

PhD thesis, Universit´e Pierre et Marie Curie, Paris VI, 2004.

3. M. Bardet, J.-C. Faug`ere, B. Salvy, and B.-Y. Yang. Asymptotic behaviour of the degree of regularity of semi-
regular polynomial systems. Presented at MEGA’05, Eighth International Symposium on Eﬀective Methods in
Algebraic Geometry, 2005.

4. L. Bettale, J.-C. Faug`ere, and L. Perret. Hybrid approach for solving multivariate systems over ﬁnite ﬁelds.

Journal of Mathematical Cryptology, pages 177–197, 2009.

5. W. Bosma, J. J. Cannon, and C. Playoust. The Magma algebra system I: The user language. J. Symb. Comput.,

24(3/4):235–265, 1997.

6. D. R. L. Brown and R. P. Gallant. The static Diﬃe-Hellman problem. Cryptology ePrint Archive, Report

2004/306, 2004. http://eprint.iacr.org/.

7. B. Buchberger. Gr¨obner bases: An algorithmic method in polynomial ideal theory. In N. Bose, editor, Multi-
dimensional systems theory, Progress, directions and open problems, Math. Appl. 16, pages 184–232. D. Reidel
Publ. Co., 1985.

8. H. Cohen, G. Frey, R. Avanzi, C. Doche, T. Lange, K. Nguyen, and F. Vercauteren, editors. Handbook of elliptic
and hyperelliptic curve cryptography. Discrete Mathematics and its Applications (Boca Raton). Chapman &
Hall/CRC, Boca Raton, FL, 2006.

9. D. Cox, J. Little, and D. O’Shea.

Ideals, varieties, and algorithms. Undergraduate Texts in Mathematics.

Springer, New York, third edition, 2007.

10. C. Diem. On the discrete logarithm problem in elliptic curves. Preprint, available at: http://www.math.

uni-leipzig.de/~diem/preprints/dlp-ell-curves.pdf, 2009.

11. W. Diﬃe and M. E. Hellman. New directions in cryptography. IEEE Trans. Information Theory, IT-22(6):644–

654, 1976.

12. C. Eder and J. Perry. F5C: a variant of Faug`ere’s F5 algorithm with reduced Gr¨obner bases. arXiv/0906.2967,

2009.

13. T. ElGamal. A public key cryptosystem and a signature scheme based on discrete logarithms. In Advances in
cryptology (Santa Barbara, Calif., 1984), volume 196 of Lecture Notes in Comput. Sci., pages 10–18. Springer,
Berlin, 1985.

14. J.-C. Faug`ere. A new eﬃcient algorithm for computing Gr¨obner bases (F4). Journal of Pure and Applied Algebra,

139(1-3):61–88, June 1999.

15. J.-C. Faug`ere. A new eﬃcient algorithm for computing Gr¨obner bases without reduction to zero (F5).

In

Proceedings of ISSAC 2002, New York, 2002. ACM.

16. J. C. Faug`ere, P. Gianni, D. Lazard, and T. Mora. Eﬃcient computation of zero-dimensional Gr¨obner bases by

change of ordering. Journal of Symbolic Computation, 16(4):329–344, 1993.

17. G. Frey and H.-G. R¨uck. A remark concerning m-divisibility and the discrete logarithm in the divisor class group

of curves. Math. Comp., 62(206):865–874, 1994.

18. P. Gaudry.

Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm

problem. J. Symbolic Computation, 2008. doi:10.1016/j.jsc.2008.08.005.

19. P. Gaudry, E. Thom´e, N. Th´eriault, and C. Diem. A double large prime variation for small genus hyperelliptic

index calculus. Mathematics of Computation, 76:475–492, 2007.

20. R. Gebauer and H. M. M¨oller. On an installation of Buchberger’s algorithm. J. Symbolic Comput., 6(2-3):275–286,

1988.

21. A. Joux, R. Lercier, D. Naccache, and E. Thom´e. Oracle assisted static Diﬃe–Hellman is easier than discrete
In M. G. Parker, editor, IMA Int. Conf., volume 5921 of Lecture Notes in Comput. Sci., pages

logarithms.
351–367. Springer, 2009.

12

Antoine Joux and Vanessa Vitse

22. N. Koblitz. Elliptic curve cryptosystems. Math. Comp., 48(177):203–209, 1987.
23. N. Koblitz and A. Menezes. Another look at non-standard discrete log and Diﬃe-Hellman problems. J. Math.

Cryptol., 2(4):311–326, 2008.

24. D. Lazard. Gr¨obner bases, Gaussian elimination and resolution of systems of algebraic equations. In Computer

algebra (London, 1983), volume 162 of Lecture Notes in Comput. Sci., pages 146–156. Springer, Berlin, 1983.

25. A. J. Menezes, T. Okamoto, and S. A. Vanstone. Reducing elliptic curve logarithms to logarithms in a ﬁnite

ﬁeld. IEEE Trans. Inform. Theory, 39(5):1639–1646, 1993.

26. V. S. Miller. The Weil pairing, and its eﬃcient calculation. J. Cryptology, 17(4):235–261, 2004.
27. S. Pohlig and M. Hellman. An improved algorithm for computing logarithms over GF (p) and its cryptographic

signiﬁcance. IEEE Transactions on Information Theory, IT-24:106–110, 1978.

28. J. M. Pollard. Monte Carlo methods for index computation (mod p). Math. Comp., 32(143):918–924, 1978.
29. J. M. Pollard. Kangaroos, Monopoly and discrete logarithms. J. Cryptology, 13(4):437–447, 2000.
30. T. Satoh and K. Araki. Fermat quotients and the polynomial time discrete log algorithm for anomalous elliptic

curves. Comment. Math. Univ. St. Paul., 47(1):81–92, 1998.

31. I. Semaev. Summation polynomials and the discrete logarithm problem on elliptic curves. Cryptology ePrint

Archive, Report 2004/031, 2004.

32. I. A. Semaev. Evaluation of discrete logarithms in a group of p-torsion points of an elliptic curve in characteristic

p. Math. Comp., 67(221):353–356, 1998.

33. D. Shanks. Class number, a theory of factorization, and genera. In 1969 Number Theory Institute (Proc. Sympos.
Pure Math., Vol. XX, State Univ. New York, Stony Brook, N.Y., 1969), pages 415–440. Amer. Math. Soc.,
Providence, R.I., 1971.

34. J. H. Silverman. The arithmetic of elliptic curves, volume 106 of Graduate Texts in Mathematics. Springer-Verlag,

New York, 1986.

35. N. P. Smart. The discrete logarithm problem on elliptic curves of trace one. J. Cryptology, 12(3):193–196, 1999.
36. N. Th´eriault. Index calculus attack for hyperelliptic curves of small genus. In Heidelberg, editor, Advances in
Cryptology, ASIACRYPT 2003, volume 2894 of Lecture Notes in Comput. Sci., pages 75–92. Springer, September
2003.

A Symmetrized summation polynomials

In this appendix, we detail the two methods used to compute the symmetrized summation polynomials, as
mentioned in section 3. The goal is to write the Semaev’s summation polynomials in terms of the elementary
symmetric functions of the unknowns

e1 =

(cid:88)

i

xPi,

e2 =

(cid:88)

i<j

xPixPj ,

. . . ,

em−1 =

(cid:89)

i

xPi.

The ﬁrst method consists of symmetrizing after each resultant computation and is summarized by the

following proposition:

Proposition 4 Let E be an elliptic curve deﬁned over a ﬁeld K of characteristic diﬀerent from 2 or 3, with
reduced Weierstrass equation y2 = x3 + ax + b. The symmetrized summation polynomials are determined by
the following induction. The initial value for n = 3 is given by

˜f3(e1,2 , e2,2 , X3) = (cid:0)e2

1,2 − 4e2,2

(cid:1) X 2

3 − 2 (e1,2(e2,2 + a) + 2b) X3 + (e2,2 − a)2 − 4b e1,2

and for m ≥ 3 by

˜fm+1(e1,m , . . . , em,m , Xm+1) = Symm

(cid:16)

ResY

(cid:16) ˜fm(e1,m−1, . . . , em−1,m−1, Y ), f3(e1,1, Xm+1, Y )

(cid:17)(cid:17)

,

where

∗ er,n is the r-th elementary symmetric polynomial in variables X1, . . . , Xn,

∗ f3(X1, X2, X3) = (X1 − X2)2X 2

3 − 2 ((X1 + X2)(X1X2 + a) + 2b) X3 + (X1X2 − a)2 − 4b(X1 + X2) is

the third Semaev’s summation polynomial,

∗ Symm denotes the operation of rewriting a partially symmetrized polynomial in terms of elementary

Title Suppressed Due to Excessive Length

13

symmetric functions






e1,m = e1,1 + e1,m−1

e2,m = e1,1e1,m−1 + e2,m−1

...

em−1,m = e1,1em−2,m + em−1,m−1

em,m = e1,1em−1,m−1

Obviously it is also possible to deﬁne ˜fm from resultants of ˜fm−j and ˜fj+2 for 1 ≤ j ≤ m − 3, as in [31].
This has the advantage of reducing the number of resultant computations, but increases the complexity of
the symmetrization step. In our context, since m is small (m ≤ 6), the approach of Proposition 4 is the
fastest.

We now detail the second method for the computation of the symmetrized summation polynomials.
Let E be an elliptic curve of equation y2 = x3 + ax + b deﬁned over K of characteristic diﬀerent from
2 or 3, and let P1, . . . , Pm ∈ E(K) be such that P1 + . . . + Pm = O. We consider the principal divisor
D = (P1) + . . . + (Pm) − m(O) ∈ Div0
K(E). Up to a constant, there exists a unique function gm ∈ K(E)
such that D = div(gm) (cf. [34] Corollary 3.5). Same techniques as the ones used in Miller’s algorithm [26]
enable us to compute recursively the function gm.

Let li(X, Y ) = 0 (1 ≤ i ≤ m − 1) be the equations of the lines passing through P1 + . . . + Pi and Pi+1
and vi(X, Y ) = 0 (1 ≤ i ≤ m − 2) the equations of the vertical lines passing through P1 + . . . + Pi+1, then
we have

An easy induction shows that

gm(X, Y ) =

l1 . . . lm−1
v1 . . . vm−2

(X, Y ).

gm(X, Y ) = gm,1(X) + Y gm,2(X)

(8)

where gm,1 and gm,2 are two polynomials of degree lower than dm,1 and dm,2 respectively:

dm,1 =

(cid:40)

m/2 if m is even

(m − 1)/2 if m is odd

and dm,2 =

(cid:40)

(m − 4)/2 if m is even

(m − 3)/2 if m is odd

Note that the function gm is uniquely determined if the equations of li and vi are normalized at the point
at inﬁnity. The intersection between the curve (gm = 0) and E is exactly the set of points Pi, 1 ≤ i ≤ m,
thus the following proposition is quite immediate:

Proposition 5 Let E be an elliptic curve of equation y2 = x3 +ax+b deﬁned over a ﬁeld K of characteristic
diﬀerent from 2 or 3. Let P1, . . . , Pm ∈ E(K) be such that P1 + . . . + Pm = O and gm,1 and gm,2 be the
polynomials given by equation (8). Then we have gm,1(x)2 − gm,2(x)2(x3 + ax + b) = 0 if and only if x is the
x-coordinate of one of the points Pi.
Conversely, if gm,1 and gm,2 are two arbitrary polynomials in K[X] with degree dm,1 and dm,2, then the roots
in K of Fm(X) = gm,1(X)2 − (X 3 + aX + b) gm,2(X)2, counted with multiplicity, are the x-coordinates of
points Q1, . . . , Qm ∈ E(K) such that Q1 + . . . + Qm = O.

The second assertion comes from the fact that in K(E), we have Fm = (gm,1+Y gm,2)(gm,1−Y gm,2). Since
deg(Fm) = m, Fm has exactly m roots counted with multiplicity over K, each of which is the x-coordinate
of two opposite points ±Qi ∈ E(K). Up to a change of sign, we can assume that Qi is a zero of gm,1 + Y gm,2

14

Antoine Joux and Vanessa Vitse

(and so −Qi is a zero of the second factor gm,1 − Y gm,2). Thus, the principal divisor Div(gm,1 + Y gm,2) is
equal to (Q1) + . . . + (Qm) − m(O), which implies Q1 + . . . + Qm = O.

We can now use this proposition to construct the symmetrized summation polynomials. Let A =

K[α0, . . . , αdm,1, β0, . . . , βdm,2, xP1 , . . . , xPm ]. We deﬁne the following elements of A[X]:

hm,1(X) =

dm,1
(cid:88)

i=0

αiX i,

hm,2(X) = X dm,2 +

dm,2−1
(cid:88)

i=0

βiX i,

Fm(X) = hm,1(X)2 − (X 3 + aX + b) hm,2(X)2

Finally, let I be the ideal of A generated by Fm(xP1), . . . , Fm(xPm). We can easily ﬁnd a diﬀerent set of
generators of I by identifying the coeﬃcients of Fm with the elementary symmetric functions e1, . . . , em of
the variables xP1, . . . , xPm, and consider the result as an ideal J of K[α0, . . . , αdm,1, β0, . . . , βdm,2 , e1, . . . , em].
Elimination theory (cf. [9]) allows to compute eﬃciently (e.g. with appropriate Gr¨obner bases) a set of gener-
ators of the ideal J (cid:48) = J ∩K[e1, . . . , em]. According to the second part of Proposition 5, a m-tuple (e1, . . . , em)
belongs to the algebraic set V(J (cid:48)) if and only if the roots of the polynomial T m + (cid:80)m
i=1(−1)ieiT m−i are the
x-coordinates of points of E(K) whose sum is the point at inﬁnity O. Actually, using Semaev’s results, this
elimination ideal J (cid:48) is principal, generated by the m-th symmetrized summation polynomial. Hence, this
elimination computes the m-th summation polynomial directly in terms of e1, . . . , em. Note that with this
approach, it is also possible to compute directly the partially symmetrized polynomial ˜fm.

A worked example

For m = 5, following the previous construction, we obtain

F5(X) = (α2X 2 + α1X + α0)2 − (X 3 + aX + b)(X + β0)2

with a, b ∈ K. By identifying the coeﬃcients of this polynomial with the elementary symmetric polynomials
e1, . . . , e5 of the variables xP1 , . . . , xP4, xP5 , we deduce the polynomial system :






2 − 2β0
0 + a − 2α1α2

e1 = α2
e2 = β2
e3 = 2α0α2 + α2
e4 = aβ2
e5 = α2

0 − bβ2

0

1

0 + 2bβ0 − 2α0α1

and using a Gr¨obner basis computation with an elimination order, we obtain the ﬁfth summation polynomial
f5 directly in terms of e1, . . . , e5.

Some comparisons

Here we give a comparison of computer times between the classical computation using resultants followed by
a ﬁnal symmetrization and our two methods. In all cases, we have used the software Magma (V2.16-4) [5] on
a 3.6 GHz Intel Pentium D processor ; the symmetrizations have been done via an elimination order Gr¨obner
basis computation. In view of the applications we have in mind, we chose to compute the 5-th symmetrized
summation polynomial on an extension ﬁeld Fp5, p prime.

Title Suppressed Due to Excessive Length

15

log2(p) resultant + symmetrization 1rst method 2nd method

8
16
32

2.55 + 15.28 = 17.83 sec
2.61 + 15.45 = 18.06 sec
12.65 + 31.77 = 44.42 sec

1.64 sec
1.82 sec
5.09 sec

2.75 sec
2.86 sec
14.37 sec

We also tried to perform the same computations for the 6-th symmetrized summation polynomial. Unfor-
tunately, in this case, both resultant and Gr¨obner based computations exceeded the capacity of our personal
computer. However, note that we were able to obtain with our ﬁrst method (partially symmetrized resul-
tants) the 6-th symmetrized summation polynomial over Fp6 (|p|2 = 8), for a ﬁxed value of the last variable
x6, in less than 3 min, expressed in the variables e1,5, . . . , e5,5. This means that, when using a decomposition
into 5 points of the factor base, it would be possible to perform this computation, if we are willing to pay
the price of redoing it for each relation search instead of precomputing it at the beginning.

