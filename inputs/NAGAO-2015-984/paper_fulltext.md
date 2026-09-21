<!--
Extracted from inputs/NAGAO-2015-984/eprint-2015-984.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao.

NOT hand-cleaned. Ligature and math artifacts from the PDF's fonts are left as
the extractor produced them: `fi`/`ff`/`fl` ligatures, `Gr¨obner`, `⁄=` for the
non-equality sign in Definition 5, and superscripts and summation limits
flattened onto the baseline (so displayed formulas break across lines).

Section, equation, definition, lemma, proposition and theorem numbers below are
the paper's own and are the citable anchors. The load-bearing ones for this
program:

  Definition 2  EQS1(m,R) -- Semaev's chained S_3 system, m-1 links
  Definition 4  EQS2(m,R) -- its Weil descent, n(m-1) variables
  Definition 5  first fall degree d_F, the TRUE definition
  Definition 6  FAKE first fall degree d'_F, reduced mod the field equations
  Assumption 1  degree in the F4 computation is <= d_F  (Nagao's numbering)
  Lemma 3/4     d_F <= d'_F, so the fake version is a safe upper bound
  Lemma 6       first fall degree of a Weil descent is <= (p-1)n + deg F
  Prop. 2       d_F(EQS2) <= 4 (p = 2), <= 3p+1 (p >= 3)
  Section 7     DISJOINT (coset) factor base: Fb_i = {P : x(P) in V + v_i}
  Definition 7  EQS3(m,R) -- the chained system over disjoint cosets
  Definition 8  EQS4(m,R) -- its Weil descent
  Prop. 5       d_F(EQS4) <= 4 (p = 2), <= 3p+1 (p >= 3), stated with the
                proof OMITTED ("the situation is the same as the Semaev's
                case"). This is the paper's load-bearing unproven step.
  Theorem 1     under the first fall degree assumption, ECDLP over F_{p^n}
                costs O(n^{8w+1}) for p = 2 and O(n^{(6p+2)w+1}) for p >= 3

Reference [14] of this paper is Semaev ePrint 2015/310, frozen at
inputs/SEMAEV-2015-310/. Reference [5] is Galbraith-Gebregiyorgis ePrint
2014/806. Section 7's opening sentence credits the disjoint factor base to the
author's own [10] (ePrint 2013/548) and says [5] re-discovered it.
-->

Complexity of ECDLP under the First Fall Degree
Assumption (Draft)

Koh-ichi Nagao (nagao@kanto-gakuin.ac.jp)

Faculty of Science and Engineering, Kanto Gakuin Univ.,

Abstract. Semaev [14] shows that under the ﬁrst fall degree assumption, the complex-
ity of ECDLP over F2n , where n is the input size, is O(2n1/2+o(1)
). In his manuscript,
the cost for solving equations system is O((nm)4w), where m (2 ≤ m ≤ n) is the num-
ber of decomposition and w ∼ 2.7 is the linear algebra constant. It is remarkable that
the cost for solving equations system under the ﬁrst fall degree assumption, is poly in
input size n. He uses normal factor base and the revalance of ”Probability that the
decomposition success” and ”size of factor base” is done.
Here, using disjoint factor base to his method, ”Probability that the decomposition
success becomes ∼ 1 and taking the very small size factor base is useful for complexity
point of view. Thus we have the result that states
”Under the ﬁrst fall degree assumption, the cost of ECDLP over F2n , where n is the
input size, is O(n8w+1).”
Moreover, using the authors results in [11], in the case of the ﬁeld characteristic ≥ 3,
the ﬁrst fall degree of desired equation system is estimated by ≤ 3p + 1. (In p = 2 case,
Semaev shows it is ≤ 4. But it is exceptional.) So we have similar result that states
”Under the ﬁrst fall degree assumption, the cost of ECDLP over Fpn , where n is the
input size and (small) p is a constant, is O(n(6p+2)w+1). ”

1 Notation

Let p be a prime and

E/Fpn : y2 + a1xy + a3y − x3 − a2x2 − a4x − a6 = 0

be an elliptic curve. Here, we discuss the complexity of ECDLP considering extension degree
n being input size.

Problem 1 ((ECDLP)) Let P, Q ∈ E(Fq) such that < P >(cid:51) Q. ECDLP is the problem
ﬁnding integer N satisfying Q = N P .

Petit et al. [12] shows that when p = 2 under the ﬁrst fall degree assumption, it is in
O(n2/3+o(1)). The author [11] shows this result can be generalized in the case p ≥ 3. Recently,
many researchers [6] [14] propose the method using 3 terms Semaev’s formula. In [14], Semaev
shows that when p = 2 under the ﬁrst fall degree assumption, it is in O(n1/2+o(1)).

Throughout this paper, we ﬁx {α1, ..., αn} (αi ∈ Fpn) by the base of vector space Fpn /Fp

and put

V = V (k) := {

k(cid:88)

i=1

xiαi | xi ∈ Fp}

by k dimension vector space in Fpn.

2 Semaev’s formula

Here, we deﬁne the Semaev formula [13] and show its property.

Deﬁnition 1. In the case p = 2. Let

E/F2n : y2 + xy = x3 + Ax2 + B

(A, B ∈ F2n ).

Put

S2(x1, x2) := x1 − x2,

S3(x1, x2, x3) := (x1x2 + x1x3 + x2x3)2 + x1x2x3 + B, and

Sm(x1, ., xm) := Resx(Sm−j(x1, ..., xm−j−1, x), Sj(xm−j, ..., xm, x))

recursively.

In the case p ≥ 3. Let

Put

E/Fpn : y2 = x3 + A4x + A6

(A4, A6 ∈ Fpn ).

S2(x1, x2) := x1 − x2,

S3(x1, x2, x3) := (x1 −x2)2x2

3 −2((x1 +x2)(x1x2 +A4)+2A6)x3 +(x1x2 −A4)2 −4A6x1x2, and

Sm(x1, ., xm) := Resx(Sm−j(x1, ..., xm−j−1, x), Sj(xm−j, ..., xm, x))

recursively.

Proposition 1 (Semaev [13]). The following two conditions are equivalent;
1) There exists some P1, ..., Pm ∈ E(Fpn)\{∞} such that P1 + ... + Pm = 0.
2) Sm(x(P1), ..., x(Pm)) = 0.

