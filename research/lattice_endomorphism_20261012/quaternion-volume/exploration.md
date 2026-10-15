# Quaternion volume: pair generation, closure collisions and the prime gate

Recorded2026-10-14 by `/root/lattice_exploration`, Idea Generator for
TASK-20261012-7017ce. Proposal IDEA-20261014-6e60f1; RQ-SSI-3e3f54;
planned EXP-SSI-39bae9. **Derivation tier; independent review pending.**
No scientific trial, performance measurement or status decision is recorded.

## The exact supplied model and trace normalization

Start in the Hamilton quaternion algebra over Q:
\(i^2=j^2=-1\), \(ij=k=-ji\). Its finite ramified prime is2.
The supplied Hurwitz order has basis \((1,i,j,h)\), where
\(h=(1+i+j+k)/2\). Voight's Lemma11.1.2 proves maximality using the
equivalent generator omega=h−1 and establishes that the Lipschitz order
\(\mathbb Z[1,i,j,k]\) has index2 in Hurwitz. The algorithm is supplied
this maximal order and multiplication; it does not derive it from a curve.

Conjugation negates the imaginary coordinates. Reduced trace is twice the
real coordinate, and reduced norm is the sum of four squared coordinates.
The reduced-trace pairing is twice the Euclidean dot product:
\(G_{rs}=\operatorname{Trd}(a_r\bar a_s)\).
For the Hurwitz basis,

\[
G_O=\begin{pmatrix}
2&0&0&1\\0&2&0&1\\0&0&2&1\\1&1&1&2
\end{pmatrix},\qquad \det G_O=4.
\]

An independent check uses its Euclidean coordinate determinant1/2:
\(\det G_O=2^4(1/2)^2=4\). For any full-rank L contained in O,
with basis matrix B in the ambient basis, \(G_L=B^T G_O B\), so
\(\det G_L=4\det(B)^2=4[O:L]^2\).
This scaling holds for **lattices**, regardless of multiplication closure.
The general maximal-order version is \(p^2[O:L]^2\) for
\(B_{p,\infty}\); the first implementation only instantiates p2.

The quadratic norm matrix is G/2, so in rank4 its determinant is
\(\det G/16\). Mixing these conventions silently changes the inferred
index by4. Internal H-SSIQ-a9df38 already distinguishes the normalizations
and the limited shortest-vector meaning of determinant-only bounds; it is
related work, not experimental evidence for this pilot. Determinant gives
no lower bound on the actual shortest endomorphism or isogeny degree.

## Noncommuting pairs have full rational span but may be incomplete

Write \(a=a_0+u\), \(b=b_0+v\), with imaginary vectors u,v.
Subtracting scalar and lower-degree terms converts basis candidates
\((1,a,b,ab)\) to \((1,u,v,u\times v)\) by determinant-one
column operations. Thus noncommutation (nonzero u×v) is equivalent to rank4
of this **product span**, not rank4 of the two-element additive span.
Moreover, with \(A=|u\times v|^2\),

\[
\det G(1,a,b,ab)=16 A^2,\qquad
[a,b]=2u\times v,\qquad
N([a,b])=4A,
\]

so \(\det G=N([a,b])^2\). For a,b in supplied Hurwitz O and
noncommuting, the pair-product lattice has
\([O:L]=N([a,b])/2\). This is a compact **derived diagnostic**, awaiting
independent review; it is not a measured improvement in scoring cost.
For a general supplied maximal O of prime discriminant p, the same
determinant identity would give index N([a,b])/p under the same assumptions.
Practical evaluation of the commutator from actual curve maps is not free.

For two actual elements of one quaternion order the product-span lattice
is closed. Their reduced characteristic equations reduce a² and b², and

\[
ba=-ab+\operatorname{Trd}(a)b+\operatorname{Trd}(b)a
 +\operatorname{Trd}(ab)-\operatorname{Trd}(a)\operatorname{Trd}(b)
\]

reduces the reverse product with integral coefficients. This proves that
\(\mathbb Z[1,a,b,ab]\) is the generated order when rank4. Still,
verify multiplication explicitly in the implementation; arbitrary independent
full-rank lattices do not inherit pair-product closure.

The pair i,j gives Lipschitz: commutator2k, norm4, determinant16,
index2. The pair i,h gives Hurwitz: commutator k−j, norm2,
determinant4, index1. Explicitly h−ih=1+j, so the generated ring contains
j and hence k=ij; it already contains h. Both pairs have individual norms1
and1 and are noncommuting; shortest-generator norms and noncommutation alone
cannot distinguish complete generation. These are symbolic controls, not
observations or an unknown-map discovery result.

## An equal-volume closure collision

Define
\(L=\mathbb Z\langle1,i,j,2k\rangle\) and
\(R=\mathbb Z\langle1,i,j+k,j-k\rangle\).
Each lies in Hurwitz, is integral, has rank4 and index4. Both therefore have
determinant64, but only R is closed.

L fails because ij=k is missing. For R, set x=j+k and y=j−k.
Then i²=−1, x²=y²=−2, ix=−y, iy=x,
xi=y, yi=−x, xy=−2i, yx=2i. These products certify closure.
Their Gram matrices are diag(2,2,2,8) and diag(2,2,4,4), respectively,
both determinant64. This collision disproves closure inference from
(rank, determinant, integrality) alone in the supplied model. It does not
contradict a complete ambient-containment equality certificate.

