<!--
Extracted from inputs/NAGAO-2013-549/eprint-2013-549.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao.

NOT hand-cleaned, and the extraction of THIS paper is materially worse than the
2015/984 one: the manuscript is a draft that typesets vectors as overset arrows,
so pdfminer emits the arrow accents as separate lines and the displayed formulas
in Sections 2-3 interleave with them. Read the PDF alongside this file for any
formula that matters; this text is a searchable index of the paper, not a
substitute for it. Ligature and math artifacts are left as produced.

WHY THIS PAPER IS FROZEN. Nagao 2015/984 -- whose Theorem 1 claims ECDLP over
F_{2^n} in O(n^{8w+1}) and which GOAL-SEMBIN-fcb7a2 audits -- cites this paper as
[11] for Lemma 3, and declines to reproduce its proof: "Proof of this Lemma is
complicated and not constructive". Lemma 3 is what licenses replacing the true
first fall degree d_F by the FAKE one d'_F taken modulo the field equations, and
the fake one is the only quantity a Macaulay-rank instrument can compute. So the
instrument EXP-SEMBIN-4fa22c builds rests on a lemma proved here and nowhere the
program had read. IDEA-20260913-352163 recorded that as a disclosed limitation
with the pointer unread; this freeze is the step that converts the pointer into a
source an agent has actually opened.

Landing-page metadata, transcribed 2026-09-13 (see provenance.json):
  title      Equations System coming from Weil descent and subexponential attack
             for algebraic curve cryptosystem
  category   Foundations;  Publication info: Preprint. MINOR revision.
  keywords   Decomposition Attack, ECDLP, first fall degree
  history    2013-11-05: last of 2 revisions;  2013-09-04: received
  licence    CC BY;  short URL https://ia.cr/2013/549

The served PDF is the LAST of two revisions. The abstract's own revision note
records that the first version's Section 3 estimate was wrong for the stated aim
and had to be repaired by replacing a monomial by a polynomial in (X_i - tau);
that note is reproduced in the text below and is a fact about this source, not a
judgement of it.
-->

Equations System coming from Weil descent and
subexponential attack for algebraic curve cryptosystem
(Draft)

Koh-ichi Nagao (nagao@kanto-gakuin.ac.jp)

Fac. of Engineering, Kanto Gakuin Univ.,

Joint-work with Kazuto Matsuo(Kanagawa Univ.,) and Tsuyoshi Takagi(Kyushu Univ.))

−→
m0

−→
F ]

#

−→
m0 := Q

−→
Xi

pα¡1¡Ei ∈

#

−→
m0

−→
F ]

−→
X1, ...,

