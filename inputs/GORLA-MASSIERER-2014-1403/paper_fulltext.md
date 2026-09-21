<!-- Extracted 2026-09-20 from arXiv:1403.0126 (Gorla–Massierer). pdfminer.six. NOT hand-cleaned. -->

4
1
0
2

r
a

M

1

]

G
A

.

h

t

a

m

[

1
v
6
2
1
0

.

3
0
4
1

:

v

i

X

r
a

Point compression for the trace zero subgroup
over a small degree extension ﬁeld∗

Elisa Gorla1 and Maike Massierer2

1Institut de math´ematiques, Universit´e de Neuchˆatel, Rue Emile-Argand 11, 2000 Neuchˆatel,
Switzerland, elisa.gorla@unine.ch
2Mathematisches Institut, Universit¨at Basel, Rheinsprung 21, 4051 Basel, Switzerland,
maike.massierer@unibas.ch

Abstract Using Semaev’s summation polynomials, we derive a new equation for the Fq-
rational points of the trace zero variety of an elliptic curve deﬁned over Fq. Using this
equation, we produce an optimal-size representation for such points. Our representation is
compatible with scalar multiplication. We give a point compression algorithm to compute
the representation and a decompression algorithm to recover the original point (up to some
small ambiguity). The algorithms are eﬃcient for trace zero varieties coming from small
degree extension ﬁelds. We give explicit equations and discuss in detail the practically
relevant cases of cubic and quintic ﬁeld extensions.

Keywords
elliptic curve cryptography, pairing-based cryptography, discrete logarithm
problem, trace zero variety, eﬃcient representation, point compression, summation poly-
nomials

Mathematics Subject Classiﬁcation 14G50, 11G25, 14H52, 11T71, 14K15

1

Introduction

Given a (hyper)elliptic curve deﬁned over Fq and a ﬁeld extension Fq|Fqn , consider the Fqn -
rational points of trace zero. They form a subgroup of the group of Fqn -rational points of the
curve, and can be realized as the Fq-rational points of an abelian variety built by Weil restriction
from the original curve, called the trace zero variety. The trace zero subgroup was ﬁrst proposed
for use in cryptography by Frey [15], and further studied by Naumann [35], Weimerskirch [44],
Blady [5], Lange [31, 32], Avanzi–Cesena [1, 8], and Diem-Scholten [12]. Trace zero subgroups
are interesting because they allow eﬃcient arithmetic, due to a speed-up of the standard scalar
multiplication using the Frobenius endomorphism. This is analogous to the use of endomorphisms
to speed up scalar multiplication on Koblitz curves (see [30]) and GLV–GLS curves (see [19, 17]),
which are the basis for several recent implementation speed records for elliptic curve arithmetic
(see [34, 14, 6]).

The trace zero subgroup is of interest in the context of pairing-based cryptography. Rubin
and Silverberg have shown in [37, 40] that the security of pairing-based cryptosystems can be
improved by using abelian varieties of dimension greater than one in place of elliptic curves.
Jacobians of hyperelliptic curves and trace zero varieties are therefore the canonical examples
for such applications.

∗This article appeared in Designs, Codes and Cryptography,

the ﬁnal publication is available at

http://link.springer.com/article/10.1007%2Fs10623-014-9921-0 .

1

 
 
 
 
 
 
Since the trace zero subgroup is contained in the group of Fqn -rational points of the (Jacobian
of the) curve, the DLP in the trace zero subgroup is at most as hard as the DLP in the curve.
It is easy to show that in fact the DLP’s in the two groups have the same complexity. From
a mathematical point of view therefore, trace zero variety cryptosystems may be regarded as
the (hyper)elliptic curve analog of torus-based cryptosystems such as LUC [43], Gong–Harn [25],
XTR [33], and CEILIDIH [38].

The hardness of the discrete logarithm problem in a group is closely connected with the size
of the representation of the group elements. Usually, the hardness of the DLP is measured as
a function of the group size. However, for practical purposes, the comparison with the size of
the representation of group elements is a better indicator, since it quantiﬁes the storage and
transmission costs connected with using the corresponding cryptosystem. Therefore, in order to
make the comparison between DLP complexity and group size a fair one, we are interested in a
compact representation that reﬂects the size of the group. Such an optimal-size representation
consists of log2 N bits, where N is the size of the group. See also [26] for a discussion on the
signiﬁcance of compact representations.

An optimal-size representation for elliptic curves is well-known. In the cryptographic setting,
it is standard procedure to represent an elliptic curve point by its x-coordinate only, since the
y-coordinate can easily be recomputed, up to sign, from the curve equation. If desired, the sign
can be stored in one extra bit of information. Representing a point via its x-coordinate gives an
optimal representation for the elements of the group of Fqn -rational points of an elliptic curve:
Each of the approximately qn points can be represented by one element of Fqn , or n elements
of Fq after choosing a basis of the ﬁeld extension. Notice moreover that storing the sign of the
y-coordinate is unnecessary, since this representation is compatible with scalar multiplication of
points: For any k ∈ Z, the x-coordinates of the points kP and −kP coincide.

The trace zero variety of an elliptic curve with respect to a prime extension degree n has
dimension n − 1, and we are interested in the Fq-rational points. Hence, an optimal represen-
tation should have log2 qn−1 bits, or consist of n − 1 elements of Fq. For practical purposes, it
is important that the representation can be eﬃciently computed (“compression”) and that the
original point can be easily recovered, possibly up to some small ambiguity, from the represen-
tation (“decompression”). Naumann [35], Rubin–Silverberg [37, 39, 42], and Lange [32] propose
compact representations with compression and decompression algorithms for genus 1 and genus
2 curves, respectively. The work by Eagle–Galbraith–Ong [13] on point compression methods for
Koblitz curves is also related.

In this paper, we concentrate on extension ﬁelds of degree n = 3 or 5. This is due to the fact
that an index calculus attack [20] and a cover attack [9, 10, 11] apply to Tn, making it vulnerable
for large values of n. In this work we brieﬂy discuss these attacks and come to the conclusion
that there are no security issues for n = 3. For n = 5 the cover attacks can be avoided by
imposing extra conditions, and the known index calculus attacks do not threaten the security of
pairing-based cryptosystems involving trace zero subgroups of supersingular curves.

The main purpose of this paper is introducing a new representation for the points on the trace
zero variety of an elliptic curve. The compression and decompression algorithms are more eﬃcient
than that of [42], and points are recovered with smaller ambiguity. In addition, our representation
is (to the extent of our knowledge) the only one that is compatible with scalar multiplication of
points, which is the only operation needed in Diﬃe–Hellman-based cryptographic protocols.

The paper is structured as follows: In Section 2, we ﬁx the notation, give the relevant deﬁni-
tions, and brieﬂy recall the standard representation for points on the trace zero variety. We also
discuss the simple case of the trace zero variety for a quadratic ﬁeld extension. Using Semaev’s
summation polynomials, in Section 3 we derive a single equation whose Fq-solutions describe
the Fq-points of the trace zero variety, up to a few well-described exceptions (see Lemma 1 and

2

Proposition 4). In Section 4, using the equation that we produced in the previous section, we
propose a new representation for the points on the trace zero variety. The size of the represen-
tation is optimal, and we give eﬃcient compression and decompression algorithms. In Sections
5 and 6 we analyze in detail what our method produces for the cases n = 3 and 5. We give
explicit equations and concrete examples computed with Magma and comment on security issues
for these parameters. It is generally agreed that 3 and 5 are the practically relevant extension
degrees in the case of elliptic curves (see e.g. [32]).

2 Preliminaries

Let Fq be a ﬁnite ﬁeld with q elements, and let E be an elliptic curve deﬁned over Fq by an
aﬃne Weierstraß equation. We consider the group E(Fqn ) of Fqn -rational points of E for ﬁeld
extensions of prime degree n. The group operation is point addition, and the neutral element is
the point at inﬁnity, denoted by O. We denote indeterminates by lower case letters and ﬁnite
ﬁeld elements by upper case letters.

Deﬁnition 1. The Frobenius endomorphism on E is deﬁned by

ϕ : E → E, (X, Y ) 7→ (X q, Y q), O 7→ O.

One can deﬁne a trace map

Tr : E(Fqn ) 7→ E(Fq), P 7→ P + ϕ(P ) + ϕ2(P ) + . . . + ϕn−1(P ),

relative to the ﬁeld extension Fqn |Fq. The kernel of the trace map is the trace zero subgroup of
E(Fqn ), which we denote by Tn.

By the process of Weil restriction, the points of Tn can be viewed as the Fq-rational points

of an abelian variety V of dimension n − 1 deﬁned over Fq. V is called the trace zero variety.

In trace zero subgroups, arithmetic can be made more eﬃcient by using the Frobenius endo-
morphism, following a similar approach to Koblitz curves and GLV–GLS curves. They turn out
to be extremely interesting in the context of pairing-based cryptography, where they achieve the
largest security parameters in some cases, as discussed in [37, 40, 1, 8].

It is easy to show that the DLP in E(Fqn ) is as hard as the DLP in Tn. An explanation is
given in [27] for the analogous case of algebraic tori: The trace maps a DLP in E(Fqn ) to a DLP
in E(Fq). By solving it in the smaller group, the discrete logarithm is obtained modulo the order
of E(Fq). The remaining modular information required to compute the full discrete logarithm
comes from solving a DLP in Tn. A formal argument, which applies to any short exact sequence
of algebraic groups, is given in [18].

Proposition 1. Consider the exact sequence

0 −→ Tn −→ E(Fqn ) Tr−→ E(Fq) −→ 0.

Then solving a DLP in E(Fqn ) has the same complexity as solving a DLP in Tn and a DLP in
E(Fq).

In the conclusions of [1], large bandwidth is mentioned as the only drawback of using trace
zero subgroups in pairing-based cryptography. In this paper we solve this problem by ﬁnding an
optimal representation for the elements of the trace zero subgroup.

3

Deﬁnition 2. Let G be a ﬁnite set. A representation for the elements of G is a bijection between
G and a set of binary strings of ﬁxed length ℓ. Equivalently, it is an injective map from G to Fℓ
2.
A representation is optimal if |G| ∼ 2ℓ, i.e. if we need approximately log2 |G| bits to represent an
element of G.

Abusing terminology, in this paper we call representation a map from G to Fℓ

2 with the
property that an element of Fℓ
2 has at most d inverse images, for some small ﬁxed d. In this case,
we say that the representation identiﬁes classes of at most d elements, namely those that have
the same representation. Notice that the number of classes is about |G|/d ∼ |G|, if d is a small
constant.

Remark 1. Since the elements of a ﬁnite ﬁeld Fq can be represented via binary strings of length
log2 q, a representation for G can be given via a bijection between G and a subset of Fm
q , for
some m and some prime power q. Such a representation is optimal if and only if |G| ∼ qm.

Representing points of an elliptic curve via their x-coordinate is a standard example of optimal

representation.

Example 1. It is customary to represent a point (X, Y ) ∈ E(Fqn ) via its x-coordinate X ∈ Fqn .
The y-coordinate can then be recovered, up to sign, from the curve equation. If desired, the sign
can be stored in one extra bit of information. Such a representation is optimal, since by Hasse’s
Theorem |E(Fqn )| ∼ qn.

The representation from the previous example identiﬁes pairs of points, since P and −P have
the same x-coordinate. We often say that the x-coordinate is a representation for the equivalence
class consisting of P and −P . The representation that we propose in this paper identiﬁes a small
number of points as well. Before we discuss our representation, we notice that representing a
point P ∈ Tn via its x-coordinate is no longer optimal.

Remark 2. Since a point P = (X, Y ) ∈ Tn is an element of E(Fqn ), we can represent P via
X ∈ Fqn . Choosing an Fq-basis of Fqn , we can represent X ∈ Fqn as an n-tuple (X0, . . . , Xn−1) ∈
Fn
q however is not optimal, since
|Tn| ∼ qn−1.

q . Representing P ∈ Tn as X ∈ Fqn or as (X0, . . . , Xn−1) ∈ Fn

In this paper we ﬁnd a representation for the elements of Tn, via n − 1 coordinates in Fq. Our
representation is not injective, but it identiﬁes a small number of points. Our approach is the
following: We start from the representation of P ∈ Tn as an n-tuple ρ(P ) = (X0, . . . , Xn−1) ∈ Fn
q ,
and write an equation in Fq[x0, . . . , xn−1] which vanishes on ρ(P ) for all P ∈ Tn. This allows
us to drop one coordinate of ρ(P ) and reconstruct it using the equation. Therefore, we can
represent elements of Tn via n − 1 coordinates in Fq, which is optimal.

We now ﬁx some notation that we will use when writing explicit equations in Sections 4, 5,
and 6. Let Fq be the ﬁnite ﬁeld with q elements, n a prime. For the sake of concreteness, we
assume that n | q − 1. Due to its simplicity, we always consider this case when writing explicit
equations. All of our arguments however work for any n and q, see also Remark 3. If n | q − 1,
thanks to Kummer theory we can write the extension ﬁeld as

Fqn = Fq[ζ]/(ζn − µ),

where µ is not an n-th power in Fq. Where necessary, we take 1, ζ, . . . , ζn−1 as a basis of the
ﬁeld extension.

When doing Weil restriction, we associate n new variables x0, . . . , xn−1 to the variable x.

They are related via

x = x0 + x1ζ + . . . + xn−1ζn−1.

(1)

4

We abuse terminology and use the term Weil restriction not only for the variety, but also for
the process of writing equations for the Weil restriction. In particular for us, Weil restriction is
a procedure that can be applied to a polynomial deﬁned over Fqn and results in n polynomials
with n times as many variables, and coeﬃcients in Fq.

Remark 3. If n does not divide q − 1, we choose a normal basis {α, αq, . . . , αqn−1
Fq and Weil restriction coordinates

} of Fqn over

x = x0α + x1αq + . . . + xn−1αqn−1

.

It is easy to show that the case n = 2 allows a trivial optimal representation for the elements

of Tn. Hence in the next sections we concentrate on the more interesting case of odd primes n.

Proposition 2. The trace zero subgroup T2 of E(Fq2 ) can be described as

T2 = {(X, Y ) ∈ E(Fq2 ) | X ∈ Fq, Y /∈ Fq} ∪ E[2](Fq).

In particular, representing a point (X, Y ) ∈ T2 by X ∈ Fq yields a representation of optimal size.

Proof. We ﬁrst prove that T2 is contained in the union of sets on the right hand side of the
equality. Let P ∈ T2, P 6= O, so P = (X, Y ) ∈ E(Fq2 ). If P ∈ E(Fq), then 2P = O, hence
P ∈ E[2](Fq). If P /∈ E(Fq), then (X, Y ) = −(X q, Y q). In particular X = X q, so X ∈ Fq, which
also implies Y /∈ Fq.

To prove the other inclusion, observe that by deﬁnition P ∈ E[2](Fq) satisﬁes 2P = O, so
P ∈ T2. Let P = (X, Y ) ∈ E(Fq2 ) with X ∈ Fq, Y /∈ Fq. Since X ∈ Fq, the points (X, Y ) and
ϕ(X, Y ) = (X, Y q) are distinct points on E which lie on the same vertical line x − X = 0. Hence
(X, Y ) + ϕ(X, Y ) = O and (X, Y ) ∈ T2.

The next proposition will be useful when writing equations for the Fq-rational points of the
trace zero variety. For a multivariate polynomial h, we denote by degxi (h) the degree of h in the
variable xi.

Proposition 3. Let h ∈ Fq[x0, . . . , xn−1] be a polynomial with h(X0, . . . , Xn−1) = 0 for all
(X0, . . . , Xn−1) ∈ Fn
q , and assume that degxi (h) < q for i ∈ {0, . . . , n − 1}. Then h is the zero
polynomial.

Proof. Write

V (h) = {(X0, . . . , Xn−1) ∈ F n

q | h(X0, . . . , Xn−1) = 0} ⊆ F n

q

for the zero locus of h over the algebraic closure of Fq and

I(V ) = {f ∈ Fq[x0, . . . , xn−1] | f (X0, . . . , Xn−1) = 0 for all (X0, . . . , Xn−1) ∈ V }

for the ideal of the polynomials vanishing on some V ⊆ F n
q .
0 − x0, . . . , xq

q ) = Jn where Jn = (xq

n−1 − xn−1). We proceed by
induction on n. The claim holds for n = 1, since the elements of Fq are exactly those elements

