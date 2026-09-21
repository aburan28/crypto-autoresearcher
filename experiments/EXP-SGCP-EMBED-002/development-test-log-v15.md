# EXP-SGCP-EMBED-002 V15 Development Test Log

## Scope

V15 is a no-run repair of the V14 exact-commit accounting and red-team review
findings. It aligns the output-path claim with Python path normalization, adds
normalized-alias control coverage, refreshes current-state records, and restores
the durable inventory. It does not change the curve grid, predicate families,
representative compiler, optimizer, family gate, publication protocol, or
mathematical claim.

No generated V15 curve-family density row, canonical matrix, runner, launch
plan, or run was created. Historical V1 development artifacts remain
historical. `maximum_runs=0`.

## Exact artifact hashes

These SHA-256 values bind the files tested before commit:

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `45997a75438a477a4503944fb130f4ee079ae72be50fffae48ab20426a3ed6e3` |
| `src/verify_sgcp_embed_family.py` | `0c3338234fd182ec08952005259f22f0184d540c35bc4a492c388bcfb215a023` |
| `tests/test_sgcp_embed_family.py` | `0a330ef3decd637fc9ae7d7e8ccd3909e8cf9d65fbb2b003d1d53b1ae913530f` |
| `hypothesis.json` | `97f5f8461e8e674df455886590a404aec0126494bf2e0c399b4dbda8ab72c95f` |
| `specification.json` | `7d9549c7984ab3aaf947465f9609228dc2f9546d21f8896a9b176986ca23d9f5` |
| `contract.md` | `1a72ce64a8cfd206ba9e17f3827282376f9256d64c4e1b88ea9bdcfda9d19d64` |
| `protocol-amendment-v15.json` | `042d112fbb1825d0c0bb71a3139dac8cd89614c6215f23bd0b6a8adcd6327ba2` |
| `revision-response-v15.md` | `a402d76241294852332ea3d939d114d2c5f47e0829c7c0c1a8426ef4a36bee43` |
| `source-self-review-v15.md` | `f6bdcd7723f26f30c628ebcab5f450d92cb6f4b59a8d67d065a6da91df5066d2` |

## Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  tests/test_sgcp_embed_family.py
```

Observed result:

```text
Ran 81 tests in 13.906s
OK
```

The V15-specific controls establish:

1. Producer and verifier emit V15; V1-V14 schemas reject before row
   verification.
2. Raw in-root `.` and repeated-separator spellings normalize to the same
   destination in the writer, receipt-path, and status APIs.
3. Publication through that alias binds the normalized relative path, and
   production plus standalone validators attribute the same accepted pair.
4. Explicit `..` parent traversal rejects in the public writer, status
   function, and private descriptor walker without creating an outside artifact.
5. All V14 attempt-bound receipt, stale-name, race, direct-write, hard-link,
   standalone-validation, state-lifecycle, accounting, parser, graph,
   expansion, replay, proof, semantic, and family-gate controls continue to
   pass.
6. The exact completed operation vector remains 480 prime candidates, 112
   draws, 336 curve hashes, 218 registered-curve point enumerations, and 4,218
   predicate hashes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m crypto_autoresearcher validate experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 17 record(s)
```

Repository-index comparison:

```text
freshly generated index is byte-identical to ledger.json
```

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m unittest discover -s tests -v
```

Observed result:

```text
Ran 225 tests in 70.367s
FAILED (failures=1)
```

The other 224 tests passed, including all 81 V15 focused tests. The sole failure
is the preserved pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V15 assertion failure.

## Interpretation

`OBSERVATION`: V15 aligns the source, controls, and documents on normalized
in-root alias behavior and explicit parent-traversal rejection. The focused
suite, record validator, and ledger comparison pass; the repository-wide suite
has only the preserved unrelated immutable-run guard failure described above.

No artifact establishes coordinate-family advantage, relation generation,
rank, linear algebra, target descent, fixed-curve preprocessing crossover, rho
improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

Run validation, freeze the nine hashes, commit the exact V15 snapshot, and
obtain fresh read-only theory, accounting, and red-team review. Keep launch-plan
design and execution `NO-GO` and `maximum_runs=0`.
