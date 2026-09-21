# Analysis

## Current status

`OBSERVATION`, `NEGATIVE RESULT` for split compression, `TOY-EVIDENCE`, and `MODEL-BOUND`. The wider coordinate-family hypothesis remains `OPEN`.

The canonical generator and independent verifier runs both completed valid and are immutable. A prior reduced smoke run remains non-evidence.

The `v1` draft at commit `b28b813` received an independent `REVISE` verdict. The audit is preserved in `pre-run-audit-v1.md`. Protocol `v2` at commit `90ff031` closed its four required fixes and received an independent `GO`, preserved in `pre-run-audit-v2.md` with SHA-256 `541e36ea90f0aeb6e0146f42efbe6b8760ca2d5f32806f781210efa324cd0690`. After execution, independent result review returned `REVISE_INTERPRETATION`; the specification is now `amended`.

## V1 revision closure

- The promotion predicate now uses functional advice deep bytes, average online group operations, exact success probability, and subgroup order in a matched-random normalized `S*T^2/(epsilon*q)` metric. Entry count alone cannot pass.
- Generator output binds its own source and the imported coordinate-arithmetic source; the verifier recomputes and enforces both hashes.
- Duplicate-key and non-finite JSON rejection are explicit self-tests.
- The unimplemented shuffled-source promise was removed and replaced by a hash-chain control.
- The `p mod 4 = 3` field-prime restriction is emitted and disclosed.
- The contract now supplies every required frozen generator argument and the second-run verifier command.

## Canonical result

- Generator raw SHA-256: `cf9e8fc8fa26bb5ea40e289bae435f0147ecc6e87da17482772528c8496d2890`.
- Verifier raw SHA-256: `a99acde52f07d52600fa89a93250b4e253eca70bcdbe5c25c165c4153b3f81b0`.
- The verifier replayed 216 configurations across six curves and reproduced all source hashes, curve orders, targets, factor bases, supports, witnesses, counters, rho trials, and promotion decisions.
- The frozen gate selected `rational_union`, `square_map`, and `x_interval` under sign-complete `m=8`, with counts four, three, and three.

## Result correction

- Every per-instance passing row had generic-maximum four-term support: `225` for `B=8` or `985` for `B=12`. Advice-byte ratios were approximately one. The result does not show split compression.
- The signal came from larger eight-term support/coverage and sampled first-witness work relative to one random-scalar draw.
- The independent random-x/random-scalar frontier ratios ranged from `0.5705` to `1.4155`; no family met the three-instance threshold against both controls.
- Seed `1473002` at 12 bits produced the anomalous curve `p=q=3931`, trace `1`. The candidate checklist excludes anomalous curves, but the generator and verifier rejected trace `0` only.
- The result-red-team verdict is `REVISE_INTERPRETATION`, preserved at SHA-256 `6ff6ba623b34bb363115b1a00d90b7ef9e67b0ca869c17ed8e5b9a7f465e5e77`.

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

Create `EXP-ECDLP-RECURSIVE-002` as a versioned successor. Reject trace `0` and `1` plus special `j`, estimate paired random-scalar/random-x null distributions, replace order-sensitive sampled scans with shuffled and order-independent controls, and require exact four-/eight-term support percentiles before promotion.
