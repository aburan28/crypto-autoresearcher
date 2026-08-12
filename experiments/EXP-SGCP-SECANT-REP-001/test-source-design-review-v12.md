# Handoff: Test-source design V12 review

## Status

Theory and accounting: `REVISE`.

## Evidence so far

- Commit `9002d14e9d1a22d360a076ecdef8d5c0052e5b17`, tree
  `cbc9f6c8656e7869efd301868f0c1a9afad84a16`, and all supplied digests
  match.
- Literal authorization arrays, principal disjointness, carry-forward locks,
  permitted import surface, and no-shared-body restriction pass.
- The prospective test path remains absent and all runtime authority remains
  false.

## Failure modes

- The decision rationale is required but not fixed to a literal value.
- Receipt references do not explicitly require exact `role,path,sha256` keys,
  mapped retained paths, and byte-identical digest resolution.
- The immutable review target is described but not retained as one literal
  commit/tree/digest tuple.
- Receipt `experiment_id` is not explicitly fixed.

## Next concrete action

Publish a non-self-referential target manifest and a V13 amendment binding that
manifest, a literal rationale, exact receipt references, and literal receipt
identity rules.