3 Index Calculus of ECDLP

Here, we remember the Index Calculus algorithm of ECDLP [1]. Recall

k(cid:88)

V = {

i=1

xiαi | xi ∈ Fp}

is k dimension vector space in Fpn and put factor base F b by

F b := {P ∈ E(Fpn) | x(P ) ∈ V }.

In the index calculus, random element R(∈ E(Fpn)) is decomposed into m elements in F b,
i.e,. R is decomposed by R = P1 + ..., +Pm for some Pi ∈ F b. This process reduces to solving
some equations system and if we take parameter k, m as km ∼ n, the probability that the
decomposition success is 1/m!.

4 Decomposition using S3

Here, we describe the method for the Decomposition using S3 ([6], [14]), which decompose
R ∈ E(Fpn) into m elements P1, ..., Pm ∈ F b.

Deﬁnition 2 (EQS1). EQS1(m,R) consists of the m − 1 equations

S3(X1, X2, U1) = 0, S3(U1, X3, U2) = 0, ..., S3(Um−3, Xm−1, Um−2) = 0, S3(Um−2, Xm, x(R)) = 0,

where variables Xi moves in V and Ui in Fpn.

Algorithm 1 Index Calculus algorithm of ECDLP [1]

Input: E/Fpn elliptic curve, P, Q ∈ E(Fq) st. < P >(cid:51) Q
Output: Integer N satisfying N P = Q
Set parameter k, m satisfying km ∼ n
Put V = {
Put F b := {P ∈ E(Fpn ) | x(P ) ∈ V }
Decompose step:i := 0, {PB1, ..., PB#F b} := F b
while i ≤ #F b do

i=1 xiαi | xi ∈ Fp}

Pk

n1, n2 ← random integer, Put R := n1P + n2Q
if R is written by the sum of m elements in F b,
i.e., R =

j=1 ajPBj (aj = 0 or 1,#{j|aj = 1} = m) then
i + +,Put ni,1 := n1, ni,2 := n2, ai,j := aj (j = 1, .., #F b)

P#F b

Linear algebra step:
for all i = 1, ..., #F b + 1 do

Put −→p i := (ai,1, ..., ai,#F b)

Find b1, ..., b#F b+1 ∈ Z/#E(Fpn )Z st.
Computation of ECDLP:
P#F b+1
Return −

P#F b+1

bini,1/

i=1

i=1

P#F b+1

i=1

−→pi ≡

bi

−→
0 mod #E(Fpn )

bini,2 mod #E(Fpn )

In order for solving EQS1, we consider its Weil descent. So, for a while, we describe the

deﬁnition of Weil descent.

Deﬁnition 3 (Weil descent). Let F = F (X1, ..., XN ) ∈ Fpn[X1, ..., XN ], −→v = (v1, ..., vN ) ∈
AN (Fpn) 1 and j1, ..., jN be some integers ≤ n. 2 We describe the set of new variables Xij
(1 ≤ i ≤ N, 1 ≤ j ≤ ji). Put the set of ﬁeld equations by

Sf e := {X p

ij − Xij | 1 ≤ i ≤ N, 1 ≤ j ≤ ji}.

The polynomials F ↓

j = F ↓

−→v ,j (∈ Fp[{Xij}], 1 ≤ j ≤ n) is deﬁned as follows; 3

n(cid:88)

j=1

F ↓

−→v ,j × αj = F (v1 +

j1(cid:88)

j=1

x1jαj, ..., vN +

jN(cid:88)

j=N

xN jαj) mod Sf e.

Deﬁnition 4 (EQS2). EQS2(m,R) is the equations system obtained by Weil descent (taking
v1 = ... = vN = 0) from each equations of EQS1(m,R) and ﬁeld equations.
i,e., EQS2(m,R) := {F ↓

| 1 ≤ j ≤ n, F ∈ EQS1(m,R)} ∪ Sf e.

−→
0 ,j

Remark that EQS2(m,R) consists of n(m − 1) variables, n(m − 1) degree 4 polynomials
(when p = 2 degree 3 polynomials can be taken) coming from the Weil descent of S3 and
n(m − 1) degree p ﬁeld equations.

Let P1, ..., Pm ∈ F b such that P1 + ... + Pm = R. Then we see easily EQS1m,R have

solution

(X1, ..., U1, ...) = (x1, ...u1, ...) ∈ A2m−2(Fpn)

such that xi = x(Pi) (i = 1, ..., m).

1 Here, we take −→v =

−→
0 . Latter we will consider disjoint factor base and at this time, the values

v1, ..., vN must be needed.

2 Here, j1 = ... = jN = dimFp V = k.
3 Strictly saying, we must deﬁne F ↓

j1, ..., jN must be needed in the deﬁnition of Weil descent. However, in this paper, j1 = ... = jN =
dimFp V = k and it is ﬁxed. So we simply omit this term in the deﬁnition.

j = F ↓

−→v ,

−→
J ,j

, where

−→
J = (j1, ..., JN ), since not only v1, ..., vN ,

Lemma 1 (Semaev [14]). Let x1, ..., xm ∈ V and u1, ..., um−2 ∈ Fpn. Suppose

(X1, ..., U1, ...) = (x1, ...u1, ...) ∈ A2m−2(Fpn)

is a solution of EQS1(m,R). Then we have the following;
1) There exists P1, ..., Pm ∈ E(F2n) such that

P1 + .. + Pm = R, x(P1) = x1, ..., x(Pm) = xm.

2) Such P1, .., Pm can be recovered from the solution of EQS1(m,R).
3) Put S := {P | P ∈ {P1, ..., Pm} ∩ E(Fpn)}. So, there exists some 2-torsion T ∈ E(Fpn)[2]
satisfying
(Note #S ≤ m. From 1), T = ∞ when #S = m.)

P ∈S P + T = R.

(cid:80)

From this Lemma, the decomposition of R reduces to solving EQS1(m,R) and solving

EQS2(m,R).

Semaev treats the case km ∼ n and we will suppose km ∼ n. Note that #F B ∼ #V = pk
and the Probability that the element in E(Fpn) is written by the form P1 + ... + Pm (Pi ∈ F b)
is estimated by

(#F b)m

m!

·

1

#E(Fpn)

∼

(pk)m

(m!) · pn ∼

1

m!

.

On the other hands, Probability that the element in E(Fpn) is written by the form P1 +

... + Pt + T (Pi ∈ F b, t < m, T ∈ E(Fpn)[2]\{∞}) is estimated by

3

(#F b)t

t!

·

1

#E(Fpn)

∼ 3

(pk)t

(t!) · pn ∼ 3

1

pk(m−t)t!

(cid:191)

1

m!

.

So the probability that R is written by R = P1 + ... + Pt + T for some t(< m) and T ∈
E(Fpn)[2]\{∞} is very small and negligible. Thus, further, we assume that R is written by
R = P1 + ... + Pm (Pi ∈ F b) and exceed the discussion.

5 First fall degree assumption

Deﬁnition 5 (First fall degree). Let K be a ﬁeld and f1, ..., fM ∈ K[X1, ..., XN ]. First
fall degree of {f1, ..., fM } is the minimal integer dF satisfying the following.
There exists g1, ..., gM ∈ K[X1, ..., XN ] such that
1) maxi{deg gifi} ≥ dF ,
i=1 gifi) < dF ,
2) deg(
(cid:80)M

(cid:80)M

3)

i=1 gifi (cid:54)= 0.

Under the following assumption, the algorithm for solving ECDLP in sub-exponential

complexity are proposed [12], [11], [14].

Assumption 1 {f1, ..., fM } Degree of the polynomial appears in the Gr¨obner basis compu-
tation (by F4 algorithm) of {f1, ..., fM } is ≤ dF .

From this assumption, the number of the monomial appears in the Gr¨obner basis compu-

tation is ≤ O(N dF ) So, we have the following;

Lemma 2. The complexity of Gr¨obner basis computation (by F4 algorithm) of {f1, ..., fM }
is ≤ O(N dF w), where w ∼ 2.7 is the linear algebra constant.

Many researchers misunderstand the deﬁnition of ﬁrst fall degree and use this assumption

and estimation of the complexity using the following FAKE version.

Deﬁnition 6 (Fake ﬁrst fall degree). Let f1, ..., fM ∈ Fp[X1, ..., XN ] and let Sf e := {X p
i −
Xi | 1 ≤ i ≤ N } be the set of ﬁeld equations Fake ﬁrst fall degree of {f1, ..., fM } ∪ Sf e is the
minimal integer d(cid:48)

F satisfying the following.

There exists g1, ..., gM ∈ K[X1, ..., XN ] such that

1) maxi{deg gifi mod Sf e} ≥ dF ,
i=1 gifi mod Sf e) < dF ,
2) deg(
(cid:80)M

(cid:80)M

i=1 gifi (cid:54)≡ 0 mod Sf e.

3)