First we show that I(Fn

5

of Fq that satisfy the equation xq

0 − x0. Assuming that the statement is true for n − 1, we have

I(Fn

q ) =

\
(α0,...,αn−1)∈Fn

q

(x0 − α0, . . . , xn−1 − αn−1)

=

=

\
α0∈Fq

\
(α1,...,αn−1)∈Fn−1

q

(x0 − α0, . . . , xn−1 − αn−1)

(x0 − α0, xq

1 − x1, . . . , xq

n−1 − xn−1)

\
α0∈Fq

= 



Y
α0∈Fq

= Jn.

(x0 − α0), xq

1 − x1, . . . , xq

n−1 − xn−1





q ) = Jn. The leading terms of xq

Now we show that h = 0. Since h vanishes on Fn

h ∈ I(V (h)) ⊆ I(Fn
term order are xq
xq
to zero using the generators of Jn, i.e. if we divide h by xq
is divisible by xq
degxi(h) < q for all i, h is equal to the remainder of the division of h by xq

q ⊆ V (h) ⊆ F n
q , which implies
n−1 − xn−1 with respect to any
n−1, in particular they are pairwise coprime. Hence the polynomials
n−1 − xn−1 are a Gr¨obner basis of Jn. Therefore, h ∈ Jn implies that h reduces
i − xi whenever the leading term of h
i , we must obtain remainder zero when no more division is possible. But since
n−1 − xn−1,

q , we have Fn
0 − x0, . . . , xq

0 − x0, . . . , xq

0 − x0, . . . , xq

0, . . . , xq

hence h = 0.

3 An equation for the trace zero subgroup

In this section we use Semaev’s summation polynomials [41] to write an equation for the set of
Fq-rational points of the trace zero variety. The equation involves the x-coordinates only and
will help us in ﬁnding a better representation for the elements of the trace zero subgroup.

Semaev introduced the summation polynomials in the context of attacking the elliptic curve
discrete logarithm problem. They give polynomial conditions describing when a number of points
on an elliptic curve sum to O, involving only the x-coordinates of the points.

Deﬁnition 3. Let Fq be a ﬁnite ﬁeld of characteristic diﬀerent from 2 and 3 and let E be a
smooth elliptic curve deﬁned by the aﬃne equation

with coeﬃcients A, B ∈ Fq.

Deﬁne the m-th summation polynomial fm recursively by

E : y2 = x3 + Ax + B,

f3(z1, z2, z3) = (z1 − z2)2z2

3 − 2((z1 + z2)(z1z2 + A) + 2B)z3 + (z1z2 − A)2 − 4B(z1 + z2)

fm(z1, . . . , zm) = Resz(fm−k(z1, . . . , zm−k−1, z), fk+2(zm−k, . . . , zm, z))

for m ≥ 4 and m − 3 ≥ k ≥ 1.

We brieﬂy recall the properties of summation polynomials that we will need.

Theorem 1 ([41], Theorem 1). For any m ≥ 3, let Z1, . . . , Zm be elements of the algebraic
closure Fq of Fq. Then fm(Z1, . . . , Zm) = 0 if and only if there exist Y1, . . . , Ym ∈ Fq such that
the points (Zi, Yi) are on E and (Z1, Y1) + . . . + (Zm, Ym) = O in the group E(Fq). Furthermore,
fm is absolutely irreducible and symmetric of degree 2m−2 in each variable. The total degree is
(m − 1)2m−2.

6

Remark 4. Deﬁnition 3 is the original deﬁnition that Semaev gave in [41]. Semaev polynomials
can be deﬁned and computed also over a ﬁnite ﬁeld of characteristic 2 or 3. Although the formulas
look diﬀerent, the properties are analogous to those stated in Theorem 1. Hence all the results
that we prove in this paper hold, with the appropriate adjustments, over a ﬁnite ﬁeld of any
charasteristic.

Since the points in Tn are characterized by the condition that their Frobenius conjugates
sum to zero, we can use the Semaev polynomial to give an equation only in x. It is clear that
) = 0. The opposite implication has some obvious

