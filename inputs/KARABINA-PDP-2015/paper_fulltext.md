<!--
Extracted with `pdftotext -layout` from inputs/KARABINA-PDP-2015/eprint-2015-319-v3.pdf
(sha256 in the .sha256 sidecar) on 2026-09-05. Derivative text extraction,
vendored under the paper's CC BY 4.0 license (https://creativecommons.org/licenses/by/4.0/).
Page-break artifacts and running headers/footers from the PDF layout are left
as pdftotext produced them; not hand-cleaned beyond this note.
-->

    Point Decomposition Problem in Binary Elliptic
                       Curves

                                      Koray Karabina

                 Florida Atlantic University, Boca Raton, FL, 33433, USA,
                                    kkarabina@fau.edu



      Abstract. We analyze the point decomposition problem (PDP) in binary elliptic
      curves. It is known that PDP in an elliptic curve group can be reduced to solving
      a particular system of multivariate non-linear system of equations derived from
      the so called Semaev summation polynomials. We modify the underlying system
      of equations by introducing some auxiliary variables. We argue that the trade-off
      between lowering the degree of Semaev polynomials and increasing the number of
      variables provides a significant speed-up.

      Keywords: Semaev polynomials, elliptic curves, point decomposition problem,
      discrete logarithm problem


1   Introduction

The point decomposition problem (PDP) in an additive abelian group G with respect to
a factor base B ⊂ G is the following: Given a point1 R ∈ G, find Pi ∈ B such that
                                              m
                                              X
                                         R=         Pi
                                              i=1

for some positive integer m; or conclude that R cannot be decomposed as a sum of points
in B. The discrete logarithm problem (DLP) in G with respect to a base P ∈ G is the
following: Given P and Q = aP ∈ G for some secret integer a, compute a. DLP can be
solved using the index calculus algorithm in two main steps. In the relation collection
step, fix a factor base B, and find a set of points Ri = ai P + bi Q for some randomly
chosen integers ai , bi , such that Ri can be decomposed with respect to B, i.e.,
                                          X
                                    Ri =     Pij , Pij ∈ B.
                                          j

Here, we may assume for convenience that Pij are not necessarily distinct. Note that each
decomposition induces a modular linear dependence on the discrete logarithms of Q ∈ G
and Pij ∈ B with respect to the base P . After collecting sufficiently many relations2 ,
linear algebra step solves for the discrete logarithm of Q ∈ G, as well as the discrete
logarithms of the factor base elements. Clearly, the success probability and the running
time of the index calculus algorithm heavily depend on the decomposition probability of
a random element in G, the cost of the decomposition step, and the size of the factor
1
  We prefer to use point rather than element because elliptic curve group elements are commonly
  called points.
2
  This is roughly when the number of relations exceeds |B|.
2

base. In particular, the overall cost of the relation collection and the linear algebra steps
must be optimized with a non-trivial success probability.
    In 2004, Semaev [11] showed that solving PDP in an elliptic curve group is equivalent
to solving a particular system of multivariate non-linear system of equations derived from
the so called Semaev summation polynomials. Semaev’s work triggered the possibility of
the existence of an index calculus type algorithm which is more efficient than the Pollard’s
rho algorithm to solve the discrete logarithm problem in elliptic curves defined over Fqn ,
which we denote ECDLP(q, n). Note that Pollard’s rho algorithm     p    is a general purpose
algorithm that solves DLP in a group G, and runs in time O( |G|). Gaudry [7] showed
that, for a fixed n, Semaev summation polynomials can be effectively used to solve
                                           2
ECDLP(q, n) in heuristic time O(q 2− n ), where the constant in O(·) is exponential in n.
For example, Gaudry’s algorithm and Pollard’s rho algorithm solve ECDLP(q, 3) in time
O(q 1.33 ) and O(q 1.5 ), respectively. Due to the exponential in n constant in the running
time of Gaudry’s algorithm, his attack is expected to be more effective than Pollard’s
rho algorithm if n ≥ 3 is relatively small and q is large. Diem [2] rigorously showed
that ECDLP(q, n) can be solved in an expected subexponential time when a(log q)α ≤
n ≤ b(log q)β for some a, b, α, β > 0. On the other hand, Diem’s method has expected
                                         1/2
exponential running time O(en(log n) ) for solving ECDLP(2, n). As a result, the index
calculus type algorithms presented in [7, 2] do not yield ECDLP solvers which are more
effective than Pollard’s rho method when q = 2 and n is prime. The ideas for choosing
an appropriate factor base in [2] have been adapted in [5, 10], and the complexity of the
relation collection step have been analyzed. In both papers [5] and [10], a positive integer
m, which we call the decomposition constant, is fixed to represent the number of points
in the decomposition of a random point in the relation collection step. The factor base
consists of elliptic curve points whose x-coordinates belong to an n0 -dimensional subspace
V ⊂ F2n over F2 , where n0 is chosen such that mn0 ≈ n. We refer to PDP in this setting
by PDP(n, m, n0 ) throughout the rest of this paper.
    Faugère et al. [5] showed, under a certain assumption, that ECDLP(2, n) can be solved
