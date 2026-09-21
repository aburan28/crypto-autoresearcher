# Handoff: Pure-core V8 theory review

## Claim or task

Review the unchanged V7 mathematical design and the V8 trusted-local
Coordinator control plane at exact commit
`b672372fb6e810fa129f288ae0bca406cf5ace53`.

## Status

`OPEN` - `REVISE`.

## Assumptions

- Reviewed tree: `5227118bb4e70d0ac446b642c7b40feaf6ccfe71`.
- Reviewer principal: `019fac07-14aa-7f52-b47e-6a46d12cea57`.
- Review was static Git-object inspection only.
- No source writing, import, compilation, test, or experiment was authorized.

## Evidence so far

- The V6 API, V7 API amendment, V7 consistency object, and V7 source
  authorization are byte-identical to their reviewed V7 versions.
- The chart transform, pair partition, affine addition formulas, and successful
  operation counts remain internally exact.
- The V8 trust model is adequate, under its explicit trusted-local assumptions,
  for reversible creation of the singleton source-text path. It correctly makes
  no hostile-writer resistance or external-attestation claim.

## Failure modes

- The inherited exact V7 decision schema hard-codes V7 review receipt IDs and
  paths.
- V8 requires three exact-commit V8 GO reviews but defines no receipt schema or
  decision references capable of binding them.
- The required V7 red-team JSON GO receipt does not exist; the retained V7
  red-team artifact is Markdown with verdict `REVISE`.

## Next concrete action

Define fresh exact V9 review receipt paths, IDs, hashes, and decision references
that bind the immutable V9 review target while preserving every current lock.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-v6.md`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-amendment-v7.md`
- `experiments/EXP-SGCP-SECANT-REP-001/authority-trust-model-v8.json`
- `experiments/EXP-SGCP-SECANT-REP-001/source-authorization-amendment-v8.json`
