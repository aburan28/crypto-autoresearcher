# EXP-SGCP-EMBED-002 V14 Development Test Log

## Scope

V14 is a no-run repair of the V13 exact-commit red-team findings. It changes
publication attribution, output containment, direct-write terminal validation,
and control independence. It does not change the curve grid, predicate
families, representative compiler, optimizer, family gate, or mathematical
claim.

No generated V14 curve-family density row, canonical matrix, runner, launch
plan, or run was created. Historical V1 development artifacts remain
historical. `maximum_runs=0`.

## Exact artifact hashes

These SHA-256 values bind the files tested before commit:

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `8a98e94a08ad62e35630dbc6bbc36db236f66c705113f18c197a70d39ddeefbe` |
| `src/verify_sgcp_embed_family.py` | `9aa3bef0de41a01ebf0f5bf608605292ab7117eeecca288a1c056aca50a51e2f` |
| `tests/test_sgcp_embed_family.py` | `9c61fa2bb8c9ec3a09d5b9f35a378c7c529f8568d1bf8cce4245b95db95e3170` |
| `hypothesis.json` | `d8f4df40406d85381aa7c588fa6cc7877f6c88425beb5b662224b0febdbdae83` |
| `specification.json` | `ebb0735d7a1770c4c1049a201e46813247d2f983b03e258da7c297e631f121b2` |
| `contract.md` | `ef6903daf5d98ac45bdb2bd6ed8d4348816b706b7ba67f904fbfea60d673992a` |
| `protocol-amendment-v14.json` | `365b337c9fb9c43c315de00f3ba3fbdb4aafba11de69bfd439b748100ece59f9` |
| `revision-response-v14.md` | `921758f2abf4e06e4173a1fcb29fd8d5957d3b1a3e0bfc9a63d98d2d02fb9afc` |
| `source-self-review-v14.md` | `3e4d37b4db7369b129feff73545689943dd30c3df443f7eb7597baa1ceec684f` |

## Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  tests/test_sgcp_embed_family.py
```

Observed result:

```text
Ran 81 tests in 23.981s
OK
```

The V14-specific controls establish:

1. Producer and verifier emit V14; V1-V13 schemas reject before row
   verification.
2. Every public output entry enforces normalized development-root containment,
   and the descriptor walker independently rejects parent traversal.
3. Data and receipt names are both preflighted; a stale receipt blocks
   identical-payload retry before replacement data appears.
4. Receipts bind a random 256-bit publication identifier, destination basename,
   development-relative path, payload bytes/hash, protocol, experiment, and
   canonical self-digest.
5. A barrier-controlled same-destination race has one accepted identifier and
   one no-overwrite failure. Production and standalone validators attribute
   only the winning pair.
6. Ordinary exceptions immediately after receipt commit through exclusive
   rename, actual hard link, and forced direct publication reconcile only to
   the exact expected identifier and payload and return a structured warning.
7. The actual `os.link` branch executes for both data and receipt on a test-only
   hard-link-capable root. Temporary cleanup failure remains an accepted
   warning.
8. A direct receipt write that returns one byte short fails the observed
   inode-size check; both validators classify the pair as unaccepted.
9. The standalone parser shares no production status or canonicalization
   helper and independently checks exact keys/types, canonical encoding,
   self-digest, relative destination, identifier, and payload binding.
10. A validly re-signed identifier demonstrates the unkeyed threat boundary:
    ordinary status accepts it, while exact-attempt reconciliation rejects it.
    Wrong relative-path and Boolean-byte-count receipts fail both validators.
11. All inherited state-lifecycle, exact-accounting, parser, graph, expansion,
    replay, proof, semantic, and family-gate controls continue to pass.
12. The exact completed operation vector remains 480 prime candidates, 112
    draws, 336 curve hashes, 218 registered-curve point enumerations, and 4,218
    predicate hashes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m crypto_autoresearcher validate experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 16 record(s)
```

A freshly generated repository index matches `ledger.json` exactly.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m unittest discover -s tests -v
```

Observed result:

```text
Ran 225 tests in 914.902s
FAILED (failures=1)
```

The other 224 tests passed, including all 81 V14 focused tests. The sole failure
is the preserved pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V14 assertion failure. The unusually long suite time
included repeated mounted-volume Git status waits and is reported without
normalizing it away.

## Interpretation

`OBSERVATION`: V14 closes the demonstrated ordinary synchronous attribution,
stale-retry, path-containment, direct-write-size, hard-link-control, and
standalone-validation defects under the stated controlled-workspace model.

V14 does not guarantee a success return across `BaseException`, process death,
power loss, memory exhaustion, or hostile monkeypatching. Its unkeyed receipt
does not authenticate against a hostile same-user actor, sequential snapshots
are not pair-atomic, and receipt visibility is not proof of durability. The
hard-link control proves branch behavior on its test root, not support on the
mounted development filesystem.

No artifact establishes coordinate-family advantage, relation generation,
rank, linear algebra, target descent, fixed-curve preprocessing crossover, rho
improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

Commit the exact V14 snapshot and obtain fresh read-only theory, accounting, and
red-team review. Keep launch-plan design and execution `NO-GO` and
`maximum_runs=0`.
