# Independent Red-Team Review: Typed Raw Circuit-TT Preflight V1

## Handoff: raw TT closure obstruction

### Claim or task

Determine whether the reported bond explosion is a valid obstruction to the
raw circuit wrapper, or an overclaim about minimal exact TT rank.

### Status

`ACCEPT WITH SCOPE`: valid negative for the declared raw closure, not a lower
bound for all TT or tensor-network representations.

### Evidence so far

- 12 registered rows replay exactly through an independently duplicated shape
  algebra.
- The producer contains no source-tuple enumeration.
- Direct-sum and Kronecker controls pass; three mutations are rejected.
- The raw maximum bond grows `96 -> 725,760 -> 4.04e13 -> 1.27e29`.
- The reported norm core-entry ratio over `B^5` is already above `1e114`.

### Main objections

1. Raw direct-sum/Kronecker bonds are representation upper bounds, not minimal
   TT ranks. Cancellation and exact rounding could lower them substantially.
2. The shape-only producer does not evaluate the RCB coordinates or replay
   source tensor values; semantic correctness is limited to the algebraic
   closure rules.
3. The verifier imports the producer for deterministic rerun, although it
   independently reconstructs the shape schedule and rejects mutations.
4. The entry count is a logical core-entry count, not resident allocator bytes;
   the actual allocation would be larger, not smaller.
5. The result is independent of curve coordinates and therefore cannot reveal
   coordinate-specific compression that exploits the registry.

### Strongest valid conclusion

For the frozen circuit, a naive exact TT formed solely by direct-sum addition
and Kronecker pointwise multiplication has catastrophic raw bond growth before
target specialization. Any viable source-TT route must introduce exact
compression, a common basis, or a different operator during construction.

### Next concrete action

Implement a small-curve exact TT-rounding/common-basis preflight. It must
compare the rounded cores against direct tensor evaluation, report every
compression elimination and field operation, and fail closed when the
compression path is not exact.

### Artifact paths

- `development/TYPED-RAW-CIRCUIT-TT-PREFLIGHT-V1/contract.md`
- `development/TYPED-RAW-CIRCUIT-TT-PREFLIGHT-V1/RUN-001/raw-result.json`
- `development/TYPED-RAW-CIRCUIT-TT-PREFLIGHT-V1/RUN-001/verification.json`
- `src/typed_raw_circuit_tt_preflight.py`
- `src/verify_typed_raw_circuit_tt_preflight.py`