(X, Y ) ∈ Tn implies fn(X, X q, . . . , X qn−1

exceptions.

Lemma 1. For any prime n, let Tn denote the trace zero subgroup associated with the ﬁeld
extension Fqn |Fq. We have

⌊ n

2 ⌋−1

[
k=0

(E[n − 2k](Fq) + E[2] ∩ Tn) ⊆ {(X, Y ) ∈ E(Fqn ) | fn(X, X q, . . . , X qn−1

) = 0} ∪ {O}.

Proof. Let k ∈ {0, . . . , ⌊ n
we have

2 ⌋}, and let P = Q + R with Q ∈ E[n − 2k](Fq), R ∈ E[2] ∩ Tn. Then

P + ϕ(P ) + . . . + ϕn−2k−1(P )

+ ϕn−2k(P ) − ϕn−2k+1(P ) + . . . − ϕn−1(P )

|

n−2k summands
{z
+

= Q + . . . + Q

Q − Q + . . . − Q

}

|

2k summands with alternating signs
{z

}
+R + ϕ(R) + . . . + ϕn−1(R)

n−2k summands
{z
= (n − 2k)Q + Tr(R)

}

|

2k summands with alternating signs
{z

|

}

= O,

where for the ﬁrst equality we use that Q ∈ E(Fq) and R ∈ E[2], and for the third equality we
use that Q ∈ E[n − 2k] and R ∈ Tn.

Notice that the points of the form P = Q + R with Q ∈ E[n − 2k](Fq) and R ∈ E[2] ∩ Tn are
not trace zero points if Q 6= O and 3 ≤ n − 2k ≤ n − 2. For the interesting cases n = 3 and 5 we
prove that these are the only exceptions.

Proposition 4. Let Tn be the trace zero subgroup associated with the ﬁeld extension Fqn |Fq. We
have

T3
T5 ∪ (E[3](Fq) + E[2] ∩ T5) = {(X, Y ) ∈ E(Fq5 ) | f5(X, X q, . . . , X q

= {(X, Y ) ∈ E(Fq3 ) | f3(X, X q, X q

4

2

) = 0} ∪ {O}

) = 0} ∪ {O}.

2

Proof. Let P = (X, Y ) ∈ E(Fq3 ) with f3(X, X q, X q
polynomial, there exist Y0, Y1, Y2 ∈ Fq such that (X, Y0) + (X q, Y1) + (X q
, Y2) = O. Obviously
we have Yi = ±Y qi
, i = 0, 1, 2, so P ± ϕ(P ) ± ϕ2(P ) = O. We have to show that all signs are
“+”. Suppose P − ϕ(P ) + ϕ2(P ) = O. By applying ϕ, we get ϕ(P ) − ϕ2(P ) + P = O. Adding
these two equations gives 2P = O, implying that P = −P , hence P + ϕ(P ) + ϕ2(P ) = O. In
particular, P ∈ T3. The rest follows by symmetry.

) = 0. Then by the properties of the Semaev

Now let P = (X, Y ) ∈ E(Fq5 ) with f5(X, X q, . . . , X q

) = 0. Then as before, P ± ϕ(P ) ±
ϕ2(P ) ± ϕ3(P ) ± ϕ4(P ) = O. If all signs are “+”, then P ∈ T5. We treat all other cases below.
[one minus] Assume P + ϕ(P ) + ϕ2(P ) + ϕ3(P ) − ϕ4(P ) = O. Applying ϕ to the equation and
adding the two equations, we get 2ϕ(P ) + 2ϕ2(P ) + 2ϕ3(P ) = O, and by substituting into twice

4

2

7

the ﬁrst equation, 2P = ϕ4(2P ). Hence 2P ∈ E(Fq4 ) ∩ E(Fq5 ) = E(Fq), so 2P ∈ E[3](Fq). Now
P = Q + R ∈ E[6] is the sum of Q ∈ E[3] and R ∈ E[2]. We have Q = −2Q = −2P ∈ E[3](Fq).
From the original equation P +ϕ(P )+ϕ2(P )+ϕ3(P )−ϕ4(P ) = O, we get an analogous equation
in R, which together with R ∈ E[2] gives R ∈ T5.

[two minuses in a row] Assume P + ϕ(P ) + ϕ2(P ) − ϕ3(P ) − ϕ4(P ) = O. Applying ϕ2 and

adding, we get 2ϕ2(P ) = O, hence P = −P and therefore P ∈ T5.

[two minuses not in a row] Finally, assume P + ϕ(P ) − ϕ2(P ) + ϕ3(P ) − ϕ4(P ) = O. Applying

ϕ and adding, we get 2ϕ(P ) = O, hence P = −P and therefore P ∈ T5.

The other cases follow by symmetry, thus proving the claim.

Remark 5. In the sequel, we use fn as an equation for Tn. In practice however, for any root
X ∈ Fqn of fn(x, xq, . . . , xqn−1

) we need to be able to decide eﬃciently whether (X, Y ) ∈ Tn.

For n = 3 we only need to check that Y ∈ Fq3 . This guarantees that (X, Y ) ∈ T3, by

Proposition 4.

For n = 5, by Proposition 4 we have to exclude from the solutions of f5 = 0 the points
(X, Y ) ∈ E such that Y /∈ Fq5 and the points of the form Q + R where O 6= Q ∈ E[3](Fq) and
R ∈ E[2] ∩ T5. Let L be the set of the x-coordinates of the elements Q + R ∈ E[3](Fq) + E[2] ∩ T5
with Q 6= O. Then L has cardinality at most 16. A root X ∈ Fq5 of f5(x, xq, . . . , xq
) corresponds
to a point (X, Y ) ∈ T5 if and only if X /∈ L and Y ∈ Fq5 .

4

The x-coordinates of the points of Tn correspond to zeros of the Weil restriction of the
) ∈ Fq[x]. Therefore,

). Since E is deﬁned over Fq, then fn(x, . . . , xqn−1

polynomial fn(x, . . . , xqn−1
for any α ∈ Fqn we have

fn(α, . . . , αqn−1

)q = fn(αq, . . . , αqn−1

, α) = fn(α, . . . , αqn−1

),

where the second equality follows from the symmetry of the Semaev polynomial. It follows that

fn(α, . . . , αqn−1

) ∈ Fq

for all α ∈ Fqn .

(2)

We use the relations (1) to write equations for the Weil restriction. Notice that since we are
only interested in the Fq-rational points of the Weil restriction, we may reduce the equations
that we obtain modulo xq
i − xi for i = 0, . . . , n − 1. Hence we obtain equations in x0, . . . , xn−1
of degree less than q in each indeterminate. Now (2) together with Proposition 3 implies that
the last n − 1 equations are identically zero. Therefore, although Weil restriction could produce
up to n equations, by reducing modulo the equations xq
i − xi we obtain only one equation at the
end. We denote this new equation by

˜fn(x0, . . . , xn−1) = 0.

We stress that its Fq-solutions correspond to the elements of Tn, together with some extra points
described in Lemma 1 and Proposition 4. In Remark 5 we discussed how to distinguish the extra
solutions. Since we reduce the Weil restriction of fn(x, xq, . . . , xqn−1
i − xi, the qth
powers disappear, and we are left with an equation ˜fn of the same degree as the original Semaev
polynomial fn.

) modulo xq

Concerning the representation, we now have an equation that is compatible with dropping the
y-coordinate. It is a natural idea to drop one Xi in order to obtain a compact representation,
mimicking the approach of [35, 32, 42]. The decompression algorithm could then use ˜fn to
recompute the missing coordinate. However, since ˜fn has relatively large degree, this would
identify more points than desired. Moreover, the computation of the Weil restriction of the
Semaev polynomials requires a large amount of memory. It is already very demanding for n = 5.
We present a modiﬁed approach to the problem in the next section.

8

4 An optimal representation

As the Semaev polynomials are symmetric in nature, they can be written in terms of the sym-
metric functions. We write

fn(z1, . . . , zn) = gn(e1(z1, . . . , zn), . . . , en(z1, . . . , zn)),

(3)

where ei are the elementary symmetric polynomials

ei(z1, . . . , zn) =

X
1≤j1<...<ji≤n

zj1 · . . . · zji ,

and call gn the “symmetrized” n-th Semaev polynomial. The advantage over the original Semaev
polynomial is that gn has lower degree (e.g. 2 instead of 4 for n = 3, and 8 instead of 32 for
n = 5) and fewer Fqn -solutions, as it respects the inherent symmetry of the sum (i.e. where fn has
as solutions all permutations of possible x-coordinates, gn has only one solution, the symmetric
functions of these coordinates). See [29] for how to eﬃciently compute the symmetrized Semaev
polynomials. In this sense,

gn(s1, . . . , sn) = 0

(4)

also describes the points of Tn via the relations

si = ei(x, xq, . . . , xqn−1

), i = 1, . . . , n.

Notice that for X ∈ Fqn , we have ei(X, X q, . . . , X qn−1
) ∈ Fq. Summarizing, gn is a polyno-
mial with Fq-coeﬃcients by equation (3), as well as the polynomials ˜ei that we obtain by Weil
restriction from the symmetric functions in the q-powers of x:

si = ˜ei(x0, . . . , xn−1), i = 1, . . . , n.

(5)

Furthermore, we get exactly one new relation per equation (reducing modulo xq
i −xi and applying
Proposition 3, as before). Hence we have a total of n equations in the Weil restriction coordinates
describing the symmetric functions. The qth powers in the exponents disappear thanks to the
reduction, and each ˜ei is homogeneous of degree i. A combination of the equations (4) and
(5) enables us to give a compact representation of the aﬃne points of Tn = V (Fq). It can be
computed with the compression algorithm, the full point can be recovered (up to some small
ambiguity) with the decompression algorithm.

Compression.
Input: P = (X0, . . . , Xn−1, Y0, . . . , Yn−1) ∈ V (Fq)

Compute the symmetric functions of the Frobenius conjugates of X:

Si = ˜ei(X0, . . . , Xn−1), i = 1, . . . , n − 1

Output: (S1, . . . , Sn−1) ∈ Fn−1

q

Decompression.
Input: (S1, . . . , Sn−1) ∈ Fn−1

q

9

Solve gn(S1, . . . , Sn−1, t) = 0 for t.
For each solution τ , ﬁnd a solution (if it exists) of the system

S1 = ˜e1(x0, . . . , xn−1)

...

Sn−1 = ˜en−1(x0, . . . , xn−1)

τ = ˜en(x0, . . . , xn−1).

(6)

0 , . . . , X (j)

0 + . . . + X (j)

n−1), recompute one of the y-coordinates Y (j) belonging to

For the found solution (X (j)
X (j) = X (j)
If (X (j), Y (j)) ∈ Tn, then add ±P = (X (j), ±Y (j)) and all their Frobenius conjugates to the set
of output points.
Output: All points of Tn = V (Fq) that have (S1, . . . , Sn−1) as compact representation

n−1ζn−1 using the curve equation.

Remark 6. Because of Lemma 1, in the last step of the decompression algorithm, for each root
X (j) of the polynomial fn one needs to check that the point (X (j), Y (j)) ∈ Tn. This step can in
practice be eliminated for n = 3, 5, as discussed in Remark 5.

For a small set of points, equation (4) vanishes when evaluated in the given S1, . . . , Sn−1.
For such points P , any t ∈ Fq solves the equation gn(S1, . . . , Sn−1, t) = 0, making the com-
putational eﬀort for decompressing Compress(P ) very large. Therefore, our decompression
algorithm is not practical for such points. However, for almost all points P ∈ V (Fq) the
polynomial gn(S1, . . . , Sn−1, t) has only a small number of roots in t (upper bounded by the
degree of gn in the variable t). For our analysis, we assume that we are in the latter case.
Since the points of V (Fq) are described by gn(˜e1(x0, . . . , xn−1), . . . , ˜en(x0, . . . , xn−1)), we have
P ∈ Decompress(Compress(P )). The relevant question is how many more points the output may
contain.

First of all, by compressing a point, we lose the ability to distinguish between Frobenius
conjugates of points, since for each solution of system (6), all Frobenius conjugates are also
solutions. This can be compared to the fact that when using the “standard” compression, we
lose the ability to distinguish between points and their negatives. If desired, a few extra bits can
be used to remember that information. Alternatively, we can think of working in Tn modulo an
equivalence relation that identiﬁes the Frobenius conjugates of each point and its negative. This
reduces the size of the group Tn by a factor 2n, which is a small price to pay considering the
amount of memory saved by applying the compression, especially since n is small in practice.
Notice also that it is enough to compute one solution of system (6), since the set of all solutions
consists precisely of the Frobenius conjugates of one point. This is because any polynomial in n
variables which is left invariant by any permutation of the variables can be written uniquely as
a polynomial in the elementary symmetric functions e1, . . . , en.

Now, how many diﬀerent equivalence classes of points can be output by the decompression
algorithm depends only on the degree of gn in the last indeterminate. For n = 3 the degree is one
and decompression therefore outputs only a single class. As n grows, the degree of the Semaev
polynomial also grows, thus producing more ambiguity in the recovery process. This also reﬂects
the growth in the number of extra points which satisfy the equation coming from the Semaev
polynomial, as seen in Lemma 1.

Notice moreover that there may be solutions τ of gn(S1, . . . , Sn−1, t) = 0 for which system
(6) has no solutions, and that not all the solutions of system (6) produce an equivalence class

of points on the trace zero variety. E.g., if X ∈ Fqn satisﬁes fn(X, X q, . . . , X qn−1
corresponding point P = (X, Y ) ∈ E may have Y ∈ Fq2n \ Fqn . In this case P /∈ Tn.

) = 0, the

10

Since our algorithms are most useful for n = 3 and 5, an asymptotic complexity analysis
for general n does not make much sense. In fact, it is easy to count the number of additions,
multiplications, and squarings in Fq needed to compute the representation just from looking
at the formulas for s1, . . . , sn−1. We do this for the cases n = 3 and 5 in Sections 5 and 6,
respectively. There, we also discuss the eﬃciency of our decompression algorithm and how it
compares to the approaches of [35, 42].

Remark 7. In order to compute with points of Tn, we suggest to decompress a point, perform
the operation in E(Fqn ), and compress again the result. Since compression and decompression
is very eﬃcient, this adds only little overhead.
In an environment with little storage and/or
bandwidth capacity, the memory savings of compressed points may well be worth this small
trade-oﬀ with the eﬃciency of the arithmetic. Also notice that scalar multiplication of trace zero
points in E(Fqn ) is more eﬃcient than scalar multiplication of arbitrary points of E(Fqn ), due to
a speed-up using the Frobenius endomorphism, as pointed out by Frey [15] and studied in detail
by Lange [31, 32] and subsequently by Avanzi and Cesena [1].

Our recommendation corresponds to usual implementation practice in the setting of point
compression: Even when a method to compute with compressed points is available, it is usually
preferable to perform decompression, compute with the point in its original representation, and
compress the result. For example, Galbraith-Lin show in [16] that although it is possible to
compute pairings using the x-coordinates of the input points only, it is more eﬃcient in most
cases (namely, whenever the embedding degree is greater than 2) to recompute the y-coordinates
of the input points and perform the pairing computation on the full input points. As a second
example, let us consider the following two methods for scalar multiplication by k of an elliptic
curve point P = (X, Y ) when only X is given:

1. Use the Montgomery ladder, which computes the x-coordinate of kP from X only.

2. Find Y by computing a square root, apply a fast scalar multiplication algorithm to (X,Y),

and return only the x-coordinate of the result.

All recent speed records for scalar multiplication on elliptic curves have been set using algorithms
that need the full point P , in other words with the second approach, see e.g. [4, 34, 36, 14].
Timings typically ignore the additional cost for point decompression, but there is strong evidence
that on a large class of elliptic curves the second approach is faster. This is the basis for our
suggestion to follow the second approach when working with compressed points of Tn.

5 Explicit equations for extension degree 3

We give explicit equations for n = 3, where we write Fq3 = Fq[ζ]/(ζ3 − µ) and use 1, ζ, ζ2 as
a basis for Fq3 |Fq. For completeness, we start with the standard equations for the trace zero
variety (see [15]), although we do not make further use of them in our approach. They describe
an open aﬃne part of the trace zero variety (i.e. they hold when x1, x2 6= 0):

0 + 2µy1y2 = x3

y2
2y0y1 + µy2
2y0y2 + y2

2 = 3x2
1 = 3x2
x1y2 = x2y1.

0 + µx3

1 + µ2x3
0x1 + 3µx0x2
0x2 + 3x0x2

2 + 6µx0x1x2 + Ax0 + B
2 + 3µx2
1x2 + Ax1
1 + 3µx1x2
2 + Ax2

(7)

The equation that we found in Section 3 only involves the x-coordinate and is

f3(x, xq, xq

2

) = x2q

2

+2q − 2x2q

2

+q+1 + x2q

2

+q − 2xq

2

+2q+1 − 2xq

2

+q+2 − 2Axq

2

+q

2

−2Axq

+1 − 4Bxq

2

+ x2q+2 − 2Axq+1 − 4Bxq − 4Bx + A2.

11

For Weil restriction, we write x = x0 + x1ζ + x2ζ2 and get

x = x0 + x1ζ + x2ζ2

xq = x0 + µbx1ζ + µ2bx2ζ2
= x0 + µ2bx1ζ + µbx2ζ2,

2

xq

where b = q−1
for xq

i when looking for Fq-solutions. This gives

3 . The second and third equalities follow from observing that we can substitute xi

˜f3(x0, x1, x2) = −3x4

0 − 12µ2x0x3
2 − 6Ax2

1x2

2 − 12µx0x3
0 + 6Aµx1x2 − 12Bx0 + A2.

1 + 18µx2

0x1x2

+9µ2x2

The symmetrized third Semaev polynomial is

g3(s1, s2, s3) = s2

2 − 4s1s3 − 4Bs1 − 2As2 + A2

and describes the trace zero subgroup via

2

s1 = x + xq + xq
s2 = x1+q + x1+q
s3 = x1+q+q

2

2

2

+ xq+q

= 3x0
= 3x2
= x3

0 − 3µx1x2

0 − 3µx0x1x2 + µx3

1 + µ2x3
2.

(8)

(9)

(10)

So for compression of a point (x0, x1, x2, y0, y1, y2), we use the coordinates

(s1, s2) = (3x0, 3x2

0 − 3µx1x2),

and for decompression, we have to solve g3(s1, s2, s3) = 0 for s3, where g3 is given by equation
(9). Since the equation is linear in s3, the missing coordinate can be recovered uniquely, except
when s1 = 0. This is the case only for a small set of points. Notice moreover that the points
(0, s2, s3) with s2
2 − 2As2 + A2 = 0 satisfy equation (9) for every s3. The only ambiguity in
decompression comes from solving system (10), which yields the Frobenius conjugates x, xq, xq
of the original x. So for n = 3 this gives an optimal representation in our sense.

2

The following representation is equivalent to the above, but easier to compute. Set

t1 = x0, t2 = x1x2, t3 = x3

1 + µx3
2,

(11)

and take (t1, t2) as a representation. The relation between the two sets of coordinates is

s1 = 3t1, s2 = 3t2

1 − 3µt2, s3 = t3

1 − 3µt1t2 + µt3.

In this case, we recover t3 from the equation

−3t4

1 + 18µt2

1t2 + 9µ2t2

2 − 12µt1t3 − 12Bt1 − 6At2

1 + 6Aµt2 + A2.

The equation is linear in t3, thus making point recovery unique whenever t1 6= 0, but the
total degree is higher. Compared to the representation (s1, s2), fewer operations are needed
for compression and for computing the solutions of the system during decompression. Thus,
compression and decompression for this variant of the representation are more eﬃcient. We give
timings for 10, 20, 40, 60, and 79 bit ﬁelds in Table 1, where we see that compression is about
a factor 3 to 4 faster and decompression is slightly faster for the second method. Notice that
decompression timings are for recomputing the x-coordinate only.

12

Table 1: Average time in milliseconds for compression/decompression of one point when n = 3

q

210 − 3

220 − 3

240 − 87

260 − 93

279 − 67

Compression si
Compression ti
Decompression si
Decompression ti

0.007
0.002
0.124
0.090

0.014
0.007
0.159
0.132

0.028
0.008
0.731
0.610

0.039
0.010
0.987
0.956

0.064
0.015
1.586
1.545

All computations were done with Magma version 2.19.3 [7], running on one core of an Intel
Xeon Processor X7550 (2.00 GHz) on a Fujitsu Primergy RX900S1. Our Magma programs
are straight forward implementations of the methods presented here and are only meant as an
indication. No particular eﬀort has been put into optimizing them.

We give a concrete example, before concluding the section with a more detailed analysis of

the eﬃciency of our algorithms.

Example 2. Let E be the curve y2 = x3 + x + 368 over Fq, where q = 279 − 67 is a 79-bit prime,
and µ = 3. The trace zero subgroup of E(Fq3 ) has prime order of 158 bits. We choose a random
point (to save some space, we write only x-coordinates)

P = 260970034280824124824722 + 431820813779055023676698ζ + 496444425404915392572065ζ 2 ∈ T3

and compute

Compress(P ) = (178447193035157787121145, 159414355696879147312583)

Decompress(178447193035157787121145, 159414355696879147312583) =

{260970034280824124824722 + 431820813779055023676698ζ + 496444425404915392572065ζ 2 ,
260970034280824124824722 + 318397306102476549147695ζ + 124410673032925784958936ζ 2 ,
260970034280824124824722 + 458707699733097601881649ζ + 88070721176787997175041ζ 2 }

where the results of decompression are exactly the Frobenius conjugates of P . In our Magma
implementation, we solve system (10) over Fq similarly to how one would do it by hand, as
described below. Note that the solutions could also be found by computing the roots of the
polynomial x3 − s1x2 + s2x − s3 over Fq3 , but since the system is so simple for n = 3, solving
the system directly is faster in all instances.

When using the second variant of the representation, we compute

(t1, t2) = (260970034280824124824722, 492721032528256431308437)

and naturally get the same result for decompression by solving system (11) in a similar way.

Operation count for representation in the si. Where possible, we count squarings (S),
multiplications (M), and divisions (D) in Fq. We do not count multiplication by constants, since
they can often be chosen small (see [32]), and multiplication can then be performed by repeated
addition. Compressing a point clearly takes 1S+1M. Decompression requires the following steps.

• Evaluating g3(s1, s2, s3) in the ﬁrst two indeterminates and solving for the third indeter-

minate means computing s3 = 1

4s1 (s2(s2 − 2A) − 4Bs1 + A2), which takes 1M+1D.

• Given s1, s2, s3, we need to solve system (10) for x, or for x0, x1, x2. The most obvious
way would be to compute the roots of the univariate polynomial x3 − s1x2 + s2x − s3 over

13

Fq3. Finding all roots of a degree d polynomial over Fqn takes O(nlog2 3dlog2 3 log d log(dqn))
operations in Fq using Karatsuba’s algorithm for polynomial multiplication (see [22]). In
our case, the degree and n are constants, and hence factoring this polynomial takes O(log q)
operations in Fq. However, since the system is so simple, in practice it is better to solve
directly for x0, x1, x2 over Fq. We know that the system has exactly three solutions (except
in very few cases, where it has a unique solution in Fq, i.e. x1 = x2 = 0). We get x0 from
s1 for free. Assuming that x1 6= 0 (the special case when x0 = 0 is easier than this general
case), we can solve the second equation for x2, plug this into the third equation, and
multiply by the common denominator 27µ3x3

1. In this way, we obtain the equation

27µ4x6

1 + 27µ3(x0(s2 − 2x2

0) − s3)x3

1 + µ2(3x2

0 − s2)3,

1 is a constant, the coeﬃcient of x3

which must be solved for x1. The coeﬃcient of x6
1 can be
computed with 1S+1M, and the constant term can then be computed with 1S+1M. Now
1 with the quadratic formula, which takes 1S and a square root in Fq for
we can solve for x3
the ﬁrst value, which will have either no or three distinct cube roots. In case it has none,
we compute the second value for x3
1, using only an extra addition, and the three distinct
cube roots of this number. This gives a total of 3 values for x1. Finally, we can compute
x2 = 3x
3µx1 , which takes 1D for the ﬁrst, and a multiplication by the inverse of a cube
root of unity for the other two values. Altogether, solving system (10) takes a total of at
most 3S+2M+1D, 1 square root, and 2 cube roots in Fq.

0−s2

2

• Finally, for each of the at most 3 values for x, we recompute a corresponding y-coordinate
from the curve equation and check that it belongs to Fq3 . Since these are standard proce-
dures for elliptic curves, we do not count operations for these tasks.

Therefore, the decompression algorithm takes at most 3S+3M+2D, one square root, and two
cube roots in Fq. The cost of computing the roots depends on the speciﬁc choice of the ﬁeld and
on the implementation, but it clearly dominates this computation.

Operation count for representation in the ti. In this case, compression takes only 1M. For
decompression, we proceed as follows.

• Given t1 and t2, we recover t3 from the equation t3 = 1

12µt1 (−3t4

1+(18µt2

1 +9µ2t2 +6Aµ)t2 −

12Bt1 − 6At2

1 + A2). This takes 2S+1M+1D.

• To solve system (11), again assuming x1 6= 0, we have to ﬁnd the roots of the equation

x6

1 − t3x3

1 + µt3
2.

The coeﬃcients of this equation can be computed with a total of 1S+1M. We proceed as
above to compute 3 values for x1 using 1S, 1 square root, and 2 cube roots. Finally, we
compute x2 = t2
x1 using 1D. Thus, solving the system takes a total of at most 2S+1M+1D,
1 square root, and 2 cube roots.

In total, decompression takes at most 4S+2M+2D, 1 square root, and 2 cube roots. The cost
of this computation is comparable to the decompression using si. This corresponds to our
experimental results with Magma (see Table 1).

Comparison with Silverberg’s method. The representation of [42] consists of the last n − 1
Weil restriction coordinates, together with three extra bits, say 0 ≤ ν ≤ 3 to resolve ambiguity

14

in recovering the x-coordinate and 0 ≤ λ ≤ 1 to determine the sign of the y-coordinate. So
in our notation, Silverberg proposes to represent a point (x, y) ∈ T3 is via the coordinates
(x1, x2, ν, λ). The compression and decompression algorithms (in characteristic not equal to 3)
carry out essentially the same steps:

• Compute a univariate polynomial of degree 4. The coeﬃcients are polynomials over Fq in

2 indeterminates of degree at most 4.

• Compute the (up to 4) roots of this polynomial. During compression, this determines ν.
During decompression, ν determines which root is the correct one, and it is then used to
compute x0 via addition and multiplication with constants.

• During decompression, compute the y-coordinate from the curve equation, using λ to de-

termine its sign. We disregard this step when estimating the complexity.

Since [42] does not contain a detailed analysis of the decompression algorithm, we cannot compare
the exact number of operations. However, the essential diﬀerence with our approach is that
Silverberg’s compression and decompression algorithms both require computing the roots of a
degree 4 polynomial over Fq. For compression, this is clearly more expensive than our method,
which consists only of evaluating some small expressions. For decompression, this is also less
eﬃcient than our method, which computes only a root of a quadratic polynomial, since running
a root ﬁnding algorithm, or using explicit formulas for the solutions (i.e. solving the quartic by
radicals), is much more complicated than computing the roots of our equation.

One might argue that it is possible to represent (x, y) via the coordinates (x1, x2) only. In
such a case, compression would consist simply of dropping y and x0 and would therefore have
no computational cost. Without remembering ν and λ to resolve ambiguity, this representation
would identify up to 4 x-coordinates and up to 8 full points. This is not much worse than our
representation, which identiﬁes up to 3 x-coordinates and 6 full points. However, it is not clear
that this identiﬁcation is compatible with scalar multiplication of points. Therefore, one may
want to use at least ν to distinguish between the recovered x-coordinates. This is in contrast
with our situation, where we know exactly which points are recovered during decompression (i.e.
the three Frobenius conjugates of the original point). Identifying these three points is compatible
with scalar multiplication, since P = ϕi(Q) implies kP = ϕi(kQ) for all k ∈ N and P, Q ∈ T3,
and so no extra bits are necessary.

Comparison with Naumann’s method. Naumann [35] studies trace zero varieties for n = 3.
He does not give explicit compression and decompression algorithms, but he derives an equation
In fact, his equation is identical to
for the trace zero subgroup that may be used for such.
our equation (8), the Weil restriction of the (unsymmetrized) Semaev polynomial. However, he
obtains it in a diﬀerent way, namely, by eliminating from system (7).

Naumann suggests a compression method analogous to the one of Silverberg: A point is
represented via the coordinates (x1, x2, ν, λ). For decompression, x0 is recomputed from a quartic
equation, 0 ≤ ν ≤ 3 determines which root of the equation is the correct x0, and 0 ≤ λ ≤ 1
determines the sign of the y-coordinate. Hence the quartic equation must be solved during
both compression and decompression. Naumann’s equation is diﬀerent from Silverberg’s, yet the
analysis of his method is analogous to that of Silverberg’s method, and the conclusions are the
same. In particular, his algorithms are less eﬃcient than ours, and it is not clear whether it is
possible to drop ν from the representation and still have a well deﬁned scalar multiplication.

Security issues. To the extent of our knowledge, there are no known attacks on the DLP
in T3 whose complexity is lower than generic (square root) attacks, provided that one chooses

15

the parameters according to usual cryptographic practice. In particular, the group should have
prime or almost prime order and be suﬃciently large (e.g. 160 or 200 bits). We stress that
index calculus methods, as detailed in [20] among many other works, do not yield an attack
which is better than generic (square root) attacks in this setting, since the trace zero variety has
dimension 2.

6 Explicit equations for extension degree 5

The ﬁfth Semaev polynomial is too big to be printed here, but a computer program can easily
work with it.
It has total degree 32 and degree 8 in each indeterminate. The symmetrized
ﬁfth Semaev polynomial has total degree 8 and degree 6 in the last indeterminate. In fact, it
has degree 6 in the ﬁrst, third and ﬁfth indeterminate, and degree 8 in the second and fourth
indeterminate. We can compute it eﬃciently with Magma.
It has a small number of terms
compared to the original polynomial, but printing it here would still take several pages.

The fact that we recover the missing coordinate from a degree 6 polynomial introduces some
indeterminacy in the decompression process. However, extensive Magma experiments for dif-
ferent ﬁeld sizes and curves show that for more than 90% of all points in T5, only a single
class of Frobenius conjugates is recovered. For another 9%, two classes (corresponding to 10
x-coordinates) are recovered. Thus the ambiguity is very small for a great majority of points.
In any case, this improves upon the approach of [42], where the missing coordinate is recovered
from a degree 27 polynomial, thus possibly yielding 27 diﬀerent x-coordinates.

The Weil restriction of the symmetric functions is

s1 = 5x0
s2 = 10x2
s3 = 10x3
s4 = 5x4

s5 = x5

0 − 5µx1x4 − 5µx2x3
0 + 5µ2x2

3x4 + 5µ2x2x2
0x1x4 − 15µx2

4 + 5µx1x2
0x2x3 − 5µx3

2 + 5µx2

1x3 − 15µx0x1x4 − 15µx0x2x3
2x4 − 5µ3x3x3

3 − 5µ2x3

1x2 − 5µ2x1x3

0 − 15µx2

1x3 + 10µx0x1x2

2 + 10µ2x0x2

3x4 + 10µ2x0x2x2

2 − 5µ2x1x3

2x3 − 5µ3x1x2x3

4 − 5µ3x2x3

4 + 10µx0x2
3 + µ4x5

4 + µx5
3 − 5µ2x0x3
0x1x2

1x3 + 5µx2

+5µ2x2

1x2
0 + µ3x5
−5µ2x0x1x3
+5µx2
+5µ2x2

0x2

1x2

2x4 + 5µ2x2

1x2x2

1 + µ2x5
2x4 − 5µ3x0x3x3
2 + 5µ2x2

0x2x2
3 + 5µ3x1x2

4 − 5µ2x3
0x2
4 + 5µ3x2

4 + 5µ2x2
3x2

0x1x4 − 5µx3

1x3x4 − 5µx3
3x4 + 5µ2x0x2
2x3x2

1x2
4 − 5µ2x0x1x2x3x4.

4 + 5µ2x0x2

2x2

3

1x2

4 + 5µ2x2
4 − 5µ2x1x2x3x4
3x4 − 5µx0x3
0x2x3
2x2

3

The compression algorithm computes s1, . . . , s4 according to these formulas over Fq. The de-
compression algorithm solves a degree 6 equation for s5 and then recomputes the x-coordinate
of the point. For the last step, we test two methods: We compute x by factoring the polynomial
x5 − s1x4 + s2x3 − s3x2 + s4x − s5 over Fq5 , and we compute x0, . . . , x4 by solving the above
system over Fq with a Gr¨obner basis computation. Our experiments show that polynomial fac-
torization can be up to 20 times as fast as computing a lexicographic Gr¨obner basis in Magma
for some choices of q, and the entire decompression algorithm can be up to a factor 6 faster
when implementing the polynomial factorization method. We give some exemplary timings for
both methods for ﬁelds of 10, 20, 30, 40, 50 and 60 bits in Table 2. However, these experimental
results can only be an indication: In Magma, the performance of the algorithms depends on the
speciﬁc choice of q. In addition, any implementation exploiting a special shape of q would most
likely produce better results.

16

Table 2: Average time in milliseconds for compression/decompression of one point when n = 5

q

210 − 3

220 − 5

230 − 173

240 − 195

250 − 113

260 − 695

Compression si
Compression ti
Decompression si poly factorization
Decompression si Gr¨obner basis
Decompression ti Gr¨obner basis

0.041
0.017
5.536
24.134
38.375

0.048
0.022
16.480
26.470
40.198

0.052
0.024
21.423
39.593
60.438

0.106
0.031
45.080
101.559
132.484

0.108
0.021
55.872
104.490
133.088

0.112
0.048
59.520
118.991
150.083

As for n = 3, we suggest an equivalent representation (t1, t2, t3, t4) where

t1 = x0
t2 = x1x4 + x2x3
1x3 + x1x2
t3 = x2
3 + µx2
t4 = µx2
t5 = x5

2x2
1 + µx5
+5µ2x1x2

3x2

3x4 + µx2x2

4

2 + µx2
1x2

2 + µ2x5

4 − µx1x3
3 + µ3x5

1x2 − µx3
3 − x3
4 + 5µx2
1x2x2
1x3x4 − 5µ2x2x3

4 − 5µx3

2x4 − µ2x3x3

4 + µx1x2x3x4

1x2

3 + 5µx2
3x4 − 5µ2x1x2x3

2x4 + 5µ2x2

2x3x2
4 − 5µx1x3

4

2x3

and

s1 = 5t1
s2 = 10t2
s3 = 10t3
s4 = 5t4
s5 = t5

1 − 5µt2
1 − 15µt1t2 + 5µt3

1 − 15µt2

1t2 + 10µt1t3 + 5µt4

1 − 5µt3

1t2 + 5µt2

1t3 + 5µt1t4 + µt5.

(12)

(13)

Compared to the representation in the si, this representation gives a faster compression, but a
slower decompression. Therefore, this approach may be useful in a setting where compression
must be particularly eﬃcient.

For decompression, the missing coordinate t5 can be recomputed from a degree 6 equation,
which we obtain by substituting the relations (13) into the symmetrized ﬁfth Semaev polynomial.
Afterwards we may either recompute s1, . . . , s5 from t1, . . . , t5 according to system (13) and
solve x5 − s1x4 + s2x3 − s3x2 + s4x − s5 for x, or else we may solve system (12) directly for
x0, . . . , x4 with Gr¨obner basis techniques. The polynomial factorization method is equivalent
to using the representation in the si, only that some of the computations are shifted from the
compression to the decompression algorithm. The Gr¨obner basis method (use ti and compute
Gr¨obner basis, “second method”) compares to using si with Gr¨obner basis (“ﬁrst method”) as
given in Table 2. We see that the second method is a factor 2 to 3 faster in compression, but
slower in decompression. The reason for this is that the polynomial used to recompute the
missing coordinate is more complicated for the second method, and evaluation of polynomials
is quite slow in Magma. Solving for the missing coordinate takes 5 times longer for the second
method. The solution of system (6), which we achieve by computing a lexicographic Gr¨obner
basis and solving the resulting triangular system in the obvious way, takes the same amount of
time in both cases.

We now give an example of our compression/decompression algorithms, including two points
P on the trace zero variety where Decompress(Compress(P )) produces the minimum and maxi-
mum possible number of outputs.

Example 3. Let E be the curve y2 = x3 + x + 135 over Fq, where q = 260 − 695 is a 60-bit
prime, and µ = 3. The trace zero subgroup of E(Fq5 ) has prime order of 240 bits. We choose a

17

random point

P = 697340666673436518 + 801324486821916366ζ + 191523769921581598ζ

2

+193574581008452232ζ

3

+ 808272437423069772ζ

4

∈ T5

and compute

Compress(P ) = (27938819546643747, 599177118073319826, 587362643323803394, 899440023033601132)

Decompress(27938819546643747, 599177118073319826, 587362643323803394, 899440023033601132)

= {697340666673436518 + 801324486821916366ζ + 191523769921581598ζ 2

+ 193574581008452232ζ 3 + 808272437423069772ζ 4 ,
697340666673436518 + 836712212802745328ζ + 506907366758395901ζ 2
+ 517000572714098077ζ 3 + 268866625974497959ζ 4 ,
697340666673436518 + 960543166171367987ζ + 126552294958642222ζ 2
+ 448251978051599093ζ 3 + 74315924307841334ζ 4 ,
697340666673436518 + 810370833605859760ζ + 539948230971075773ζ 2
+ 1032750511909194579ζ 3 + 944608723064092684ζ 4 ,
697340666673436518 + 49813814418649402ζ + 940911346603997068ζ 2
+ 114265365530348581ζ 3 + 209779298444190813ζ 4 }.

When using the second variant of the representation, we compute

(t1, t2, t3, t4) = (697340666673436518, 553115374027544004, 315951679773440541, 285024754797056479).

For this point, the results of decompression are exactly the Frobenius conjugates of P . However,
this is not always the case. In rare cases, the algorithm may recover up to six classes of Frobenius
conjugates. We give an example of a point for which three classes of Frobenius conjugates are
recovered:

P = 760010909342414570 + 568064535058825884ζ + 244006548504894796ζ

2

+446522043528586762ζ

3

+ 731314735984238952ζ

4

∈ T5.

Operation count for representation in the si. Given x0, . . . , x4, the numbers t1, . . . , t4
can be computed with a total of 5S+13M according to (12). Then s1, . . . , s4 can be computed
from those numbers with 2S+3M as given in (13). This seems to be the best way to compute
s1, . . . , s4, since these formulas group the terms that appear several times. Hence compression
takes a total of 7S+16M.

For decompression, the most costly part of the algorithm is factoring the polynomials. First,
the algorithm has to factor a degree 6 polynomial over Fq, and next, a degree 5 polynomial over
Fq5 . The asymptotic complexity for both of these is O(log q) operations in Fq.

Operation count for representation in the ti. Compression takes 5S+13M. For decom-
pression, we can either recompute s1, . . . , s5 from t1, . . . , t5 and factor the polynomial, in which
case this approach is exactly the same as the above. Or else we can solve system (12) by means
of a Gr¨obner basis computation over Fq. Since there are no practically meaningful bounds for
Gr¨obner basis computations, a complexity analysis of this approach makes no sense.

Comparison with Silverberg’s method. Concrete equations are presented in [42] for the
case where the ground ﬁeld has characteristic 3. The most costly parts of the compression and
decompression algorithms are computing the resultant of two polynomials of degree 6 and 8 with
coeﬃcients in Fq, and ﬁnding the roots of a degree 27 polynomial over Fq. In general, resultant
computations are diﬃcult, and the polynomial to be factored has much larger degree than those

18

in our algorithm. In Silverberg’s approach, ﬁve extra bits are required to distinguish between
the possible 27 roots of the polynomial.

Although neither Silverberg nor we give explicit equations for larger n, our understanding is
that our algorithm scales better with increasing n, since our method is more natural and respects
the structure of the group.

Security issues. We brieﬂy discuss the security issues connected with use of T5 in DL-based
and pairing-based cryptosystems.

Since T5 is a group of size q4, generic algorithms that solve the DLP in T5 have complexity
O(q2). Security threats in the context of DL-based cryptosystems are posed by algorithms for
solving the DLP that achieve lower complexity. There are two types of algorithms that one
needs to consider: First, cover attacks aim to transfer the DLP in E(Fq5 ) to the DLP in the
Picard group of a curve of larger (but still rather low) genus, see [21, 9]. The DLP is then
solved there using index calculus methods. Combining the results of [9] and [10], it is sometimes
possible to map the DLP from T5 into the Picard group of a genus 5 curve (which is usually
not hyperelliptic), where it can be solved with probabilistic complexity ˜O(q4/3) following the
approach of [11]. However, only a very small proportion of curves is aﬀected by this attack, and
such curves should be avoided in practice. Moreover, in order to avoid isogeny attacks, the curve
should be chosen such that 4 does not divide the order of T5, see [9]. Second, the index calculus
attack of [20] applies to T5 and has complexity ˜O(q3/2). This makes T5 not an ideal group to
use in a DL-based cryptosystem. Notice that in practice, however, the constant in the O is
very large, since the attack requires Gr¨obner basis computations, which are very time consuming
(their worst case complexity is doubly exponential in the size of the input), and often do not
terminate in practice. It is our impression that more in depth study is needed in order to give
a precise estimate of the feasibility of such an attack for a practical choice of the parameters.
We carried on preliminary experiments, which indicate that a straightforward application of
the method from [20] to T5 yields a system of equations which is very costly to compute (it
requires computing the Weil descent of the ﬁfth Semaev polynomial) and which Magma cannot
solve in several weeks and using more than 300 GB of memory on the same machine that we
used to carry out the experiments reported on in Sections 5 and 6 of this article. Notice that
solving such a system would (possibly) produce one relation, to be then used in an index calculus
attack. Therefore, in practice one would need to solve many such systems, in order to produce
the relations needed for the linear algebra step of the index calculus attack.

Trace zero varieties are even more interesting in the context of pairing-based cryptography.
The main motivation comes from [40], where Rubin and Silverberg show that supersingular
abelian varieties of dimension greater than one oﬀer more security than supersingular elliptic
curves, for the same group size. Trace zero varieties are explicitly mentioned in [40] as one of the
most relevant examples of abelian varieties for pairing-based cryptography. In order to estimate
the security of T5 in pairing-based cryptosystems, one needs to compare the complexities of
solving the DLP in T5 and in F
q5k , where k is the embedding degree, i.e., the smallest integer k
such that F
q5k contains the image of the pairing. A ﬁrst observation is that, since the results of
[40] hold over ﬁelds of any characteristic, one should avoid ﬁelds of small characteristic, so that
the recent attacks from [23, 28, 24, 2, 3] do not apply. Over a ﬁeld of large characteristic, the cover
and index calculus attacks that we discussed in the previous paragraph do not seem to pose a
serious security concern in the context of pairing-based cryptography. This is due to the fact that,
for most supersingular elliptic curves, the Frey-R¨uck or the MOV attack have lower complexity
than cover and index calculus attacks in the lines of
[20, 21, 9, 11]. In some cases however, the
choice of the security parameter may need to be adjusted, according to the complexity of these
index calculus attacks. As an example, let us discuss the choice of parameters for a pairing with

19

80-bits security. One needs a ﬁeld of about 1024-bits as the target of the pairing (avoiding ﬁelds
of small characteristic). If we assume that the pairing ends up in an extension ﬁeld of degree
k = 2 of the original ﬁeld Fq5 (this is the case for most supersingular elliptic curves), then q
should be a 102-bit number. A q3/2 attack on the group T5 on which the pairing is deﬁned would
result in 153-bit security, while a q4/3 attack would result in 136-bit security. However, on the
side of the ﬁnite ﬁeld the system has an 80-bit security, so the attacks from [20, 21, 9, 11] end
up not inﬂuencing the overall security of the pairing-based cryptosystem in this case. A related
comment is that an interesting case for pairings is when the DLP in T5 and in the ﬁnite ﬁeld
extension F
q5k where the pairing maps have the same complexity. In order to achieve this in our
previous example, we would need to have a security parameter k = 4, which can be achieved
by supersingular trace zero varieties. In this case, the complexity of solving a DLP in T5 and
in Fq20 are both about 80-bits when q ∼ 253. Summarizing, the complexity of the DLP in T5
coming from the works [20, 21, 9, 11] inﬂuences the choice of the speciﬁc curves that we use in
pairing-based applications, since it inﬂuences the security parameter k that makes the hardness
of solving the DLP in T5 and in F
q5k comparable, and the value of k depends on the choice of
the curve. However, in general it does not inﬂuence the size q of the ﬁeld that we work on, since
an attack can inﬂuence the value of q only if it has lower complexity than the Frey-R¨uck or the
MOV attack for supersingular elliptic curves. Therefore, using trace zero varieties instead of
elliptic curve groups in pairing-based cryptography has the advantages of enhancing the security
and allowing for more ﬂexibility in the setup of the system.

7 Conclusion

The Semaev polynomials give rise to a useful equation describing the Fq-rational points of the
trace zero variety. Its signiﬁcance is that it is one single equation in the x-coordinates of the
elliptic curve points, but unfortunately its degree grows quickly with n. Using this equation, we
obtain an eﬃcient method of point compression and decompression. It computes a representation
for the Fq-points of the trace zero variety that is optimal in size for n = 3 and for n = 5. Our
polynomials have lower degree than those used in the representations of [42] (1 compared to 4 for
n = 3, and 6 compared to 27 for n = 5) and [35] (1 compared to 3 for n = 3), thus allowing more
eﬃcient compression and decompression and less ambiguity in the recovery process. Finally, our
representation is interesting from a mathematical point of view, since it is the ﬁrst representation
(to our knowledge) that is compatible with scalar multiplication of points.

Acknowledgements We thank Pierrick Gaudry and Peter Schwabe for helpful discussions and Tanja
Lange for pointing out the work of Naumann. We are grateful to the mathematics department of the
Univerity of Z¨urich for access to their computing facilities. The authors were supported by the Swiss
National Science Foundation under Grant No. 123393.

References

[1] R. M. Avanzi and E. Cesena. Trace zero varieties over ﬁelds of characteristic 2 for cryptographic
applications. In Proceedings of the First Symposium on Algebraic Geometry and Its Applications
(SAGA ’07), pages 188–215, 2007.

[2] R. Barbulescu, C. Bouvier, J. Detrey, P. Gaudry, H. Jeljeli, E. Thom´e, M. Videau,
at

logarithm in GF(2809) with FFS.

Available

and P. Zimmermann.
http://hal.inria.fr/hal-00818124/.

Discrete

20

[3] R. Barbulescu, P. Gaudry, A. Joux, and E. Thom´e. A quasi-polynomial algorithm for discrete
logarithm in ﬁnite ﬁelds of small characteristic. Available at http://arxiv.org/abs/1306.4244,
2013.

[4] D. J. Bernstein, N. Duif, T. Lange, P. Schwabe, and B.-Y. Yang. High-speed high-security signatures.

J. Cryptogr. Eng., 2(2):77–89, 2012.

[5] G. Blady. Die Weil-Restriktion elliptischer Kurven in der Kryptographie. Master’s thesis, Univerit¨at

GHS Essen, 2002.

[6] J. W. Bos, C. Costello, H. Hisil, and K. Lauter. High-performance scalar multiplication using 8-
dimensional GLV/GLS decomposition. Available at http://eprint.iacr.org/2013/146, accepted
at CHES ’13, 2013.

[7] W. Bosma, J. Cannon, and C. Playoust. The Magma algebra system. I. The user language. J.

Symbolic Comput., 24:235–265, 1997.

[8] E. Cesena. Trace Zero Varieties in Pairing-based Cryptography. PhD thesis, Universit`a degli studi
Roma Tre, Available at http://ricerca.mat.uniroma3.it/dottorato/Tesi/tesicesena.pdf,
2010.

[9] C. Diem. The GHS attack in odd characteristic. Ramanujan Math. Soc., 18(1):1–32, 2003.

[10] C. Diem. An index calculus algorithm for plane curves of small degree. In F. Hess, S. Pauli, and
M. Pohst, editors, Algorithmic Number Theory (ANTS VII), volume 4076 of LNCS, pages 543–557,
Berlin–Heidelberg–New York, 2006. Springer.

[11] C. Diem and S. Kochinke. Computing discrete logarithms with special linear systems. Available at

http://www.math.uni-leipzig.de/~diem/preprints/dlp-linear-systems.pdf, 2013.

[12] C. Diem and J. Scholten.

An attack on a trace-zero cryptosystem.

Available at

http://www.math.uni-leipzig.de/diem/preprints.

[13] P. N. J. Eagle, S. D. Galbraith, and J. Ong. Point compression for Koblitz curves. Adv. Math.

Commun., 5(1):1–10, 2011.

[14] A. Faz-Hern´andez, P. Longa, and A. H. S´anchez. Eﬃcient and secure algorithms for GLV-
Available at

based scalar multiplication and their implementation on GLV–GLS curves.
http://eprint.iacr.org/2013/158, 2013.

[15] G. Frey. Applications of arithmetical geometry to cryptographic constructions. In Proceedings of
the 5th International Conference on Finite Fields and Applications, pages 128–161. Springer, 1999.

[16] S. D. Galbraith and X. Lin. Computing pairings using x-coordinates only. Des. Codes Crytogr.,

50(3):305–324, 2009.

[17] S. D. Galbraith, X. Lin, and M. Scott. Endomorphisms for faster elliptic curve cryptography on a

large class of curves. J. Cryptology, 24(3):446–469, 2011.

[18] S. D. Galbraith and B. A. Smith. Discrete logarithms in generalized Jacobians. Available at

http://uk.arxiv.org/abs/math.NT/0610073, 2006.

[19] R. P. Gallant, R. J. Lambert, and S. A. Vanstone. Faster point multiplication on elliptic curves with
eﬃcient endomorphisms. In J. Kilian, editor, Advances in Cryptology: Proceedings of CRYPTO ’01,
volume 2139 of LNCS, pages 190–200. Springer, 2001.

[20] P. Gaudry. Index calculus for abelian varieties of small dimension and the elliptic curve discrete

logarithm problem. J. Symbolic Comput., 44(12):1690–1702, 2009.

[21] P. Gaudry, F. Hess, and N.P. Smart. Constructive and destructive facets of Weil descent. J.

Cryptology, 15(1):19–46, 2002.

[22] J. Gerhard and J. von zur Gathen. Modern Computer Algebra. Cambridge University Press, Cam-

bridge, 1999.

[23] F. G¨olo˘glu, R. Granger, G. McGuire, and J. Zumbr¨agel. On the function ﬁeld sieve and the
impact of higher splitting probabilities: application to discrete logarithms in F21971 . Available at
http://eprint.iacr.org/2013/074, 2013.

21

[24] F. G¨olo˘glu, R. Granger, G. McGuire, and J. Zumbr¨agel. Solving a 6120-bit DLP on a desktop

computer. Available at http://eprint.iacr.org/2013/306, 2013.

[25] G. Gong and L. Harn. Public-key cryptosystems based on cubic ﬁnite ﬁeld extensions. IEEE Trans.

Inform. Theory, 45(7):2601–2605, 1999.

[26] E. Gorla. Torus-based cryptography.

In S. Jajodia and H. v. Tilborg, editors, Encyclopedia of

Cryptography, pages 1306–1308. Springer, Berlin–Heidelberg–New York, 2nd edition, 2011.

[27] R. Granger and F. Vercauteren. On the discrete logarithm problem on algebraic tori. In V. Shoup,
editor, Advances in Cryptology: Proceedings of CRYPTO ’05, volume 3621 of LNCS, pages 66–85.
Springer, 2005.

[28] A. Joux. A new index calculus algorithm with complexity L(1/4 + o(1)) in very small characteristic.

Available at http://eprint.iacr.org/2013/095, 2013.

[29] A. Joux and V. Vitse. Elliptic curve discrete logarithm problem over small degree extension ﬁelds.
Application to the static Diﬃe-Hellman problem on E(Fq5 ). To appear in Journal of Cryptology,
Springer, DOI: 10.1007/s00145-011-9116-z, 2012.

[30] N. Koblitz. CM-curves with good cryptographic properties. In J. Feigenbaum, editor, Advances in
Cryptology: Proceedings of CRYPTO ’91, volume 576 of LNCS, pages 179–287. Springer, 1991.

[31] T. Lange. Eﬃcient Arithmetic on Hyperelliptic Curves. PhD thesis, Univerit¨at GHS Essen, Available

at http://www.hyperelliptic.org/tanja/preprints.html, 2001.

[32] T. Lange. Trace zero subvarieties of genus 2 curves for cryptosystem. Ramanujan Math. Soc.,

19(1):15–33, 2004.

[33] A. K. Lenstra and E. R. Verheul. The XTR public key system. In M. Bellare, editor, Advances in
Cryptology: Proceedings of CRYPTO ’00, volume 1880 of LNCS, pages 1–19. Springer, 2000.

[34] P. Longa and F. Sica. Four-dimensional Gallant–Lambert–Vanstone scalar multiplication.

In
X. Wang and K. Sako, editors, Advances in Cryptology: Proceedings of ASIACRYPT ’12, volume
7658 of LNCS, pages 718–739. Springer, 2012.

[35] N. Naumann. Weil-Restriktion abelscher Variet¨aten. Master’s thesis, Univerit¨at GHS Essen, Avail-

able at http://web.iem.uni-due.de/ag/numbertheory/dissertationen, 1999.

[36] T. Oliveira, J. L´opez, D. F. Aranha, and F. Rodr´ıguez-Henr´ıquez. Lambda coordinates for binary
elliptic curves. Available at http://eprint.iacr.org/2013/131, accepted at CHES ’13, 2013.

[37] K. Rubin and A. Silverberg. Supersingular abelian varieties in cryptology. In M. Yung, editor, Ad-
vances in Cryptology: Proceedings of CRYPTO ’02, volume 2442 of LNCS, pages 336–353. Springer,
2002.

[38] K. Rubin and A. Silverberg. Torus-based cryptography. In D. Boneh, editor, Advances in Cryptology:

Proceedings of CRYPTO ’03, volume 2729 of LNCS, pages 349–365. Springer, 2003.

[39] K. Rubin and A. Silverberg. Using primitive subgroups to do more with fewer bits. In D. Buell,
editor, Algorithmic Number Theory (ANTS VI), volume 3076 of LNCS, pages 18–41, Berlin–
Heidelberg–New York, 2004. Springer.

[40] K. Rubin and A. Silverberg. Using abelian varieties to improve pairing-based cryptography. J.

Cryptology, 22(3):330–364, 2009.

[41] I. Semaev. Summation polynomials of the discrete logarithm problem on elliptic curves. Available

at http://eprint.iacr.org/2004/031, 2004.

[42] A. Silverberg. Compression for trace zero subgroups of elliptic curves. Trends Math., 8:93–100,

2005.

[43] P. Smith and C. Skinner. A public-key cryptosystem and a digital signature system based on
the Lucas function analogue to discrete logarithms. In J. Pieprzyk and R. Safavi-Naini, editors,
Advances in Cryptology: Proceedings of ASIACRYPT ’94, volume 917 of LNCS, pages 357–364.
Springer, 1995.

22

[44] A. Weimerskirch.

The

application

of

the Mordell-Weil

group

to

graphic
Institute, Available
http://www.emsec.rub.de/media/crypto/attachments/files/2010/04/ms_weika.pdf, 2001.

thesis, Worcester Polytechnic

Master’s

systems.

crypto-
at

23

