# F7 source review before implementation

26 October 2026; worker `/root/pass2_geometry`, task TASK-20261026-59f4c9.
This source review precedes implementation and all second-pass observation
data. Native inherited model binding is unprobed; no novelty is asserted.

- **Internal, read:** prior F7 `exact.sage.py`, report, obligations, elliptic
  quotient record, map/cover review and Cartier-component derivation. The
  sextic `w^2=z^6-3z^2+b` has two rational infinities. Prior fibre Mumford
  congruences do not supply arbitrary-class arithmetic. The separate quartic
  component argument does not implement a Jacobian solver.
- **Retrieved and read:** [Galbraith, Harrison and Mireles Morales, full
  ANTS 2008 paper](https://www.math.auckland.ac.nz/~sgal018/ANTS08.pdf),
  sections 2–4, Algorithms 1–5 and their assumptions. The split model requires
  an infinity balance in addition to an affine Mumford pair. Its composition,
  reduction, balancing and inversion algorithms are the implementation
  reference. The IACR PDF endpoint returned HTTP 403; the author-hosted full
  version was accessible and read.
- **Retrieved and read:** [Galbraith's corrected book chapter 10](https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch10.pdf),
  split-model representation discussion. It distinguishes affine effective
  divisors from divisor classes and explains the infinity bookkeeping.
- **Retrieved and read:** [Sage issue 37109](https://github.com/sagemath/sage/issues/37109)
  and [Sage 10.6 Jacobian source](https://github.com/sagemath/sage/blob/10.6/src/sage/schemes/hyperelliptic_curves/jacobian_morphism.py).
  The reported ambiguous even-degree pair arithmetic prevents treating that
  API as an independent oracle here. No such API is invoked.

Implementation will use balanced triples `(u,v,n)`, with base divisor
`infinity_plus+infinity_minus`; the identity has `(u,v,n)=(1,0,1)`.
Both infinity-difference classes must survive. Polynomial congruences and
independent extension-field support sums check the norm. Matching norms never
proves class equality, because this norm has a nontrivial complementary
elliptic factor. Balanced arithmetic identities therefore receive separate
checks and explicit principal-divisor controls.

No primary source for a costed solver on the P-256 elliptic image has been
supplied by this review. This pass implements an interface, not an advantage
claim. The new protocol/export requirements and real S3 gate remain binding;
no pilot or observation panel may run before root's explicit Phase B release.