The coordinator also freezes
\(L'=\mathbb Z\langle1,2i,2j,3k\rangle\).
Here (2i)(2j)=4k is missing, index24 and determinant2304.
Keep this independent nonclosure control alongside the equal-volume pair;
its numbers too are derived, not run output. Invalid nonintegral rational
lattices and rank-deficient commuting spans must be classified before taking
an index square root. If a contained rank4 L has determinant4, it equals
the supplied O, hence is closed and maximal in this algebra; that argument
does **not** certify any identification with a curve's geometric End(E).

## Selection and characteristic-prime obligations

Use the fixed coordinator candidate domain: coefficients −1,0,1 in the
Hurwitz basis. Compare index/volume-driven and norm-driven selection only
on that common pool and price all enumeration, scoring, pair products,
commutators, lattice updates and certificate checks. A determinant score
may help post-discovery selection; every candidate's actual-curve acquisition
remains a different and possibly dominant task. No new exponent, time or
memory advantage is asserted, and no prime-independent distribution is
assumed from this unusually symmetric small algebra.

Keep exact characteristic-zero **lattice division** separate from actual
finite-field **etale torsion certification**. Dividing a supplied Hurwitz
element by2 can be tested by lattice membership. For a supersingular curve
in characteristic2, a point basis of E[2] cannot provide the usual two-point
etale module certificate. The full group scheme or another explicit faithful
construction is required. Odd primes3/5/7 are permitted for a future etale
interface if independently supplied; p2 does not make all algebraic division
invalid. Fuselier AppendixA.5's odd-prime p-saturation definition must not
be silently applied as a ready implementation at2.

## Four cheap audits and next experiment

1. **Baseline:** full Hurwitz, explicit products, determinant4 and
   Lipschitz index2. Independent coordinate and trace-Gram calculations.
2. **Collision:** equal-volume L/R closure pair, i/j versus i/h,
   commuting product span, coordinator L', half-Gram and nonintegral controls.
3. **Quantifiers:** every full-rank L **contained in certified O** has
   the volume identity; every noncommuting supplied pair has rank4 product
   span; none of that quantifies over unknown maps or certifies index1 for
   every noncommuting pair. At arbitrary p, actual-order certification and
   a model/map embedding are additional witnesses.
4. **Ceiling:** exact input-side order/index/closure diagnostics. A
   determinant-only shortest-vector estimate still has the classical
   full-rank ceiling discussed in H-SSIQ-a9df38 and cannot force a smaller
   actual minimum or a faster EndRing/isogeny/ECDLP algorithm.

The next bounded experiment is EXP-SSI-39bae9's supplied Hurwitz panel,
including the extra derived fixed controls above. Record every Gram entry,
rank/index, ambient coefficient vector, product closure witness, commutator,
candidate cost and division/certification gate separately. A full-rank included
volume disagreement first localizes normalization/instrument correctness;
a nonclosed equal-volume lattice is the intended discriminating control.
Passing the pilot motivates a **new** certified maximal order at an odd p,
then a separately frozen realization of a selected element as an actual
supersingular map. The initial lane remains open regardless of policy ranking.

## Source and retrieval receipt

Retrieved Voight's *Quaternion Algebras* PDF from
<https://jvoight.github.io/quat-book.pdf> on2026-10-14 into scratch
`/tmp/lattice-voight.pdf`; converted to text. Read Lemma11.1.2 and adjacent
Hurwitz passage (pp159–160), Lemma15.2.15 (p236), Theorem15.5.5 and
Example15.5.7 (p241). They support maximal Hurwitz/Lipschitz distinction,
index-squared discriminant scaling and prime-discriminant maximal orders.
The entire book was not reviewed. Browser fetch rejected its size; the
authorized network-enabled downloader succeeded. No credentials were read.

Retrieved Fuselier et al. <https://aiezzi.it/documents/art7.pdf>, reduced-trace
Gram definition (section2.2.1) and AppendixA.1–A.5 passages on2026-10-14.
Read-scope is those passages; not the full algorithm or complexity proof.
The retrieved Appendix explicitly separates quadratic module, multiplication,
generated order and enlargement. The pair commutator and equal-volume
derivations above are independently derived here, not represented as novel
theorems of that paper.

Generated indexes exposed H-SSIQ-a9df38; opened its full record for
normalization, ceiling and input-scope comparison. KN-OPEN-013 was read as
an adjacent historical knowledge stub; its cost summary is not adopted as
current state of the art. Frontier rows and unavailable KB MCP are recorded in the proposal/Hom receipt.
KN-TECH-080 is tracked but was not materialized in the sparse checkout; this
is not evidence of repository absence. Novelty remains
**unverified**; unavailable retrieval is not absence of related quaternion
generator-selection literature.

The material unresolved lift is a certified maximal order at another prime,
an explicit isomorphism/embedding into the geometric End(E), evaluable maps
with the declared field, and faithful full torsion/action certificates.
Exit criterion: a frozen actual supersingular instance with independent
trace/norm/composition, ambient maximality and map-action checks. That lifts
one certificate, not arbitrary-p discovery or any ECDLP cost claim. See
[the coordinator problem record](../coordinator/quaternion-volume/problem.md).
Root/Coordinator owns editable diagrams and inspected PDF; this note contains
no trial outcomes and no canonical graph correction supported by new evidence.
