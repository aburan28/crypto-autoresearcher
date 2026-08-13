# Theorem dossier: signed-sum Kummer structure of Semaev covers

## 0. Status, scope, and conventions

This is a proof draft for review. It is not an evidence record and does not
supersede or promote any `KN-*`, `EV-*`, `DEC-*`, or `GOAL-*` record.

Let \(k\) be a field of characteristic different from \(2\) and \(3\), and let

\[
  E/k:\qquad y^2=f(x)=x^3+Ax+B
\]

be nonsingular. Thus \(f\) is separable. Let \(S_m\) denote the classical
\(m\)-th Semaev summation polynomial, normalized only up to a nonzero scalar.
Its defining property is:

\[
 S_m(a_1,\ldots,a_m)=0
 \quad\Longleftrightarrow\quad
 \exists P_i\in E(\bar k),\ x(P_i)=a_i,\ \sum_{i=1}^m P_i=O,
\]

away from the standard projective/leading-coefficient degeneracies. Its degree
in every variable is \(2^{m-2}\).

Fix \(m\ge3\). We view

\[
  S_m(X,x_2,\ldots,x_m)\in F[X],
  \qquad F=k(x_2,\ldots,x_m),
\]

as a one-variable polynomial over the rational function field. Put
\(r=m-1\). For \(i=2,\ldots,m\), introduce

\[
  y_i^2=f(x_i),\qquad P_i=(x_i,y_i),
\]

and define

\[
  L=F(y_2,\ldots,y_m).
\]

The phrase **generic root** below means a root over the nonempty open set on
which the signed sums are finite, pairwise distinct up to sign, and the
one-variable Semaev polynomial has its full degree.

---

## 1. Independence of the Kummer generators

### Lemma 1 (independent square classes)

The classes of \(f(x_2),\ldots,f(x_m)\) are linearly independent in
\(F^\times/F^{\times2}\). Consequently,

\[
 [L:F]=2^r,\qquad
 \operatorname{Gal}(L/F)\cong(C_2)^r,
\]

with independent generators \(\sigma_i:y_i\mapsto-y_i\).

### Proof

Suppose a nonempty product

\[
  \prod_{i\in I}f(x_i)
\]

were a square in \(F\). Choose \(j\in I\), and choose any irreducible factor
\(g(T)\) of the separable polynomial \(f(T)\) over \(k\). Consider the discrete
valuation associated with the prime divisor \(g(x_j)=0\) in the UFD
\(k[x_2,\ldots,x_m]\).

The factor \(f(x_j)\) has valuation one at that divisor because \(f\) is
separable. Every \(f(x_i)\) with \(i\ne j\) has valuation zero there because it
depends on a different transcendental variable. Hence the product has odd
valuation one. A square has even valuation at every prime divisor, a
contradiction.

Thus no nonempty product is a square. Standard Kummer theory now gives degree
\(2^r\), and every independent sign change of the \(y_i\) defines an
\(F\)-automorphism. ∎

### Scope note

The argument uses separate transcendental variables, not genericity of the
curve coefficients. Rational 2-torsion, \(j=0\), \(j=1728\), and complex
multiplication do not create a dependency. The excluded cases are singular
curves and the characteristic-two setting where the sign/Kummer model changes.

---

## 2. The signed-sum root set

Let

\[
  \Sigma=\{\pm1\}^{r}/\{\varepsilon\sim-\varepsilon\}.
\]

For a sign class \([\varepsilon]\in\Sigma\), define

\[
  R_\varepsilon=\sum_{i=2}^m\varepsilon_iP_i,\qquad
  \rho_{[\varepsilon]}=x(R_\varepsilon).
\]

This is well-defined on sign classes because \(x(-R)=x(R)\).

### Lemma 2 (generic distinctness)

There is a nonempty Zariski-open subset of the parameter space on which:

1. every \(R_\varepsilon\) is finite; and
2. \(\rho_{[\varepsilon]}\ne\rho_{[\eta]}\) whenever
   \([\varepsilon]\ne[\eta]\).

