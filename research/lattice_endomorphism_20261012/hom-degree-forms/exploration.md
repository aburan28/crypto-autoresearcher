# Hom degree forms: completeness and graph identifiability

Recorded 2026-10-14 by `/root/lattice_exploration`, Idea Generator for
TASK-20261012-16a86e. Proposal IDEA-20261014-5a3847; RQ-ENDO-73c60f;
planned EXP-ENDO-371597. **Derivation tier; independent review pending.**
No scientific trial, experimental outcome or official status decision is recorded.

## Starting identity and an independent construction

Kani's *Products of CM elliptic curves*, Corollary 42, gives for a complete
Hom degree form

\[
\Delta=D_K\operatorname{lcm}(f,g)^2,\qquad
c=\operatorname{lcm}(f,g)/\gcd(f,g),\qquad
P=\Delta/(D_Kc)=fg.
\]

This is established literature, not the proposed novelty. The following
construction is an elementary derivation for the first implementation's
**principal supplied lattices**; it is not a construction from unknown curves.
Write \(O_K=\mathbb Z+\mathbb Z\omega\),
\(\omega^2=t\omega-n\), and \(D_K=t^2-4n\).
Take \(\Lambda_f=O_f=\mathbb Z+f\mathbb Z\omega\).
For \(\alpha=a+b\omega\), containment
\(\alpha\Lambda_f\subseteq\Lambda_g\) forces
\(a\in\mathbb Z\), \(b\in g\mathbb Z\) and \(g\mid fa\).
Conversely these conditions suffice on the two source basis vectors.
Thus, with \(d=\gcd(f,g)\), a full Hom basis is
\((g/d,g\omega)\).

Degree is the covolume quotient
\(q(\alpha)=N(\alpha)\operatorname{covol}(\Lambda_f)/
\operatorname{covol}(\Lambda_g)=N(\alpha)f/g\).
In that basis, putting \(s=fg/d^2\),

\[
q(x,y)=s(x^2+dtxy+d^2ny^2),\quad
\Delta=s^2d^2D_K=D_K\operatorname{lcm}(f,g)^2,\quad c=s.
\]

The coefficient of \(xy\) is the binary form coefficient, not a Gram
off-diagonal entry. These expressions are a comparison oracle; production
construction must solve containment and compute the norm independently rather
than call this formula twice. Nonprincipal CM lattices are a later scope.

## Incomplete bases and the collision that matters

For an integral nonsingular basis matrix \(B\) of index \(h=|\det B|\),
\(q_B(x)=q(Bx)\) has \(\Delta_B=h^2\Delta\).
Content need not scale in a fixed way for anisotropic restrictions. In
particular \(B=mI\) gives
\(q_B=m^2q\), \(\Delta_B=m^4\Delta\), \(c_B=m^2c\), and
\(P_B=m^2fg\).

Apply the same \(m>1\) restriction to all edges of a triangle. The usual
recovery \(\hat f_1^2=P_{12}P_{13}/P_{23}\) returns
\(\hat f_i=mf_i\), and every product-only cycle check passes. This is a
rigorous scoped **false completeness certificate** for the product-only
observable, with independent review pending. It does not refute Kani's
complete-basis identity.

An additional check defeats this particular collision: inferred conductors
\(mf_i\) predict discriminants \(m^2\Delta_{ij}\) and unchanged contents
\(c_{ij}\), whereas the restrictions produced \(m^4\Delta_{ij}\) and
\(m^2c_{ij}\). Retain and recheck both invariants. This catches uniform
scaling; it is **not a general completeness theorem** for arbitrary
sublattices. Search anisotropic and edge-dependent restrictions for further
fibers. The claim that merely consistent products certify full Hom must fail.

For a small hand-verifiable example in \(K=\mathbb Q(i)\), \(f=2,g=3\),
\(q=6x^2+6y^2\), \(\Delta=-144,c=6,P=6\).
Doubling the Hom basis gives \(24x^2+24y^2\),
\(\Delta=-2304,c=24,P=24\). Inferred endpoint conductors doubled to
\(4,6\) would instead predict \(\Delta=-576,c=6\).
All numbers in this paragraph are symbolic arithmetic, not measured output.

## Product graphs: exactly what is identifiable

For any prime \(\ell\), let \(x_i=v_\ell(f_i)\) and
\(s_{ij}=v_\ell(P_{ij})\). An edge imposes \(x_i+x_j=s_{ij}\).
Given one solution, the difference of two solutions satisfies
\(z_i+z_j=0\). Propagating along a path alternates its sign.

In a connected non-bipartite graph an odd cycle imposes \(z_i=-z_i\),
hence \(z=0\). So there is **at most** one positive rational conductor
assignment; existence still requires all cycle checks and positive integral
conductors. A triangle gives a rational square-root test before integrality.
The derivation is graph linear algebra, not a probabilistic claim.