(cid:80)n

In [14], Semaev says from the equation S3(x, u, RX ) = 0, where x =

i=1 xiαi u =
i=1 uiαi and RX ∈ Fpn , the relations of low ﬁrst degree do not appears. Considering
F ≤ 4. He uses

xuS3(x, u, RX ), one can easily have the relation that its Fake ﬁrst fall degree d(cid:48)
the true deﬁnition of ﬁrst fall degree.

In [11], the author shows the following lemma and it has no problem to use Fake ﬁrst fall

degree instead of use true ﬁrst fall degree.

(cid:80)k

Lemma 3 ([11]). Let F = F (X1, ..., XN ) be a polynomial in Fp[X1, .., XN ] such that F ≡
i − Xi). So,
0 mod Sf e. i.e., There are f1, ..., fM ∈ Fp[X1, .., XN ] such that F :=
there are some polynomials f new
i −
Xi) and deg f new

M ∈ Fp[X1, .., XN ] satisfying F :=

≤ deg F − p (i = 1, ..., N ).

i=1 fi · (X p
(cid:80)N

i=1 f new

, ..., f new

· (X p

(cid:80)N

1

i

i

Example 1 Let X, Y, Z are variables moves in F2. Note that the set of ﬁeld equations is
written by Sf e = {X 2 + X, Y 2 + Y, Z 2 + Z}.
Let F = (X 2 + X)(Y 2 + Y ) + (X 2 + X)(Y 2 + Z) ∈ F2[X, Y, Z]. From its construction,
F ≡ 0 mod Sf e and expanding the formula, we have F = X 2Y +Y 2Z +Y Z +X 2Z +XY 2+XZ
and deg F = 3.

F can be transformed by F = (X 2 + X)(Y 2 + Y ) + (X 2 + X)(Y 2 + Z)

= (X 2 + X)(Y 2 + Y ) + (X 2 + X)(Y 2 + Y ) + (X 2 + X)(Y 2 + Y ) + (X 2 + X)(Y 2 + Z)
= (X + Z)(Y 2 + Y ) + (X 2 + X)(Y + Z), and F can be written by the sum of smaller degree
polynomials, which are divided by a certain ﬁeld equation.

Proof of this Lemma is complicated and not constructive.
From this lemma, we have the following:

Lemma 4. Let f1, ..., fM ∈ Fp[X1, ..., XN ]. Put dF by the ﬁrst fall degree of {f1, ..., fM } and
put d(cid:48)

F by the Fake ﬁrst fall degree of {f1, ..., fM } ∪ Sf e. Then dF ≤ d(cid:48)

F .

Now, we will estimate the ﬁrst fall degree of EQS2(m,R) in case of p ≥ 3. For this purpose,

we prepare the following

Lemma 5 (Also the author ’s result in [11]). Let F = F (X1, ..., XN ) be a polynomial
in Fp[X1, .., XN ] and let m = m(X1, ..., XN ) be a monomial in Fp[X1, .., XN ]. Then we have

[m · F ]↓

j ≡

n(cid:88)

i=1

[αi · m]↓

j [F ]↓

i mod Sf e

(j = 1, ..., n).

Lemma 6. Let F = F (X1, ..., Xn) be a polynomial in Fpn[X1, .., Xn]. The ﬁrst fall degree of
the equations system {F ↓
j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} ∪ Sf e is heuristically ≤ (p − 1)n + deg F .

Proof. Put m = m(X1, ..., Xn) = X p−1

1

· · · X p−1

n

. From Lemma 5, we have

[m · F ]↓

j mod Sf e ≡

n(cid:88)

i=1

[αi · m]↓

j [F ]↓

i mod Sf e

(j = 1, ..., n).

From ﬁeld equation, deg([m · F ]↓
deg[αi · m]↓

j is heuristically = (p − 1)n and deg[F ]↓

j mod Sf e) is ≤ (p − 1)n + deg F − 1. On the other hands,
i is also heuristically = deg F . 4 Thus the

4 We use heuristic argument only here.

Fake ﬁrst fall degree of {F ↓
from Lemma 4, we have this lemma.

j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} is bounded by ≤ (p − 1)n + deg F and

From this proposition, we have the following:

Proposition 2 (Semaev [14] and its generalization to p ≥ 3). First fall degree of
EQS2(m,R)

5 is bounded by

(cid:189)

4
3p + 1

(p = 2)
(p ≥ 3)

.

From this proposition and Lemma 2, we can estimate the complexity:

Proposition 3 (Semaev [14] and its generalization to p ≥ 3). Under the ﬁrst fall degree
assumption, the complexity of solving EQS2(m,R) is bounded by

(cid:189)

O((nm)4w)
(p = 2)
O((nm)(3p+1)w (p ≥ 3)

.

6 Complexity estimation by Semaev

Here, we adopt the easy and rough estimation. For this reason, the complexity of input size
n is written by the form O(exp(nα+o(1))), where limn→∞ o(1) = 0. Many complicated terms
are included into the o(1) term and so for normal size input n, o(1) has HUGE value although
limn→∞ o(1) = 0.

Semaev considers the case m ∼ n1/2+o(1) then k is taken k ∼ n

m = n1/2+o(1). Then we

have
1) #F b ∼ pk = pn1/2+o(1)
2) The probability that decomposition success = 1

= O(exp(n1/2+o(1))),

m! ∼

O(exp(n1/2+o(1))) ,

1

3) The complexity of ”Decompose step” = #F b× cost of solving EQS2
4) The complexity of ”linear algebra step” = (#F B)w = O(exp(n1/2+o(1))) (w ∼ 2.7 linear
algebra constant).