Hence there are exactly \(2^{r-1}=2^{m-2}\) distinct signed-sum roots
generically.

### Proof

The group-law expressions are rational functions, so failure of finiteness is
contained in a closed denominator locus. It remains to show that no equality

\[
 x(R_\varepsilon)=x(R_\eta)
\]

holds identically for two distinct sign classes.

On an elliptic curve, \(x(P)=x(Q)\) implies \(P=\pm Q\). Therefore such an
identity would imply one of

\[
 \sum_{i=2}^m(\varepsilon_i-\eta_i)P_i=O,\qquad
 \sum_{i=2}^m(\varepsilon_i+\eta_i)P_i=O.
\]

For distinct classes, at least one coefficient vector is nonzero, and every
coefficient lies in \(\{0,\pm2\}\).

It is enough to produce one specialization with no such relation. Choose the
points \(Q_2,\ldots,Q_m\in E(\bar k)\) inductively. At each step, the finitely
many forbidden relations constrain the new point \(Q_j\) to a finite union of
fibres of the finite morphism \([2]:E\to E\). Since \(E(\bar k)\) is infinite,
a point outside that finite union exists. Also exclude the finitely many
choices making a signed sum equal to \(O\).

Thus one good specialization exists. Each equality above therefore defines a
proper closed subset, and deleting their finite union together with the
denominator locus leaves a nonempty open set. ∎

### Lemma 3 (root polynomial)

Define

\[
  \Psi_m(X)=
  \prod_{[\varepsilon]\in\Sigma}
  \left(X-\rho_{[\varepsilon]}\right).
\]

Then \(\Psi_m(X)\in F[X]\), and it is the monic normalization of
\(S_m(X,x_2,\ldots,x_m)\).

### Proof

The group \(H=\operatorname{Gal}(L/F)\cong(C_2)^r\) acts on sign vectors by
coordinatewise multiplication and therefore permutes the factors of
\(\Psi_m\). The product is \(H\)-invariant, hence belongs to \(F[X]\).

For every sign class, let \(P_1=-R_\varepsilon\). Then
\(x(P_1)=\rho_{[\varepsilon]}\) and

\[
 P_1+\sum_{i=2}^m\varepsilon_iP_i=O.
\]

The defining property of \(S_m\) gives
\(S_m(\rho_{[\varepsilon]},x_2,\ldots,x_m)=0\). Thus every root of
\(\Psi_m\) is a root of the one-variable Semaev polynomial.

Both polynomials have degree \(2^{m-2}\), and Lemma 2 gives that many distinct
generic roots. They therefore agree up to the nonzero leading coefficient of
\(S_m\). ∎

### Consequence

This proof isolates the only imported Semaev facts: the vanishing criterion and
the degree \(2^{m-2}\). A submission should either cite the exact primary
theorem or include an induction from the resultant definition as an appendix.

---

## 3. Correct splitting field and monodromy

Let

\[
 \delta=\sigma_2\sigma_3\cdots\sigma_m\in H
\]

be simultaneous sign reversal.

### Theorem 4 (fixed-field splitting theorem)

The splitting field \(K\) of \(S_m(X,x_2,\ldots,x_m)\) over \(F\) is

\[
  K=L^{\langle\delta\rangle}.
\]

Consequently,

\[
  \operatorname{Gal}(K/F)
  \cong H/\langle\delta\rangle
  \cong(C_2)^{m-2}.
\]

The action on the \(2^{m-2}\) roots is regular.

### Proof

For \(h=(h_2,\ldots,h_m)\in H\cong\{\pm1\}^r\),

\[
 h(\rho_{[\varepsilon]})
 =\rho_{[h\varepsilon]}.
\]

Simultaneous sign reversal sends \(R_\varepsilon\) to \(-R_\varepsilon\), so
\(\delta\) fixes every \(x\)-coordinate root. Therefore

\[
  K\subseteq L^{\langle\delta\rangle}.
\]

