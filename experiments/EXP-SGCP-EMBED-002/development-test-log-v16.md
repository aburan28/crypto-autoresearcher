# EXP-SGCP-EMBED-002 V16 Development Test Log

## Scope

V16 is a no-run repair of the V15 exact-commit review findings. It distinguishes
the POSIX `//` anchor from internal repeated separators, expands lexical path
controls, checks accepted attribution through the raw alias, repairs version and
current-state records, and narrows the broad regression label to its exact
unittest-discover scope. It does not change the curve grid, predicate families,
representative compiler, optimizer, family gate, publication protocol, or
mathematical claim.

No generated V16 curve-family density row, canonical matrix, runner, launch
plan, or run was created. Historical V1 development artifacts remain
historical. `maximum_runs=0`.

## Exact artifact hashes

These SHA-256 values bind the exact files tested in the committed snapshot:

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `7af442bb69e06b2e36453353e100bb103086c8f791ce8a5434e1ffe54afa93d9` |
| `src/verify_sgcp_embed_family.py` | `40eb3d503122ece701841004207f7f60311f5e0992baa0d450dd8fdd4cf5ae9f` |
| `tests/test_sgcp_embed_family.py` | `0e4a368bd9a1be2634d94a98c582a07ae2a9416cfae5f214c132e4ac09b67383` |
| `hypothesis.json` | `9a7600ce7bcbd02cfdf08be228bd498c07f94ea18239ba1926804171bcbe30d5` |
| `specification.json` | `d298e18078a632d6b387d98d7057138fdbed0bb6ffbdbd1dca1c3d986a81cffa` |
| `contract.md` | `4526ebcbb62b60d2a01718e185ab891b77a8702e37f74b3f4fb9116b0b9ecc33` |
| `protocol-amendment-v16.json` | `30c63bc705a9bbf48c0a0d1a3c980eba8f54490bddf78bb8808b218f0d83bf3a` |
| `revision-response-v16.md` | `34e4376ff11646e87620d9e75cbe6c90b1f0137d9d5d4267a7e99c330fb2bf73` |
| `source-self-review-v16.md` | `d26932f93971bb03ea21cb31c2dd2541a449eda7e6b8f7197650269d739f7497` |

## Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  tests/test_sgcp_embed_family.py
```

Observed result:

```text
Ran 81 tests in 3.995s
OK
```

The V16-specific controls are intended to establish:

1. Producer and verifier emit V16; V1-V15 schemas reject before row
   verification.
2. Dot, internal repeated-separator, absolute in-root, three-leading-separator,
   and combined raw spellings normalize to one destination.
3. Exactly two leading POSIX separators, explicit parent traversal, the
   development root, and ordinary outside paths reject across every lexical
   entry.
4. Publication through the combined raw alias binds the normalized relative
   path, and production plus standalone status attribute the accepted pair
   through every admitted spelling after publication.
5. The private descriptor walker independently enforces anchor, traversal,
   root, containment, and symlink-parent boundaries.
6. Contract, specification, ledger, producer, and verifier identify version 16.
7. All V15 attempt-bound receipt, stale-name, race, direct-write, hard-link,
   standalone-validation, state-lifecycle, accounting, parser, graph,
   expansion, replay, proof, semantic, and family-gate controls continue to
   pass.
8. The exact completed operation vector remains 480 prime candidates, 112
   draws, 336 curve hashes, 218 registered-curve point enumerations, and 4,218
   predicate hashes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m crypto_autoresearcher validate experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 18 record(s)
```

Repository-index comparison:

```text
freshly generated index is byte-identical to ledger.json
```

## Repository-wide unittest-discover suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m unittest discover -s tests -v
```

Observed result:

```text
Ran 225 tests in 101.446s
FAILED (failures=1)
```

This command collects unittest-discover methods only. The 27 module-level
pytest-style functions identified by the V15 reviews are outside this recorded
result unless a separate pytest run is explicitly preserved.

The other 224 tests passed, including all 81 V16 focused tests. The sole
failure is the preserved pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V16 assertion failure.

## Interpretation

`OBSERVATION`: the focused suite, record validator, and repository-index
comparison pass. The repository-wide unittest-discover suite has only the
preserved unrelated immutable-run guard failure described above. These results
apply to the exact V16 files hashed above, and establish only that source,
controls, and documents agree on the exact POSIX anchor and normalized-alias
policy.

No artifact establishes coordinate-family advantage, relation generation,
rank, linear algebra, target descent, fixed-curve preprocessing crossover, rho
improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

Obtain fresh read-only theory, accounting, and red-team reviews of the exact
commit containing this log. Keep launch-plan design and execution `NO-GO` and
`maximum_runs=0`.