−→
Xd]. For our aim, the solution of the equations system {[

Revise 6 NOV. In §3, we estimate the degree of the [
Fpn [
Sf e} must equals to {[
τ ∈ Fpn \ {P
monomial but polynomial), we have this property and all lemmas still hold.
Revise 9/8 Lemma 9 of the ﬁrst version of this manuscript is false and I delete the content of §4
and related footnote. In §4 of the ﬁrst version, we only showed the existence of many trivial relations,
and please note that this revise does not inﬂuence our theorems, which state the subexponential
complexity of ECDLP/JACDLP under ﬁrst fall degree assumption.

i = 0 |1 ≤ i ≤ n} ∪ {f = 0 |f ∈
i = 0 |1 ≤ i ≤ n} ∪ {f = 0 |f ∈ Sf e}. However, it is not true. Let
−→
Xd] (not

k for some monomial
−→
F ]

i=1 xiwi | xi ∈ Fp}, and take new

−→
Xi − τ )pα¡1¡Ei ∈ Fpn [

−→
m0 by Q

−→
X1, ...,

i=1(

d
i=1

n

d

#

0

Abstract. In [2], Faug´ere et al. shows that the decomposition problem of a point of
elliptic curve over binary ﬁeld F2n reduces to solving low degree equations system over
F2 coming from Weil descent. Using this method, the discrete logarithm problem of
elliptic curve over F2n reduces to linear constrains, i.e., solving equations system using
linear algebra of monomial modulo ﬁeld equations, and its complexity is expected to be
subexponential of input size n. However, it is pity that at least using linear constrains,
it is exponential. In [7], Petit et al. shows that assuming ﬁrst fall degree assumption,
from which the complexity of solving low degree equations system using Gr¨obner basis
computation is subexponential, its total complexity is heuristically subexponential. On
the other hands, the author [6] shows that the decomposition problem of Jacobian of
plane curve over Fpn also essentially reduces to solving low degree equations system over
Fp coming from Weil descent. In this paper, we revise (precise estimation of ﬁrst fall
degree) the results of Petit et al. and show that the discrete logarithm problem of elliptic
curve over small characteristic ﬁeld Fpn is subexponential of input size n, and the
discrete logarithm problem of Jacobian of small genus curve over small characteristic
ﬁeld Fpn is also subexponential of input size n, under ﬁrst fall degree assumption.

Keywords Decomposition Attack, ECDLP, ﬁrst fall degree

1 Notations and Results

Through out of this paper, let p be a small prime number( or power of prime number), n, n0,
d, (d, n0 • n), N = n0d be positive integers 1 , fwigi=1,...,n be a ﬁxed base of Fpn/Fp, and

n0∑

B := f

i=1

xiwi j xi 2 Fpg(‰ Fpn).

Let

¡!
Xi (i = 1, .., d) be variables which move in extension ﬁeld Fpn.
¡!
X1, ...,

ables and a polynomial
be variables which moves in base ﬁeld Fp. fXi,jg are called local variables and a polynomial

¡!
Xd] is called global polynomial. Let fXi,jgi=1,...,d,j=1,...,n0

¡!
Xi are called global vari-

¡!
F 2 Fpn [

1 In elliptic curve case N > n, and in Jacobian case N > ng, where g is the genus of the curve, is

needed.

F 2 Fp[fXi,jg] is called local polynomial. (We sometimes write fXi,jg by fX1, ..., XN g where
N = dn0 for simplicity.) Since Xi,j’s are the variables, whose values are in Fp, there is a set
of equations

Sf e := fX p

i,j

¡ Xi,j j1 • i • d, 1 • j • n0g

called ﬁeld equations.

For global polynomial

obtained by substituting

¡!
X1, ...,

¡!
¡!
F 2 Fpn[
F )(2 Fpn [fXi,jg]) be the polynomial
n0
j=1 Xi,jwj (i = 1, ..., d) and decreasing the degrees of Xi,j’s

¡!
Xd], let wd(

¡!
Xi :=

∑

taking modulo ﬁeld equations Sf e

2 i.e.,

¡!
F ) :=

wd(

¡!
F j¡!

Xi:=P

n0
j=1 Xi,j wj

mod Sf e.

¡!
F ]

Let [

#

k(2 Fp[fXi,jg]) (k = 1, ..., n) be the local polynomials such that

¡!
F ) =

wd(

¡!
F ]

[

#

kwk.

n∑

k=1

¡!
F .

We will call wd(

¡!
F ), [

¡!
F ]

#

k by Weil descent of

Let E/Fpn : f (x, y) = y2 + a1xy + a3y ¡ x3 ¡ a2x2 ¡ a4x ¡ a6 = 0 be an elliptic curve.
From technical reason, we assume that E has no Fpn rational point at x = 0, i.e., the equation
f (0, y) = 0 has no solution in Fpn, which does not lose the generality. Put decomposed factor

DF := fP 2 E(Fpn) j x(P ) 2 Bg,

#

i,j

i,j

¡!
X1, ...,

¡¡!
SemP 0(

where x(P ) is the x-coordinate of P , and consider the decomposition problem which states
that for arbitrary P0 2 E(Fpn ) ﬁnding P1, ..., Pd 2 DF satisfying P0 + P1 + ... + Pd = 0.
¡!
Xd) of degree < 2d such that
From Semaev [8], there is a global polynomial
¡¡!
SemP 0(x(P1), ..., x(Pd)) = 0. So the problem reduces
¡¡!
k = 0 (k = 1, ..., n) and ﬁeld equations
SemP0]
¡ Xi,j = 0 (i = 1, ..., d, j = 1, ..., n0). From the assumption that E has no Fpn rational

P0 + P1 + ... + Pd = 0 is equivalent to
to solving local equations system consisting [
X p
points at x = 0, this problem also reduces to solve [c ¢ ¡!
m ¢
equations X p

k = 0 (k = 1, ..., n) and ﬁeld
¡!
¡ Xi,j = 0, where c is arbitrary element of F£
ei is arbitrary
m =
¡!
Xig 3. In this paper, we show that taking n0 = O(n2/3), d = O(n1/3) and the
k is O(exp(n2/3+o(1))), where o(1) ! 0 when n ! 1.

complexity of computing [
Moreover, if we assume the ﬁrst fall degree assumption of [7], the complexity of solving local
equations system is also O(exp(n2/3+o(1))). So the total cost of solving discrete logarithm of
E(Fpn ) which consists of DF times decomposition of a point of E(Fpn ) and linear algebra
computation of #DF £ #DF size matrix, is also O(exp(n2/3+o(1))).

¡¡!
SemP0]
pn and

monomial of f

¡¡!
SemP0]

¡!
m0 ¢

Let C/Fpn : f (x, y) = 0 be a plane curve of small constant genus g. Fix 1 2 C(Fpn) be
some point of C at x = 1. From technical reason, we assume that C has no Fpn rational
point at x = 0, i.e., the equation f (0, y) = 0 has no solution in Fpn, which does not lose the
generality. 4 Put decomposed factor

¡!
Xi

d
i=1

∏

#

#

DF := fP ¡ 1 jP 2 C(Fpn), x(P ) 2 Bg

−→
F ) ≤ p − 1.

wd(

2 For each i, j, degXi,j
3 In order for solving ECDLP in subexponential complexity, we will take deg
4 From this assumption, solving equations system [c · −→

−→
m = O(exp(n1/3+o(1))).
k = 0 (k = 1, ..., n) and ﬁeld
equations, is equivalent condition of ﬁnding P1, ..., Pd. Note that if this assumption does not hold,
it is only a necessary condition.

−−→
SemP0 ]

m ·

#

¡¡¡!
F(D0)1, ...,

and consider the decomposition problem which states that for arbitrary divisor D0 2 Jac(C/Fpn )
ﬁnding D1, ..., Dd 2 DF satisfying D0+D1+...+Dd » 0. From the author [6], there is a set of g
¡¡¡!
F(D0)g of degree < C d (C is some constant)such that this prob-
global polynomials
¡¡¡!
j = 0 (i = 1, ..., g, j = 1, ..., n)
F(D0)i]
¡ Xi,j = 0 (i = 1, ..., d, j = 1, ..., n0). From the assumption that C

lem reduces to solving local equations system consisting [
and ﬁeld equations X p
has no Fpn rational points at x = 0, this problem also reduced to solve [c ¢ ¡!
(i = 1, ..., g, j = 1, ..., n) and ﬁeld equations X p
F£

j = 0
¡ Xi,j = 0, where c is arbitrary element of
¡!
Xig. In this paper, we show that taking

ei is arbitrary monomial of f

¡¡¡!
F(D0)i]

¡!
m =

¡!
Xi

m ¢

∏

i,j

i,j

#

#

pn and

n0 = O(n2/3), d = O(gn1/3) = O(n1/3) and the complexity of computing [c ¢ ¡!
j is
O(exp(n2/3+o(1))), where o(1) ! 0 when n ! 1. Moreover, if we assume ﬁrst fall degree
assumption of [7], the complexity of solving local equations system is also O(exp(n2/3+o(1))).
So the total cost of solving discrete logarithm of Jac(C/Fpn) which consists of DF times
decomposition of a divisor in Jac(C/Fpn) and linear algebra computation of #DF £ #DF
size matrix, is also O(exp(n2/3+o(1))).

m ¢

It must be noted that although its complexity is subexponential, the practical computa-
tion, especially in cases of p > 2 or g ‚ 2, is diﬃcult and it is only a result of the complexity.

#

¡¡¡!
F(D0)i]

d
i=1

2 First fall degree assumption

Deﬁnition 1 (First fall degree [7]). Let K be a ﬁeld and let f1, ..., fl 2 K[X1, ..., XN ].
ﬁrst fall degree Df f is the (minimal) positive integer satisfying the following;
There exists gi 2 K[X1, ..., XN ] (i = 1, ..., l) such that
1) max1•i•l deg(gifi) = Df f , 2)

i=1 gifi) < Df f , 4) deg(fi) • Df f .