in time O(2ωn/2 ), where 2.376 ≤ ω ≤ 3 is the linear algebra constant. The running time
analysis in [5] considers the linearization technique to solve the multivariate nonlinear
system of equations which are derived from the (m + 1)’st Semaev polynomial Sm+1
during the relation collection step to solve PDP(n, m, n0 ). Faugère et al. further argue
that, Groebner basis techniques may improve the running time by a factor m in the
exponent, where m is the decomposition constant. This last claim has been confirmed
in the experiments in [5] for elliptic curves defined over F2n with n ∈ {41, 67, 97, 131}
and m = 2. Petit and Quisquater’s heuristic analysis in [10] claims that ECDLP(2, n)
                                                 2/3
can asymptotically be solved in time O(2cn log n ) for some constant 0 < c < 2. The
subexponential running time in [10] is based on a rather strong assumption on the be-
havior of the systems of equations that arise from Semaev polynomials. In particular, it
is assumed in [10] that the degree of regularity Dreg and the first fall degree DFirstFall of
the underlying polynomial systems to solve PDP(n, m, n0 ) are approximately equal. The
analysis in [10] also assumes that n0 = nα and m = n1−α for some positive constant α.
Experiments with a very limited set of parameters (n, m, n0 ), n ∈ {11, 17}, m ∈ {2, 3},
n0 = dn/me were conducted in [10] in the favor of their assumption.
    A recent paper by Shantz and Teske [13] presented some extended experimental results
on solving PDP(n, m, n0 ) for the same setting as in the Petit and Quisquater’s paper
[10]. In particular, [13] validates the degree of regularity assumption in [10] for the set of
parameters (n, m, n0 ) such that n ∈ {11, 13, 15, 17, 19, 23, 29}, m = 2, n0 = dn/me; and
for (n, m, n0 ) such that n ∈ {11, 13, 15, 17, 19, 21}, m = 3, n0 = dn/me. Shantz and Teske
                                                                                               3

[13] were able to extend their experimental data for the parameters (n, m, n0 , ∆), n ≤ 48,
m = 2, and where ∆ = n − mn0 is chosen appropriately to possibly improve the running
time of ECDLP(2, n). In another recent paper [8], Huang et al. exploit the symmetry in
Semaev polynomials, and improve on the running time and memory requirements of the
PDP(n, m, n0 ) solver in [5]. The efficiency of the method in [8] is tested for parameters
(n, m, n0 ) such that n ≤ 53, m = 3, n0 = 3, 4, 5, 6.
    Petit and Quisquater’s heuristic analysis [10] claims that index calculus methods for
solving ECDLP(2, n) is more effective than the Pollard’s rho method for n > 2000, m ≥ 4
and mn0 ≈ n. However, all the experiments reported so far on solving PDP(n, m, n0 ) for
the set of parameters (n, m, n0 , ∆) with ∆ = n − mn0 ≤ 1 and m = 3 are limited to
n ≤ 19; see [13, 8]. Similarly, all the experiments for the set of parameters (n, m, n0 , ∆)
with m = 3 are limited to n0 ≤ 6, which forces ∆ ≥ 2 for n ≥ 20. In general, it is desired
to have n0 increasing as a function of n, rather than having some upper bound on n0 , so
that n ≈ mn0 as assumed in the running time analysis of ECDLP(2, n) solvers in [5, 10].
Therefore, it remains a challenge to run experiments on an extensive set of parameters
(n, m, n0 ) with larger prime n values, m ≥ 4, and mn0 ≈ n. For example, it is stated in
[8, Section 4.1] that
    On the other hand, the method appears unpractical for m = 4 even for very small
    values of n because of the exponential increase with m of the degrees in Semaev’s
    polynomials.
    In a more recent paper [6], Galbraith and Gebregiyorgis introduce a new choice of
variables and a new choice of factor base, and they are able to solve PDP with various
n ≥ 17, m = 4, n0 = 3, 4 using Groebner basis algorithms; and also with various n ≥ 17,
m = 4, n0 ≤ 7 using SAT solvers.
    In this paper, we modify the system of equations, that are derived from Semaev poly-
