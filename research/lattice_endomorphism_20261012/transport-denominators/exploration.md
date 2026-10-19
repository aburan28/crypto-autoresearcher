# Transport denominators: primitivity, coordinate modules and anchors

Recorded 2026-10-14 by `/root/lattice_exploration`, Idea Generator for
TASK-20261012-3380fd. Proposal IDEA-20261014-25b2b6; RQ-ENDO-c5a7e4;
planned EXP-ENDO-aec0b2. **Derivation tier; independent review pending.**
No trial, observed performance gain or status decision is recorded.

## A direct matrix derivation

Take the principal supplied lattices \(\Lambda_f=\mathbb Z+f\mathbb Z\omega\),
where \(\omega^2=t\omega-n\). The primitive generator \(f\omega\)
acts in the basis \((1,f\omega)\) by

\[
A_f=\begin{pmatrix}0&-f^2n\\1&ft\end{pmatrix}.
\]

For source conductor \(f\), target \(g\), and \(d=\gcd(f,g)\),
multiplication by \(c=g/d\) is an isogeny of supplied tori. Its integer
matrix is \(M=\operatorname{diag}(g/d,f/d)\); its kernel has order
\(\det M=fg/d^2\). Column coordinates give

\[
M A_f M^{-1}
=\begin{pmatrix}0&-fgn\\f/g&ft\end{pmatrix}.
\]

The least positive denominator is \(g/\gcd(f,g)\). This follows from
reduced rational matrix entries, or independently from requiring
\(D f\omega\Lambda_g\subseteq\Lambda_g\).
Any nonzero scalar Hom isogeny gives the same rational scalar action on
the target; choosing \(c\) is convenient for a concrete integer matrix,
not a claim of optimal map discovery or evaluation. Inputs \(f,g\) are
planted; this is not an algorithm that extracts them from a curve.

For \(\gamma=a+b f\omega\), \(a,b\in\mathbb Z\), the target matrix is

\[
\begin{pmatrix}a&-bfgn\\bf/g&a+bft\end{pmatrix},\qquad
D(\gamma)=g/\gcd(bf,g).
\]

Primitivity modulo scalars means \(b=\pm1\) in the actual source order.
An arbitrary noninteger source endomorphism is not necessarily primitive.
For \(f=2,g=6\), primitive \(2\omega\) has denominator 3, but
\(6\omega\) has denominator 1. The latter is an honest target
endomorphism; it nevertheless conceals the denominator information expected
from a primitive source generator. Trace/norm or existence of a noninteger
map is not a source-primitivity certificate. Scalar additions do not repair
that deficiency. These numbers are derived controls, not experiment output.

## Ratios identify relative conductors, with a distinct gauge

Let \(D_{ij}=f_j/\gcd(f_i,f_j)\) for primitive source transport. Then
\(D_{ij}\) and \(D_{ji}\) are coprime and

\[
f_j/f_i=D_{ij}/D_{ji},\qquad
v_\ell(f_j)-v_\ell(f_i)
=v_\ell(D_{ij})-v_\ell(D_{ji}).
\]

A connected graph gives relative conductor ratios; cycle products must
equal 1. Unlike **product-only** Hom graphs, an odd cycle does not remove
the common-scale ambiguity: both \((f_i)\) and \((cf_i)\) have the same
denominator pairs for every positive integer \(c\). A denominator1 edge
only says that this primitive element is integral at the target; two
denominator1 directions say equal conductors, not maximality.

One independently certified actual conductor \(f_a\) fixes all ratios
in its connected component, provided the recovered conductors are integral.
Alternatively, declared local valuation anchors can fix particular primes.
A Frobenius conductor \(f_\pi\) restricts \(f_E\mid f_\pi\) but normally
does not select one global scale. Nor does normalizing the gcd of recovered
conductors to1 prove that actual orders attain that normalized scale.

There is a useful **later composition target**, not a present result: one
complete certified Hom product edge \(f_i f_j\), combined with a ratio
\(f_j/f_i\), fixes absolute \(f_i^2\). This could replace an external
anchor only if the product edge is genuinely complete; an incomplete scaled
edge inherits the previous lane's false certificate. Compare the cost of
that additional certified edge with direct actual-order certification before
calling it a cheaper anchor. No independence or free access is assumed.

## Coordinate changes and kernel descent

For unimodular source/target basis changes, least denominator is invariant:
integrality of \(D\gamma\) as a lattice operator is invariant. Multiplying
the isogeny matrix by a scalar also leaves its conjugated rational action
unchanged. Nonunimodular matrices need an explicit interpretation as a
sublattice or rational coordinate change; they are not interchangeable with
another integral basis of the same lattice.