i=1 gifi 6= 0, 3) deg(

∑

∑

l

l

Petit et al. [7] assume the following assumption show the subexponentiality of the discrete
logarithm problem of elliptic curve over binary ﬁeld.

Assumption 1 (First fall degree Assumption) Upper bound of the degree of the polyno-
mial for computing Gr¨obner basis of f1, ..., fl of F4 algorithm is Df f + O(1).

This assumption has some counter examples and Petit et al. assume that the polynomials
f1, ..., fl are general polynomials. However, if f1, ..., fl are randomly chosen, the value of Df f
seems to be very large. In our situation, we treat only the cases that Df f » maxi deg fi and
so, f1, ..., fl cannot be randomly chosen.

For my opinion, if there are many l-ple (g1, ..., gl) 2 Al(K[X1, ..., XN ]) satisfying the deﬁ-
nition of ﬁrst fall degree, assumption seems to be true. For example, for any l£l size invertible









matrix M , put





 := M



 . Deﬁne Df f (M ) by minimal integer satisfying the fol-

1

f (N )
...
f (M )

l

f1

...

fl

i

2 K[X1, ..., XN ] (i = 1, ..., l) such that

lowing;
There exists g(M )
1) max1•i•l deg(g(M )
) <
Df f , 4) deg(f (M )
) • Df f (M ). Put ﬁrst fall degree Df f := maxM Df f (M ). However, by us-
ing this new assumption, I can not prove that the equations system coming from Weil descent
have low ﬁrst fall degree in strict way and it remains a future work.

) = Df f (M ), 2)

6= 0, 3) deg(

i=1 g(M )

i=1 g(M )

f (M )

f (M )

f (M )

∑

∑

i

i

i

i

i

i

i

l

l

Lemma 1. Under the Assumption 1, the complexity of computing Gr¨obner basis of f1, ..., fl
by F4 algorithm is estimated by • O(N Df f ¢C+O(1)), when N (cid:192) Df f and where C is some
constant » 3.

Proof. The number of the monomials of degree • Df f + O(1) is

N Df f +O(1). So, in order to compute Gr¨obner basis of f1, ..., fl, it is suﬃcient to compute

(

Df f + O(1) + N ¡ 1
Df f + O(1)

)

<

linear algebra of the matrix of size N Df f +O(1) £ N Df f +O(1). So its complexity is estimated
by • O(N Df f ¢C+O(1)), where C is linear algebra constant.

#

k = 0, (k = 1, ..., n) and ﬁeld equations X p

In the discussion of [7], the decomposition of arbitrary Fpn rational point of elliptic curve
into d-elements of decomposed factor DF (they treat only binary ﬁeld F2n case and we make
its generalization here), reduces to solving equations system
¡!
f ]

