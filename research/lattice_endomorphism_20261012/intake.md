# Lattice methods for endomorphism rings: user-directed research intake

Recorded 2026-10-12. The user requests exploration, runnable experiments,
tracking in Crypto Autoresearcher, and a separate ready-for-review PR for each
of four directions. No merge or scientific promotion is requested.

## Scope and established starting points

Complex CM curves E_i = C / Lambda_i have multiplier rings
O_(f_i) = Z + f_i O_K in one imaginary quadratic field K. Without CM,
complex curves in the isogeny class have endomorphism ring Z. Ordinary
finite-field analogues require certified actual orders; Frobenius conductor
and actual endomorphism conductor are different quantities. Supersingular
geometric endomorphism rings are rank-four quaternion orders.

The first implementations must be exact synthetic algebra experiments,
not finite-field curve-map benchmarks. Represent supplied orders and rational
lattices explicitly. Report which inputs are planted/known and what is inferred.
No ECDLP, cryptographic-scale, novelty, or performance improvement is established.

## Four requested directions

1. Hom degree forms. For a complete Hom basis, q(x,y)=deg(xu+yv).
   Delta(q)=D_K*lcm(f_i,f_j)^2 and content(q)=lcm(f_i,f_j)/gcd(f_i,f_j).
   P_ij=Delta/(D_K*content)=f_i*f_j; a triangle reconstructs conductors.
   Explore incomplete Hom bases, conductor-product inference, graph
   identifiability, and false consistency under uniform sublattice scaling.
   Controls: actual full bases; index-two/scaled and anisotropic sublattices;
   bipartite graphs with ambiguous products; non-bipartite graphs.

2. Transport denominators. For an integer isogeny matrix M, transport an
   endomorphism A by M*A*M^-1. For the primitive CM generator f_i*omega,
   the least denominator is f_j/gcd(f_i,f_j). Both directions give signed
   conductor valuations. Explore reconstruction, anchors, nonprimitive
   generators, rational changes of basis, and kernel/module preservation.
   Use independently constructed multiplication matrices, not only the gcd
   formula as implementation and oracle.

3. Order growth and saturation. Compare generator-selection policies by
   actual discovered order index and full selection costs in planted CM
   orders. Test division of actual endomorphism gamma by ell via the exact
   action on Lambda/ell*Lambda. Distinguish additive rank, ring generation,
   and complete saturation. Reject misleading short/collinear generators.
   Keep any policy comparison diagnostic until matched independent evidence
   supports a qualified performance claim.

4. Supersingular/quaternion lattice volume. For full-rank L in a supplied
   maximal order of B_(p,infinity), G_rs=Trd(alpha_r*conjugate(alpha_s))
   has det(G)=p^2*[O:L]^2. Explore noncommuting generator pairs and
   determinant-driven selection against short/commuting controls.
   Begin with the exact Hurwitz order in B_(2,infinity), whose maximality and
   multiplication are checkable; this is one quaternion model, not an
   implementation of arbitrary supersingular curve maps. Separate integrality,
   multiplicative closure, full rank, and the characteristic-prime gate.

## Sources read in the initiating conversation

- Kani, Products of CM elliptic curves, Corollary 42.
  https://doi.org/10.1007/s13348-010-0029-1 ; primary paper text retrieved via
  https://paperzz.com/doc/6967916/products-of-cm-elliptic-curves .
- Bisson and Sutherland, Computing the endomorphism ring of an ordinary
  elliptic curve over a finite field. https://arxiv.org/abs/0902.4670 .
  Abstract retrieved; do not imply the full algorithm was inspected.
- Fuselier et al., Computing supersingular endomorphism rings using
  inseparable endomorphisms. https://aiezzi.it/documents/art7.pdf .
  Introduction and Appendix A Gram-matrix passages retrieved.

All proposal novelty labels remain unverified until a substantive audit.
Existing proposal indexes must be consulted and related work linked.

## Concrete delivery requirements

Each direction gets independent additive records, a bounded experiment with
exact checks and adverse controls, runnable code, meaningful regression tests,
machine-readable outputs when admitted to execution, a dated research report,
editable diagram/SVG and inspected PDF, and an open GitHub tracking issue.
Link existing GOAL-ENDO-001 where appropriate without rewriting its historical
evidence or marking it complete. A problem record names any material unresolved
lift, access, implementation, certification, or review obligation.

Use the existing run skill and supervisor for admitted scientific trials.
Development tests are software checks, not canonical experiment evidence.
Prepare all authorized implementation work before PR creation; stop at each
ready-for-review PR and do not watch CI or merge. Four proposals remain active
research directions after the initial pilots.
