# Order growth: actual index, full module action and paid selection

Recorded 2026-10-14 by `/root/lattice_exploration`, Idea Generator for
TASK-20261012-6a1e88. Proposal IDEA-20261014-2a4b38; RQ-ENDO-4a2bfa;
planned EXP-ENDO-854769. **Derivation tier; independent review pending.**
No scientific trial, measured policy advantage or official status decision.

## Quadratic ring generation is a gcd problem with exact assumptions

Let the supplied actual multiplier ring be
\(O_f=\mathbb Z+f\mathbb Z\omega\), with \(\omega^2=t\omega-n\).
Any supplied actual endomorphism is \(\alpha_j=a_j+b_j f\omega\),
\(a_j,b_j\in\mathbb Z\). The **unital** generated ring is

\[
\mathbb Z[\alpha_1,\ldots,\alpha_k]
=\mathbb Z+g f\mathbb Z\omega,\qquad
g=\gcd(b_1,\ldots,b_k),
\]

when at least one \(b_j\ne0\). Its index in the supplied O_f is g.
Proof decomposition: subtract integers to obtain \(b_j f\omega\);
Bezout gives \(g f\omega\); all products have noninteger coefficient
divisible by g because

\[
(a+bf\omega)(c+df\omega)
=(ac-bdf^2n)+(ad+bc+bdf t)f\omega.
\]

The ring \(\mathbb Z+gf\mathbb Z\omega\) is closed by the same
formula. Thus containment in it and generation of it establish equality.
If every b is zero, the ring is Z of rank1; do not interpret gcd0 as a
finite rank2 index. Explicitly include 1; additive generation without a unit
is a distinct task. A coefficient gcd oracle is a baseline, so any proposed
selection policy must disclose that it is operating on already supplied
endomorphisms whose complete coordinates are known.

Rank2 and closure do not certify saturation: \(O_{6f}\) has both but
index6 in O_f. Multiple collinear noninteger inputs, e.g. b6 and b12,
also do not improve that index. Once the unit is present, any noninteger
quadratic generator gives rank2, so rank growth becomes blind to almost all
subsequent conductor growth.

It is possible to be full rank and nonclosed even in the quadratic model
when the unit is omitted: in Q(i), \(L=2\mathbb Z+\mathbb Z i\)
has rank2, but \(i^2=-1\notin L\). Adding the unit closes that
particular lattice to \(\mathbb Z[i]\); that does not justify an
algorithm that silently assumes a unit or conflates additive rank and ring
closure. In this special supplied **unital quadratic** model the gcd argument
already proves closure; preserve the distinction for quaternion lifting.

## Division must use the actual multiplier lattice

For \(\gamma=a+b f\omega\), multiplication on \(\Lambda_f=O_f\)
is the matrix

\[
A_\gamma=\begin{pmatrix}a&-b f^2n\\b&a+bft\end{pmatrix}.
\]

For every positive integer ell,

\[
\gamma/\ell\in (\Lambda_f:\Lambda_f)
\iff A_\gamma\equiv0\pmod\ell
\iff \ell\mid a\ \text{and}\ \ell\mid b.
\]

More generally on any supplied lattice, gamma/ell preserves that lattice iff
gamma maps every basis vector into ell times the lattice. Zero action on
the **whole** quotient module is exactly the criterion, not one selected
image or just a characteristic polynomial condition. This is an elementary
containment derivation, not an empirical correlation. A modular change of
integral basis cannot change the zero operator predicate.

In the actual lattice \(O_2=\mathbb Z+2\mathbb Z i\), take
\(\gamma=2i\). Its norm is4, divisible by \(2^2\), and its
coefficients in the **maximal field basis** look divisible by2. But its actual
lattice matrix is
\(\left(\begin{smallmatrix}0&-4\\1&0\end{smallmatrix}\right)\),
which is nonzero mod2. Thus \(\gamma/2=i\notin O_2\). Its action on
the second quotient basis vector is zero, so a one-vector-only test can
also falsely accept it. This simultaneously controls norm-only division,
ambient-order confusion and incomplete module checking.

An existing suborder R can be enlarged by inspecting
\(\gamma\in R\cap \ell O_f\) and admitting verified
\(\gamma/\ell\). For \(R=O_{6f}\), \(6f\omega/2=3f\omega\)
and then \(3f\omega/3=f\omega\) are legitimate. Index decreases
6→3→1. A complete local saturation certificate requires **all** relevant
prime-index overorder directions to be excluded or adopted; merely checking
divisions of the initially named generators does not generally suffice.
In this rank2 unital model a primitive basis/gcd identifies those directions.
Factoring an unknown index is a separate cost; a planted factorization is not
free information for an unknown-ring algorithm.

