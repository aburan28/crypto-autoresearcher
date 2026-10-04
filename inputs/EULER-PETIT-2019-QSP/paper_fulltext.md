<!--
Extracted from inputs/EULER-PETIT-2019-QSP/arxiv-1909.11326v2.pdf (sha256 in the .sha256
sidecar) on 2026-09-16 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
detect_vertical=False). Derivative text extraction vendored under
the manuscript's CC BY-NC-ND 4.0 licence (https://creativecommons.org/licenses/by-nc-nd/4.0/), stated on its first page; a mechanical text extraction is reproduced here for non-commercial research verification only, unmodified,
with attribution to Marie Euler and Christophe Petit.

NOT hand-cleaned. Ligatures, superscripts flattened onto the baseline, displayed
formulas broken across lines, and (cid:NN) glyph placeholders are left exactly as
the extractor produced them. Section, lemma, proposition, theorem and remark
numbers are the paper's own and are the citable anchors.
-->

1
2
0
2

n
u
J

5
2

]

R
C

.

s
c
[

2
v
6
2
3
1
1

.

9
0
9
1

:

v

i

X

r
a

New Results on Quasi-Subﬁeld Polynomials

Marie Eulera,1,∗, Christophe Petitb,c,1

aDGA MI, France
bUniversit´e libre de Bruxelles, D´epartement d’informatique, Belgium
cUniversity of Birmingham, School of Computer Science, United Kingdom

Abstract

1 Quasi-subﬁeld polynomials were introduced by Huang et al. together with a
new algorithm to solve the Elliptic Curve Discrete Logarithm Problem (ECDLP)
over ﬁnite ﬁelds of small characteristic.
In this paper we provide both new
quasi-subﬁeld polynomial families and a new theorem limiting their existence.
Our results do not allow to derive any speedup for the new ECDLP algorithm
compared to previous approaches.

linearized polynomials, cryptography, elliptic curve discrete

Keywords:
logarithm problem,
2000 MSC: 11T06,11T71,94A60

1. Introduction

Let p be a prime and let n, n′ be two positive integers. For any prime power
q, let Fq be the ﬁnite ﬁeld with q elements. When n′ divides n, the ﬁnite ﬁeld
F

pn′ is a subﬁeld of Fpn . The polynomial

X pn′

− X

splits over Fpn and its roots are exactly all the elements of F
pn′ . Quasi-subﬁeld
polynomials, introduced by Huang et al. [1], naturally generalize this polyno-
mial.

∗Corresponding author

Email addresses: marie.euler@hotmail.com (Marie Euler),

christophe.f.petit@gmail.com (Christophe Petit)

1Part of this work was done in fulﬁllment of a master thesis requirement of the ﬁrst author

at the University of Oxford

2Supported in part by an EPSRC grant EP/S01361X/1.
1Declarations of interest: none
© 2021. This manuscript version is made available under the CC-BY-NC-ND 4.0 license

http://creativecommons.org/licenses/by-nc-nd/4.0/

Preprint submitted to Finite Fields and Their Applications

May 2021

 
 
 
 
 
 
Deﬁnition 1 (informal). A quasi-subﬁeld polynomial (QSP) is a polynomial
of the form

L(X) := X pn′

− λ(X)

such that “most” of its roots are distinct and deﬁned over Fpn , and moreover
d := deg λ is “small”.

When n′ does not divide n, the degree of λ cannot be too small, as shown

in the following lemma.

Lemma 1. [1, Lemma 4.1] Let L(X) = X pn′
spliting over Fpn , such that ℓ := logp deg λ > 0. Then we have

− λ(X) ∈ Fpn [X] completely

ℓ + (n mod n′) ≥ n′.

n
n′

j

k

A similar result in the non split case is also provided in [1, Lemma C.2].

In light of this lemma, it is useful to associate to any QSP a “quality”
parameter β := ℓn/n′2, where ℓ := logp deg λ as above. This leads to a more
formal deﬁnition of QSP :

Deﬁnition 2. A quasi-subﬁeld polynomial (QSP) is a polynomial of the form

L(X) := X pn′

− λ(X) ∈ Fpn [X]

which splits completely (or at least has approximately pn′

roots), for which more-

over β(L) :=

nℓ

n′2 ≤ 1 with ℓ := logp deg λ.

In their paper, Huang et al. provide a QSP family over Fpn [x] with n = pa+1

and β = 1 −

(1 − 1/pr + 1/(prpa)) with pa = 1 + pr + p2r + · · · + par. Most

importantly, they show how quasi-subﬁeld polynomials can be used to solve
the Elliptic Curve Discrete Logarithm Problem (ECDLP), a problem of major
importance for cryptography.

1

pa

Our results. We expand the study of quasi-subﬁeld polynomials initiated in [1],
focusing on polynomials whose roots form a subgroup of either the additive or
the multiplicative group of ﬁnite ﬁelds. In the additive case this amounts to
searching for a linearized polynomial

L(X) = X pn′

− (aℓX pℓ

+ aℓ−1X pℓ−1

+ · · · + a0X)

splitting over Fpn , with “small” ℓ. In the multiplicative case this amounts to
searching for a polynomial of the form

L(X) = X pn′

− X d

where pn′

− d divides pn − 1, and d is small.

Our main result is the following theorem on linearized QSPs.

2

Theorem 1. Let L(X) := X pn′
+· · ·+a0X) be a linearized
polynomial over Fpn , with ℓ ≥ 1. If L splits completely over Fpn then β :=
ℓn/n′2 ≥ 3/4.

+aℓ−1X pℓ−1

−(aℓX pℓ

The equality is obtained for example with X p2
p3[X]. The theorem
improves on Lemma 1 for linearized polynomials with parameters n, n′ satisfying
(n mod n′) ≥ n′/4.
In the special case of trinomials, a similar result was
independently obtained with similar techniques by McGuire and Mueller [2].

+X p +X in F

We also introduce methods to generate new families of linearized QSP from

known ones, and we exhibit new additive and multiplicative QSP families.

Finally, we apply our results to Huang et al.’s ECDLP algorithm.

Impact on ECDLP security. The complexity of Huang et al.’s ECDLP algorithm
crucially relies on the quality parameter β of the quasi-subﬁeld polynomial used.
Based on their complexity estimations, a value of β at most 0.1 would be needed
to obtain a complexity improvement over generic, state-of-the-art ECDLP algo-
rithms. In contrast, Theorem 1 rules out any β smaller than 3/4 in the case of
linearized polynomials, and the best quasi-subﬁeld polynomial we found so far
has β ≃ 0.7. Further work will be needed to improve Huang et al.’s approach
with new ideas and better QSP families, or to provide a deﬁnite proof that it
will not improve on generic algorithms.

Outline. The remaining of this paper is organized as follows. Section 2 recalls
our new lower bound for the β value of linearized QSPs and it provides its proof.
Section 3 includes our new QSP families. Section 4 discusses the impact of our
results on ECDLP and Section 5 concludes the paper.

2. A new lower bound on β for linearized quasi-subﬁeld polynomials

In this section we ﬁrst recall known properties of linearized polynomials,
including a characterization of linearized polynomials that split completely over
their ﬁeld of deﬁnition. We then proceed to prove Theorem 1, and we compare
the bound it provides with the bounds given in [1] and [2].

2.1. Linearized polynomials

Let p be a prime and n be positive integer. Let Fpn be the ﬁnite ﬁeld with pn
elements. We write Gal(Fpn /Fp) for the Galois group of Fpn with respect to Fp.
For any automorphism σ ∈ Gal(Fpn /Fp), there exists s ∈ Z with gcd(s, n) = 1
such that σ(X) = X ps

. In the following we write X σ for σ(X).

Deﬁnition 3 (Linearized polynomials). Let σ ∈ Gal(Fpn /Fp) and let f = X d +
ad−1X d−1 + . . . + a1X + a0 ∈ Fpn[X]. The linearized polynomial related to f
and σ is the polynomial

Lf,σ = X σd

+ ad−1xσd−1

+ . . . + a1X σ + a0X ∈ Fpn [X].

Moreover d is called the σ-degree of Lf,σ.

3

Let L := Lf,σ ∈ Fpn [X] be a linearized polynomial with coeﬃcients in Fpn

as above. Let CL be the companion matrix of f , namely

CL :=

We also deﬁne the matrix

0
1
0



...

0








0 · · · 0 −a0
0 · · · 0 −a1
1 · · · 0 −a2

...

. . .

...

0 · · · 1 −ad−1

.










AL := CL · Cσ

L · Cσ2

L · · · Cσn−1

L

,

where Cσ
that AL and CL are square matrices of dimension d.

L is the matrix obtained by applying σ coeﬃcient-wise on CL. Note

The following result (independently due to McGuire and Sheekey [3] and

Csajb´ok et al. [4]) characterizes linearized polynomials that split completely.

Proposition 1. Let L = X σd
+ . . . + a1X σ + a0X be a linearized
polynomial with coeﬃcients in Fpn . Then L has pn1 roots deﬁned over Fpn ,
where n1 is the dimension of the eigenspace of AL with eigenvalue 1. In partic-
ular, L splits completely over Fpn [X] if and only if AL is the identity matrix.

+ ad−1xσd−1

A corollary of this proposition is that the maximum number of roots of L is
pd, and Lf,σ splits completely in Fpn only if σ(X) = X p. From now on, we will
therefore only consider the case σ(X) = X p and thus write Lf instead of Lf,σ.
Another important property of completely splitting linearized polynomials

is the following one.

Proposition 2. Let f = a0 + a1X + · · · + X d ∈ Fp[X]. Then the following
properties are equivalent.

1. Lf (X) splits completely over Fpn [X]

2. Lf (X) divides X pn

− X

3. f divides X n − 1

This proposition directly follows from the fact that Lf divides Lg for the
composition of polynomials if and only if f |g for the multiplication of polyno-
mials [5, Chapter 11].

2.2. Proof of Theorem 1

We will now prove Theorem 1, namely that for any linearized polynomial
+· · ·+a0X) with ℓ ≥ 1, aℓ 6= 0 and ∀i, ai ∈ Fpn ,

