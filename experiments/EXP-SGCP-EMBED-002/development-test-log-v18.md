# EXP-SGCP-EMBED-002 V18 Development Test Log

## Scope

V18 is a no-run repair of the V17 red-team findings. It preserves decoded CLI
output strings through admission, validates verifier output before input work,
scopes arbitrary `__fspath__` callback effects, qualifies historical evidence,
and replaces the path-name receipt with a NUL-delimited Git-entry metadata
receipt over an expanded normative surface.

V18 creates zero generated V18 curve-family density rows and zero canonical
runs. It preserves 17 historical V1 development rows and one historical
development run manifest. `maximum_runs=0`.

## Exact artifact hashes

These SHA-256 values will bind the exact tested files in the review-root
snapshot:

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8` |
| `src/verify_sgcp_embed_family.py` | `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199` |
| `tests/test_sgcp_embed_family.py` | `f5360f3f1dc345c9e29fb69fc673c67208918b5c8288c31f74dbf7f4a769b01e` |
| `hypothesis.json` | `aca55cd96f5d94116d4a8ba811937f66c5087e26a0ca3d0a9672258538c49b86` |
| `specification.json` | `579a4bd0bc8d8af67592635b3407754c95bb4a9cf5bb0a93fe668d65391e08a8` |
| `contract.md` | `b93084cf19634533210fd0c48fd7ea2f84f9b718b9320f5d390b363f403df2fe` |
| `protocol-amendment-v18.json` | `3dafb3f249225f99583d9ce90b8630e93013d40a06dfa8bd8f6312cf77b483d5` |
| `revision-response-v18.md` | `49a37f395b36c40440f59aeb7153df853e897182c7800e8d1c5b9694424d0ba9` |
| `source-self-review-v18.md` | `20f62ef17789fb94446dd6b0d5a489f2db13ac601d88bb9ed4d03e4990b0ef32` |
| `review-surface-manifest-v18.json` | `587fd50831976921101060d1cac2e2d249f193b63b77bdf1362d08e1261a5c08` |

The manifest receipt is separate from these byte digests. It binds selected
entry mode, type, and path only; the exact reviewed Git tree remains the
complete review-byte binding root.

## Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  tests/test_sgcp_embed_family.py
```

Observed result:

```text
Ran 81 tests in 3.747s
OK
```

The V18-specific controls are intended to establish:

1. Producer and verifier emit V18; V1-V17 schemas reject before row
   verification.
2. Verifier and producer preserve terminal `/` and terminal `/.` through CLI
   parsing.
3. Verifier `main` rejects those invalid outputs before input verification,
   writer invocation, or parent creation.
4. An admitted decoded raw alias reaches the writer unchanged.
5. Direct Python path entries retain the finite V17 grammar and normalized
   containment behavior.
6. Caller `__fspath__` side effects are observed and explicitly separated from
   verifier-created effects.
7. The review-surface selectors reproduce the exact NUL-delimited
   mode/type/path receipt, contain no predicted Git identifiers, and include
   the normative plus historical entries.
8. Current records state zero generated V18 curve-family density rows, zero
   canonical runs, 17 historical V1 development rows, one historical
   development run manifest, and `maximum_runs=0`.
9. All inherited receipt, parser, state-lifecycle, accounting, graph,
   expansion, replay, proof, semantic, and family-gate controls continue to
   pass.
10. The exact completed operation vector remains 480 prime candidates, 112
    draws, 336 curve hashes, 218 registered-curve point enumerations, and 4,218
    predicate hashes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  -m crypto_autoresearcher validate experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 20 record(s)
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
Ran 225 tests in 63.529s
FAILED (failures=1)
```

This command collects unittest-discover methods only. The 27 module-level
pytest-style functions identified by prior reviews remain outside this recorded
result unless a separate pytest run is explicitly preserved.

The other 224 tests passed, including all 81 V18 focused tests. The sole
failure is the preserved pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V18 assertion failure.

## Interpretation

`OBSERVATION`: record validation and repository-index comparison pass. The
repository-wide unittest-discover suite has only the preserved unrelated
immutable-run guard failure described above. The focused suite passes on the
exact hashed files.

No artifact establishes coordinate-family advantage, relation generation,
rank, linear algebra, target descent, fixed-curve preprocessing crossover, rho
improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

After exact hashes and completed validation receipts are inserted and
committed, obtain fresh independent read-only theory, accounting, and red-team
reviews of that exact Git commit and tree. Keep launch-plan design and execution
`NO-GO` and `maximum_runs=0`.
