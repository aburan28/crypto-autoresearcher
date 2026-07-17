# Analysis

## Current status

`OPEN`, `HYPOTHESIS`, `TOY-EVIDENCE`, and `MODEL-BOUND`.

The generator and independent verifier are implemented. A reduced noncanonical smoke run was used only to test determinism, invariants, and verifier integration; it is not experiment evidence and is not registered as a run.

The `v1` draft at commit `b28b813` received an independent `REVISE` verdict. The audit is preserved in `pre-run-audit-v1.md`. Protocol `v2` at commit `90ff031` closed its four required fixes and received an independent `GO`, preserved in `pre-run-audit-v2.md` with SHA-256 `541e36ea90f0aeb6e0146f42efbe6b8760ca2d5f32806f781210efa324cd0690`. The specification is approved for the two frozen toy runs only.

## V1 revision closure

- The promotion predicate now uses functional advice deep bytes, average online group operations, exact success probability, and subgroup order in a matched-random normalized `S*T^2/(epsilon*q)` metric. Entry count alone cannot pass.
- Generator output binds its own source and the imported coordinate-arithmetic source; the verifier recomputes and enforces both hashes.
- Duplicate-key and non-finite JSON rejection are explicit self-tests.
- The unimplemented shuffled-source promise was removed and replaced by a hash-chain control.
- The `p mod 4 = 3` field-prime restriction is emitted and disclosed.
- The contract now supplies every required frozen generator argument and the second-run verifier command.

## Implemented measurement boundary

- Exact support sizes are computed for every depth through `m`; unordered Poisson occupancy is diagnostic only.
- Sign-canonical and sign-complete schedules are compared.
- The compiler stores functional witnesses for the two split depths.
- Online search scans the smaller split support and stops at the first exact witness.
- Full `m`-fold expansion is separately counted as diagnostic work and excluded from compiler operations.
- Random-scalar and construction-matched random-x controls are both present.
- Factor-base construction, compiler, online query, diagnostic expansion, and rho counters are separate.
- The verifier independently reconstructs every arithmetic object, source hash, and exact promotion decision.

## Unresolved interpretation risks

- `sys.getsizeof`-based deep bytes are runtime-specific and do not measure allocator overhead, cache misses, or actual bandwidth.
- The normalized functional-byte `S*T^2/(epsilon*q)` field is an implementation diagnostic without a calibrated reduction to the generic preprocessing theorem.
- Exact support and a fast split lookup do not establish independent relations, matrix rank, sparse linear-algebra cost, or individual descent.
- Three toy sizes cannot justify an asymptotic exponent claim.

## Next decision

Run the frozen generator through the immutable wrapper. Commit that run, run the independent verifier as the second immutable run, and red-team the interpretation before any promotion decision.