¡!
[
Xd] is
some global polynomial and N = dn0 is an integer > n. Moreover they show that there exists
heuristically some local polynomials g, g1, ..., gn 2 Fp[fXi,jg] such that
1) g ·
2) deg gi • 1 (i = 1, , ..., n), and 3) deg g • maxi deg[

¡ Xi,j = 0, where

¡!
f 2 Fpn [

i mod Sf e,

¡!
X1, ...,

i=1 gi[

¡!
f ]

¡!
f ]

∑

i,j

n

#

#

So, from the deﬁnition of ﬁrst fall degree, the ﬁrst fall degree of equations system

i .

k

f[

∑

2 Fp[fXi,jg]1•i•d,1•j•n0 j k = 1, ..., ng seems to be 1 + maxi deg[

i . However, g is
i modulo ﬁeld equations. So. it seems to include some gap.
only equivalent to
However, from the following lemma, we see that it is not a gap and the equations system
f[
2 Fp[fXi,jg]1•i•d,1•j•n0 j k = 1, ..., ng [ Sf e heuristically has low ﬁrst fall degree
• 1 + maxi deg[

i=1 gi[

¡!
f ]

¡!
f ]

¡!
f ]

n

k

#

#

#

i .

¡!
f ]

#

¡!
f ]

#

Lemma 2. Let G1, ..., GN 2 Fp[X1, .., XN ] be local polynomials and put F :=
(X p
satisfying F :=

¡ Xi) and D := deg F . So, there are some local polynomials G0

1, ..., G0

¢ (X p

∑

N

N

i

¡ Xi) and deg G0
∏

i

• D ¡ p (i = 1, ..., N ).
∑

∏

i=1 G0

i

∑

i

Proof. Fix some monomial order > satisfying
fi. For a local
polynomial H 2 Fp[X1, ..., Xd], let LM (H) (resp. LM (H)) be the leading term (resp. leading
monomial) of H associated with monomial order >. Put

i when

i >

ei >

X ei

X fi

∑

N

i=1 Gi ¢
2 Fp[X1, .., XN ]

G := f(G1, ..., GN ) 2 AN (Fp[X1, ..., Xd]) j F =

N∑

i=1

Gi(X p

i

¡ Xi)g.

For G = (G1, ..., GN ) 2 G, let ψ(G) be the maximal monomial i.e.,
ψ(G) 2 fLM (G1X p

N )g and ψ(G) ‚ LM (GiX p

1 ), ..., LM (GN X p

i ) for all i = 1, ..., N . Put

IN D(G) := fi j ψ(G) = LM (GiX p

i )g, N U M (G) := #IN D(G).

For G = (G1, ..., GN ) 2 G, if N U M (G) = 1, there is some I(• N ) such that ψ(G) =
i ) for i 6= I. So, we have D = deg F = deg ψ(G) ‚

LM (GI X p
p + deg LM (Gi) and deg Gi • D ¡ p (i = 1, ..., N ).

I ) and ψ(G) > LM (GiX p

Assume N U M (G) > 1 and deg ψ(G) > D, and we will construct Gnew 2 G such that

ψ(Gnew) < ψ(G) and from the induction of ψ(G), we will prove this lemma.

Let fI1, .., Ikg = IN D(G). (k = N U M (G) > 1 is assumed.) We have easily

1) X p
∑

2)

I1
k

jGIi (2 • i • k),
) =

i=1 LT (GIiX p

Ii

∑

k

i=1 LT (GIi X p

Ii

) = 0 and

3) (X p

Ii

¡ XIi)GIi = (X p

Ii

¡ XIi)(GIi

¡ LT (GIi) + LT (GIi )

X p¡1

I1

)

+ LT (GIi )

X p
I1

(X p

I1

¡ XI1)(X p

Ii

¡ XIi) (i = 1, ..., k).

So, put

:= GI1 +

∑

k
i=2

LT (GIi )
X p
I1

(X p

Ii

¡ XIi )

¡ LT (GIi ) + LT (GIi )

:= GIi
:= Gi for i 62 IN D(G).

X p¡1

I1

Gnew

I1

Gnew

Ii

Gnew

i

for(2 • i • k) and

Then we have
Gnew = (Gnew
LM (Gnew

1

i

, ..., Gnew

N ) 2 G and LM (Gnew

i

) < ψ(G) (i = 1, ..., N ). Here, we prove

) < ψ(G) only in the case i = I1. (In other cases, proofs are easy.)

From the deﬁnition of Gnew

, we have

∑

I1

∑

I1

I1

X p

= GI1X p

