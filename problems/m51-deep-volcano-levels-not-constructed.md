# m=51 deep volcano levels are not constructed

- **Status:** `open`
- **Kind:** implementation gap and proof gap
- **Affected work:** the unmeasured `f_E=120,871` and
  `f_E=271*120,871` levels in the [m=51 volcano study](../research/isogeny_volcano_m51_rho_20261013/README.md), its [frozen protocol](../research/isogeny_volcano_m51_rho_20261013/PROTOCOL.md), and any complete-level or vertical-transfer comparison for that isogeny class
- **Next action owner:** unassigned executor after a construction protocol is frozen
- **Last updated:** 2026-10-13

## Problem

We cannot yet measure the two deeper levels of the ordinary `m=51` binary
isogeny class because no durable curve model with independently certified
endomorphism conductor `f_E=120,871` or `f_E=271*120,871` has been produced,
and no explicit adjacent map/dual certificate reaches either level.

The fixed class is over
`F=GF(2)[z]/(z^51+z^6+z^3+z+1)` with trace `t=-38,684,515`, ambient order
`N=2,251,799,852,369,764`, prime subgroup order `r=17,192,986,687`, and

```text
Delta_pi = -7*(271*120,871)^2,
f_pi = 32,756,041 = 271*120,871.
```

The accepted experiment constructed and measured only `f_E=1` and
`f_E=271`. A same-action comparison at every conductor level requires valid,
precommitted models for `f_E=120,871` and `f_E=f_pi`; a vertical-transfer
comparison additionally requires executable maps, duals, subgroup
preservation, recovery, and complete cost accounting.

## Evidence and uncertainty

- **Observed:** the accepted [m=51 report](../research/isogeny_volcano_m51_rho_20261013/README.md)
  records 25,600 verified solves on the crater and 16 fixed representatives
  of the 272-model `f_E=271` slice. It explicitly states that the
  factor-120871 descent and bottom level were neither constructed nor
  measured. The sealed [archive](../research/isogeny_volcano_m51_rho_20261013/ARCHIVE.md)
  supports only that two-level scope.
- **Observed:** introducing revision
  `f0bdf9f739462766a9060532c59f9bfed69d00b1` contains the source
  `research/ecc2k130_conductor_isogenies_20261007/m51_m53/cm51_120871.gp`.
  It proposes constructing the degree-120,870 class polynomial, reducing and
  factoring it modulo 2, and writing `floor51_120871_cm.txt`. That revision
  contains the source but not the named output. Its `m5153.out` reports the
  structural values `h(-7*120871^2)=120870` and a kernel-field degree of
  `60,435` for the degree-120871 direction. These are planning facts, not a
  completed endpoint construction, map, or measured resource failure.
- **Derived or proved:** the arithmetic assessment in
  [`TRACE_ZERO_LANE.md`](../research/isogeny_volcano_m51_rho_20261013/TRACE_ZERO_LANE.md)
  derives that `tau^17` belongs to the orders of conductor 1 and 271 but not
  to the orders of conductor 120,871 or `271*120,871`. Thus negation is the
  currently specified native action common to all four levels. This does not
  predict a conductor-only collision-work effect.
- **Suspected explanation:** the high-degree class-polynomial and kernel
  constructions may be the practical bottleneck. No preserved attempt
  establishes which stage, algorithm, memory requirement, or runtime is
  limiting, so the cause remains unknown.
- **Missing capability:** two exact endpoint models and endomorphism-ring
  certificates; a fixed Frobenius-orbit sampling frame for any level-wide
  inference; and serialized or deterministically reconstructible adjacent
  maps and duals with point evaluation, exceptional-input handling, subgroup
  checks, recovery, and measured costs.
- **What this evidence does not establish:** it does not show that either
  deeper level is empty, unreachable, infeasible to construct, weak, or as
  hard as the measured levels. It does not establish a conductor effect or
  conductor independence. The completed `f_E=271` result cannot be
  extrapolated across the unmeasured factor-120871 gap or to the bottom.

## What would unblock it

