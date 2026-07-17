# Analysis

## Current status

`OPEN`, `HYPOTHESIS`, `TOY-EVIDENCE`, and `MODEL-BOUND`.

The generator and independent verifier are implemented. A reduced noncanonical smoke run was used only to test determinism, invariants, and verifier integration; it is not experiment evidence and is not registered as a run.

The specification remains `review_required` with `approved_by: null`. No canonical generator or verifier run may be launched until a separate pre-run audit returns `GO`.

## Implemented measurement boundary

- Exact support sizes are computed for every depth through `m`; unordered Poisson occupancy is diagnostic only.
- Sign-canonical and sign-complete schedules are compared.
- The compiler stores functional witnesses for the two split depths.
- Online search scans the smaller split support and stops at the first exact witness.
- Full `m`-fold expansion is separately counted as diagnostic work and excluded from compiler operations.
- Random-scalar and construction-matched random-x controls are both present.
- Factor-base construction, compiler, online query, diagnostic expansion, and rho counters are separate.
- The verifier independently reconstructs every arithmetic object and exact promotion decision.

## Unresolved interpretation risks

- `sys.getsizeof`-based deep bytes are runtime-specific and do not measure allocator overhead, cache misses, or actual bandwidth.
- The `S*T^2` fields are diagnostics without a calibrated reduction to the generic preprocessing theorem.
- Exact support and a fast split lookup do not establish independent relations, matrix rank, sparse linear-algebra cost, or individual descent.
- Three toy sizes cannot justify an asymptotic exponent claim.

## Next decision

Obtain an independent `GO`, `REVISE`, or `NO-GO` pre-run audit. On `GO`, record coordinator approval in a separate Git commit, run the frozen generator through the immutable wrapper, run the independent verifier as a second immutable run, and red-team the interpretation before any promotion decision.