L = X pn′
if L splits completely over Fpn then β := ℓn/n′2 ≥ 3/4.

+aℓ−1X pℓ−1

−(aℓX pℓ

This result is in fact a consequence of the following lemma which highlights
that the ﬁeld has to be big enough to have completely splitting sparse linearized
polynomials in it.

4

Lemma 2 (Lower bound on n). Let Lf = X pn′
with ℓ ≥ 1, aℓ 6= 0 and ∀i, ai ∈ Fpn . If Lf splits completely over Fpn then

+aℓ−1X pℓ−1

−(aℓX pℓ

+· · ·+a0X)

n ≥ n′ + (n′ − ℓ)

n′ − 1

ℓ

j

k

Let us ﬁrst observe that this result is indeed enough to prove the theorem.

Indeed one can notice that since n′ and ℓ are integers, we have

Therefore, by Lemma 2 we have n ≥ n′ + (n′ − ℓ)

− (n′ − ℓ) ≥

− n′ + ℓ.

ℓn

ℓ

ℓ2

Thus, β =

n′2 ≥ 1 −

n′ +

n′2 = 1 −

ℓ
n′

ℓ
n′

1 −

≥ 1 − 1/4 = 3/4.

(cid:18)
We will now show that Lemma 2 boils down to the proof of a result about
the power of a matrix. By Proposition 1, L := Lf splits completely over Fpn if
and only if AL := CL · Cσ
= I where CL is the companion matrix of
f .

L · · · Cσn−1

(cid:19)

L

≥

−1.

n′

ℓ

n′ − 1

j

ℓ

n′2
k

ℓ

n′

ℓ

Therefore we have to prove that

If n < n′ + (n′ − ℓ)

n′ − 1

ℓ

j

k

, then AL 6= I

The remainder of the proof will consider matrices deﬁned over the polynomial
ring Fpn [a0, . . . , aℓ], where ai are the coeﬃcients of L as above. However as our
result only depends on the value of n′ and ℓ but not on the speciﬁc coeﬃcients
ai, we represent any element x ∈ Fpn [ai] by a symbol ˜x ∈ {0 , 1 , a•, ⊛}, noting
it x   ˜x, according to the following rules :

• if x   0 then x = 0;

• if x   1 then x = 1;

• if x   a• then x is a power of (−aℓ) and thus x 6= 0;

• (x   ⊛ implies no condition on x).

For instance −a0   ⊛, −aℓ   a•, a0 + aℓ   ⊛, and also −aℓ   ⊛. One can
notice that if x1   ˜x1 and x2   ˜x2, then x1 + x2   z1 and x1 · x2   z2 with
z1 and z2 given by the following tables.

1
1

a• ⊛
+ 0
a• ⊛
0
0
1 ⊛ ⊛ ⊛
1
a•
a• ⊛ ⊛ ⊛
⊛ ⊛ ⊛ ⊛ ⊛

1
0
0
0
0
1
0 a•

a• ⊛
·
0
0
0
a• ⊛
1
a•
a• ⊛
⊛ 0 ⊛ ⊛ ⊛

For instance, if x1   a•, x2   a•, x3   ⊛, then x1 + x2   ⊛, x1 · x2   a•

and x1 · x3   ⊛.

We extend this notation to matrices over Fpn [ai]: Let M = (mi,j) be a square
matrix of dimension n′ with coeﬃcients in Fpn . If for all i and j, mi,j   ˜mi,j,

5

we denote M   ˜M := ( ˜mi,j). We observe that if M   ˜M and N   ˜N then
M + N   ˜M + ˜N and M N   ˜M ˜N where the operations are done according
to the above tables.

Let M and ˜M such that M   ˜M . If there is a zero on the main diagonal
of ˜M or there is a non zero coeﬃcient (1 or a•) outside of this diagonal, then
we see that ˜M cannot represent the identity matrix (denoted I 6  ˜M ) and then
M 6= I.

Therefore we will give ˜AL such that AL   ˜AL and prove that if n < n′ +

(n′ − ℓ)

n′ − 1

ℓ

then I 6  ˜AL.

First of all, we can recall that AL := CL · Cσ

j

k

L · · · · · Cσn−1

L

with

CL =

0
1
0

0

...

...
...

0



















0
0
1

...

0

...
...

0

· · ·
· · ·
· · ·

. . .

· · ·

0
0
0

1

...
...

· · ·
· · ·
· · ·

. . .

· · ·

. . .

. . .

· · · −a0
· · · −a1
· · · −a2

...

· · · −aℓ



















0

...

0

· · ·

· · ·

1

Moreover, since σ acts on matrices coeﬃcient-wise, we can observe that for

all k ≥ 0, Cσk

L

  M with

0 0
1 0
0 1



· · · 0
· · · 0
· · · 0

...

...

. . .

M :=

· · ·
· · ·
· · ·

. . .

· · ·

. . .

· · · ⊛
· · · ⊛
· · · ⊛



...

· · · a•
















0

...

0

· · · 1

. . .

...
...

· · ·

· · ·

1
















0 0

...
...

...
...

0 0

Therefore AL   M n. Our goal is then to study the powers of M , which is

a companion matrix deﬁned on {0, 1, a•, ⊛} and to prove the following result.

Lemma 3 (Small powers are not the identity).

If n < n′ + (n′ − ℓ)

,

then I 6  M n.

n′ − 1

ℓ

j

k

More precisely, we will prove the following lemma which exhibits a non zero
coeﬃcients outside of the main diagonal. We will note M n
i,j the coeﬃcient in
the i-th row, j-th column of the matrix M n.

Lemma 4 (A non zero coeﬃcient). The following two claims are true:

6

• If n < n′, then M n

n+1,1 = 1.

• If n′ ≤ n < n′ + (n′ − ℓ)

, then we have M n

in,1 = a• 6= 0

with in = n − (n′ − ℓ)

k

+ 1 ∈ [2, n′]

n′ − 1

ℓ
n − ℓ
j
n′ − ℓ

j

k

Proof. Adapting a result of Chen and Louck [6] (see Appendix A for details)
on powers of companion matrices we have M n

i,j = 1 if n = i − j and otherwise

M n

i,j =

wk · 0k1+···+kn′−ℓ−1 · (a•)kn′ −ℓ · ⊛kn′−ℓ+1+···+kn′

k=(k1,··· ,kn′ )
X
n′

ιkι=n−i+j

Pι=1

where k = (kι)1≤ι≤n′ are non-negative integers and

wk =

kn′−i+1 + · · · + kn′
k1 + · · · + kn′

k1 + · · · + kn′
k1, · · · , kn′

(cid:18)

.
(cid:19)

The ﬁrst part of Lemma 4 follows from the case n = i − j.

When n 6= i − j, the contribution of any k with k1 + · · · + kn′−ℓ−1 > 0 to

the sum is null. Therefore we get

M n

i,j =

wk · a• · ⊛kn′−ℓ+1+···+kn′ ,

(1)

k=(kn′−ℓ,··· ,kn′ )
X

n′

ιkι=n−i+j

Pι=n′−ℓ

where wk is now

wk =

kmax(n′−i+1,n′−ℓ) + · · · + kn′
kn′−ℓ + · · · + kn′

kn′−ℓ + · · · + kn′
kn′−ℓ, · · · , kn′

(cid:18)

.
(cid:19)

Note that here we do not want to remove the exponents over the unknown
symbol. Indeed when kn′−ℓ+1 + · · · + kn′ = 0, we have ⊛kn′−ℓ+1+···+kn′ = 1; so
we get a term wk · a• which in the case wk = 1 is exactly what we need to prove
that this coeﬃcient is a•.

Let n′ ≤ n ≤ n′ + (n′ − ℓ)

We have

j

− 1, and let in := n − (n′ − ℓ)

j

ℓ

k

n − ℓ
n′ − ℓ

+ 1.

k

n′ − 1

n − (n′ − ℓ)

n − ℓ
n′ − ℓ

+ 1 ≤ in ≤ n − (n′ − ℓ)

n − ℓ
n′ − ℓ
n − (n − ℓ) + 1 ≤ in ≤ n − (n − n′ + 1) + 1

(cid:18)

−

n′ − ℓ − 1
n′ − ℓ

+ 1

(cid:19)

2 ≤ ℓ + 1 ≤ in ≤ n′

In particular, M n

in,1 is well-deﬁned and it is not in the top left corner.

7

Moreover, n′−in+1 ≤ n′−(ℓ+1)+1 = n′−ℓ so max(n′−in+1, n′−ℓ) = n′−ℓ.

Also, n − in + 1 = (n′ − ℓ)

j
kn′−ℓ + · · · + kn′
kn′−ℓ + · · · + kn′

wk =

n − ℓ
n′ − ℓ

. We then have :

k

kn′−ℓ + · · · + kn′
kn′−ℓ, · · · , kn′

(cid:18)

(cid:19)

=

=

kn′−ℓ + · · · + kn′
kn′−ℓ, · · · , kn′

(cid:19)
(cid:18)
(kn′−ℓ + · · · + kn′ )!
kn′−ℓ! · · · kn′ !

and

M n

in,1 =

wk · a• · ⊛kn′−ℓ+1+···+kn′

Xkn′−ℓ,··· ,kn′

ιkι=(n′−ℓ)

n′

Pι=n′−ℓ

n − ℓ
n′ − ℓ

j

k

In order to show that M n

in,1 = a•, we now show that this sum in fact only

involves one term, and that this term is exactly a•.

Clearly k = (kn′−ℓ, · · · , kn′ ) =

n − ℓ
n′ − ℓ

k

(cid:18)j

, 0, · · · , 0

is a solution to

(cid:19)

n − ℓ
n′ − ℓ

k

(2)

n′

Xι=n′−ℓ

ιkι = (n′ − ℓ)

j

and for this k we have wk · a• · ⊛kn′−ℓ+1+···+kn′ = 1 · a• · 1 = a•. It remains to
show that it is the only valid k to prove that M n

in,1 = a•.

By contradiction, let us assume that there exists a solution (kn′−ℓ, · · · , kn′ )

to Equation (2) such that

n′

ℓ−1

kι =

kn′−ι > 0

Xι=n′−ℓ+1

ι=0
X

(3)

We recall that by deﬁnition, all the kι are non-negative. From Equation (2),

we have :

n − ℓ
n′ − ℓ

(n′ − ℓ)

j

n′

ℓ

=

ιkι =

(n′ − ι)kn′−ι

k

Xι=n′−ℓ

ι=0
X

ℓ

ℓ−1

= (n′ − ℓ)

kn′−ι +

(ℓ − ι)kn′−ι

(4)

ι=0
X
ℓ

ι=0
X

ι=0(ℓ − ι)kn′−ι

ℓ−1

+

(ℓ − ι)kn′−ι

≥ (n′ − ℓ)

n′ − ℓ

ℓ

≥

(cid:18)

P

ℓ

ℓ−1

ι=0
X

+ 1

(ℓ − ι)kn′−ι =

(cid:19)

ι=0
X

8

n′

ℓ

ℓ−1

ι=0
X

(ℓ − ι)kn′−ι

(5)

From Equation (4), we have (n′ − ℓ)|

pothesis (3), that
(n′ − ℓ).

ℓ−1

ι=0(ℓ − ι)kn′−ι ≥

ℓ−1

ι=0(ℓ − ι)kn′−ι. We also have, by hy-
ι=0(ℓ − ι)kn′−ι ≥

ℓ−1
ι=0 kn′−ι > 0 hence
P

ℓ−1

Together with Equation (5) this implies (n′ − ℓ)

P

P

n − ℓ
n′ − ℓ

n′

ℓ

P
≥

k

(n′ − ℓ) so

(6)

j

≥

n′

ℓ

.

n − ℓ
n′ − ℓ

j

k

On the other hand, thanks to the condition on n being not too big, we have

n − ℓ
n′ − ℓ

≤

n′ + (n′ − ℓ)

n′ − 1

ℓ
n′ − ℓ

j

− 1 − ℓ

k

This implies

j
deduce that k = (

thus

j

n − ℓ
n′ − ℓ

n − ℓ
k
n′ − ℓ

≤

n′ − 1

ℓ

<

n′

ℓ

j

k

k

M n

in,1 = a• 6= 0

n′ − 1

ℓ

≤

j

+

1 −

(cid:18)

k

1
n′ − ℓ

.

(cid:19)

, contradicting Equation (6). We

, 0, · · · , 0) is the only solution to Equation (2) and

2.3. Comparison with other lower bounds

Theorem 1 improves on the bound given in Lemma 4.1 of [1] whenever the

QSP is linearized and (n mod n′) ≥ n′/4.

Our bound is similar to the one given by Daniela Mueller and Gary McGuire
in [2], which was established during the completion of this article.
Indeed,
Theorem 1.1 in [2] shows (using also [3] and [4]) that a linearized trinomial
L = X qd
− bX q − aX ∈ Fpn, with b 6= 0 and q = pk a power of p such that
n = k˜n, splits completely only if

˜n ≥ (d − 1)d + 1 = d2 − d + 1.

Let us compare it with the bound given by Lemma 2. We write n = k˜n so

that q = pk. Thus L = X pkd

− bX pk

− aX. Lemma 2 gives:

k˜n = n ≥ kd + (kd − k)

≥ k(d + (d − 1)(d − 1))

kd − 1

k

j
Thus, as Mueller and McGuire, we get ˜n ≥ d + (d − 1)2 = d2 − d + 1.

k

While their bound is less general than ours as it only applies to trinomi-
als, they gave a more complete description of completely splitting linearized
trinomials. Indeed, they also take into account the case ℓ = 0 which we did
not consider in this article, and they exhaustively describe all possible such
polynomials when ˜n ≤ (d − 1)d + 1:

• either ˜n = id with i ≤ d − 1, b = 0 and a1+qd+···+q(i−1)d

= 1,

9

Quasi-subﬁeld polynomial

p

n

β

Lfa with f0 =
1 + X q−1 + · · · + X qd −1,
fa = a+X +X q +· · ·+X qd
for any a 6= 0 ∈ Fq and q a
power of p

L(Xn−1)/f with Lf a
completely splitting QSP
of degree n’

− X a with n′

X pn′
and a = pn′

mod ( pn−1

= n − i
p2i−1 )

X p − X a with k ≥ 2 and

a = p mod (

p − k

k − 1

)

X pn−1
− X a with k ≥ 2
and r = (pn−1)(k−(−1)n)
a = pn−1 mod r

(kn−k)(kn−(−1)n)

any

qd+1 − 1

1 −

qd−1
(1+q+···+qd−1)2

any

any

kn + k − 1

kn −k −(−1)n

any
integer

2ik,
k ≥ 2

any
integer

n > 2
kn ≫ 1

1 − ( n′

n−n′ )2(1 − β(Lf ))

≤ 1 −

1
(2k − 1)2

≤ 1

≤ 1

Table 1: New families of quasi-subﬁeld polynomials

• either ˜n = (d − 1)d + 1, a1+q+···+q(d−1)d

= (−1)d−1, b = −aqe1 where

e1 =

d−1

i=0 qid and d − 1 is a power of p

See also [7] for the complete description of completely splitting linearized

P

trinomials when ˜n ≤ (d − 1)d + d − 1.

3. New families of quasi-subﬁeld polynomials

In this section, we will prove that the additive polynomials of Proposition 5
and the multiplicative polynomials of Proposition 6 are quasi-subﬁeld polyno-
mials. We ﬁrst provide general tools to deduce new linearized QSPs from known
ones and we deﬁne equivalence classes among linearized quasi-subﬁeld polyno-
mials. We then successively focus on additive and multiplicative families, and
we ﬁnish with the case where the extension degree is a Mersenne prime.

Since the case logp deg λ = 0 corresponds to subﬁeld polynomials, which are

well-known, we will only consider the case logp deg λ > 0.

3.1. Equivalent classes of linearized quasi-subﬁeld polynomials

In order to simplify our search of quasi-subﬁeld polynomials, we will ﬁrst dis-
cuss transformations to deduce new linearized quasi-subﬁeld polynomials from

10

known ones. We will introduce two types of transformations. The ﬁrst transfor-
mation will change the value of β and thus potentially improve it. The second
one will keep the same β, thus it will not produce more interesting linearized
quasi-subﬁeld polynomials, but it will allow us to group them by equivalence
classes.

Both transformations will only concern completely splitting QSPs with co-
p,n for the set of completely splitting linearized

eﬃcients in Fp. We will write QL
QSPs in Fpn [X].

The ﬁrst way to obtain a linearized quasi-subﬁeld polynomial from another

one is what we call the inversion process.

Proposition 3 (Inversion). Let f = X n′
Lf ∈ QL
is the inverse of Lf .

p,n and n′ < n. Let g = (X n − 1)/f . Then Lg ∈ QL

+ aℓX ℓ + · · · + a0 ∈ Fp[X] such that
p,n. We say that Lg

Proof. By Proposition 2, we know that f |X n − 1 so g is well-deﬁned.

Let us write g as X n−n′
Indeed, X n − 1 = f · g = (X n′
X n + brX r+n′
coeﬃcient of X r+n′
non zero. Conversely, if r + n′ < ℓ + n − n′ then the coeﬃcient of X ℓ+n−n′
f · g comes exclusively from (aℓX ℓ) · X n−n′
and thus is not zero. We deduce

+brX r+· · ·+b0. We will prove that r+n′ = n−n′+ℓ.
+ brX r + · · · + b0) =
+ · · · + a0b0. So, if r + n′ > ℓ + n − n′ then the
and is therefore
in

in f · g comes exclusively from (brX r) · X n′

+ aℓX ℓ + · · · + a0)(X n−n′

+ aℓX ℓ+n−n′

β(Lg) =

n.r

(n − n′)2 =

n.(n − 2n′ + ℓ)
(n − n′)2

= 1 −

n′2 − ℓ.n
(n − n′)2

= 1 −

n′
n − n′

2

(cid:19)

(cid:18)

(1 − β(Lf )) ≤ 1.

Our second family of transformations keep the value of β unchanged.

Proposition 4 (Transformations preserving β). Let k ≥ 1 and γ ∈ F∗
f = X n′

pn. Let
+ aℓX ℓ + · · ·+ a0 ∈ Fp[X]. Then the following properties are equivalent:

(a) Lf ∈ QL

p,n,

(b) Lf (X k) = X pk.n′

+ aℓX pk.ℓ

+ · · · + a1X pk

+ a0X ∈ QL

p,kn,

(c) (when n|p−1) for any α ∈ Fp with αn = 1, α−n′

Lf (α.X) = α−n′

(αn′

X pn′

+

αℓaℓX pℓ

+ · · · + αa1X p + a0X) ∈ QL

p,n,

(d) γ−pn′
p,n.

QL

Lf (γ.X) = γ−pn′

((γ.X)pn′

+ aℓ(γ.X)pℓ

+ · · · + a1(γ.X)p + a0γX) ∈

11

Proof. One can observe that these four quasi-subﬁeld polynomials have the same
β. Therefore, we only have to show that their splitting conditions are equivalent.
The equivalence between (a) and (b) directly comes from Proposition 2. Indeed,

Lf ∈ QL

p,n ⇔ f |X n − 1 ⇔ f (X k)|X kn − 1 in Fpn [X]

⇔ Lf (X k) ∈ QL

p,kn.

Properties (a) and (c) are also equivalent as

Lf ∈ QL

p,n ⇔ f |X n − 1 ⇔ f (α.X)|(α.X)n − 1

⇔ f (α.X)|X n − 1 since αn = 1
⇔ α−n′

f (α.X)|X n − 1

⇔ α−n′

Lf (α.X) ∈ QL

p,n.

Finally, replacing X by γ·X clearly does not change the fact that the polynomial
is split, therefore (a) ⇔ (d) is trivial.

Let us now reconsider the transformations (a) ⇔ (b) and (a) ⇔ (c). As
these transformations do not change the value of β and they send completely
splitting linearized quasi-subﬁeld polynomials with coeﬃcients in Fp onto other
ones, we can deﬁne equivalence classes by saying that two completely splitting
linearized quasi-subﬁeld polynomials with coeﬃcients in Fp are equivalent to
each other if one can be obtained from the other with one through one of the
previous transformations. Obviously, since the transformations leave the value
of β - which determines the eﬃciency of the ECDLP algorithm - unchanged, we
are only interested in ﬁnding one representative of each class.

3.2. Examples of completely splitting linearized QSPs

In order to ﬁnd examples of linearized QSPs, we performed a systematic
search of representatives of classes of equivalence of completely splitting QSPs.
We will now explain how we did this search, and present our results.

From now on, we will only consider polynomials with coeﬃcients in the base

ﬁeld Fp. Then any L of the shape X pkn′
(in the above sense) to X pn′
p,n. Whenever we have a
non trivial factor d of all the element of the set {i ≥ 1, ai 6= 0} ∪ {n}, we may
use it to reduce the degree of the polynomial by a factor d. Therefore we may
reduce the search of representatives of each class to polynomials of the shape

p,kn is equivalent

+ · · · + a0 ∈ QL

+· · ·+a0 ∈ QL

+aℓX pkℓ

+ aℓX pℓ

X pn′

+ aℓX pℓ

+ · · · + a0 ∈ Fpn [X] with {i ≥ 1, ai 6= 0} ∪ {n} setwise coprime.

One can also notice that transformation (a) ⇔ (c) cannot often be used.

Indeed if n is prime then αn = 1 implies n|p − 1.

Since we restrict the search to polynomials in Fp[X], all the coeﬃcients of
L. Hence, Proposition 1 says that L splits

CL are in Fp and thus AL is merely Cn
completely over Fpn if and only if Cn

Let L = X pn′

+ · · · + a0 be a ﬁxed linearized polynomial in Fp[X].
We can assume a0 6= 0 since if a0 = 0 then 0 is a root of L with multiplicity

+ aℓX pℓ

L = I.

12

L = I then Lf ∈ QL

at least p so L does not split completely. We can search for the smallest n
such that L splits completely over Fpn . This amounts to searching for n such
that Cn
L = I, in other words ﬁnding the order of CL. Note that CL is in
GLn′(Fp) since det CL = (−1)n′
a0 6= 0, hence n exists. Moreover as we also
L with k < n′2/ℓ. If we
want β(L) = n.ℓ/(n′)2 ≤ 1, we only have to compute Ck
ﬁnd such a k with Ck

p,k.
This naturally leads to an algorithm to produce a set of representatives of
the previously deﬁned equivalence classes. The results output by our algorithm
when asking for representatives of the equivalence classes for p ∈ {2, 3, 5, 7},
n′ ≤ 16 and coeﬃcients values restricted to {0, 1, −1}, are presented in appendix
(Table B.2). Observing patterns in them allowed us to conjecture new types of
quasi-subﬁeld polynomials. We present one representative per equivalence class,
as other quasi-subﬁeld polynomials can be obtained by using the rules listed in
Proposition 4.

Proposition 5 (Families of linearized QSPs). The following types of linearized
polynomials are quasi-subﬁeld polynomials:

Type 1 Lh with h = X pa + · · · + X p0 + 1, where q = pr, r ≥ 0, n = pa+1, pi =
). It is the family introduced