In a connected bipartite graph with parts A,B, the kernel is one-dimensional:
\(x'_i=x_i+u\) on A and \(x'_i=x_i-u\) on B. For integral conductors,
each prime allows exactly the integer interval
\(-\min_Ax_i\le u\le\min_Bx_i\).
A rational one-dimensional family may intersect nonnegative integer
valuations in a singleton: if both parts have a valuation-zero vertex, that
prime allows only \(u=0\). Report the actual integer fiber, not just graph
bipartiteness. A connected product graph can be solved with rational tree
propagation and an odd-cycle square-root constraint without fully factoring
every product; exhaustive valuation-family enumeration requires factorization
and must account for that separate cost.

Path products \(12,18\) admit conductors \((2,6,3)\) and \((6,2,9)\).
A square alternating \(2,3\) also admits alternating \(1,6\) as a
product-only explanation. Full discriminant/content data add information:
they recover edge lcm and gcd, hence the unordered endpoint pair; the above
examples do **not** assert collision of the full forms. An alternating
\((2,3)\) versus \((3,2)\) labeling remains an ambiguity even with complete
forms on a bipartite square because each unordered edge pair is unchanged.
Isolated vertices and disconnected components each need separate treatment.

## Four cheap audits and the next experiment

1. **Baseline:** reproduce the full containment-derived Hom basis and both
   Kani invariants on the coordinator's eight fundamental discriminants and
   conductors 1..12. Identity matrix is the exact baseline slice.
2. **Collision:** retain doubled triangles, index-two anisotropic restrictions,
   bipartite examples and contradictory cycles. Distinguish product-only
   acceptance from joint-invariant acceptance in machine-readable output.
3. **Quantifiers:** universal identities require complete Hom; odd-cycle
   uniqueness requires valid products but does not certify their provenance.
   A finite exhaustive fixture panel tests only its supplied lattices.
4. **Ceiling:** certify supplied-input consistency, not actual unknown Hom
   completeness. Nearby incomplete bases must remain labeled incomplete even
   when products are consistent. A singleton bipartite integer fiber is not
   an odd cycle and must not be misclassified.

The next bounded experiment is the frozen matrix/basis/graph panel in
EXP-ENDO-371597. Independently calculate containment index, degree form,
discriminant/content residuals, conductor solution class and explicit
ambiguity witnesses. A complete-basis disagreement is initially an instrument
or normalization failure to localize, not an unexplained theorem refutation.
Passing controls motivates an actual Hom acquisition/certification study;
failure localizes the exact invariant or graph rule without retiring the lane.
Do not convert a finite panel into a universal completeness result.

## Literature and retrieval receipt

Retrieved and read 2026-10-14: Kani, Corollary 42 and its neighboring text,
authored paper transcription at
<https://paperzz.com/doc/6967916/products-of-cm-elliptic-curves>, corresponding
to DOI <https://doi.org/10.1007/s13348-010-0029-1>. The former author-site
CMprod.pdf URL redirected to a profile; it did not deliver that PDF. The
Corollary text was read; the entire paper and its referenced proofs were not
audited. The formulas are established starting inputs, not novelty support.

Generated-index searches read conductor/Hom/transport/saturation/quaternion
excerpts. Related conductor-vector proposals IDEA-20260807-3f5545 and
IDEA-20260807-a2b59a were visible in the index; only the adjacent intake
IDEA-20260905-1dd2e5 was opened in full. It records unresolved auxiliary-task,
transport and cost interfaces, not a successful experiment. Frontier matching
returned several index-calculus rows because of words such as trace/degree;
their actual claims are orthogonal. KR-RHO-755e35, KR-RHO-53c89f and
KR-RHO-13bf67 delimit isogeny/ECDLP interpretations, without implying all
endomorphism arithmetic is constant. All checked rows are listed in the proposal.

Crypto-KB MCP is unavailable. KN-TECH-080 is tracked in the repository but
was not materialized in the sparse checkout; this is not evidence of
repository absence. Inventor-protocol section 8 and the target-result profile
were read. Missing
retrieval is not absence of related work. Novelty remains **unverified**.
No invented timings, discovery success probability or source inspection is used.

The remaining material obstacle is an independently certified full Hom basis
from actual ordinary finite-field maps and actual conductor \(f_E\), separately
from Frobenius conductor \(f_\pi\). Exit criterion: one frozen actual-curve
instance with field, full-basis completeness proof, independently computed
degrees and actual-order certificate. That would validate one lifted
instance, not generic ECDLP transfer or an exponent change. See
[the coordinator problem record](../coordinator/hom-degree-forms/problem.md).
Root/Coordinator supplies editable diagrams and inspected PDF within its
assigned publication scope; these notes are derivations, not run evidence.
