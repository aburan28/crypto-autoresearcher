# K-163 degree-45,641 explicit forward-map gate

## Frozen question

Can one deterministic descending degree-45,641 endpoint below NIST K-163 be
upgraded from an endpoint coefficient to a replayable kernel-polynomial
isogeny evaluator that preserves the standard prime-subgroup discrete
logarithm?

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
6. certifies that the sampled kernel line is not either of the two
   `tau`-stable horizontal lines, using the two roots of
   `T^2-T+2 (mod 45641)`, and therefore descends from conductor 1 to 45,641;
7. checks the normalized codomain point count, non-source j-invariant, and the
   frozen deterministic endpoint orbit minimum; the six older sampled orbit
   minima are retained as non-gating metadata, not an exhaustive allow-list;
8. evaluates both coordinates with the kernel-polynomial characteristic-2
   Vélu formula; and
9. checks the mapped standard generator, prime-subgroup order, one frozen
   planted logarithm, and 16 deterministic homomorphism samples.

The emitted `kernel163_45641_map.txt` contains the complete kernel polynomial
from constant to leading coefficient, exact source/endpoint identities, the
mapped generator, and all frozen construction parameters.

## Admission and stopping rules

- The native degree-73 map/dual and 1,024-target recovery control must pass
  before interpreting this run.  The self-contained
  [`map73_dual_control.gp`](../../isogeny_volcano_rho_20261005/map73_dual_control.gp)
  constructs both degree-73 kernel-polynomial maps, fixes the dual sign,
  checks both compositions, and recovers every frozen target plus a separate
  planted target.  Its retained receipt is
  [`map73_dual_control.out`](../../isogeny_volcano_rho_20261005/map73_dual_control.out).
  Earlier forward-map and cross-basis bridge evidence is retained in
  `aburan28/crypto` commits
  [`03ac279b2`](https://github.com/aburan28/crypto/commit/03ac279b2e0945ab8b42561df50db5b4d8475cd6)
  and
  [`2ada30059`](https://github.com/aburan28/crypto/commit/2ada300594e486850842d2fa54bcc57f72cd58f1),
  with archived input SHA-256
  `eb4773d556886672e8b80735fc486c16b73765fd5069ff81133100bfc3eafa90`.
  Those earlier controls certify the forward signed map and cross-basis
  bridge, but their root-finding reverse path is not an algebraic dual.  The
  new local degree-73 control closes that proxy prerequisite; it does not
  discharge the degree-45,641 dual-composition gate.
- Every exact identity above is fail-closed.  A failure is retained as an
  implementation result; parameters or samples are not changed after launch.
- The run is limited to one kernel, one endpoint, one planted scalar, and 16
  homomorphism samples.  It is not a runtime comparison and yields no ECDLP
  speedup estimate.
- Peak memory is capped at 14 GiB.  Timeout, OOM, field-construction failure,
  or inability to descend every coefficient makes this gate indeterminate.
- The raw artifact and stdout/stderr receive SHA-256 digests before review.

## Deterministic endpoint preflight

PARI/GP 2.15.2 with seed 45,641 reaches orbit minimum
`24362196697750487851526857852297647817644684697`.  This is not one of the six
historical samples, as expected: the 45,640 descending lines form 280
absolute-Frobenius orbits of size 163, while the archive sampled only six.
The bounded preflight in `probe163_45641_seed.gp` stops before kernel-polynomial
construction.  A separate structural check found the same source and
target point count and horizontal degree-11 cycle length 9,128 (crater control
1), matching the archived conductor-45,641 predicate.  These checks repair the
old acceptance rule; they are not a forward-map, dual, runtime, or weakness
result.

## Relative-tower implementation status

[`probe163_45641_relative_tower.gp`](probe163_45641_relative_tower.gp)
replaces the absolute `F_(2^3260)` plus `ffembed` route with the direct tower
`F_(2^163)[u]/P_20(u)`.  Its retained bounded replay constructs an exact-order
descending witness and certifies its exact absolute x-coordinate degree 3,260
by closure plus all prime-factor exclusions.  By the prime-line/Frobenius
argument, the certificate applies to every nonzero multiple on the
prime-order kernel line.  The probe enumerates
all 22,820 half-kernel abscissae in 90 batched inversions and reaches endpoint
orbit minimum
`664574991296028830578085892445595444511031875`.  It intentionally stops
before the kernel polynomial and point map.

The retained standalone probes and controls must be launched through their
`run_*.gp` drivers.  The canonical command sizes the stack before the driver
calls `read()`; the driver catches unexpected GP exceptions, requires a
completion sentinel, and clears its token before returning.  Direct
implementation-file execution is
refused.  Injecting `GP_FAIL_CLOSED_FAULT=1` must terminate nonzero without a
success sentinel.

Stack sizing is part of the command line, never the included driver file:

```text
gp -q -f run_check_char2_velu_function_identity_small.gp
gp -q -f -s 64M run_control163_45641_horizontal_endomorphism.gp
gp -q -f -s 64M --default parisizemax=1G run_probe163_45641_relative_tower.gp
gp -q -f -s 1G --default parisizemax=8G run_probe163_45641_seed.gp
gp -q -f -s 1G run_verify163_45641_seed_endpoint.gp
```

[`kernel163_45641_map_relative.gp`](kernel163_45641_map_relative.gp) and its
driver implement the remaining forward-map construction with coefficient
descent and fail-closed map gates.  The exact function-field checker has a
passing degree-7 positive fixture and a wrong-endpoint negative control in
[`check_char2_velu_function_identity_small.gp`](check_char2_velu_function_identity_small.gp).
The full files are code-under-review, not a completed scientific execution:
no canonical experiment contract currently admits this run, no full artifact
has been emitted, and no construction-cost or weakness claim follows from
their presence.

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
