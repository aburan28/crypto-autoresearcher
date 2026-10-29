# Geometry implementation: leads 1 and 5

This implementation is prospective until a frozen protocol and root launch
authorization exist. `run(config)` returns raw exact finite observations; the CLI
takes `--config` and `--output`. No scientific trial was run while writing it.

The frozen selector first finds the lexicographically first nonsingular generic
curve with nonzero a,b and prime group order different from p. It selects the least admissible
coset value c with at least five usable x coordinates. If none exists, the cell
is ineligible and is retained, never replaced by a curve selected for a favorable
solver outcome. The d=4 negative cell uses the least c without that filter.

Lead 1 has two different instruments. The forward census enumerates point
multisets and checks a coefficient representation. It is not a fast coefficient
solver. The p=17 inverse arm exhausts all four free coefficients of A and B,
deriving the fifth from the target equation, and tests the two membership
circuits directly. Every tested coefficient assignment is charged. It is a real
but exhaustive inverse search, with no asserted asymptotic gain. Neither arm
measures degree of regularity, solving degree, matrix rank, or full ECDLP work.
Hermite interpolation retains repeated point multiplicities; opposite signs at
the same x, target-x overlap, target identity and vanishing recovery denominators
are explicitly stratified. Prime group order excludes rational 2-torsion on the
lead 1 curves; lead 5 deliberately includes such exceptional points.

Lead 5 compares unsaturated closure, a certified finite-field saturation
presentation, and inverse-variable elimination. Let P=(u,v), h=x-u,
f1=y^2-(x^3+a*x+b), f2=h*l-y+v. Then

    h*(l*(y+v)-(x^2+u*x+u^2+a)) = f1+(y+v)*f2
    h*(1-h^(p-1)) = -(x^p-x)

over F_p when P is on the curve. These are checked coefficient identities, not
sample evaluations. The second identity is specific to finite-field equations.
The ideal with 1-h^(p-1) equals the h-nonzero component because all variables
also satisfy t^p-t. Inverse-variable elimination independently checks this ideal.
All h=0 additions, doubling, inverse pairs and identity inputs are restored by
explicit charts and checked against an independently written projective law.
SymPy does not expose a Macaulay solving-degree trace here: its output basis
degree and term counts are labelled only as output presentation observations.

Prior-art reconciliation at source commit d45d95e4c33f3cfbef5149718806a79e097c155c:
`experiments/EXP-SDEG-8dfcf9/` has only `specification.yaml` in the current tree;
`git log --all -- experiments/EXP-SDEG-8dfcf9/runs` returned no tracked run history.
The specification is `review_required` and names prospective RUN-SDEG-7dd157
and RUN-SDEG-74f830 artifacts. This is not evidence that external artifacts do
not exist. No predecessor result is reused or represented as reproduced.

Sources read before implementation:

- Original proposal IDEA-20261029-3d0e71 and derivation-notes.md: divisor chart,
  Graeffe sign convention, high-degree implicit membership and exclusions.
- IDEA-20261029-ec08bc and EXP-SDEG-8dfcf9 specification: guarded elimination
  predecessor, full exceptional coverage and no substitution of a pivot count
  for total solve work.
- Petit, Kosters, Messeng, sections 1 and factor-base framework:
  https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf . Low-degree
  towers and smooth p-1 cosets are prior art; no novelty or speed claim is made.
- SymPy polynomial reference, Groebner API:
  https://docs.sympy.org/latest/modules/polys/reference.html . Explicit field,
  variable order and algorithm are bound in the input.

All output timings are unisolated descriptive timings. Exact loop counters are
not a complete field-operation metric. Raw models, hashes, certificates and
input identities are retained for independent verification. Root owns freezing,
execution custody, exports, artifacts and scientific interpretation.