nomials, by introducing some auxiliary variables. We show that PDP(n, m, n0 ) can be
solved by finding a solution to a system of equations derived from several third Se-
maev polynomials S3 each of which has at most three variables. For a comparison,
PDP(n, m, n0 ) in E(F2n ) with decomposition constant m = 5 would be traditionally
attacked via considering the Semaev polynomial S6 with 5 variables, which is likely to
have a root in V 5 , where V ⊂ F2n is a subspace of dimension n0 = bn/5c. On the other
hand, when m = 5, our polynomial system consists of third Semaev polynomials S3,i
(i = 1, 2, 3, 4), and a total of 8 variables which is likely to have a root in V 5 × F32n , where
V ⊂ F2n is a subspace of dimension bn/5c. As a result, our technique overcomes the diffi-
culty of dealing with the (m+1)’st Semaev polynomial Sm+1 when solving PDP(n, m, n0 )
with m ≥ 4. We should emphasize that choosing m ≥ 4 is desirable for an index calculus
based ECDLP(2, n) solver to be more effective than a generic DLP solver such as Pol-
lard’s rho algorithm. Our method introduces an overhead of introducing some auxiliary
variables. However, we argue that the trade-off between lowering the degree of Semaev
polynomials and increasing the number of variables provides a significant speed-up. In
particular, we present some experimental results on solving PDP(n, m, n0 ) for the follow-
ing parameters:
– n ≤ 19, m = 4, 5, and n0 = bn/mc. We are not aware of any previous experimental
 data for n > 15 and m = 5.
– n ≤ 26, m = 3, n0 = bn/mc. We are not aware of any previous experimental data for
 n > 21, m = 3, and ∆ = n − mn0 ≤ 2.
We observe in our experiments that regularity degrees of the underlying systems are rel-
atively low. We also observe that running time and memory requirement of algorithms
4

can be improved significantly if the Groebner basis computations are first performed on
a subset of polynomials and if the ReductionHeuristic parameter in Magma is set to be
a small number; see Section 5 for more detail. We would like to emphasize that these
techniques are aplied for the first time in this paper to solve the point decomposition
problem. As a result, we gain significant improvement over the recently published ex-
perimental results [12]. For a comparison, we are able to solve PDP(15, 5, 3) instances
in about 7 seconds (with 256 MB memory). Note that, PDP(15, 5, 3) is solved in about
175 seconds (with 2635 MB memory) in [12]. In general, our experimental findings with
m = 3, 4, 5 extend and improve on the recently reported results in [13, 8, 12].
    The rest of this paper is organized as follows. In Section 2, we recall Semaev poly-
nomials and their application to ECDLP(2, n). In Section 3, we describe and analyze a
new method to solve PDP(n, m, n0 ) in E(F2n ). In Section 4, we present our experimental
results. In Section 5, we extend our results from Section 3.


2    Semaev Polynomials and ECDLP
Let F2n = F2 [σ]/hf (σ)i be a finite field with 2n elements, where f (σ) is a monic irre-
ducible polynomial of degree n over the field F2 = {0, 1}. let E be a non-singular elliptic
curve defined by the short Weierstrass equation

                           E/F2n : y 2 + xy = x3 + ax2 + b, a, b ∈ F2n .