Conversely, an element \(h\in H\) fixes every root if and only if translation
by \([h]\) fixes every element of the sign-class set \(\Sigma\). By Lemma 2 the
root labels are distinct, so the action on labels detects the action on roots.
Coordinatewise multiplication on
\(\{\pm1\}^r/\{\pm(1,\ldots,1)\}\) is regular. Its kernel in \(H\) is exactly

\[
 \{1,\delta\}.
\]

Hence

\[
  \operatorname{Gal}(L/K)=\langle\delta\rangle.
\]

The fundamental theorem of Galois theory gives
\(K=L^{\langle\delta\rangle}\), and quotienting \(H\) by its order-two diagonal
subgroup gives \((C_2)^{r-1}=(C_2)^{m-2}\). The quotient acts simply
transitively on the sign classes, so the root action is regular. ∎

### Why this corrects the earlier proof sketch

The roots cannot generate each \(y_i\) separately: if they did, they would
generate all of \(L\), but \(\delta\) fixes every root and does not fix the
individual \(y_i\). The correct lower-bound argument is a kernel computation,
not recovery of each square root.

### Corollary 5 (generic irreducibility)

The normalized polynomial \(S_m(X,x_2,\ldots,x_m)\) is irreducible over \(F\).

### Proof

A separable polynomial is irreducible exactly when its Galois group acts
transitively on its roots. A regular action is transitive. ∎

### Corollary 6 (no curve-specific exceptional monodromy locus)

For every nonsingular short-Weierstrass curve in characteristic different from
two and three, the generic group is \((C_2)^{m-2}\). Extra automorphisms or CM
do not shrink the group.

### Proof

The proof uses only separability of \(f\), independence of the variables, and
the generic distinctness argument. None depends on the endomorphism ring of
\(E\). ∎

The statement is about this generic one-variable cover. Special parameter
tuples can still land on collision, ramification, or degree-drop loci.

---

## 4. Cycle structure and discriminant

Put \(d=2^{m-2}\).

### Corollary 7 (two cycle types)

In the regular action of \((C_2)^{m-2}\):

- the identity has cycle type \(1^d\);
- every nonidentity element has cycle type \(2^{d/2}\).

### Proof

Every nonzero group element has order two. Translation by a nonzero element has
no fixed point, because \(g+x=x\) would imply \(g=0\). The orbits therefore all
have size two. ∎

### Corollary 8 (square discriminant for \(m\ge4\))

For \(m\ge4\), the discriminant of the normalized generic one-variable Semaev
polynomial is a square in \(F\).

### Proof

A nonidentity element is a product of \(d/2=2^{m-3}\) transpositions. For
\(m\ge4\), this number is even. Thus every element of the Galois group is an
even permutation, so the group lies in \(A_d\). In characteristic different
from two, a separable polynomial has square discriminant precisely when its
Galois group is contained in the alternating group. ∎

For \(m=3\), the group is \(C_2=S_2\), and the exact identity is

\[
 \operatorname{disc}_{x_3}S_3(x_1,x_2,x_3)
 =16f(x_1)f(x_2),
\]

which is generically nonsquare.

---

## 5. Classification of block systems

The regular group is imprimitive for \(m\ge4\), but the complete structure is
more precise than “the recursion gives two blocks.”

### Proposition 9 (all blocks)

Let a finite group \(G\) act on itself by translation. A subset containing the
identity is a block if and only if it is a subgroup. Therefore every block
system is the set of cosets of a subgroup.

### Proof

Every subgroup and its cosets plainly form a block system.

Conversely, let \(B\) be a block containing \(0\). For any \(b\in B\), the
translate \(b+B\) contains \(b\), so it intersects \(B\). The block property
forces \(b+B=B\). Hence \(B\) is closed under translation by its elements.
In particular, \(b+B=B\) implies \(b+b'\in B\) for every \(b'\in B\).
Because \(0\in b+B=B\), there is some \(c\in B\) with \(b+c=0\), so
\(c=-b\in B\). Thus \(B\) is a subgroup. ∎

### Corollary 10 (many quadratic decompositions)