¡ XIi ) =
Gnew
the monomial ψ(G) cancels and we have LT (Gnew
LT (Gnew

= 0. So the term of
) < LT (GI1) = ψ(G). Similarly we have
) < ψ(G) for all i = 1, ..., N . This means ψ(Gnew) < ψ(G) and the proof is ﬁnished.

i=2 LT (GIi )(X p

i=1 LT (GIi)X p

+

I1

I1

Ii

Ii

k

k

i

following n + N number equations f[

From this lemma, the ﬁrst fall degree of the equations system, which consists of the
2 Fp[fXi,jg]1•i•d,1•j•n0 j k = 1, ..., ng [ Sf e, is
¡!
f » exp(n1/3+O(1)),
i is very diﬃcult and its complexity
¡!
f ) is

heuristically 1 + max1•i•n deg[
which is used for solving ECDLP, computation of such G0

(using direct computation) seems to be exponential of n, although computation of wd(
subexponential. 5

i . We also remark that when deg

¡!
f ]

¡!
f ]

k

#

#

3 Weight Theory and precise estimation of ﬁrst fall degree

¡!
F ) and [

¡!
F ]

#
i

∑blogp ec

k=0

ek.

Here, we compute the precise values of the degree of the polynomial deg wd(

¡!
F ¿ pn0¡1, and show
(i = 1, ..., n) of a global polynomial
that the equations system coming from Weil descent have strictly low ﬁrst fall degree. In order

¡!
Xd] satisfying deg

¡!
F 2 Fpn[

¡!
X1, ...,

to develop the strict argument, instead of computing wd(
¡!
¡!
F ) is written by the form pα ¡ 1 6.
m0,

¡!
m1 are some global monomials such that deg(
∑blogp ec

ekpk (0 • ek • p ¡ 1) be a positive integer • pn0¡1. Put its

Deﬁnition 2. Let e =

¡!
m0

¡!
F ), we compute wd(

¡!
m1

¡!
m0

¡!
F ) where

weight by wt(e) :=

For a global variable

monomial

¡!
m =

∏

d
i=1

k=0

¡!
X and positive integer e (• pn0¡1), put wt(
¡!
¡!
ei satisfying 0 • ei • pn0¡1, put wt(
m) :=
Xi

∑

d

¡!
X e) := wt(e) and for a global

i=1 wt(ei).

Further we assume the following assumption of the choice of the base fwig of Fpn/Fp, which
does not lose the generality;

Assumption 2 (choice of the base) n0 £n0 size matrix M := (wpi¡1

j

)1•i,j•n0 is invertible.

Lemma 3. For a monomial
∑

d

i=1 wt(ei).

¡!
m =

∏

d
i=1

¡!
Xi

ei satisfying 0 • ei • pn0¡1, deg(wd(

¡!
m)) =

Proof. It is suﬃcient to show deg(wd(









¡!
Xl

el )) = wt(el). Let el =

∑blogp elc

k=0

el,kpk (0 • el,k • p¡

Y1

...

Yn0

Xl,1

...

Xl,n0

¡!
Xl

el ) ·

∏blogp elc

i=0

1) and



 := M



 . From

¡!
Xl =

∑

n0
j=1 Xl,jwj, we have

¡!
Xl

pi¡1 ·

∑

n0

j=1 Xl,jwpi¡1

j mod

Sf e = Yi and wd(

which is equivalent to logp el • n0¡1.) So, we have degY1,...,Yn0 wd(
el) = degXl,1,...,Xl,n0 wd(
¡!
Xl

invertibility of M , we also get deg wd(

assume wt(el) > deg wd(

el ) = degXl,1,...,Xl,n0 wd(

¡!
Xl

¡!
Xl

el ), substituting Xl,i :=

el ) = wt(el). (Note that
∑

n0

j=1 M ¡1

i,j Yj

Y el,i

i+1 mod Sf e. (Here we use the condition el • pn0¡1
el ) = wt(el) and from the

¡!
Xl
¡!
Xl

el ) and we obtains degY1,...,Yn0 wd(

el ) < wt(el), which is a contradiction. )

¡!
Xl

i seems to be able to recover using Gr¨obner basis computation and under the ﬁrst fall degree

assumption, complexity of the computation is subexponential.

−→
F is not zero, solution(s) of

−→
m

−→
F = 0 equals to the solution(s)

6 Note that if the constant term of
−→
m

−→
F can be used instead of

−→
F = 0 and

of

−→
F .

¡!
Xl

to wd(

5 G0

Lemma 4. For a monomial

such that deg[c

¡!
m]

#

j = wt(

¡!
m) for arbitrary j = 1, ..., n.

¡!
m =

∏

¡!
Xi

d
i=1

ei satisfying 0 • ei • pn0¡1, there is some c 2 F£

pn

Proof. Let c0 ¢ m (c0 2 F£
equals to deg wd(

¡!
m). Take c := c¡1

∑

n

¢

pn, m 2 M on(fXi,jg)) be a certain term of wd(

0

i=1 wi, we have a desired result.

¡!
m) whose degree

Lemma 5. Let α be a positive integer. Then wt(pα ¡ 1) = (p ¡ 1)α and for any x • 2pα ¡
pα¡1 ¡ 2 except x = pα ¡ 1, wt(x) < (p ¡ 1)α.

Proof. trivial.

¡!
F 2 Fpn[

¡!
X1, ...,

¡!
Xd] be a global polynomial satisfying deg

¡!
F ¿ pn0¡1. We ﬁx

¡!
M max =

Let
∏

¡!
Xi

d
i=1

Ei 2 M on(

¡!
F ) such that deg

¡!
M max ‚ deg

¡!
M for any M 2 M on(
¡!
F < 2pα ¡ pα¡1 ¡ 2 • pn0¡1.

¡!
F ). Let α = α(

¡!
F )

¡!

be a positive integer satisfying pα ¡ 1 + deg
From deg
Put H := pα ¡ pα¡1 ¡ deg

¡!
F ¡ 1(> 0), D :=

F ¿ pn0¡1, such α can be take in O(logp deg

∑

d

Let τ 2 Fpn nf

∑

Since τ 62 f

n0

¡!
i=1 xiwi j xi 2 Fpg, and put
m0 :=
i=1 xiwi j xi 2 Fpg, we have the follwing;

n0

∑

i=1 Ei = deg
∏
i=1(

d

¡!
F ).

¡!
F .

¡!
Xi¡τ )pα¡1¡Ei 2 Fpn[

¡!
X1, ...,

¡!
Xd].

Lemma 6. The solutions of the equations system f[
equals to that of f[

i = 0 j1 • i • ng [ ff = 0 jf 2 Sf eg.

¡!
F ]

¡!
m0

#

¡!
F ]

#

i = 0 j1 • i • ng [ ff = 0 jf 2 Sf eg

ei 2 M on(

¡!
F ) and

¡!
m =

¡!
M =

∏

¡!
Xi

∏

d
i=1
d
i=1

Let
¡!
m

¡!
M ) = wt(
¡!
F • 2pα ¡ pα¡1 ¡ 1. From Lemma 5, we have wt(ei + e0

wt(
pα ¡ 1 + deg
¡!
M ) • (p ¡ 1)dα. Further, we study the condition that wt(

i=1 wt(ei + e0

¡!
Xi

i) =

ei+e0

¡!
m

¡!
m

d

i

∑

∏

e0

d
i=1

¡!
Xi
i) and 0 • ei + e0

i 2 M on(

¡!
m0). We remark that
• pα ¡ 1 + (ei ¡ Ei) <
i) • (p ¡ 1)α and
¡!
M ) = (p ¡ 1)dα, which is

i = pα ¡ 1 for all i 2 [1, ..., d]. Since

i=1 pα ¡ 1 ¡ Ei = d(pα ¡ 1) ¡ D, this condition is equivalent to e0

∑

¡!
F =

∑

d

d

i=1 ei • deg

i=1 Ei = D and
i = pα ¡ 1 ¡ Ei
pα¡1¡Ei .) Thus, from Lemma 4,

¡!
Xi

¡!
M =

¡!
M max,

¡!
m =

∏

d
i=1

wt(
equivalent to ei + e0
∑
•

∑

d

d

i=1 e0

i

and ei = Ei (i 2 [1, ..., d]). (i.e,
we obtain the following;

¡!
F ¿ pn0¡1 and let α be a positive integer satisfying pα ¡1+deg

¡!
F <

Lemma 7. Assume deg
2pα ¡ pα¡1 ¡ 2 • pn0¡1. Then we have
¡!
m0 ¢
1) deg wd(
2) There is some c0 2 F£

¡!
F ) = (p ¡ 1)dα.

∏

pn such that deg[c0
¡!
Xi

d
i=1

fi (0 • fi • H). Let
¡!
m ¢

¡!
m0). Then we have wt(

¡!
m1

j = (p ¡ 1)dα for any j = 1, ..., n.
¡!
M =

ei 2 M on(

∏

d
i=1

¡!
Xi
∏

¡!
¡!
m =
F ) and
pα¡1+fi+(ei¡Ei)) and

¡!
M ) = wt(

¡!
Xi

d
i=1

¡!
m1 :=

i 2 M on(

¡!
m0 ¢

¡!
F ]

#

0 • fi + ei + e0
¡!
m1

¡!
m0 ¢

i < pα ¡ 1 + fi + (ei ¡ Ei) • pα ¡ 1 + deg

¡!
M ) • (p ¡ 1)dα form Lemma 5. Thus, from Lemma 4, we obtain the following;

¡!
F + N • 2pα ¡ pα¡1 ¡ 1, we have

wt(

Also put
∏
e0

¡!
Xi

d
i=1

since

¡!
F ¿ pn0¡1 and let α be a positive integer satisfying pα ¡1+deg

¡!
F <

Lemma 8. Assume deg
2pα ¡ pα¡1 ¡ 2 • pn0¡1. Then we have
1) deg wd(
2) For all c 2 F£

m1 ¢ ¡!
m0 ¢
pn , deg[c ¢ ¡!

¡!
F ) • (p ¡ 1)dα.

m1 ¢ ¡!
m0 ¢

¡!
F ]

