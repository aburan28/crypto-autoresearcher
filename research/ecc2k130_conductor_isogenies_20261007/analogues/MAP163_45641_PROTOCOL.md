# K-163 degree-45,641 explicit forward-map gate

## Frozen question

Can one archived conductor-45,641 endpoint below NIST K-163 be upgraded from
an endpoint coefficient to a replayable kernel-polynomial isogeny evaluator
that preserves the standard prime-subgroup discrete logarithm?

This gate constructs one degree-45,641 descending edge.  It is preparation
for, not a substitute for, the complete five-arm transfer experiment in
`docs/experiments/koblitz-isogeny-rho-transfer.md`.

## Frozen implementation

Run `run163_45641_map.gp` as GP's direct input from this directory in
PARI/GP 2.15.2 (for example, `gp -q -f run163_45641_map.gp`).  Do not load
the driver with `read()`: GP abandons the remainder of an included file when
that file grows the PARI stack.  The driver allocates a 4 GB initial stack
with a 14 GB maximum before it calls `kernel163_45641_map.gp`, uses
deterministic seed 45,641, and refuses to append to an existing artifact.

The producer:

1. fixes the standard sect163k1 field, curve, generator, order, and cofactor;
2. derives the scalar action of q-Frobenius on 45,641-torsion and checks that
   kernel abscissae have relative degree 20;
3. constructs one exact-order kernel witness in `F_(2^(163*20))`;
4. enumerates all 22,820 half-kernel abscissae;
5. descends 1,141 degree-20 Frobenius-orbit factors and multiplies them over
   the standard NIST base field;
6. checks that the normalized codomain has the source point count and belongs
   to one of the six archived conductor-45,641 Galois orbits;
7. evaluates both coordinates with the kernel-polynomial characteristic-2
   Vélu formula; and
8. checks the mapped standard generator, prime-subgroup order, one frozen
   planted logarithm, and 16 deterministic homomorphism samples.

The emitted `kernel163_45641_map.txt` contains the complete kernel polynomial
from constant to leading coefficient, exact source/endpoint identities, the
mapped generator, and all frozen construction parameters.

## Admission and stopping rules

- The native degree-73 signed-map and 1,024-target bridge tests must pass
  before interpreting this run.
- Every exact identity above is fail-closed.  A failure is retained as an
  implementation result; parameters or samples are not changed after launch.
- The run is limited to one kernel, one endpoint, one planted scalar, and 16
  homomorphism samples.  It is not a runtime comparison and yields no ECDLP
  speedup estimate.
- Peak memory is capped at 14 GiB.  Timeout, OOM, field-construction failure,
  or inability to descend every coefficient makes this gate indeterminate.
- The raw artifact and stdout/stderr receive SHA-256 digests before review.

## Claim boundary and next gate

A pass establishes an explicit, replayable **forward** map on the standard
K-163 subgroup.  It does not yet establish the algebraic dual, either dual
composition, endpoint-to-source recovery, the transported action, or a weak
curve.

The next mandatory gate constructs a complementary 45,641-torsion line,
maps it to the endpoint to obtain the reverse kernel, and verifies
`dual(phi(P)) = [45641]P` and `phi(dual(Q)) = [45641]Q`.  Only then may the
five-arm cost experiment charge construction, forward map, dual, recovery,
native signed Frobenius, endpoint negation, and the transported action.