Let \(s=m-2\). The group \(G\cong\mathbb F_2^s\) has \(2^s-1\) index-two
subgroups, one for each nonzero linear functional. Hence the splitting field
has \(2^{m-2}-1\) quadratic intermediate fields.

Over each such quadratic field, the polynomial factors into two factors of
degree \(2^{m-3}\). More generally, every subspace flag gives a tower of block
factorizations.

### Cryptanalytic boundary

The recursive resultant construction realizes a natural coordinate flag.
It does **not** follow from Proposition 9 that every other flag is
algorithmically equivalent or equally dense. Establishing that would require a
separate sparsity/elimination theorem. The alternative flags are therefore a
well-defined remaining research direction, not a claimed speedup.

---

## 6. Finite-field Frobenius and factorization

Now take \(k=\mathbb F_q\), with \(q\) odd. Let
\(a=(a_2,\ldots,a_m)\in\mathbb F_q^r\) satisfy:

1. \(f(a_i)\ne0\) for every \(i\);
2. the specialized polynomial has degree \(d\); and
3. the signed-sum roots remain distinct.

Call such a specialization **good**. Choose square roots
\(y_i\in\mathbb F_{q^2}\), and put

\[
  \chi_i=\chi(f(a_i))\in\{\pm1\}.
\]

Then \(y_i^q=\chi_i y_i\).

### Theorem 11 (all-or-nothing factorization law)

At a good specialization, Frobenius acts on root labels by translation by the
class

\[
  [\chi_2,\ldots,\chi_m]
  \in\{\pm1\}^r/\{\pm(1,\ldots,1)\}.
\]

Therefore:

1. if all \(\chi_i\) are equal, the polynomial splits into \(d\) distinct
   linear factors over \(\mathbb F_q\);
2. otherwise, it factors into exactly \(d/2\) distinct irreducible quadratics.

In particular, every good specialization splits completely over
\(\mathbb F_{q^2}\).

### Proof

Frobenius sends \(P_i=(a_i,y_i)\) to
\((a_i,\chi_i y_i)=\chi_iP_i\). Hence

\[
 \rho_{[\varepsilon]}^q
 =x\left(\sum_i\varepsilon_iP_i\right)^q
 =x\left(\sum_i\varepsilon_i\chi_iP_i\right)
 =\rho_{[\chi\varepsilon]}.
\]

This is translation by \([\chi]\) in the regular root-label group. The class is
trivial exactly when \(\chi=(1,\ldots,1)\) or
\(\chi=(-1,\ldots,-1)\), i.e. when all characters agree. Corollary 7 then gives
the two possible cycle types. Frobenius cycles are the irreducible-factor
degrees of a separable polynomial over a finite field. ∎

### Corollary 12 (rational and twist loci both split)

Complete splitting occurs on both:

- the all-square locus, where every \(a_i\) lifts to a non-2-torsion point of
  \(E(\mathbb F_q)\); and
- the all-nonsquare locus, where every \(a_i\) lifts to a point of the quadratic
  twist over \(\mathbb F_q\), or equivalently a trace-zero point of
  \(E(\mathbb F_{q^2})\).

Thus complete splitting is a common-character phenomenon, not a property unique
to the usual rational-point factor base.

### Corollary 13 (no partial splitting on the good locus)

A mixed character vector has no fixed root. Hence a good mixed-character
specialization has no linear factor at all.

This is stronger than saying the average split rate is constant: it gives the
entire factor-degree profile.

---

## 7. Exact character counts and split density

Let

\[
  Z=\#\{x\in\mathbb F_q:f(x)=0\},\qquad
  t=q+1-\#E(\mathbb F_q).
\]

Let \(S\) and \(N\) be the counts of \(x\in\mathbb F_q\) for which \(f(x)\) is,
respectively, a nonzero square or a nonsquare.

### Lemma 14 (square/nonsquare counts)

\[
  S=\frac{q-t-Z}{2},\qquad
  N=\frac{q+t-Z}{2}.
\]

### Proof

Each nonzero square value gives two affine points, each zero gives one, and the
point at infinity contributes one. Therefore

\[
 \#E(\mathbb F_q)=1+2S+Z=q+1-t.
\]