For example on \(\mathbb Z[i]\), \(A=\left(\begin{smallmatrix}0&-1\\1&0\end{smallmatrix}\right)\).
With rational coordinates defined by \(S=\operatorname{diag}(1,2)\),
\(S^{-1}AS=\left(\begin{smallmatrix}0&-2\\1/2&0\end{smallmatrix}\right)\).
Its naive entry denominator is2, but the original lattice in the new
coordinates is \(S^{-1}\mathbb Z^2\), not \(\mathbb Z^2\).
The operator remains integral on that represented module. If one instead
chooses \(\mathbb Z^2\) in these coordinates, one has changed the actual
lattice to \(\mathbb Z+2\mathbb Z i\). Record the basis matrix **and
module** before attributing denominator changes to conductor changes.

For a scalar isogeny with \(c\Lambda_i\subseteq\Lambda_j\), the kernel
is the finite module \(\Lambda_j/(c\Lambda_i)\) after rescaling the
source. A source endomorphism \(\gamma\) descends to the target iff it
preserves this kernel. Since it already preserves \(c\Lambda_i\), the
additional requirement is \(\gamma\Lambda_j\subseteq\Lambda_j\).
Check this by containment and a Smith quotient representation; record
the intertwining identity \(A' M=M A\). Denominator1 and kernel
stability are equivalent for this correctly supplied scalar setup, but that
does not supply a kernel witness for an unknown finite-field map.

## Four cheap audits and next experiment

1. **Baseline:** primitive direct multiplication matrices in principal O_f;
   form M by source/target basis images, conjugate exactly, and compare a
   separately constructed target action and containment calculation.
2. **Collision:** common-scaled conductor networks; nonprimitive scales2/3;
   the \((2,6,3)\) cancellation; rational-coordinate modules versus genuine
   changed lattices; incompatible anchors and cycle products.
3. **Quantifiers:** every valid primitive supplied-source instance has the
   denominator identity; every connected consistent network has at most one
   solution **after specifying a compatible absolute anchor**. No universal
   primitive-map finder or unanchored absolute estimator is claimed.
4. **Ceiling:** ratios and verified integrality of specific supplied
   operators, not maximality or actual map acquisition. Even perfect
   denominator observations on a complete graph retain the global gauge.

EXP-ENDO-aec0b2 freezes eight discriminants, conductors1..12, scales1/2/3,
specified basis matrices, and quotient-module primes2/3/5/7. Record matrices,
modules, denominator pairs, primitivity provenance, cycle residuals,
anchor provenance, kernel witnesses and all counted operations. Failure in
valid primitive data localizes algebra/normalization; cancellation in
nonprimitive data is the expected control, not rejection of the lane. A
successful synthetic pilot leads to one actual curve/isogeny/primitive-map
fixture and independently certified actual-order anchor, with the total
discovery and certification costs charged.

## Source and scope receipt

Retrieved 2026-10-14: Bisson–Sutherland,
<https://arxiv.org/abs/0902.4670> and PDF
<https://arxiv.org/pdf/0902.4670>, introduction and section2, pp1–3.
Those passages distinguish actual conductor u and Frobenius conductor v
and frame class-group relation methods and conditional runtimes. They
are context, not the transport denominator proof above. The full algorithms
and certificate/runtime proofs were **not audited**. No numerical runtime
from that paper is quoted here.

Opened internal IDEA-20260905-1dd2e5; it is an auxiliary-arithmetic research
intake, not evidence of an advantage. Relevant prior conductor/transport
ideas were inspected through generated index excerpts. The ECDLP frontier
comparison and unavailable-KB receipt are shared with the Hom notes and
enumerated in this proposal. KN-TECH-080 is tracked but was not materialized
in the sparse checkout; this is not evidence of repository absence. No matching row is evidence of absence;
novelty remains **unverified**. Primitive matrices and graph arguments above
are elementary derivations awaiting independent review.

Material unresolved lift: certify an actual primitive source endomorphism,
the map's field/kernel, actual source/target orders and a compatible absolute
anchor. Acceptance requires independently checked identities and full kernel
action on a frozen actual instance. That establishes one denominator/ratio
lift, not an ECDLP shortcut. See
[the coordinator problem record](../coordinator/transport-denominators/problem.md).
Root/Coordinator owns diagrams and inspected PDF; no run evidence is created here.