= O(exp(n1/2+o(1)))

Probability

Thus we have the following;

Proposition 4 (Semaev [14] and its generalization to p ≥ 3). Under the ﬁrst fall
degree assumption, the complexity of solving ECDLP for an elliptic curve E/Fpn is estimated
by O(exp(n1/2+o(1))).

7 Disjoint factor base

The idea of using disjoint factor base is known by [10] and recently re-discovered by [5].

i=1 xiαi | xi ∈ Fp} be a dimension k vector space in Fpn and m, k be the

Recall V = {
parameter mk ∼ n.

(cid:80)k

Let v1, ..., vm be elements in Fpn such that all V + vi (i = 1, ..., m) are disjoint. Put

Vi := V + vi

(i = 1, ..., m),

F bi := {P (∈ E(Fpn)) |x(P ) ∈ Vi}

(i = 1, ..., m),

F b := ∪m

i=1F Bi, and

consider the decomposition of R(∈ E(Fpn)) by

R = P1 + ... + Pm

(Pi ∈ F bi)

and the index calculus whose factor base is F b.

Note that #F bi ∼ #Vi = #V ∼ pk, #F b ∼ m · pk.
Using the similar argument in §2, the decomposition reduces to solving the following

equations system

5 Assume Sf e ⊆ EQS2(m,R)

Deﬁnition 7 (EQS3). EQS3(m,R) consists of the m − 1 equations

S3(X1, X2, U1) = 0, S3(U1, X3, U2) = 0, ..., S3(Um−3, Xm−1, Um−2) = 0, S3(Um−2, Xm, x(R)) = 0,

where variables Xi moves in Vi and Ui in Fpn.

Substituting Xi = vi +

j=1 Xijαj and Ui =
EQS3(m,R) and the equations in Fp[{Xij}] are obtained from Weil descent process.

j=1 X(m+i)jαj to the equations in

(cid:80)k

(cid:80)n

Deﬁnition 8 (EQS4). EQS4(m,R) is the equations system obtained by Weil descent from
each equations in EQS3(m,R) and ﬁeld equations.
i,e., EQS4(m,R) := {F ↓

−→v ,j | 1 ≤ j ≤ n, F ∈ EQS3(m,R)} ∪ Sf e where −→v = (v1, .., vN ).

Similarly, solving EQS3 reduces to solving EQS4 and its complexity is estimated as

follows; 6

Proposition 5. First fall degree of EQS4(m,R) is bounded by

(cid:189)

4
3p + 1

(p = 2)
(p ≥ 3)

.

Proposition 6. Under the ﬁrst fall degree assumption, the complexity of solving EQS4(m,R)
is bounded by

(cid:189)

O((nm)4w)
O((nm)(3p+1)w)

(p = 2)
(p ≥ 3)

.

(cid:81)m

The diﬀerence between using normal factor base and disjoint factor base is the probability
that decomposition success. The number of the elements in E(Fpn) written by the form
i=1 #F bi ∼ (pk)m ∼ pk ∼ #E(Fpn ). So, the probability that
P1 + ... + Pm (Pi ∈ F bi) is
decomposition success, is O(1). On the other hands, the size of all factor base ∪F bi became
m times large. However, it is not heavy problem.

Now ﬁx k = C0 be a small natural number and put the parameter m ∼ n

. Then we
i=1 #F bi ∼ (pk)m ∼ pn. (Note: if one takes k = 1, it sometimes happens #F bi = ∅
have
i=1 #F bi ∼ pn, we choose suitable
for some i. To avoid such case and conﬁrm the relation
constant C0.) From m ∼ n
· n = O(n). So from Lemma 6,
since we must collect #F b + 1 decompositions, the cost of ”decompose step” is estimated by

