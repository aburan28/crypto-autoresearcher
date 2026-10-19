# Conductor lease gap during implementation

The local Conductor CLI task `T-5` initially held write scopes for this study and
`problems/`. Its lease expired at approximately 09:10:25 America/Los_Angeles on
2026-10-15. This session continued editing the prepared-input generator,
verifier, exact-interval code, controls and study notes before discovering the
expiry at approximately 09:16:30. The files were not published during that gap.

The follow-up CLI conflict check returned `allow`. Reclaiming `T-5` produced a
claim without scopes, then releasing it moved it to `cancelled`; it could not be
claimed again. Replacement task `T-20` was created with
`dir:research/conductor_relation_yield_20261014` and
`path:problems/prime-field-arity3-relation-oracle.md`, and claimed at
09:17:16 with fencing epoch 1 and lease expiry 09:27:16. No overlapping holder
was reported by the follow-up check. The unscoped interval remains a procedural
deviation, not relation-yield evidence. A reviewer should inspect this record
alongside the source and control receipts before formal protocol admission.