This gives the formula for \(S\), and \(S+N+Z=q\) gives the formula for \(N\).
∎

### Theorem 15 (exact Frobenius-class counts before collision removal)

Let \(r=m-1\). Among tuples with every \(f(a_i)\ne0\), the number with trivial
Frobenius class is

\[
  S^r+N^r
  =
  \left(\frac{q-Z-t}{2}\right)^r
  +
  \left(\frac{q-Z+t}{2}\right)^r.
\]

More generally, if a quotient sign class has a representative with \(w\)
negative entries, its exact tuple count is

\[
  S^{r-w}N^w+S^wN^{r-w}.
\]

### Proof

A quotient class consists of a character vector and its simultaneous negative.
The two representatives with \(w\) and \(r-w\) negative entries contribute the
two monomials. The identity class consists of the all-positive and all-negative
vectors. ∎

Let \(Q=q-Z\). The complete-splitting character density is

\[
 \frac{(Q-t)^r+(Q+t)^r}{2^rQ^r}
 =
 2^{1-r}
 \sum_{\substack{0\le j\le r\\j\ {\rm even}}}
 \binom rj\left(\frac tQ\right)^j.
\]

Using \(|t|\le2\sqrt q\), for fixed \(m\) this is

\[
 2^{1-r}+O_m(q^{-1})
 =2^{2-m}+O_m(q^{-1}).
\]

The generic bad set is contained in the zero locus of a nonzero denominator/
discriminant polynomial. For fixed \(m\), removing it changes counts by at most
\(O_m(q^{r-1})\). A submission should make the degree-dependent constant
explicit if it claims a uniform-in-\(m\) estimate.

### Correction of terminology

The all-square condition is not a proper algebraic “measure-zero locus” in the
finite-field counting problem. It is an arithmetic quadratic-character
condition with density approximately \(2^{-r}\) for fixed \(r\). A small
factor base may of course be sparse inside that set, but the rational-liftable
condition itself has constant density.

---

## 8. Conservation with the sign quotient made explicit

The abstract conservation identity in `KN-FIND-007` counts fibres of a map from
a finite family of decomposition witnesses to the group. To combine it with
Semaev polynomials, the witness signs must be retained.

Let \(D_x\subset\mathbb F_q\) contain only \(x\)-coordinates with
\(f(x)\) a nonzero square. Choose one lift \(P_x\in E(\mathbb F_q)\) above every
\(x\in D_x\). For ordered arity \(m\), define

\[
 C_{D_x}(R)=
 \#\left\{
 (x_1,\ldots,x_m,\varepsilon_1,\ldots,\varepsilon_m):
 x_i\in D_x,\ \varepsilon_i\in\{\pm1\},\
 \sum_i\varepsilon_iP_{x_i}=R
 \right\}.
\]

### Theorem 16 (signed-witness conservation)

\[
 \sum_{R\in E(\mathbb F_q)} C_{D_x}(R)
 =2^m|D_x|^m.
\]

Therefore the whole-group mean signed-witness count is