(1 − pa−1

1 + q + · · · + qi and a ≥ 2, β = 1 − 1
in [1].

pa

q′.pa

Type 1bis X pn−1

+ · · · + X p2

+ X p + X, n′ = n − 1, β = 1 − 1

(n−1)2 .

Type 2 Lfa with fa =

(

X qd−1 + · · · + X q−1 + 1
X qd

+ · · · + X q + X + a otherwise

if a = 0

, n = qd+1 −1,

q = pr, r ≥ 1, a ∈ Fq, β = 1 −

qd−1
(1+q+···+qd−1)2

Type 3 Inverses of Type 1 and inverses of Type 2.

Proof. Type 1 is proven in [1, Lemma 4.3]. Moreover it is obvious that LX−1
is a quasi-subﬁeld polynomial over Fpn for any p prime and n (tolerating here
ℓ = 0). By Proposition 3, its inverse L(X n−1)/(X−1) = LX n−1+···+X 2+X+1 is a
quasi-subﬁeld polynomial in Fpn . This proves the Type 1bis. One can notice
that it is in fact a particular case of Type 1 (when r = 0).

For Type 2 polynomials, we need to show that fa divides X n − 1 and thus
we look at the factorisation of X qd+1−1 − 1. It appears easier to compute this
by looking at X(X qd+1−1 − 1) = X q(d+1) − X since the Frobenius is easy to
compute in Fpn. One can observe with g = X qd
+ · · · + X q + X, we have that
X qd+1
− X = gq − g, Thus, as in Berlekamp’s polynomial trace factorization
algorithm, we get that X qd+1
− X, g + a). But we
also have X qd+1

− X = (g + a)q − (g + a) so ga|X qd+1

a∈Fq gcd(X qd+1

− X and X qd+1

− X =

− X =

Q

a∈Fq (g + a) = Xf0

a∈Fq∗ fa

That is why,

Q
completely over Fpn . Thus it only remains to verify that β ≤ 1.

Q

a∈Fq fa = X n − 1. This gives that Type 2 polynomials split

Q

13

If a = 0, then n′ = qd − 1 and ℓ = qd−1 − 1 hence

β =

(qd−1 − 1)(qd+1 − 1)
(qd − 1)2

= 1 −

qd+1 + qd−1 − 2qd
(qd − 1)2

= 1 −

qd−1(q − 1)2
(qd − 1)2

= 1 −

qd−1

(1 + q + · · · + qd−1)2 < 1,

while if a 6= 0, then n = qd+1 − 1, n′ = qd, ℓ = qd−1 hence

β =

qd−1(qd+1 − 1)
q2d

= 1 −

1

qd+1 < 1.

Proposition 3 addresses Type 3 polynomials. We know that for Type 1 we
have Xhq = h + X n − 1 thus X n − 1 = h(Xhq−1 − 1) and the inverse of Lh is
a∈Fp fa = X n − 1, thus the inverse of Lfa is
LXhq−1−1. For Type 2, we have
L

b6=a fb .

Q

Q

Recall that this list does not cover all the equivalence classes. It was only
conjectured from what was found with small n and small p and coeﬃcients
values in {0, 1, −1}. For example, when we launch the algorithm for very small
n with coeﬃcients allowed to be anything in Fp, we get for p = 5 and n = 4,
that L(X 2+X+3) is a linearized QSP. Indeed (X 2 + X + 3)(X 2 − X + 3) =
(X 2 + 3)2 − X 2 = X 4 + X 2 − 1 − X 2 = X 4 − 1, so X 2 + X + 3 splits in
F
54 and β = 4 × 1/4 = 1. Moreover, computing its equivalence class using
Proposition 4, we observe that no element of its equivalence class has all its
coeﬃcients in {0, 1, −1}.

3.3. Examples of multiplicative quasi-subﬁeld polynomials

We now study another family of quasi-subﬁeld polynomials considered in [1],

namely polynomials whose roots form a multiplicative group of Fpn .

More precisely, we consider quasi-subﬁeld polynomials of the type

L = X pn′

− X a

together with an integer r such that a = pn′
mod r, r|pn − 1 and n′ > logp(r).
Indeed, L factors as X a(X pn′
−a − 1), so the number of roots of L in Fpn is at
most 1 + pn′
− a. Moreover, there are gcd(k, pn − 1) roots of X k − 1 in Fpn .
In order to have the maximal number of distinct roots, we must choose tuples
(p, n, n′, r) such that for a = pn′
− a, i.e.
pn′

mod r, and gcd(pn′

− a, pn − 1) = pn′

− a|pn − 1.

Proposition 6 (Multiplicative quasi-subﬁeld polynomials). Let p, n, n′, r be
deﬁned in any of the following three ways:

1. Let p prime and k ≥ 2 and i ≥ 1 integers. Let n = 2ik, n′ = i(2k − 1) =

n − i and r = pn−1

p2i−1 ;

14

2. Let p = kn + k − 1 prime and k ≥ 2 an integer. Let n′ = 1 and r =

(p − k)/(k − 1);

3. Let p = kn − k − (−1)n be prime, n > 2 and k > 1 integers such that

kn ≫ 1. Let n′ = n − 1 and let r = (pn−1)(k−(−1)n)

(kn−k)(kn−(−1)n) .

Let a = pn′
polynomial.

mod r and let L = X pn′

− X a ∈ Fpn [X]. Then L is a quasi-subﬁeld

We make a few observations before proving this proposition. For the ﬁrst
family when p = 2, i = 1 and k = 2, we get r = (24 − 1)/(22 − 1) = 5 and
a = 3, and thus L = X 8 − X 3 is a quasi-subﬁeld polynomial. On the other
hand, β(L) = log2(3).4/32 ≃ 0.70 < 0.75. This shows that Theorem 1 is not
valid for multiplicative quasi-subﬁeld polynomials.

In the second and last families, we can choose n prime as is the case for the
subﬁeld curves recommended by NIST. However, there are values of n which
may not lead to any suitable parameter set for the second and third types. For
example, with n = 5 and k > 1, the integer k5 + k − 1 = (k3 + k2 − 1)(k2 − k + 1)
so k5 + k − 1 is not prime. More generally, for all n ≡ 5 mod 6, (k2 − k +
1)|(kn + k − 1) and thus any integer of the shape k5+6i + k − 1 with k > 1 is
composite. Similarly, for all n ≡ 2 mod 6, (k2 − k + 1)|(kn − k + 1) and thus
there is no prime of the shape k2+6i − k + 1 with k > 1 and i > 0.

The last two families overlap when n = 2 as (k −1)2 +(k −1)−1 = k2 −k −1.
We excluded the case n = 2 in the last family, because such a choice of n′ and
r would lead to β = 0, which is not allowed in our deﬁnition of quasi-subﬁeld
polynomials. Yet, thanks to the last two families, we have a multiplicative
quasi-subﬁeld polynomial for any n and p = kn − k − (−1)n prime.

Finally, it is worth noticing that the case p = kn − k − (−1)n is the most
promising one among the families introduced. Indeed, primes of the form f (2m),
where f (x) is a low-degree polynomial with small integer coeﬃcients, are often
used in cryptography since they were introduced in [8]. Indeed as well as for
Mersenne primes, they allow fast modular reduction. They are called Soli-
nas primes, or generalized Mersenne primes. Coming back to our exemple,
f (x) = xn − x − (−1)n veriﬁes the constraint required about the weights of
the coeﬃcients, so the last family when applied with k a power of 2 corre-
sponds to Solinas primes. It is then important to notice that Curve448, which
is part of the approved elliptic curves for use by the US Federal Government,
uses a prime exactly of this shape: p = 2448 − 2224 − 1.[9][10]. Moreover, four
others curves that were recommended by NIST in 1999 [11] also uses Solinas
primes: p-192 (p = 2192 − 264 − 1), p-224 (p = 2224 − 296 + 1) and p-256
(p = 2256 − p224 + 2192 + 296 − 1) and p-384 (p = 2384 − 2128 − 296 + 232 − 1).
Therefore, it may seem interesting to study more deeply multiplicative quasi-
subﬁeld polynomials when p is a Solinas prime. For a list of Solinas primes of
the shape 2n − 2m ± 1, one can consult [8]. Of course, this approach is still far
from threatening the security of these curves: they are deﬁned on a prime ﬁeld
Fp while we are considering an extension ﬁeld Fpn with n ≥ 2 and have β ≃ 1
so we obtain a complexity of O(p0.95n). (See Remark 1 for the detail)

15

Proof. In each case, we show that for a := pn′

mod r, we have pn′

− a|pn − 1

and β :=

n logp a

n′2 ≤ 1.

1. We ﬁrst note that r = pn−1

p2i−1 is an integer since 2i|n.

We now show that a = pn′

mod r = pi(2k−1) +1

pi+1

. Indeed, we have

pn′

−

pi(2k−1) + 1
pi + 1

=

pn − 1
p2i − 1

(pi − 1) = r(pi − 1)

and

pi(2k−1) + 1
pi + 1

1

r

=

(pi(2k−1) + 1)
(pi + 1)

(p2i − 1)
(p2ik − 1)

= (pi(2k−1) + 1)

(pi − 1)
(p2ik − 1)

=

p2ik − pi(2k−1) + pi − 1
(p2ik − 1)

= 1 −

pi(2k−1) − pi
p2ik − 1

< 1

since 2k − 1 > 1.
Therefore, we have pn′
pi+1 and thus pn′
This implies that L splits completely over Fpn and it has pn′
roots.

− a = r(pi − 1) = p2ik−1

pi+1 + 1 ≈ pi(2k−1) = pn′

p2ik−1

− a|pn − 1.

− a + 1 =

Moreover, using a = pi(2k−1)+1

pi+1 =

2k−2

j=0 (−pi)j ≤ pi(2k−2), we get

β =

logp(a) · n
n′2

≤

P
i(2k − 2) · 2ik

(i(2k − 1))2 = 1 −

1

(2k − 1)2 ≤ 1.

2. We ﬁrst note that r = p−k

k−1 is integer since k − 1|kn − 1. Moreover,
k−1 (k − 1) + k = r(k − 1) + k with k < 1 + k + · · · + kn−1 = r so

p = p−k
a = (p mod r) = k and p − a = kn − 1. Therefore,

k−1 = kn−1

pn − 1 = (kn + k − 1)n − 1 =

n

n

i

i=1 (cid:18)
X

(kn − 1)ikn−i

(cid:19)

= (kn − 1)

(kn − 1)i−1kn−i

n

n

i

(cid:19)

= (p − a)

i=1 (cid:18)
X
n

n

i

i=1 (cid:18)
X

(kn − 1)i−1kn−i.

(cid:19)

Consequently, we have p − a|pn − 1, so L = X p − X a splits in Fpn and it
has pn′
− a + 1 = p − a + 1 = (kn + k − 1) − k + 1 = kn roots. This is very

16

close to p = pn′
have

if kn ≫ 1. Furthermore, since kn ≤ kn + k − 1 = p, we

β = logp(a) · n/1 = logp(an) = logp(kn) ≤ 1.

3. The third proof is very similar to the ﬁrst two proofs, and presented in

Appendix C.

3.4. Quasi-subﬁeld polynomials with n Mersenne

When n = 2k − 1 is a Mersenne prime, (X n − 1)/(X − 1) has (n − 1)/k
irreducible factors of degree k over F2, which gives a large number of potential
candidates for linearized quasi-subﬁeld polynomials in F2n . We note that for
p = 2, pd+1 − 1 is a Mersenne number, hence Type 2 of Proposition 5 gives
examples of such polynomials.

The case of linearized quasi-subﬁeld polynomials with n a Mersenne prime
number is also treated in the appendix of [1]. Interestingly, [1] argued that such
parameters were unlikely to exist. We now recall (and slightly extend) their
heuristic argument, and we show that Type 2 polynomials from Proposition 5
give a counter-example to it.

Reasoning from [1]. Let us consider k such that n = 2k − 1 is prime, and denote
by N (k, n′) the number of distinct polynomials of degree n′ that divide X n − 1.
Then [1] gives the following lemma:

Lemma 5. We have N (k, n′) =

⌊n/k⌋
⌊n′/k⌋

if n′ mod k ∈ {0, 1}, and N (k, n′) = 0

otherwise. Moreover, log

n′/k ≫ 1.

⌊n/k⌋
(cid:0)
⌊n′/k⌋

(cid:16)(cid:0)

(cid:1)(cid:17)

≃ (n′/k) log(n/n′) when n/k ≫ 1 and

(cid:1)

The argument in [1] relies on the following heuristic approximation: for n a
Mersenne prime, we may assume that the density of “sparse enough” polyno-
mials (i.e. polynomials of the shape X n′
− λ(X) with deg(λ) small) is identical
for factors of X n − 1 as for random polynomials of the same degree.

Since in F2[X], there are 2n′

monic polynomials of degree n′ and 2ℓ monic
polynomials of degree at most ℓ, this assumption allows us to approximate the
number of polynomials of degree n′ that divide X n − 1 and are sparse enough
by N (k, n′)2ℓ−n′

. Accordingly, such polynomials a priori exist if and only if

ℓ > n′ − (n′/k) log(n/n′).

The case considered in the appendix of the article is when the quasi-subﬁeld
polynomial approach beats generic algorithms on ECDLP, which as we will
prove in Lemma 8 requires αβ = 1

2κβ ≥ 1 for some algorithmic constant κ.

this category since its αβ ≃ 1

We recall their argument in this case ﬁrst, even if Type 2 does not fall in
2κ is not bigger than 1. To improve on generic
2κn . With the previous

2κℓn/n′2 ≥ 1 hence ℓ ≤ n′2

algorithms, we want αβ =

1

17

2κn > 1−log(n/n′)/ log(n) = log(n′)/ log(n). Therefore, log(n)

constraint on ℓ, we obtain n′2
2κn > n′ − (n′/k) log(n/n′). Thus, since k ≃ log(n),
2κn > log(n′)
we get n′
.
Since 2κ ≃ 10, and n′ < n, this inequality can never be satisﬁed (except if
n′ = 1) so according to the above heuristic approximation, there should not
be any linearized quasi-subﬁeld polynomials with n Mersenne and big n and n′
beating the generic algorithms.

n′

The case of Type 2 polynomials. The same reasoning can be extended to quasi-
subﬁeld polynomials that do not verify αβ ≥ 1.

In this case, we only require β = ℓ · n/n′2 ≤ 1. Therefore, we have ℓ ≤ n′2/n
(instead of ℓ ≤ n′2
2κn before). This constraint added to the same heuristic as
before gives: n′2
n > n′ − (n′/k) log(n/n′) which similarly as in the previous
paragraph gives log(n)
. Since the function log(x)/x is decreasing for
x > e, we deduce (following the same heuristic reasoning) that quasi-subﬁeld
polynomials are unlikely to exist for n > n′ ≥ 3.

n > log(n′)

n′

This conclusion, however, is contradicted by the existence of Type 2 poly-

nomials from Proposition 5.

On the heuristic approximations used in [1]. The above contradiction shows
that the heuristic approximation used in [1] idoes not hold in general: when n
is a Mersenne prime, there exists an ℓ such that the density of “sparse enough”

polynomials (i.e. polynomials of the shape X pn′
bigger for factors of X n − 1 than for random polynomials.

− λ(X) with deg(λ) ≤ ℓ) is

A similar heuristic in [1] says that there are only rare parameters for which
we can have a quasi-subﬁeld multiplicative polynomials. It uses really similar
arguments to the ones introduced before for the case where n is a Mersenne
prime. Property 6 shows that this heuristic about the distribution of completely
splitting polynomials also fails.

4. Application to Cryptography

While quasi-subﬁeld polynomials are mathematical objects of independent
interest, the main motivation for their introduction in [1] is a cryptographic
In this section we ﬁrst recall the Elliptic Curve Discrete Loga-
application.
rithm Problem (ECDLP) and standard approaches to solve it. We then describe
Huang et al.’s algorithm [1] using quasi-subﬁeld polynomials and we explain how
its complexity crucially depends on the parameter β of the polynomial. Next,
we apply our results to this ECDLP algorithm, and discuss the resulting com-
plexity. Finally, we introduce some aspects of coding theory where our results
on linearized polynomials could be useful.

4.1. ECDLP and previous ECDLP algorithms

Let us consider an ECDLP instance: Let E be an elliptic curve on K = Fpn ,
P a point on the curve E and Q a point in < P >, the group generated by P .
We are looking for k such that Q = kP .

18

Before considering the algorithm using QSPs [1], we recall two algorithms

for solving the ECDLP and their complexity.

• Exhaustive search (or brute-force algorithms) :

it corresponds to the
computation all the elements of < P > until ﬁnding Q. The cost is
O(< P >) = O (pn) for typical parameters.

• Generic algorithms such as Baby-Step-Giant-Step or Pollard-Rho [12]:

The complexity is O(

| < P > |) ≈ O

pn/2

.

(cid:0)

p

These will be used as benchmarks to assess the performance of our algorithm.
For more information about these algorithms and other approaches to solve the
ECDLP, the reader can consult Recent progress on the elliptic curve discrete
logarithm problem [13] by Galbraith and Gaudry. It is also worth noticing that
these two algorithms can solve the discrete logarithm problem in any group and
we can hope that the new algorithm, which uses the structure of the group, has
a better complexity.

(cid:1)

When n is composite, we can write n = ˜nk and consider q = pk so that
Fpn = F
q ˜n . Better algorithms exist in this situation: Gaudry [14] succeeded in
2009 to ﬁnd an algorithm solving the elliptic curve discrete logarithm problem on
F
q ˜n in O(q2−2/˜n). For ˜n = 2, it leads to an algorithm with cost O(p(n/2)(2−1)) =
O(pn/2) comparable with generic algorithms. For ˜n = 3, it leads to an algorithm
with cost O(p(n/3)(2−2/3)) = O(p4/9n), slightly better than generic algorithms.
Diem also proved that there exists a sequence of prime powers Qi = qni
i with
log(qi) such that the ECDLP in E(FQi ) can be solved in subexponential
ni ≃
time [15]. It works with any elliptic curve over FQi and uses an approach similar
to the one introduced below but with subﬁeld polynomials instead of quasi-
subﬁeld polynomials. This was one of the motivation of this new approach.

p

4.2. The quasi-subﬁeld approach

We will now introduce the algorithm of [1], which uses quasi-subﬁeld poly-

nomials to solve elliptic curve discrete logarithm problems.

Let E be an elliptic curve on K = Fpn , P ∈ E and Q ∈< P >. The elliptic
curve discrete logarithm problem asks for computing k such that Q = kP . For
simplicity and concreteness, we assume the curve is given in reduced Weierstrass
coordinates.

Let R ∈ Fpn [X] be a quasi-subﬁeld polynomial. We deﬁne V as the set of
the roots of R and F := {(x, y) ∈ E|x ∈ V }. The algorithm ﬁrst computes more
than |V | relations of the shape:

ajP + bjQ = P1 + · · · + Pm

with aj, bj random and Pi ∈ F . Linear algebra on the relations then gives the
value of k such that Q = kP .

In order to compute these relations, the algorithm uses Semaev’s summa-
for an elliptic curve E deﬁned over a ﬁeld K, the rth

tion polynomials [16]:
summation polynomial Sr ∈ K[X] is such that

Sr(x1, · · · , xr) = 0 ⇔ ∃(x1, y1), · · · (xr, yr) ∈ E, (x1, y1) + · · · + (xr, yr) = 0

19

For given aj, bj, we compute ajP + bjQ = (Xj, Yj). Then, computing

P1, · · · , Pm such that

ajP + bjQ = P1 + · · · + Pm = (x1, y1) + · · · + (xm, ym)

with xi ∈ V amounts to ﬁnding x1, · · · , xm ∈ V such that Sm+1(Xi, x1, · · · , xm) =
0 and then ﬁnding the associated yi.

The polynomial equation Sm+1(Xi, x1, · · · , xm) = 0 is solved as follows. Let
M be the set of monomials in K[x1, · · · , xm], and let i be a positive integer.

For f =
φ : K[x1, · · · , xm] → K[x1, · · · , xm] deﬁned by

M∈M aM M ∈ K[x1, · · · , xm], let F i(f ) =

P

P

f (x1, · · · , xm) 7→ F n′

(f )(λ(x1), · · · , λ(xm)).

M∈M api

M M . Let also

Note that f pn′

≡ φ(f ) mod (xpn′

1 − λ(x1), · · · , xpn′

m − λ(xm)).

Finally, let S(0)(x1, · · · , xm) = Sm+1(Xi, x1, · · · , xm) and for k ∈ {1, · · · , m − 1},

let S(k)(x1, · · · , xm) = φ(S(k−1)(x1, · · · , xm)). One can then solve the polyno-

mial equation Sm+1(Xi, x1, · · · , xm) = 0 by solving the system S =
This is a sparse polynomial system with m equations and m variables.

S(k) = 0

m−1

k=1 .

(cid:8)

(cid:9)

4.3. Complexity of the quasi-subﬁeld approach

We now recall the complexity estimations of this algorithm as given in [1].

m−1

S(k)

(cid:8)

(cid:9)

We know that S =

k=1 is a sparse polynomial system of m equa-
tions and m variables. Therefore,
it can be solved eﬃciently using Rojas’
sparse resultant algorithm [17] and a univariate polynomial root ﬁnding al-
gorithm such as BTA [5]. According to [1] (Lemma 3.1) the cost of this step
is ˜O(m5.188(3pℓ)κm2
). Here we introduce the notation κ as the numerical value
4.876 used in [1] may be suboptimal. Moreover, the system has solutions only
with probability |F |m/m!
since (Xi, Yi) is a random point on E with |E| ≃ pn
and the number of sums of m points in F is approximately |F |m/m!. Also,
heuristically, half of the values in V are the x-coordinates of exactly two points
on the curve so |F | ≃ |V | ≃ pn′
. As we need pn′
relations of this type, the cost
of the relation search phase is pn′ m!pn

˜O(m5.188(3pℓ)κm2

).

pn

Once all the pn′

relations are gathered, each of them involves m points.
Therefore, the system built from these relations is sparse. Thus, a sparse linear
algebra algorithm can be used to ﬁnish the computation [18], at a cost approx-
imately mp2n′

. This gives the complete cost of the algorithm:

pn′m

m!pn−n′m+n′ ˜O(m5.188(3pℓ)κm2

) + mp2n′

Rewriting this expression to make β appear, we get the following estimation of
the complexity:

Proposition 7 (Complexity of Huang et al.’s algorithm). Let P = X pn′
be a β-quasi-subﬁeld polynomial and let ℓ = logp(deg λ). If |F | ≃ |V| ≃ pn′

−λ(X)
, the

20

complexity of Huang et al.’s algorithm is

˜O

m!p

n

1+κβ

(cid:18)

n′m
n

2

(cid:17)

(cid:16)

− n′m

n (cid:19)

+n′

m5.1883κm2

+ mp2n′

!

where κ is a constant involved in the cost of the resolution of the system S
currently majored by 4.876.

In the following we deﬁne α = n′m/n > 0, and we try to ﬁnd α which

minimises the complexity. We will assume that m is ﬁxed.

Proposition 8 (Best choice of parameters). We can observe the following re-
sults in order to optimize the complexity:

• The minimal complexity is obtained for α = αβ with αβ := 1

2κβ . Then,

the complexity becomes ˜O

pmax(2αβ /m,1−αβ (1/2−1/m))n

.

• In order to beat brute force algorithms, m > max(2αβ, 2) is required. So

(cid:1)

(cid:0)

we have interest not to choose a very small integer for m.

• If αβ < 2 and m ≫ 1, then the complexity becomes ˜O

p(1−αβ /2)n

• Therefore, to beat generic algorithms, we need αβ > 1

(cid:0)

(cid:1)

We remark that the condition αβ < 2 is not really restrictive. Indeed for all
the quasi-subﬁeld polynomials exhibited in this paper, we have αβ < α0.5 < 1.

Proof. Let us now prove these four results. The complexity of the algorithm is
bounded by ˜O(m!pn(1+κβ(n′m/n)2−n′m/n)+n′
which with the
α-notation and the fact that m is considered as a ﬁxed integer, can be rewritten
as ˜O(pn(κβα2−α+1)+αn/m + p2αn/m).

m5.1883κm2

)+mp2n′

Since κβα2 − α + 1 is minimum for α = 1

consider β > 0) and then has minimal value κβ 1
we get that the complexity can be rewritten as

2κβ = αβ (we recall that we only
(κβ)2 − 1
2 ,

2κβ +1 = 1− 1

4κβ = 1− αβ

˜O

pmax(2αβ /m,1−αβ (1/2−1/m))n

.

(cid:16)

(cid:17)

In order to beat the brute force algorithms (which corresponds to a com-
plexity of O(pn)), what we need is to have on one side 2αβ/m < 1 which is true
as soon as m > 2αβ, and on the other side, 1 − αβ(1/2 − 1/m) < 1, namely
m > 2. Hence m > max(2αβ, 2).

Moreover, one can notice that 2αβ/m ≤ 1−αβ(1/2−1/m) if only if αβ(1/m+
1/2) ≤ 1. Therefore if m ≫ 1 then αβ ≤ 2 implies 2αβ/m ≤ 1−αβ((1/2−1/m),
so we can rewrite the complexity as ˜O

p(1−αβ /2)n

.

Generic algorithms have a complexity of O(pn/2), therefore we need αβ > 1

(cid:0)

(cid:1)

to run faster than them.

21

 
The following table gives concrete complexity estimates for various values of

β, assuming κ = 4.876.

β
1 − αβ/2

1.0
0.949

0.8
0.936

0.6
0.915

0.4
0.872

0.2
0.744

0.15
0.658

0.1
0.487

Complexity estimates of Huang et al ’s algorithm for various values of β. By Proposition 8

the complexity of Huang et al.’s algorithm is ˜O (cid:16)p(1−αβ /2)n

(cid:17).

Remark 1. We observe that for β = 1, we have 1 − αβ/2 ≈ 0.95 so we get
a complexity slightly better than the one of brute force algorithms. We can
beat generic algorithms for αβ > 1, which for this speciﬁc value of κ implies
β < 0.103.

4.4. Impact of our results on ECDLP

We will now study the consequences of Theorem 1. Let L be a linearized
quasi-subﬁeld polynomial. Then by Theorem 1 we have β(L) ≥ 3/4 and with

1

2

≤

2 · κβ(L)

3 · κ

κ ≃ 4.876 we get αβ =

< 1/7. This shows that aβ < 1 and it

is not possible to beat generic algorithms with L. The best complexity we can
hope is indeed ˜O(p(1−αβ (1/2−1/m))n), which is bigger that ˜O(p(1−1/14)n).

The previous estimation uses the approximation κ ≃ 4.876. If we succeeded
to have κ < 1.5 then, when β(L) = 3/4, we would have αβ > 1, so such a
polynomial L could allow us to have an algorithm running faster than generic
algorithms.

All the quasi-subﬁeld polynomials exhibited in this article have β > 0.7 and
thus αβ < 1. In particular, none of them currently leads to an algorithm running
faster than generic algorithms.

4.5. Links with coding theory

Linearized polynomials have attracted considerable interest, and our results

can therefore be used in other contexts as well.

For example, linearized polynomials occur in rank-metric codes. The char-
acterisation of completely splitting linearized trinomials given in [7] is used in
the same article to study codes of the shape C3,n,σ = hx, xσ, xσ3
iFqn , with both
their result on existence and non existence of such trinomials being used. In
[19], codes of the shape

CT :=

a0X qt0 + a1X qt1 + . . . ak−1X qtk−1 , a0, a1, . . . , ak−1 ∈ Fqn

n

o

for sets T = {t0 < t1 < · · · < tk−1} ⊂ {0, . . . , n − 1} are studied. Maybe, The-
orem 1, which gives wider results than [7] on completely splitting linearized
polynomials could help to study such codes.

22

This notion also appears in cyclic subspace codes. For instance in [7], families
of cyclic subspace codes are exhibited via linearized polynomials. Interestingly,
the paper uses a parameter called gap which characterizes the sparsity of a
polynomial and implies bounds on the minimal distance of an associated code.
−λ(X) ∈ Fpn [X]

The gap is deﬁned as n′−ℓ for a linearized polynomial P = X pn′

with λ of degree pℓ. It is therefore similar to our parameter β :=

ℓ · n

n′2 .

5. Conclusion

We studied the existence of quasi-subﬁeld polynomials (QSP) introduced by
Huang et al. [1]. We proved a new lower bound on the β parameter of linearized
QSP, and we introduced several new QSP families. We leave as an open problem
the classiﬁcation of all the QSP.

The main motivation underlying [1] is a new algorithm to solve the elliptic
curve discrete logarithm problem, with a complexity depending on the β param-
eter of the QSP used. We showed that this algorithm is currently outperformed
by other algorithms even with our new QSP families. Moreover, our new bound
suggests that Huang et al.’s algorithm will remain worse if only linearized QSPs
are used.

Acknowledgements

We would like to thank the reviewers for their helpful comments, especially

for pointing out the link between this work and coding theory.

References

[1] M.-D. Huang, M. Kosters, C. Petit, S. L. Yeo, Y. Yun, Quasi-subﬁeld
polynomials and the elliptic curve discrete logarithm problem, Journal of
Mathematical Cryptology 14 (1) (2020) 25–38.

[2] G. McGuire, D. Mueller, Some results on linearized trinomials that split

completely, Finite Fields and their Applications (2020) 149.

[3] G. McGuire, J. Sheekey, A characterization of the number of roots of lin-
earized and projective polynomials in the ﬁeld of coeﬃcients, Finite Fields
and Their Applications 57 (2019) 68–91.

[4] B. Csajb´ok, G. Marino, O. Polverino, F. Zullo, A characterization of lin-
earized polynomials with maximum kernel, Finite Fields and Their Appli-
cations 56 (2019) 109–130.

[5] E. Berlekamp, Algebraic coding theory, World Scientiﬁc, 1968.

23

[6] W. Y. C. Chen, J. D. Louck, The combinatorial power of the companion matrix,

Linear Algebra
doi:10.1016/0024-3795(95)90163-9.
URL http://www.sciencedirect.com/science/article/pii/0024379595901639

its Applications

261–278.

(1996)

and

232

[7] P. Santonastaso, F. Zullo, Linearized trinomials with maximum kernel,

arXiv preprint arXiv:2012.14861.

[8] J. A. Solinas, et al., Generalized mersenne numbers, Citeseer, 1999.

[9] M. Hamburg, Ed448-Goldilocks, a new elliptic curve, Tech. Rep. 625

(2015).
URL https://eprint.iacr.org/2015/625

[10] I.

T.

Computer
Transition Plans for Key Establishment Schemes | CSRC (Oct. 2017).
URL https://csrc.nist.gov/News/2017/Transition-Plans-for-Key-Establishment-Schemes

Division,

Security

L.

[11] NIST, Recommended elliptic curves for federal government use (1999).

[12] P. C.

van Oorschot, M.

J. Wiener, Parallel

J. Cryptology 12

collision search
1–28.

(1999)

with cryptanalytic
doi:10.1007/PL00003816.

applications,

[13] S. D. Galbraith, P. Gaudry, Recent progress on the elliptic curve discrete logarithm problem,

Codes

Designs,
doi:10.1007/s10623-015-0146-7.
URL http://link.springer.com/10.1007/s10623-015-0146-7

Cryptography

(2016)

and

(1)

78

51–72.

[14] P. Gaudry, Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem,

of

Symbolic Computation

Journal
doi:10.1016/j.jsc.2008.08.005.
URL https://linkinghub.elsevier.com/retrieve/pii/S074771710800182X

1690–1702.

(2009)

(12)

44

[15] C. Diem, On the discrete logarithm problem in elliptic curves, Compositio

Mathematica 147 (1) (2011) 75–104. doi:10.1112/S0010437X10005075.
URL https://www.cambridge.org/core/product/identifier/S0010437X10005075/type/journal_article

[16] I. Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves,

Tech. Rep. 031 (2004).
URL http://eprint.iacr.org/2004/031

[17] J. M. Rojas,

Solving Degenerate Sparse Polynomial Systems Faster,
155–186.

Symbolic Computation

Journal
doi:10.1006/jsco.1998.0271.
URL http://www.sciencedirect.com/science/article/pii/S0747717198902711

(1999)

(1)

28

of

[18] D. Wiedemann, Solving sparse linear equations over ﬁnite ﬁelds,
(1986) 54–62.

IEEE Transactions on Information Theory 32 (1)
doi:10.1109/TIT.1986.1057137.

24

[19] B. Csajbok, G. Marino, O. Polverino, Y. Zhou, Mrd codes with maximum

idealizers, Discrete Mathematics 343 (9) (2020) 111985.

Appendix A. Adaptation of the results from [6]

In [6], Chen and Louck give a formula for computing the powers of the

following companion matrices :

Comparing it with our deﬁnition of companion matrices,

C(u1, · · · , um) :=

D(a1, a2, ..., am) =

u1 u2
0
1
1
0



...

0

...

0








· · ·
· · ·
· · ·

. . .

· · ·

· · · um
· · ·
· · ·

0
0

...

0

1










0 · · ·
0 · · ·

· · ·
· · ·

1 · · ·

· · ·

...

...

. . .

0

0 · · ·

...

1

0
1



0









a1
a2

...

am

,











we notice that D(a1, a2, ..., am) is the antitranspose of C(am, · · · , a2, a1). For-
mally, we have :

D(a1, a2, ..., am) = P · C(am, · · · , a2, a1)T · P with P =



0

· · · 0 1

...
...

1







· · · 1 0

...

0

· · ·



.







Since P 2 = Id, we get that for all n ≥ 0, D(a1, a2, ..., am)n is the antitrans-
pose of C(am, · · · , a2, a1)n. Chen and Louck give the following formula for the
coeﬃcient (i, j) of C(u1, · · · , um)n:

c(n)

i,j =

Xk1,...,km

kj + kj+1 + · · · + km
k1 + · · · + km

k1, k2, · · · , km

k1 + · · · + km (cid:19)

(cid:18)

uk1

1 · · · ukm

m

where the summation is over non-negative integers satisfying
Moreover, when the previous sum is not deﬁned, i.e. when n = i − j, c(n)

ιkι = n − i + j.
i,j = 1.
Since applying the antitranspose boils down to swapping the coeﬃcients
(i, j) and (m + 1 − j, m + 1 − i)3, we get the expression of the coeﬃcient (i, j)
of D(a1, a2, ..., am)n:

P

3We number the rows, as well as the columns from 1 to m.

25

d(n)

i,j = c(n)

m+1−j,m+1−i

=

Xk1,...,km

km−i+1 + km−i+2 + · · · + km
k1 + · · · + km

(cid:18)

k1, k2, · · · , km

k1 + · · · + km (cid:19)

ak1

m · · · akm

1

where the summation is over non-negative integers satisfying

ιkι = n − (m − j + 1) + m − i + 1 = n − i + j

Moreover, when the previous sum is not deﬁned (i.e. when n = j − i) then

X

d(n)

i,j = 1.

In the proof of Lemma 4, we consider M := D(⊛, . . . , ⊛, a•, 0, . . . , 0) a matrix

of dimension n′, which leads to M n

i,j = 1 if n = i − j, and

M n

i,j =

wk · 0k1+···+kn′−ℓ−1 · (a•)kn′ −ℓ · ⊛kn′−ℓ+1+···+kn′

k=(k1,··· ,kn′ )
X

n′

ιkι=n−i+j

Pι=1

otherwise, where k = (kι)1≤ι≤n′ are non-negative integers and

wk =

kn′−i+1 + · · · + kn′
k1 + · · · + kn′

k1 + · · · + kn′
k1, · · · , kn′

(cid:18)

.
(cid:19)

Appendix B. Some linearized QSP

In this section we provide the list of linearized QSP found through the sys-
tematic search described in Section 3.2. Recall that this search only covers
representatives of equivalence classes for p ∈ {2, 3, 5, 7}, n′ ≤ 16, and coeﬃ-
cients values restricted to {0, 1, −1}.

For the sake of readability, we list polynomials f instead of their correspond-
ing quasi-subﬁeld polynomials Lf . We provide the values of n and p such that
Lf is in QL
p,n and indicate the associated value β. We mark by a checkmark
in the table when the linearized polynomial belongs to the category (as deﬁned
in Proposition 5), except for the last category where we give the value of the
inverse.

26

2
7

f
X 2 + X + 1
X 2 + X + 1
X 3 + X + 1
X 3 + X + 1
X 3 + X 2 + X + 1
X 4 + X + 1
X 4 + X + 1
X 4 + X 2 + X + 1
X 4 + X 3 + X 2 + X + 1
X 5 + X + 1
X 5 + X + 1
X 5 + X 4 + X 3 + X 2 + X + 1
X 5 − X 3 − X 2 + X − 1
X 6 + X + 1
X 6 + X 5 + · · · + X 2 + X + 1
X 7 + X + 1
X 7 + X 3 + X + 1
X 7 + X 6 + · · · + X 2 + X + 1
X 8 + X + 1
X 8 + X + 1
X 8 + X 4 + X 2 + X + 1
X 8 + · · · + X 2 + X + 1
X 9 + X + 1
X 9 + X + 1
X 9 + X 3 + X + 1
X 9 − X 6 − X 5 + X 3 − X 2 + X − 1
X 9 + · · · + X 2 + X + 1

n
3
3
7
8
4
15
13
7
5
21
24
6
8
31
7
48
15
8
63
57
15
9
73
80
26
13
10

β
0.75
0.75
0.78
0.8
0.8
0.9
0.8
0.8
0.9
0.8
0.9
0.9
0.9
0.8
0.9
0.9
0.9
0.9
0.9
0.8
0.9
0.9
0.9
0.9
0.9
0.9
0.9

T3

X 3 + X + 1

X 3 + X + 1

p
2
3,5,7
2
3

T1 T2
X X
X
X X
X

2,3,5,7 X

2
3
2

X

X
X X

X

2,3,5,7 X
X

2
5

2,3,5,7 X

3
5

X
2,3,5,7 X

7
2

X
X X

2,3,5,7 X

2
7
2

X

X
X X X 7+X 3+X+1

2,3,5,7 X
X

2
3
3
3

2,3,5,7 X

X
X

X 4 + X + 1

f
X 10 + X + 1
X 10 + · · · + X 2 + X + 1
X 11 + X 8 + X 7 + X 5 + X 3 + X 2 + X + 1
X 11 + · · · + X 2 + X + 1
X 12 + · · · + X 2 + X + 1
X 13 + X 4 + X + 1
X 13 + · · · + X 2 + X + 1
X 14 + · · · + X 2 + X + 1
X 15 + X 7 + X 3 + X + 1
X 15 + X 14 + · · · + X 2 + X + 1
X 16 + X + 1
X 16 + X 4 + X + 1

X 16 + X 8 + X 4 + X 2 + X + 1

X 16 + X 12 + X 11 + X 8 + X 6 + X 4 + X 3 + X 2 + X + 1
X 16 + · · · + X 2 + X + 1

β
0.9
0.9
0.9
0.9
0.9
0.9
0.9
0.9
0.9
0.9
0.9
0.9

0.9

0.9
0.9

n
91
11
15
12
13
40
14
15
31
16
255
63

31

21
17

...

2
8

T3

X 4 + X + 1

2

p
3

T1 T2
X
2,3,5,7 X
X
2,3,5,7 X
2,3,5,7 X
X
2,3,5,7 X
2,3,5,7 X

3

2

X X

2,3,5,7 X

2
2

2

X
X

X X

2

X
2,3,5,7 X

X 15 + X 7 +
X 3 + X + 1
X 5 + X + 1

Table B.2: Classiﬁcation of the outputs of the algorithm

Appendix C. Proof of the third family of multiplicative QSPs

We will now demonstrate that the third family of Proposition 6 is a family

of multiplicative QSPs. We recall that it is deﬁned as X pn′

− X a ∈ Fpn with

• p = kn − k − (−1)n prime, n > 2 and k > 1 integers such that kn ≫ 1.

• n′ = n − 1

• r = (pn−1)(k−(−1)n)

(kn−k)(kn−(−1)n)

• a := pn′

mod r

We will prove that r|pn − 1, provide an explicit formula for a and show that

β := n logp a/(n′)2 ≤ 1.

We will ﬁrst show that r = (pn−1)(k−(−1)n)

(kn−k)(kn−(−1)n) is an integer dividing pn − 1.

We can notice that (kn − k)|pn − 1. Indeed we have :

(pn − 1) = ((kn − k) + (−1)n+1)n − 1

=

n

n

i

i=1 (cid:18)
X

= (kn − k)

(kn − k)i(−1)(n+1)(n−i) + (−1)n(n+1) − 1

(cid:19)

n−1

n

i

i=0 (cid:18)
X

(kn − k)i(−1)(n+1)(n−i)

(cid:19)

Similarly, (kn − (−1)n)|pn − 1 since

(pn − 1) = ((kn − (−1)n) − k)n − 1

n

=

i=1 (cid:18)
X

n

i

(cid:19)

= (kn − (−1)n)

(kn − (−1)n)i(−k)n−i + (−k)n − 1

n−1

n

i

i=0 (cid:18)
X

(kn − (−1)n)i(−k)n−i + (−1)n

(cid:19)

!

Therefore (kn −k)(kn −(−1)n)/ gcd(kn −k, kn−(−1)n) is an integer dividing

pn − 1. Moreover,

gcd(kn − k, kn − (−1)n) = gcd((kn − (−1)n) − (kn − k), kn − (−1)n)

= gcd(k − (−1)n, kn − (−1)n)
= k − (−1)n since k − (−1)n|kn − (−1)n.

Hence pn − 1 = r.

(kn − k)(kn − (−1)n)
gcd(kn − k, kn − (−1)n)

and thus r|pn − 1

Since the value of r depends on the parity of n, we distinguish two cases for

the remaining of the proof.

29

 
If n is even. We now show that a := (pn′
pn−1 − pn−1
r ≈ kn2+1−2n for kn ≫ 1, so pn−1+1

mod r) = pn−1+1
kn−k =
kn−k ≃ kn(n−1)−n = kn2−2n while
kn−k ≃ r/k and thus for k big enough, we have

k−(−1)n . Moreover, pn−1+1

Indeed, pn−1+1

− r kn−(−1)n

kn−k = pn′

kn−k

pn−1+1

kn−k < r.

Furthermore, pn′

−a = pn−1

kn−k |pn−1 so L splits over Fpn and it has pn′

−a+1 =

pn−1

kn−k + 1 ≃ kn(n−1) roots. This is close to pn′

roots if kn ≫ 1.

Finally,

an

p(n−1)2 ≃ (kn2−2n)n

kn(n−1)2 = (kn)(n2−2n−n2+2n+1) = k−n < 1 when kn ≫ 1

so an < p(n−1)2

, thus

β = n logp a/(n − 1)2 = (logp an)/(logp p(n−1)2

) ≤ 1.

If n is odd. We now show that a = pn−1k+1
kn+1 .

Indeed pn−1k+1

kn+1 = pn−1 − pn−1

kn+1 = pn′

− r kn−k

k−(−1)n and we have

r =

(pn − 1)(k + 1)
(kn − k)(kn + 1)

(p(k + 1))

1
kn(1 − k1−n)

−

1
(kn − k)(kn + 1)

(kn+1 + kn + o(k3))k−n(1 + k1−n + o(k1−n)) + o(1) for kn ≫ 1

=

=

=

=

=

=

=

>

pn−1
kn + 1
pn−1
kn + 1
pn−1
kn + 1
pn−1
kn + 1
pn−1k + 1
kn + 1
pn−1k + 1
kn + 1
pn−1k + 1
kn + 1
pn−1k + 1
kn + 1

(k + 1 + o(k3−n))(1 + k1−n + o(k1−n)) + o(1)

(k + 1 + o(k3−n)) + o(1)

−

+

+

1
kn + 1
pn−1
kn + 1
pn−1
kn + 1

+

pn−1
kn + 1

(1 + o(k3−n)) + o(1)

(1 + o(k3−n)) + o(1)

(1 + o(1)) since n ≥ 3,

− a = pn−1
Moreover, pn′
kn+1 + 1 ≈ kn(n−1) ≈ pn′

pn−1

kn+1 |pn − 1 so L splits over Fpn and it has pn′

− a + 1 =

roots if kn ≫ 1.

30

Furthermore,

an =

=

n

pn−1k + 1
kn + 1
(cid:18)
(cid:19)
p(n−1)2+n−1kn

(kn + 1)n + o

pn−1k
kn + 1

=

(cid:18)

n

+ o(1)

(cid:19)

pn(n−1)kn
kn2

(cid:19)

(cid:18)

= p(n−1)2 pn−1kn

(kn + 1)n + o(kn(n−1)2

)

= p(n−1)2 (kn(n−1) − (n − 1)k1+n(n−2) + o(nk1+n(n−2)))kn

(1 + 1/kn)n

k−n2

+ o(kn(n−1)2

)

= p(n−1)2

(1 − (n − 1)k1−n + o(nk1−n))(1 − k−n + o(k−n)) + o(kn(n−1)2

)

= p(n−1)2

(1 − (n − 1)k1−n + o(nk1−n)) + o(kn(n−1)2

)

< p(n−1)2

Thus β := n logp a/(n − 1)2 = (logp an)/(logp p(n−1)2

) ≤ 1.

31