We denote the identity element of E by ∞. The i’th Semaev polynomial associated with
E is defined as follows:
                              (
                               (x1 x2 + x1 x3 + x2 x3 )2 + x1 x2 x3 + b                            if i = 3
 Si (x1 , x2 , . . . , xi ) =
                               ResX (Si−j (x1 , . . . , xi−j−1 , X), Sj+2 (xi−j , . . . , xi , X)) if i ≥ 4,
                                                                                                           (1)

where 1 ≤ j ≤ i − 3.
   For n0 ≤ n, let
                                                             0
                      V = {a0 + a1 σ + · · · + an0 −1 σ n −1 : ai ∈ F2 } ⊂ F2n

and define the factor base

                                   B = {P = (x, y) ∈ E : x ∈ V }.

Recall that in PDP(n, m, n0 ), we are looking for Pi = (xi , yi ) ∈ B such that

                                              P1 + · · · Pm = R,                                          (2)

for some given point R = (xR , yR ) ∈ E. We refer to (2) as an m-decomposition of R in
B. We expect that, on average, a random point R ∈ E has an m-decomposition in B with
                 0                                0
probability
     P       2mn /2n m! simply because |B| ≈ 2n and permuting Pi does not change the
sum     Pi (see [7]). As described in Section 1, the DLP in E can be solved via an index-
calculus based approach by computing about |B| explicit m-decompositions and solving
a sparse linear system of about |B| equations. Therefore, the cost of solving ECDLP(2, n)
may be estimated as
                                          0   2n m!             0 0
                                       2n           Cn,m,n0 + 2ω n ,                                      (3)
                                              2mn0
                                                                                             5

where Cn,m,n0 is the cost of solving PDP(n, m, n0 ), and ω 0 = 2 is the sparse linear algebra
constant. Semaev [11] showed that a decomposition of the form (2) exists if and only if
the x-coordinates of Pi and R are zeros of the (m + 1)’st Semaev polynomial, that is,
Sm+1 (x1 , . . . , xm , xR ) = 0. In the rest of this paper, we focus on solving PDP(n, m, n0 )
(and estimating Cn,m,n0 ) via modifying the equation induced by Sm+1 .


3     A new approach to solve the point decomposition problem

Let E/F2n , V , and B be as defined in Section 2. Recall that an m-decomposition of a
point
                                   R = P1 + · · · P m ,
where R = (xR , yR ) ∈ E, Pi = (xi , yi ) ∈ B, can be computed (if exists) by identifying a
tuple (x1 , . . . , xm ) ∈ V m that satisfies

                                   Sm+1 (x1 , . . . , xm , xR ) = 0                        (4)

Note that xi belong to an n0 -dimensional subspace of F2n . Therefore, (4) defines a system
Sys1 of a single equation over F2n in m variables. In [5, 10], the Weil descent technique
is applied, and a second system Sys2 of n equations over F2 in mn0 boolean variables
is derived from Sys1 . The cost Cn,m,n0 of solving PDP(n, m, n0 ) in [5, 10] is estimated
through the analysis of solving Sys2 using linearization and Groebner basis techniques.
Next, we describe a new approach to derive another system Sys3 of boolean equations
such that a solution of Sys3 yields an m-decomposition of a point R.

Notation. Throughout the rest of this paper, we distinguish between two classes Semaev
polynomials. The first class of Semaev polynomials is denoted by Sm,1 (x1 , . . . , xm ), which
represents the m’th Semaev polynomial with m variables. The second class of Semaev
polynomials is denoted by Sm,2 (x1 , . . . , xm−1 , xR ), which represents the m’th Semaev
polynomial with m − 1 variables (i.e., the last variable xm is evaluated at a number xR ).


3.1     The case: m = 3

Let R = (xR , yR ) ∈ E. Notice that there exist Pi ∈ B such that

                                    P1 + P2 + P3 − R = ∞

if and only if there exist Pi ∈ B and P12 ∈ E such that
                                  (
                                   P1 + P2 − P12 = ∞
                                                                                           (5)
                                   P3 + P12 − R = ∞

Therefore, a 3-decomposition of R = P1 + P2 + P3 may be found as follows:

 1. Define the following system of equations derived from Semaev polynomials
                                 (
                                   S3,1 (x1 , x2 , x12 ) = 0
                                                                                           (6)
                                   S3,2 (x3 , x12 , xR ) = 0.

      Note that this system is defined over F2n and has 4 variables x1 , x2 , x3 , x12 .
6

2. Introduce boolean variables xi,j such that
                                                     0
                                                    nX −1
                                             xi =           xi,j σ j ,
                                                    j=0

      for i = 1, 2, 3, and
                                                    n
                                                    X
                                            x12 =         x12,j σ j .
                                                    j=0

      Apply the Weil descent technique to (6) and define an equivalent system of 2n equa-
      tions over F2 with 3n0 + n boolean variables
                  {xi,j : i = 1, 2, 3, j = 0, . . . n0 − 1} ∪ {x12,j : j = 0, . . . n − 1}.
      Solve this new system of boolean equations and recover x1 , x2 , x3 ∈ F2n from xi,j ∈
      F2 .
   Note that the proposed method solves a system of 2n equations over F2 with 3n0 + n
boolean variables rather than solving a system of n equations over F2 with 3n0 boolean
variables.

3.2     The case: m = 4
Let R = (xR , yR ) ∈ E. Notice that there exist Pi ∈ B such that
                                   P1 + P2 + P3 + P4 − R = ∞
if and only if there exist Pi ∈ B and P12 ∈ E such that
                                (
                                 P1 + P2 − P12 = ∞
                                                                                               (7)
                                 P3 + P4 + P12 − R = ∞
Therefore, a 4-decomposition of R = P1 + P2 + P3 + P4 may be found as follows:
1. Define the following system of equations derived from Semaev polynomials
                               (
                                 S3,1 (x1 , x2 , x12 ) = 0
                                                                                               (8)
                                 S4,2 (x3 , x4 , x12 , xR ) = 0
   Note that this system is defined over F2n and has 5 variables x1 , x2 , x3 , x4 , x12 .
2. Introduce boolean variables xi,j such that
                                                     0
                                                    nX −1
                                             xi =           xi,j σ j ,
                                                    j=0

      for i = 1, 2, 3, 4, and
                                                     n
                                                     X
                                            x12 =           xi,j σ j .
                                                     j=0

      Apply the Weil descent technique to (8) and define an equivalent system of 2n equa-
      tions over F2 with 4n0 + n boolean variables
                 {xi,j : i = 1, 2, 3, 4 j = 0, . . . n0 − 1} ∪ {x12,j : j = 0, . . . n − 1}.
      Solve this new system of boolean equations and recover x1 , x2 , x3 , x4 ∈ F2n from
      xi,j ∈ F2 .
                                                                                                    7

   Note that the proposed method solves a system of 2n equations over F2 with 4n0 + n
boolean variables rather than solving a system of n equations over F2 with 4n0 boolean
variables.

3.3     The case: m = 5
Let R = (xR , yR ) ∈ E. Notice that there exist Pi ∈ B such that

                                   P1 + P2 + P3 + P4 + P5 − R = ∞

if and only if there exist Pi ∈ B and P123 ∈ E such that
                               (
                                 P1 + P2 + P3 − P123 = ∞
                                                                                                   (9)
                                 P4 + P5 + P123 − R = ∞

Therefore, a 5-decomposition of R = P1 + P2 + P3 + P4 + P5 may be found as follows:
1. Define the following system of equations derived from Semaev polynomials
                              (
                                S4,1 (x1 , x2 , x3 , x123 ) = 0
                                                                                                  (10)
                                S4,2 (x4 , x5 , x123 , xR ) = 0

   Note that this system is defined over F2n and has 6 variables x1 , x2 , x3 , x4 , x5 , x123 .
2. Introduce boolean variables xi,j such that
                                                     0
                                                    nX −1
                                             xi =           xi,j σ j ,
                                                    j=0

      for i = 1, 2, 3, 4, 5, and
                                                    n
                                                    X
                                           x123 =         x123,j σ j .
                                                    j=0

      Apply the Weil descent technique to (10) and define an equivalent system of 2n
      equations over F2 with 5n0 + n boolean variables

                {xi,j : i = 1, 2, 3, 4, 5 j = 0, . . . n0 − 1} ∪ {x123,j : j = 0, . . . n − 1}.

      Solve this new system of boolean equations and recover x1 , x2 , x3 , x4 , x5 ∈ F2n from
      xi,j ∈ F2 .
   Note that the proposed method solves a system of 2n equations over F2 with 5n0 + n
boolean variables rather than solving a system of n equations over F2 with 5n0 boolean
variables.

3.4     Analysis of the new polynomial systems
One of the methods to solve a multivariate non-linear system of equations is to com-
pute the Groebner basis of the underlying ideal. Groebner basis computations can be
performed using Faugère’s algorithms [3, 4], which reduce the problem to Gaussian elim-
ination of Macaulay-type matrices Md of degree d. The Macaulay matrix Md encodes
degree (at most) d polynomials, that are generated during Groebner basis computation.
8

Therefore, the cost of solving a system of equations is determined by the maximal degree
D (also known as the degree of regularity of the system) reached during the compu-
tation. If N is the number of variables in the system, then the cost is estimated as
           ω
O N +D−1        , where N +D−1
                                 
        D                   D      is the maximum number of columns in MD and ω is the
linear algebra constant. In general, it is hard to estimate D. In the recent paper [10], it
is conjectured that the degree of regularity Dreg of systems arising from PDP(n, m, n0 )
satisfies Dreg = DFirstFall + o(1), where DFirstFall is the first fall degree of the system and
defined as follows.
Definition 1. [10] Let R be a polynomial ring over a field K. Let F := {f1 , . . . , f` } ⊂ R
be a set of polynomials of degrees at most DFirstFall . The first fall degree of F is the smallest
degree DFirstFall such that there exist polynomials gi ∈ R with maxi (deg(fi ) + deg(gi )) =
                            P`                           P`
DFirstFall , satisfying deg( i=1 gi fi ) < DFirstFall but i=1 gi fi 6= 0.
Experimental studies in recent papers [10, 13] give supporting evidence that Dreg ≈
DFirstFall . However, experimental data is yet very limited (see Section 1) to verify this
conjecture. In this section, we compute the first fall degree of the systems proposed in
Section 3.1, Section 3.2, and Section 3.3. Our experimental results in Section 4 support
that Dreg ≈ DFirstFall .

DFirstFall of the system when m = 3 In this case, one needs to solve the system of 2n
equations over F2 with 3n0 + n boolean variables. The system of equations is derived by
applying Weil descent to (6) that consists of two Semaev polynomials S3,1 and S3,2 . The
monomial set of S3,1 (x1 , x2 , x12 ) is

                               {1, x21 x22 , x21 x212 , x22 x212 , x1 x2 x12 }.

Therefore, the Weil descent of S3,1 (x1 , x2 , x12 ) yields a 2n0 + n variable polynomial set
{fi } over F2 such that maxi (deg(fi )) = 3. On the other hand, the monomial set of
x1 · S3,1 (x1 , x2 , x12 ) is
                              {x1 , x31 x22 , x31 x212 , x22 x212 , x21 x2 x12 }.
Therefore, the Weil descent of x1 · S3,1 (x1 , x2 , x12 ) yields a polynomial set {Fi } over
F2 such that maxi (deg(Fi )) = 3. It follows from the definition that DFirstFall (S3,1 ) ≤ 4
because the maximum degree of polynomials obtained from the Weil descent of x1 is 1.
Similarly, the monomial set of S3,2 (x3 , x12 , xR ) is

                                    {1, x23 x212 , x23 , x212 , x3 x12 }.

Therefore, the Weil descent of S3,2 (x3 , x12 , xR ) yields a n0 + n variable polynomial set
{fi } over F2 such that maxi (deg(fi )) = 2. On the other hand, the monomial set of
x33 · S3,2 (x3 , x21 , xR ) is
                               {x33 , x53 x212 , x53 , x33 x212 , x43 x12 }.
Therefore, the Weil descent of x33 · S3,2 (x3 , x12 , xR ) yields a polynomial set {Fi } over
F2 such that maxi (deg(Fi )) = 3. It follows from the definition that DFirstFall (S3,2 ) ≤ 4
because the maximum degree of polynomials obtained from the Weil descent of x33 is 2.
We conclude that DFirstFall ≤ 4.

DFirstFall of the system when m = 4 In this case, one needs to solve the system of
2n equations over F2 with 4n0 + n boolean variables. The system of equations is de-
rived by applying Weil descent to (8) that consists of two Semaev polynomials S3,1
                                                                                                          9

and S4,2 . From our above discussion, DFirstFall (S3,1 ) ≤ 4. Now, analyzing the monomial
set of S4,2 (x3 , x4 , x123 , xR ), we can see that the Weil descent of S4,2 (x3 , x4 , x123 , xR )
yields a 2n0 + n variable polynomial set {fi } over F2 such that maxi (deg(fi )) = 6 (this
follows from the Weil descent of the monomial (x3 x4 x123 )3 ). On the other hand, an-
alyzing the monomial set of x3 · S4,2 (x3 , x4 , x123 , xR ), we see that the Weil descent of
x3 ·S4,2 (x3 , x4 , x123 , xR ) yields a polynomial set {Fi } over F2 such that maxi (deg(Fi )) = 6.
It follows from the definition that DFirstFall (S4,2 ) ≤ 7 because the maximum degree of
polynomials obtained from the Weil descent of x3 is 1. We conclude that DFirstFall ≤ 7.


DFirstFall of the system when m = 5 In this case, one needs to solve the system of
2n equations over F2 with 5n0 + n boolean variables. The system of equations is de-
rived by applying Weil descent to (10) that consists of two Semaev polynomials S4,1 and
S4,2 . From our above discussion, DFirstFall (S4,2 ) ≤ 7. Now, analyzing the monomial set
of S4,1 (x1 , x2 , x3 , x123 ), we can see that the Weil descent of S4,1 (x1 , x2 , x3 , x123 ) yields a
3n0 +n variable polynomial set {fi } over F2 such that maxi (deg(fi )) = 8 (this follows from
the Weil descent of the monomial (x1 x2 x3 x123 )3 ). On the other hand, analyzing the mono-
mial set of x3 ·S4,1 (x1 , x2 , x3 , x123 ), we see that the Weil descent of x3 ·S4,1 (x1 , x2 , x3 , x123 )
yields a polynomial set {Fi } over F2 such that maxi (deg(Fi )) = 8. It follows from the
definition that DFirstFall (S4,1 ) ≤ 9 because the maximum degree of polynomials obtained
from the Weil descent of x3 is 1. We conclude that DFirstFall ≤ 9.



4    Experimental results

We implemented the methods proposed in Section 3 on a desktop computer (Intel(R)
Xeon(R) CPU E31240 3.30GHz) using Groebner basis algorithms in Magma [1]. For
each parameter set (n, m, n0 ), we solved 5 random instances of PDP over a randomly
chosen elliptic curve E/F2n . In Table 1, we report on our experimental results for solving
PDP(n, m, n0 = bn/mc) with m = 3, 4, 5. In particular, for each of these 5 computations,
we report on the maximum CPU time (seconds) and memory (MB) required for solving
PDP. We also report on the maximum of the maximum step degrees D in the Groebner
basis computations. Recall that in Section 3, we estimated DFirstFall ≤ 4 when m = 3;
DFirstFall ≤ 7 when m = 4; and DFirstFall ≤ 9 when m = 5. In our experiments, we observe
that Dreg = 4 when m = 3; Dreg = 7 when m = 4; and Dreg ≤ 8 when m = 5.
   Let m = 5 and n0 = bn/mc. Based on our experimental data, it is tempting to assume
that the underlying system of polynomial equations has Dreg ≤ 9. Moreover, the system
has N = 5n0 + n ≈ 2n boolean variables. Therefore, when m = 5, we may estimate the
cost of solving ECDLP(2, n) (see (3)) as

                                         n
                                                      w
                                  n0 2 m! N + Dreg − 1        0 0
                                2                         + 2w n
                                     2mn0    Dreg
                                                           0
                                 ≈ 2n/5 m!(2n)9w + 2w n/5
                                 ≈ 234 2n/5 n27 + 22n/5 ,

where we assume w = 3 and w0 = 2. For example, when n ≈ 1200, the cost of solving
ECDLP(2, n) is estimated to be 2550 which is significantly smaller than the cost 2600 of
square-root time algorithms.
10

Table 1. Experimental results on solving PDP(n, m, n0 = bn/mc). Time in seconds; Memory
in MB; D is the maximum step degree.

                          m=3              m=4                m=5
                n Time Memory D Time Memory D Time Memory D
                11                                      0.520    25.8 7
                12                                      0.670    33.0 7
                13                                      0.890    42.8 7
                14                                      4.260   126.7 8
                15                                     350.100 1839.5 8
                16                   414.320 5100.7 7 408.270 2633.9 8
                17 1.690     38.8 4 1395.170 5632.8 7 506.340 4050.3 8
                18 26.680    264.5 4 497.770 5632.8 7 920.790 6186.9 8
                19 15.270    321.8 4 509.330 5634.1 7 1265.090 8282.9 8
                20 49.350    397.6 4
                21 163.100 1228.3 4
                22 126.290 1413.2 4
                23 248.820 1668.7 4
                24 1266.610 5142.2 4
                25 1623.180 6363.8 4
                26 1645.78 6596.9 4


5    Extensions and Optimization
In Section 3, we introduced a single auxiliary variable to lower the degree of Semaev
polynomials. The degree of polynomials can further be lowered by introducing more
auxiliary variables. As an example, we consider the case m = 5. Let R = (xR , yR ) ∈ E,
as before. Notice that there exist Pi ∈ B such that

                               P1 + P2 + P3 + P4 + P5 − R = ∞

if and only if there exist Pi ∈ B and P12 , P34 , P50 ∈ E such that
                                 
                                 
                                  P1 + P2 − P12 = ∞
                                 
                                 P + P − P = ∞
                                     3     4     34
                                                                                                  (11)
                                 
                                 
                                  P 5 − P 50 − R   =∞
                                   P12 + P34 + P50 = ∞
                                 

Therefore, a 5-decomposition of R = P1 + P2 + P3 + P4 + P5 may be found as follows:
 1. Define the following system of equations derived from Semaev polynomials
                                 
                                 
                                  S3,1 (x1 , x2 , x12 ) = 0
                                 
                                 S (x , x , x ) = 0
                                    3,1 3      4    34
                                                                                                  (12)
                                 
                                 
                                  S3,2 (x5 , x50 , xR ) = 0
                                   S3,1 (x12 , x34 , x50 ) = 0
                                 

    Note that this system is defined over F2n and has 8 variables x1 , x2 , x3 , x4 , x5 , x12 , x34 , x50 .
 2. Introduce boolean variables xi,j such that
                                                    0
                                                   nX −1
                                            xi =           xi,j σ j ,
                                                   j=0
                                                                                                       11

Table 2. Experimental results on solving PDP(n, m, n0 = bn/mc). Time in seconds; Memory
in MB; D is the maximum step degree; DHeuristic is set to be 4 in Groebner basis computations.

                                                      DHeuristic = 4
                                          m=5            m=5
                                 n Time Memory D Time Memory
                                 11 2.380     58   4
                                 12 4.150    116.7 4
                                 13 6.390    124.1 4
                                 14 9.510    245.2 4
                                 15 393.170 6421.9 4 7.130 256.3
                                 16 242.500 5911.7 4 6.900 320.4
                                 17 365.460 7063.8 4 6.660 320.4
                                 18 836.080 8619.4 4 11.700 394.6
                                 19 531.420 8864.2 4 45.570 2505.3



    for i = 1, 2, 3, 4, 5, and
                                                     n
                                                     X
                                            xi,j =         xi,j σ j ,
                                                     k=0


    for i = 12, 34, 50. Apply the Weil descent technique to (12) and define an equivalent
    system of 4n equations over F2 with 5n0 + 3n boolean variables

       {xi,j : i = 1, 2, 3, 4, 5 j = 0, . . . n0 − 1} ∪ {xi,j : i = 12, 34, 50, j = 0, . . . n − 1}.

    Solve this new system of boolean equations and recover x1 , x2 , x3 , x4 , x5 ∈ F2n from
    xi,j ∈ F2 .

    Note that the proposed method solves a system of 4n equations over F2 with 5n0 + 3n
boolean variables rather than solving a system of n equations over F2 with 5n0 boolean
variables. Similar to the analysis in Section 3, we can show that DFirstFall ≤ 4.
    In Table 2, we report on our experimental results for solving PDP(n, m, n0 = bn/mc)
with m = 5 deploying only the third Semaev polynomials; see (12). The time and memory
results in the second and third column of Table 2 are obtained using the Groebner basis
implementation of Magma with the grevlex ordering of monomials. We observe that the
maximum step degree is Dreg = 4 for 11 ≤ n ≤ 19. The time and memory results in the
last two columns of Table 2 are obtained using the Groebner basis implementation of
Magma with the grevlex ordering of monomials in a boolean ring. We also introduced two
modifications in the computations: We set the ReductionHeuristic parameter in Magma to
4; and we first computed Groebner bases of partial systems described by single equations
in (12), and merged them later. These two techniques yield non-trivial optimization both
in time and memory. For a comparison, when n = 15 and m = 3, (Time, Memory) values
decrease from (393.170, 6421.9) to (7.130, 256.3) when this modification is deployed in
the computation; see Table 2. For the same parameters (n = 15 and m = 3), (Time,
Memory) values are reported as (174.47, 2635.4) in [12].
    Based on our experimental data, it is tempting to assume that the underlying system
of polynomial equations has Dreg ≤ 4 for all n. Moreover, the system has N = 5n0 + 3n ≈
4n boolean variables. Therefore, when m = 5, we may estimate the cost of solving
12

ECDLP(2, n) (see (3)) as
                                   n
                                                           w
                                0 2 m!       N + Dreg − 1            0    0
                              2n mn0                             + 2w n
                                  2             Dreg
                                                       0
                              ≈ 2n/5 m!(4n)4w + 2w n/5
                              ≈ 231 2n/5 n12 + 22n/5 ,

where we assume w = 3 and w0 = 2. This running time outperforms square-root methods
when n > 457. For example, when n ≈ 550, the cost of solving ECDLP(2, n) is estimated
to be 2250 which is significantly smaller than the cost 2275 of square-root time algorithms.


Acknowledgment

I would like to acknowledge
                    √
                                   two recent papers [12, 9]. Semaev [12] claims a new com-
                  c( n ln n
plexity bound 2             ) for solving ECDLP(2, n) under the assumption that the degree
of regularity in Groebner computations of particular polynomial√ systems is Dreg ≤ 4.
Semaev also shows that ECDLP(2, p         n) can be solved in time 2o(c n ln n) under a weaker
assumption that Dreg = o( n/ ln n) The techniques used in [12] and in this paper are
similar. In [9], Kosters and Yeo provide experimental evidence that the degree of regular-
ity of the underlying polynomial systems is likely to increase as a function of n, whence
the conjecture Dreg ≈ DFirstFall may be false.
    I would like to thank Michiel Kosters and Igor Semaev for their comments on the
first version of this paper.


References

 1. W. Bosma, J. Cannon, and C. Playoust, The Magma algebra system I: The user language,
    Journal of Symbolic Computation 24 (1997), 235–265.
 2. C. Diem, On the discrete logarithm problem in elliptic curves II, Algebra and Number Theory
    7 (2013), 1281–1323.
 3. J.-C. Faugère, A New efficient algorithm for computing Groebner bases (F4), Journal of
    Pure and Applied Algebra 139 (1999), 61–68.
 4.         , A New efficient algorithm for computing Groebner bases without reduction to zero
    (F5), International Symposium on Symbolic and Algebraic Computation (2002), 75–83.
 5. J.-C. Faugère, L. Perret, C. Petit, and G. Renault, Improving the complexity of index calculus
    algorithms in elliptic curves over binary fields, Advances in Cryptology – EUROCRYPT
    2012, Lecture Notes in Computer Science 7237 (2012), 27–44.
 6. S. Galbraith and S. Gebregiyorgis, Summation polynomial algorithms for elliptic curves in
    characteristic two, Advances in Cryptology – INDOCRYPT 2014, Lecture Notes In Com-
    puter Science 8885 (2014), 409–427.
 7. P. Gaudry, Index calculus for abelian varieties of small dimension and the elliptic curve
    discrete logarithm problem, Journal of Symbolic Computation 44 (2009), 1690–1702.
 8. Y.-J. Huang, C. Petit, N. Shinohara, and T. Takagi, Improvement of Faugère et al.’s method
    to solve ECDLP, Advances in Information and Computer Security, Lecture Notes in Com-
    puter Science 8231 (2013), 115–132.
 9. M. Kosters and S. Yeo, Notes on summation polynomials, (2015), arXiv:1503.08001.
10. C. Petit and J.-J. Quisquater, On polynomial systems arising from a Weil descent, Advances
    in Cryptology – ASIACRYPT 2012, Lecture Notes In Computer Science 7658 (2012), 451–
    466.
                                                                                            13

11. I. Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves,
    Cryptology ePrint Archive: Report 2004/031, 2004.
12.        , New algorithm for the discrete logarithm problem on elliptic curves, (2015), Cryp-
    tology ePrint Archive: Report 2015/310.
13. M. Shantz and E. Teske, Solving the elliptic curve discrete logarithm problem using Semaev
    polynomials, Weil descent and Groebner basis methods – an experimental study, Number
    Theory and Cryptography. Papers in Honor of Johannes Buchmann on the Occasion of His
    60th Birthday, Lecture Notes In Computer Science 8260 (2013), 94–107.
