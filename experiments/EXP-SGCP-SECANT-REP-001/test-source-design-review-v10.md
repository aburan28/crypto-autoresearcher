# Handoff: Test-source design V10 review

## Claim or task

Review exact V10 commit `3dada9996060953bb515bb9b1d52b2e64bde8e5c`.

## Status

`OPEN` - theory and accounting `REVISE`.

## Evidence so far

- All supplied hashes, the singleton absent test path, three distinct V4 source
  GO receipts, and the zero-run/runtime locks are valid.
- Authoring one inert test file is proportionate after a corrected exact
  transition.

## Failure modes

- Three invariant-only error codes are unreachable through the public API.
- Per-pair internal branch labels are not all observable in the returned value.
- Receipt and Coordinator-decision schemas are not exact.
- V6, V7, and the V9 decision need direct bindings.
- Test-author and reviewer principal independence is not closed.
- Protected-source inspection, external inputs, introspection, monkeypatching,
  and test-source parse/import/compile/execute locks are incomplete.

## Next concrete action

Publish V11 with an exact one-path decision schema, a distinct bound test author,
publicly observable controls, invariant-only static obligations, direct
provenance hashes, and closed-world forbidden actions.