¡!

#
j

Further put

¡!

F0 := c0 ¢ ¡!

m0 ¢

¡!
F and ai,j,k 2 Fp by wiwj =

∑

n

k=1 ai,j,kwk.

• (p ¡ 1)dα for any j = 1, ..., n.

Lemma 9.

¡!
m1 ¢
[

¡!
F0]

#

k

·

n∑

i=1

[wi ¢ ¡!

m1]

#

k [

¡!
F0]

#

i mod Sf e

(k = 1, ..., n).

∑

Proof. From

∑

∑

=

n

k=1(

n

j=1 ai,j,k[

n

k=1[wi

¡!
m1]

#

k wk = wd(wi
j )wk, we have [wi

#

¡!
m1) =
¡!
m1]

¡!
m1]

n

k=1 wi [

∑

¡!
m1]

#

n

j=1 ai,j,k[

kwk =
¡!
m1]

#

j .

#

k =

∑

∑

n

j=1[

¡!
m1]

#

j wi wj

On the other hands, we have
¡!
m1 ¢

¡!
F0) · wd(

¡!
F0) mod Sf e = wd(

wd(

∑

=

∑

∑

k(

i(

j ai,j,k [

¡!
m1) £ wd(
¡!
F0]

¡!
m1]

j ) [

#

#

i ) wk =

∑

∑

k(

i[wi

¡!
m1) £ wd(

¡!
m1]

#

k [

¡!
F0]

#

i ) wk.

¡!
F0) =

∑

n
i=1

∑

n

j=1[

¡!
m1]

#

j [

¡!
F0]

#

i wiwj

For arbitrary I 2 [1, .., n], since

some integer k(I) 2 [1, ..., n] such that deg[wI
from Lemma 9, we have

¡!
m1 is not constant, and deg wd(wI

¡!
m1) ‚ 1, there exists
‚ 1. So consider the formula obtained

¡!
m1]

#

k(I)

¡!
m1

[

¡!
F0]

#

k(I)

·

n∑

i=1

[wi

¡!
m1]

#

k(I) [

¡!
F0]

#

i mod Sf e.

From Lemma 7 and Lemma 8, we remember deg[
(p ¡ 1)dα, and using Lemma 2, we have the precise estimation of ﬁrst fall degree;

i = (p ¡ 1)dα, 1 • deg[

¡!
F0]

#

¡!
m1

¡!
F0]

#

k(I)

•

Proposition 1. ﬁrst fall degree of the equations system

¡!
F0]