\[
 \frac{2^m|D_x|^m}{\#E(\mathbb F_q)},
\]

independent of the geometry of \(D_x\).

For typed bases \(D_1,\ldots,D_m\), the total is
\(2^m\prod_i|D_i|\).

### Proof

Every pair consisting of an ordered \(x\)-tuple and a sign vector maps to
exactly one group target. Summing the sizes of all target fibres recovers the
size of the domain. ∎

### Corollary 17 (what can still vary)

The following are not fixed by Theorem 16:

- the number of distinct \(x\)-tuples admitting at least one witness;
- witness multiplicity per tuple;
- target coverage and concentration;
- relation rank and independence;
- the cost of finding a witness; and
- the elimination or linear-algebra cost.

For the zero target, global sign reversal pairs witnesses. Counting distinct
Semaev tuples without multiplicity is therefore a support statistic, not the
conserved witness mass.

### Why this matters

Complete splitting says where the roots live and how a specialized polynomial
factors. It does not by itself increase total decomposition witness mass.
A claimed relation-rate gain must specify whether it changes support,
multiplicity, recognizability, rank, or solving cost.

---

## 9. The \(m=3\) discriminant as a consistency check

For

\[
\begin{aligned}
S_3(x_1,x_2,T)
={}&(x_1-x_2)^2T^2\\
&-2\big((x_1+x_2)(x_1x_2+A)+2B\big)T\\
&+(x_1x_2-A)^2-4B(x_1+x_2),
\end{aligned}
\]

direct expansion gives

\[
 \operatorname{disc}_T(S_3)
 =16(x_1^3+Ax_1+B)(x_2^3+Ax_2+B).
\]

It follows that, away from ramification and degree drop, the two roots split
over \(\mathbb F_q\) exactly when
\(\chi(f(x_1))=\chi(f(x_2))\). This is Theorem 11 at \(m=3\).

`verify.py` checks the identity symbolically rather than relying on the prose
derivation.

---

## 10. What is proved, what is conditional, and what remains open

### Proved in this dossier, conditional only on standard Semaev facts

- independent Kummer square classes;
- generic distinctness of the signed-sum roots;
- splitting field \(L^{\langle\delta\rangle}\);
- monodromy \((C_2)^{m-2}\) with regular action;
- generic irreducibility;
- the two cycle types;
- square discriminant for \(m\ge4\);
- classification of every block system;
- finite-field all-linear/all-quadratic factorization;
- exact character counts; and
- signed-witness conservation.

The imported standard facts are the Semaev vanishing criterion and degree in a
variable.

### Not proved here

1. **Novelty.** A targeted search has not yet been replaced by a systematic
   MathSciNet/zbMATH/citation-graph review.
2. **Uniform bad-locus degree bounds.** The fixed-\(m\) \(O_m(q^{r-1})\)
   statement is enough for scope, but the constant has not been optimized.
3. **Algorithmic value of alternative flags.** The subgroup lattice exists;
   no speedup is claimed.
4. **Unweighted relation-count conversion.** The exact relation between
   witness-weighted counts and each experiment's unordered/multiset convention
   requires stabilizer accounting.
5. **Characteristic two and three.** Different curve models and Artin–Schreier
   structure require separate treatment.
6. **Higher-genus or extension-field covers.** No transfer is claimed.

### Explicit non-claims

- No ECDLP speedup.
- No change to Pollard-rho security estimates.
- No claim that complete splitting makes point decomposition easy.
- No claim that every imprimitive decomposition is useful.
- No claim that the theorem package is novel until primary-literature review is
  complete.

---

## 11. Required independent review before promotion

A publication or ledger promotion should require all of the following:

1. an arithmetic-geometry reviewer reconstructs Theorem 4 from scratch;
2. a separate reviewer checks Lemma 2 in positive characteristic;
3. the exact Semaev convention is matched against the primary 2004 definition;
4. symbolic \(m=4\) and at least one \(m=5\) specialization check the predicted
   field and factor degrees;
5. the discriminant-square corollary is checked independently;
6. the experiment conventions are mapped to Theorem 16 without silently
   changing ordered/unordered or witness/support counts;
7. a novelty review searches for “summation polynomial splitting field,”
   “Semaev Galois group,” signed-sum covers, and Kummer quotients;
8. the alternative-subspace-flag question is tested against the standard
   resultant for sparsity and elimination degree; and
9. any closure or breakthrough claim receives the repository-required
   independent high-effort review.

---

## 12. Repository provenance

This dossier refines and cross-checks:

- `knowledge/findings/KN-FIND-007.md`;
- `knowledge/findings/KN-FIND-c41ea9.md`;
- `knowledge/findings/KN-FIND-a1f3c2.md`;
- `knowledge/open-problems/KN-OPEN-009.md`;
- `experiments/EXP-FB3-001/conservation.md`; and
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-061/tasks/`
  `TASK-20260804-054/monodromy_analysis.md`.

The existing records remain unchanged. This directory is a reviewable proposal
for the correction and proof package that should precede any future promotion.