If the supplied actual ring is nonmaximal O_f, successful saturation means
equality with that O_f. It must not enlarge to O_K merely because O_K is
mathematically an order in the same field. Matrix integrality on the actual
Lambda blocks precisely such invalid enlargement.

For actual finite-field E and ell different from its characteristic,
\(\gamma\) factors through \([\ell]\) iff it kills the full
ell-torsion subgroup scheme; an etale torsion basis can provide the module
test if it is faithful and complete. Explicit construction/certification of
the resulting divided map remains an interface obligation. At ell equal to
characteristic, geometric points need not detect the whole subgroup scheme;
an etale point-basis claim is invalid. Algebraic division by that integer in
the supplied characteristic-zero lattice is still meaningful. Do not merge
these two gates into one rejection rule.

## Selection policy: the quantity worth preserving

Compare policies on the same fixed candidate pool and starting suborder.
Index-first scores the genuine improvement
\(g\mapsto\gcd(g,b)\), perhaps choosing maximal index reduction per
fully counted selection cost. Norm-first ranks N(a+bf omega). Short scalar
candidates have norm1 and give no order growth; low norm can also favor
redundant noninteger candidates. A primitive noninteger candidate, when
available, immediately reaches index1, but the task of **finding** it can
dominate all supplied-input gcd work.

The coordinator's coefficient pool6/10/15 makes the difference concrete:
different orderings produce intermediate index trajectories such as
6→2→1 and6→3→1, while all three recover the same ring in the end.
Add scalar, collinear and primitive controls without making those convenient
controls available to only one policy. These are proposed symbolic
trajectories; no timing or policy advantage is observed here.

Required accounting separates candidate discovery/enumeration, norm/index
scores, rejected candidates, comparisons/tie breaks, exact lattice updates,
closure/membership tests and certificate verification. Diagnostic operation
counts are useful even if index-first spends more on scoring than it saves
in accepted updates. Any later speed claim needs matched baseline/candidate
evidence and independent review, with the progress-fidelity record. No local
selection statistic should become an end-to-end EndRing or ECDLP claim.

## Four cheap audits and next experiment

1. **Baseline:** 1 and f omega give index1; 1 and6f omega give a closed
   rank2 order at index6. Compute independent HNF index as a check on gcd.
2. **Collision:** rank2 proper suborders, unit-omitted nonclosure, scalars,
   collinear inputs and gamma2i in actual O2 versus a valid divisible
   gamma. Require all quotient basis vectors in the last control.
3. **Quantifiers:** every finite supplied unital quadratic set has the gcd
   ring; every actual multiplier has the exact full-module division test.
   There is no assertion that every candidate-discovery distribution makes
   index-first cheaper, or that the frozen panel tests a distribution.
4. **Ceiling:** complete saturation relative to the supplied actual ring;
   diagnostic selection counts on the specified pool. Ideal selection cannot
   certify an unknown curve's actual ring without authentic map/action input.

EXP-ENDO-854769 freezes eight discriminants, f1/2/3/6, b6/10/15,
module primes2/3/5/7, control generators and two integral lattice bases.
Complete exact index/action checks precede interpretation of any policy
comparison. An accepted invalid division is an instrument/certificate failure;
valid exact fixtures motivate a separately designed actual-map test. Neither
outcome abandons the saturation direction.

## Source receipt, remaining lift and interpretation

Bisson–Sutherland <https://arxiv.org/pdf/0902.4670>, introduction and section2
(pp1–3), read2026-10-14, establishes the actual/Frobenius order distinction
and ordinary order-discovery context. Fuselier et al.,
<https://aiezzi.it/documents/art7.pdf>, reduced-trace definition and
AppendixA.1–A.5 passages read2026-10-14, separates quadratic module,
multiplication structure, generated order and enlargement in the quaternion
setting. These are context: neither is claimed to contain the specific CM
gcd/division proof above. Full algorithm proofs were not audited.

Generated proposal/hypothesis indexes, named adjacent records and frontier
rows were checked as recorded in the proposal and the Hom note. KB MCP is
unavailable; KN-TECH-080 is tracked but was not materialized in the sparse
checkout, not evidence of repository absence. The four audits were read in
inventor-protocol section8. These limits leave novelty
**unverified**, not absent. No mathematical distribution heuristic is needed
for this deterministic panel; none is invented to suggest success at large p.

Material unresolved lift: authentic actual End(E) membership and full
ell-torsion/action/divided-map certificates, with field of definition and
candidate acquisition costs. Exit criterion: one actual ordinary fixture
with ell different from characteristic, full independently verified action,
explicit accepted divided map and independently certified residual/order
index. That establishes a scoped division/saturation lift, not a general
EndRing finder. See
[the coordinator problem record](../coordinator/order-saturation/problem.md).
Root/Coordinator owns editable diagrams and inspected PDF; no run is reported.
