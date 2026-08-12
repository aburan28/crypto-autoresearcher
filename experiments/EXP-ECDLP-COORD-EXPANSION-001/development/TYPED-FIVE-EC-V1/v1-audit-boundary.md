# V1 Aggregate-Only Audit Boundary

The successful output in `raw-result-v1.json` was produced from source commit
`a2f851ba` and is preserved without modification. Its source hashes are
self-consistent, all 15 rows completed, and its aggregate success gate passed.

That payload retained only the first independent equation and first successful
held-out descent per row. It therefore cannot support independent replay of
every claimed relation-rank and descent event. It is useful as a deterministic
development predecessor, not as the final evidence object.

The V2 successor adds:

- every relation target and every supported `A` split;
- all independent quotient equations and the attack-visible solution;
- every held-out target and both selected witness paths;
- canonical transcript digests;
- a standard-library-only independent verifier.

No V1 result field was edited or overwritten.