#

k

f[

j k = 1, ..., ng [ Sf e

is estimated by • (p ¡ 1)dα + 1. 7

4 Cost for computing Weil descent

In this section, we estimate the upper bound of the cost for computing wd(
Fpn[

¡!
Xd] is a global polynomial with n0, d ¿ deg

¡!
f ¿ pn0¡1.

¡!
X1, ...,

¡!
f ), where

¡!
f 2

Lemma 11. The number of the monomials of N1 variables with degree • N2 (not consider

ﬁeld equations) is

(

N1 + N2 ¡ 1
N1 ¡ 1

)

(

=

N1 + N2 ¡ 1
N2

)

Let I1 be the number of global monomial 2 M on(
deg

¡!
f + d ¡ 1

is estimated by I1 •

< (deg

¡!
f )d.

(

)

d

¡!
f ). From this lemma and d ¿ deg

¡!
f , I1

Lemma 12. Let
I2 • (p ¡ 1) d (logp deg

¡!
f + 1).

¡!
M 2 M on(

¡!
f ) and let I2 be the upper bound of the degree of wd(

¡!
M ). Then,

Proof. Put
∑

¡!
M =

∏ ¡!
Xi

ei. Remark that ei • deg

d

i=1 wt(ei) • (p ¡ 1) d maxi(blogpei + 1c) • (p ¡ 1) d (deg

¡!
f and logp ei • logp deg

¡!
M ) =
¡!
f + 1) where blogpei + 1c is the

¡!
f , we have wd(

p-adic digits of ei.

7 Note that

−→
m1 can be take degree 1 global monomial

Let I3 be the number of local monomials 2 F[fXi,jg] with degree • I2. From Lemma 11,

)

(

and from deg

f ¿ pn0¡1, we have I2 ¿ n0d and I3 • (n0d)I2.

¡!

I3 =

I2 + n0d ¡ 1
I2

¡!
f ). Since wd(

¡!
f ) =

∑

¡!
M 2M on(

¡!
f )

wd(

¡!
M ), I4 = I1£

Let I4 be the cost of computing wd(

¡!
M ). Since the cost of computing the product of two polynomials with

cost of computing wd(
degree • I2 is I 2
3 and computation of wd(
of polynomials of degree • I2, cost of computing wd(
following;

¡!
M ) which consists of at most I2 times multiplication
3 and the

¡!
M ) is estimated by • I2 I 2

¡!
X1, ...,

¡!
f 2 Fpn[

¡!
Xd] be a global polynomial with n0, d ¿ deg

¡!
f ¿ pn0¡1, and
Lemma 13. Let
let I1, ..., I4 be the complexities, which appears in the previous sentence. Then I4 • I1 £I2 £I 2
3 .
Further, we estimate the cost of computing discrete logarithm of elliptic curve E/Fpn . In
elliptic curve case, we take d = O(n1/3), n0 = O(n2/3) and we try to decompose arbitrary P0 2
¡¡!
E(Fpn ) into d- decomposed factor 2 DF . So, we must take
SemP0 whose degree < 2d.
¡!
F ) •
Since d = O(n1/3), α = α(
F0 ¿ pn0¡1 holds. Each complexities
2pα ¡ pα¡1 ¡ 2 < 2d+O(1) and the condition n0, d ¿ deg
are estimated by I1 • 2d2+O(1)d = O(exp(n2/3+o(1))), I2 • O(d(d + O(1))) • O(n2/3+o(1)),
I3 • (n0d)I2 = O(exp(n2/3+o(1))), and I4 • I1 £ I2 £ I 2
3 = O(exp(n2/3+o(1))). On the other
hands from Proposition 1, ﬁrst fall degree of the equation system f[
j k = 1, ..., ng [ Sf e is
Df f • I2 +1 If we assume the ﬁrst fall degree assumption 1, from Lemma 1, the cost of solving
this equations system also O(exp(n2/3+o(1))). So, the total cost of solving discrete logarithm
of E(Fpn ), which consists of #DF = O(n2/3) times decompositions and #DF £ #DF size
linear algebra computations is also O(exp(n2/3+o(1))). Thus we have the following;

¡!
F ) can be taken α = logp 2d + O(1) and deg

¡!
F0 = deg(c

¡!
F :=

¡!
F0]

¡!
m0

¡!

k

#

Theorem 1. Under the ﬁrst fall degree assumption 1, the cost of solving discrete logarithm of
E(Fpn ) where p is a small prime number (or a power of prime number) is O(exp(n2/3+o(1)))
when n ! 1.

Further, we estimate the cost of computing discrete logarithm of Jacobian of a curve
C/Fpn of small constant genus g. In this case, we also take d = O(g ¢ n1/3) = O(n1/3),
n0 = O(n2/3) and we try to decompose arbitrary D0 2 Jac(C/Fpn) into d- decomposed
¡¡¡!
factor 2 DF . In the author [6], there is a set of global polynomials
FD0,g such that
¡¡¡!
FD0,i < C d (C:some constant) the decomposition problem reduces to solving equations
j1 • i • g, 1 • j • ng and ﬁeld equations. By using similar trick, which use

deg
system f[
¡¡¡!
¡!
¡¡!
mi,0 such that the decomposition
mi,0
FD0,i instead of
problem also reduces to solving equations system f[
j1 • i • g, 1 • j • ng and
ﬁeld equations and its ﬁrst fall degree can be estimated • O(n2/3+O(1)). So, we similarly have
the following;

¡¡¡!
FD0,i, there exists some monomials
¡!
mi,0

¡¡¡!
FD0,1, ...,

¡¡¡!
FD0,i]

¡¡¡!
FD0,i]

#
j

#
j

Theorem 2. Under the ﬁrst fall degree assumption 1, the cost of solving discrete logarithm
of Jac(C/Fpn) of small genus g, where p is a small prime number (or a power of prime
number), is O(exp(n2/3+o(1))) when n ! 1.

Acknowledgement The author would like to have great thanks to Professor Kazuto Matsuo
in Kanagawa University, to whom the author makes many times fruitful discussions from
when the author starts this research and Professor Tsuyoshi Takagi in Kyushu University,
who teaches recent trend of researches and points out many mistakes.

References

1. C. Diem, On the discrete logarithm problem in class groups II, preprint, 2011.

2. J-C. Faug´ere, L. Perret, C. Petit, and G. Renault, Improving the complexity of index calculus
algorithms in elliptic curves over binary ﬁelds, EUROCRYPTO 2012, LNCS 7237, pp.27-44.

3. F.S. Macaulay, The algebraic Theory of modular systems, 1916, Cambridge.
4. K. Nagao, Index calculus for Jacobian of hyperelliptic curve of small genus using two large primes,

Japan Journal of Industrial and Applied Mathematics, 24, no.3, 2007.

5. K. Nagao, Decomposition Attack for the Jacobian of a Hyperelliptic Curve over an Extension
Field, 9th International Symposium,ANTS-IX., Nancy, France, July 2010, Proceedings LNCS
6197,Springer, pp.285–300, 2010.

6. K. Nagao, Decomposition formula of the Jacobian group of plane curve, draft, 2013.
7. C. Petit and J-J. Quisquater. On Polynomial Systems Arising from a Weil Descent, Asiacrypt

2012, Springer LNCS 7658, Springer, pp.451-466.

8. I. Semaev. Summation polynomials and the discrete logarithm problem on elliptic curves. Preprint,

2004.

