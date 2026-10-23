# IC target timing is confounded with execution slot

- **Status:** investigating
- **Kind:** empirical confound / protocol gap
- **Affected work:** EXP-ICPERF-3065f9, EV-ICPERF-9bf9d7, DEC-20261023-d70a08; proposed wall-time claim only
- **Next action owner:** coordinator; TASK-20261023-e485d9
- **Last updated:** 2026-10-23

## Problem

The original public toy prime-field IC experiment cannot isolate a causal wall-time improvement because fixed_window always occupies the middle execution slot; reference arms occupy only the endpoints. Reversing the two references does not test a middle-slot effect.

## Evidence and uncertainty

Independent review TASK-20261023-18b489 found this exact association in all54 cells of RUN-ICPERF-842b51. Certificates, complete timing boundary, relation streams and operation counts are independently correct. C-target is not_isolated and evidence is preliminary; its numerical gate alone does not authorize promotion. Only12/14/16-bit public prime-field m2 small_x/mitm/scalar/harvest-off instances were measured. No mathematical impossibility, production-curve, rho or asymptotic conclusion follows.

## What would unblock it

- [ ] A prospectively frozen held-out workload crosses every arm with every execution slot within each curve/solver-seed cell.
- [ ] Complete setup/miss/LA/final-verification costs, failures, environment and CPU/load context are recorded without successful-only selection.
- [ ] Independent review confirms isolation, known-confounded/zero-advantage controls fail, and any claimed improvement meets the frozen gate.

These conditions are sufficient only for a scoped observation on the specified machine/workload, not hardware-wide or cryptographic extrapolation.

## Next discriminating step

Design EXP-ICPERF-6c546e with unseen curve seeds3/4/5, three cyclic slot rotations per exact target cell and opposite orientation for the two solver seeds. Bind dependency versions and CPU affinity; process census is diagnostic rather than proof of global isolation. Retain the original experiment unchanged. A positive independently verified result supports only the frozen toy scope; a negative or noisy result retains the reference default. Recheck after that exact raw snapshot and independent review.
