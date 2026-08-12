# BATCH-037 scope decision — one certified nonlinear correspondence

Opening authority is DEC-20260802-220, implementing the sole exponent-first
successor selected by DEC-20260802-209 after DEC-20260802-211 superseded the
invalid BATCH-035 control plane.

The batch tracks one object: an explicitly represented, generically finite
algebraic correspondence `C_d ⊂ E × E`. From ordinary prime-order ECDLP input
`G,Q=[α]G`, it asks whether the object can acquire and publicly certify
`Z=[α^d]G` with fully charged expected single-instance exponent below `1/2`.

The first control is functional rigidity. A component that defines a rational
map from a normal curve to the proper curve `E` extends to a morphism (Stacks
Project tag 0BXZ). Under the exact abelian-variety hypotheses, the morphism is
a translation followed by a homomorphism (Milne 1986, Corollary 2.2). The
producer must state the subgroup-invariance assumptions needed to turn that
into affine action on the hidden scalar and derive the exact root obstruction
to `α ↦ α^d`. This conclusion must not be extended to arbitrary multivalued
correspondences.

If a genuinely multivalued object escapes that control, the producer must work
on its normalization; prove the projection degrees, branch count,
ramification, and exceptional fibers; give the correct-branch algorithm and a
sound public certificate; and charge equation/circuit size, setup, root
finding, evaluation, memory, data movement, inverse success, verification, and
the downstream Cheon solve. Description degree alone is not runtime.

Positive gate: a checkable construction and single-responsibility proof
architecture whose complete expected time exponent is strictly below `1/2`,
with memory and data/query exponents beside it.

Negative gate: a named obstruction proved for the exact representation class,
plus forward guidance naming the next class not covered. A count of failed
mechanisms is not closure.

Zero experiments, implementations, and Executors. GOAL-ECDLP-001 remains
active; H-IT-001 remains specified. Pollard rho remains the ordinary baseline;
ordinary SOTA deltas are zero. No support, rejection, knowledge promotion,
novelty, SOTA, closure, or breakthrough claim is authorized.