- [ ] Produce a durable model `E_120871/F` with `#E_120871(F)=N` and an
  independently checked certificate that
  `End(E_120871) = Z + 120871 O_K`, plus a durable model `E_bottom/F` with
  the same order and
  `End(E_bottom) = Z + (271*120871) O_K`. Record complete curve identities,
  field encodings, construction inputs, commands, software versions, hashes,
  and failures. Class-polynomial membership and matching point count alone
  do not replace the exact endomorphism-ring certificates.
- [ ] Before a level-wide statistical claim, define the finite population of
  Frobenius orbits at each new level or freeze a deterministic orbit-sampling
  rule and its estimand. Select models before any rho outcome is observed;
  conjugate models are strata, not independent replicas.
- [ ] Before a vertical-transfer claim, provide an executable degree-120871
  map `phi:E_1 -> E_120871` and degree-271 map
  `psi:E_120871 -> E_bottom`, with their duals. A kernel-polynomial or other
  compressed representation is acceptable only if it deterministically
  evaluates the exact maps over `F`. Verify the fields and directions,
  exceptional loci, both identities
  `dual(phi) o phi=[120871]` and `dual(psi) o psi=[271]`, and the reverse
  compositions on the codomains. On the order-`r` subgroups, verify nonzero
  images of exact order `r`, preservation of planted scalars, recovery using
  the inverse degree modulo `r`, and verification back on the source.
- [ ] Freeze and execute a matched four-level negation-rho experiment using
  identical planted scalars and paired random-stream namespaces, separately
  charging construction, map-in, walk, recovery, verification, field
  primitives, memory, failures, and cold-start versus genuinely amortized
  work. Compare against the existing crater native-`tau` control as a
  separate action/transfer baseline; do not mix its symmetry discount into
  the same-action level contrast.

The first condition is sufficient to admit a model-level measurement on the
two missing levels. The second is additionally required for a level-wide
inference. The third is required for transfer or source-weakness claims. Even
all four conditions would establish only the frozen proxy measurements and
certified paths, not a NIST-scale result or a weak curve without a separately
predeclared and met end-to-end advantage criterion.

## Next discriminating step

- **Action or proof obligation:** replay the exact `cm51_120871.gp`
  construction from revision
  `f0bdf9f739462766a9060532c59f9bfed69d00b1` in a pinned PARI/GP
  environment and retain every intermediate needed to validate its intended
  120,870-entry `floor51_120871_cm.txt`. If the inventory validates, choose
  the least integer-encoded valid model under a frozen tie rule, certify its
  exact endomorphism ring, then construct and persist one degree-271
  descending map/dual to a bottom model. Do not choose an endpoint from rho
  outcomes.
- **Inputs and controls:** use the fixed field polynomial, `N`, `r`, and
  conductor factorization above. Pass the known crater `b=1` and
  `m51-floor-o01` through the same point-count and conductor classifier as
  positive identity controls, and require the classifier to reject their
  deliberately wrong deeper-level labels. Verify a candidate and its
  Frobenius conjugates without treating them as independent curves.
- **Execution limits and stop condition:** run one deterministic construction
  pass under recorded host safety limits; no scientific timeout or smaller
  substitute is predeclared. The pass ends only with a sealed, fully checked
  intended inventory or a preserved process termination/failure at a named
  stage. Stop all map and performance inference on the first field, order,
  conductor, map, dual, subgroup, or recovery failure. A safety watchdog or
  resource exhaustion is infrastructure/resource evidence, not a
  mathematical result.
- **Outcomes and next actions:** a certified `f_E=120,871` model admits the
  same-negation endpoint arm even if map construction remains open. A
  certified degree-271 child adds the bottom arm. Passing maps and duals admit
  a separately frozen transfer-cost experiment. A completed inventory with
  no valid exact-conductor model refutes that implementation's construction
  output and triggers an independent conductor audit; it does not prove the
  level absent. A process or resource failure identifies the stage to replace
  or checkpoint and leaves both levels unmeasured.
- **Recheck trigger:** a committed, independently replayed deeper-level model
  inventory or a committed explicit map/dual artifact for either missing
  direction.

A planned construction is not a completed experiment. It must use the
repository's execution, review, visual-record, and archival rules before its
outputs support an inference.

## Resolution and history

Unresolved. This record preserves the two unmeasured levels and their exact
construction and transfer obligations; it asserts no impossibility and no
weakness result.
