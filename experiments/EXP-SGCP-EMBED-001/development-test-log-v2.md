# SGCP source-repair v2 development test log

Status: DEVELOPMENT ONLY. The worktree was dirty, no canonical certificate was
written, and these hashes are not a source freeze.

## Source bindings

- builder SHA-256: `ee82edc62ef1d1f14a53ea9f2beaa538eeb845e09ae29f4775a11ff413e9fc4b`
- verifier SHA-256: `c880050bc00fcd67c9445df7f80a5d1fcd414a751e3aa95e2468239d88155cf6`
- focused tests SHA-256: `e131684cd3c72ac0596e677055f3d09f949bc7fc72a186aebd5897e5d810e5a8`
- base Git commit: `f4c8109ce7ac01f7783c1af666d581c525ac8c61`

## Focused suite

```bash
PYTHONPATH=src python3 -B tests/test_sgcp_embed.py -v
```

Result: `19` tests passed in `36.381s`.

The suite includes strict JSON/integer checks, frozen controls, candidate and
subset recounts, lexicographic optimizer digests, exact builder/verifier row
comparison, scalar-table non-emission, semantic differentials, and mutations
of universes, selected witnesses, star edges, scalar placeholders, digests,
operation receipts, and argv.

## Repository suite

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Result: `59` tests passed in `47.774s`.

## Adversarial regression boundary

The following source-red-team-v1 false passes now fail in development:

- substituting `README.md` for the mathematical contract;
- shifting verifier scalar ground truth for `(0,3)`;
- selecting builder/verifier/registry/contract files as outputs;
- zeroing operation counters and recomputing the receipt digest;
- appending scalar-table material to argv and recomputing the receipt digest.

An in-memory unmodified certificate returned `valid=true` with all exact and
semantic differentials valid for `B=4,6,8`. This is a development consistency
check, not canonical evidence and not an ECDLP result.