, one has #F b ∼ m · pk = pC0

k = n

(cid:81)m

(cid:81)m

C0

C0

C0

(cid:40)

(nm)4w · pC
(nm)(3p+1)w · pC

C0

0

0

n = (n n

C0

)4w · pC

0

C0

n = (n n

C0

C0

)(3p+1)w · pC

0

C0

n = O(n8w+1)

(p = 2)

n = O(n(6p+2)w+1)

(p ≥ 3)

.

The complexity of linear algebra step is (#F b)w ∼ (n · pC0
Thus we have the following theorem:

C0

)w = O(nw) and very very small.

Theorem 1. Under the ﬁrst fall degree assumption, the complexity of solving ECDLP for an
elliptic curve E/Fpn is estimated by

(cid:189)

O(n8w+1)
O(n(6p+2)w+1)

(p = 2)
(p ≥ 3)

.

Acknowledgement I would like to have great thanks to Professor Kazuto Matsuo in Kana-
gawa University for useful advices and coments.

6 The situation is the same as the Semaev’s case. So, we omit the proof.

Algorithm 2 Index Calculus algorithm of ECDLP using dis joint factor base

Pk

Input: E/Fpn elliptic curve, P, Q ∈ E(Fq) st. < P >(cid:51) Q
Output: Integer N satisfying N P = Q
Set parameter k, m satisfying km ∼ n
Put V = {
i=1 xiαi | xi ∈ Fp}
Put v1, ..., vm ∈ Fpn st. V + vi are disjoint
Put Vi := V + vi,
Put F bi := {P ∈ E(Fpn ) | x(P ) ∈ V }
Put F b := ∪m
Decompose step:i := 0, {PB1, ..., PB#F b} := F b
while i ≤ #F b do

i=1F bi

n1, n2 ← random integer, Put R := n1P + n2Q
if R is written by the sum P1 + ... + Pm for Pi ∈ F bi, then

Put aj by R =
i + +,Put ni,1 := n1, ni,2 := n2, ai,j := aj (j = 1, .., #F b)

j=1 ajPBj (aj = 0 or 1,#{j|aj = 1} = m)

P#F b

Linear algebra step:
for all i = 1, ..., #F b + 1 do

Put −→p i := (ai,1, ..., ai,#F b)

Find b1, ..., b#F b+1 ∈ Z/#E(Fpn )Z st.
Computation of ECDLP:
P#F b+1
Return −

P#F b+1

bini,1/

i=1

i=1

P#F b+1

i=1

−→pi ≡

bi

−→
0 mod #E(Fpn )

bini,2 mod #E(Fpn )

References

1. P.Gaudry, An algorithm for solving the discrete log problem on hyperelliptic curves, Eurocrypt

2000, LNCS 1807, Springer-Verlag, 2000, pp. 19–34.

2. J. Ding, J. Buchmann, M. Mohamed, W. Mohamed and R-P Weinmann, MutantXL,

http://www.academia.edu/2863459/Jintai_Ding_Johannes_Buchmann_Mohamed_Saied_Emam_Mohamed

3. N. Courtois, A. Klimov, J. Patarin, and A. Shamir. Eﬀcient Algorithms for Solving Over deﬁned
Systems of Multivariate Polynomial Equations. In Proceedings of International Conference on the
Theory and Application of Cryptographic Tech- niques(EUROCRYPT), volume 1807 of Lecture
Notes in Computer Science, pages 392–407, Bruges, Belgium, May 2000. Springer.

4. J-C. Faug´ere, L. Perret, C. Petit, and G. Renault, Improving the complexity of index calculus
algorithms in elliptic curves over binary ﬁelds, EUROCRYPTO 2012, LNCS 7237, pp.27-44.
5. S. Galbraith and S.Gebregiyorgis, Summation polynomial algorithms for elliptic curves in charac-

teristic two, https://eprint.iacr.org/2014/806

6. Y. Huang, C. Petit, N. Shinohara, and T. Takagi, On Generalized First Fall Degree Assumptions,

https://eprint.iacr.org/2015/358

7. M. Kosters, NOTES ON SUMMATION POLYNOMIALS,

http://arxiv.org/pdf/1503.08001.pdf 2015.

8. K. Nagao, Index calculus for Jacobian of hyperelliptic curve of small genus using two large primes,

Japan Journal of Industrial and Applied Mathematics, 24, no.3, 2007.

9. K. Nagao, Decomposition Attack for the Jacobian of a Hyperelliptic Curve over an Extension
Field, 9th International Symposium,ANTS-IX., Nancy, France, July 2010, Proceedings LNCS
6197,Springer, pp.285–300, 2010.

10. K. Nagao, Decomposition formula of the Jacobian group of plane curve,

https://eprint.iacr.org/2013/548

11. K. Nagao, Equations System coming from Weil descent and subexponential attack for algebraic

curve cryptosystem, https://eprint.iacr.org/2013/549

12. C. Petit and J-J. Quisquater. On Polynomial Systems Arising from a Weil Descent, Asiacrypt

2012, Springer LNCS 7658, Springer, pp.451-466.

13. I. Semaev. Summation polynomials and the discrete logarithm problem on elliptic curves.

14. I. Semaev, New algorithm for the discrete logarithm problem on elliptic curves,

https://eprint.iacr.org/2004/031.pdf

https://eprint.iacr.org/2015/310.pdf

