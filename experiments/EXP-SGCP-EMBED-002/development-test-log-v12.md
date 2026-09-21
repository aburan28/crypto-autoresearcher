# EXP-SGCP-EMBED-002 development test log v12

## Scope

No V12 generated curve-family density row, canonical matrix, runner, launch
plan, or run was authorized or created. This log covers invocation-local
verifier state, path-permit gating, exact positive work charges, descriptor-bound
no-overwrite output, one frozen `p=19,a=2,b=9,q=23,B=4` density document,
exactly three transient noncanonical frozen legacy semantic rows at B=4,6,8,
and inherited finite mathematical controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `a0287723c447b4db29eed495e80ea06fda03a21d90159c01dd96f26aa9f9380e` |
| `src/verify_sgcp_embed_family.py` | `a203016c22f45fde84a245d611cac035cf62ddfd933cb6526621a195274207ad` |
| `tests/test_sgcp_embed_family.py` | `454693a4cce435949b07b39b531c14efaab5e918733afdcbb90645ba365f4fcc` |
| `hypothesis.json` | `fac5fb25b3d46afaee7290687f564205ea7d965fe74406bb9384f265c3bcbd82` |
| `specification.json` | `98e2d5a78aeee8f9dc7c2497f4ecbbfa191cae61750832039ff21301d8596a51` |
| `contract.md` | `49b44860fc63da06d15e605aab69ef55c11ae2db3baaf28e691ca7e53a990f94` |
| `protocol-amendment-v12.json` | `dca7fef2dfa8aa0548a2084a3735369209d2e51e3a4217f7517637b7cc014858` |
| `revision-response-v12.md` | `f30b442dde20fff87b8f5e200ec623eb816d633e564a31dd704e73edfe2f9af5` |
| `source-self-review-v12.md` | `0850dafa892c084d10c917ad4cde47cd4084963001c5d1df00044ae51e4fc74e` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-23:

```text
Ran 71 tests in 19.038s
OK
```

The transient duration includes repeated in-memory semantic controls and is not
a cryptanalytic cost metric.

## Passing controls

1. V12 accepts only its current schema and rejects V1-V11 without row
   verification. Producer family-row and canonical execution remain closed.
2. Each public path call creates a fresh context-local work, reservation, and
   registered-curve-cache state. Two synchronized concurrent verifications and
   one nested verification each reproduce the serial frozen receipt exactly.
3. Registered-curve, legacy-row, density-row, document-value, production
   test-wrapper, and path-worker semantic internals reject without the active
   identity-checked path permit.
4. Boolean, zero, negative, float, string, and null work charges reject before
   mutation. Exact completed undercharge and overcharge controls still detect
   one-unit mismatches.
5. Exactly three transient frozen legacy semantic rows are constructed at
   B=4,6,8 and receive a separate in-test digest receipt. They are noncanonical
   predecessor controls, not generated curve-family density rows.
6. Output parents are walked through no-follow descriptors below the
   development root. Existing and race-created destinations are preserved,
   parent symlinks reject, and unpublished temporary inodes are removed.
7. The exFAT volume rejects hard-link and macOS exclusive-rename publication
   with `ENOTSUP`. The descriptor-relative `O_EXCL` fallback succeeds without
   overwrite. An injected interrupted final write remains unaccepted and cannot
   be overwritten by a second call.
8. The exact canonical provenance/predicate vector remains 480 prime
   candidates, 112 draws, 336 curve hashes, 218 registered-curve point
   enumerations, and 4,218 predicate hashes.
9. All inherited exact graph/expansion, replay, proof, cache, retained-model,
   one-buffer parser, bounded-diagnostic, phase-closure, frozen-B4 oracle, and
   family-gate controls continue to pass.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 14 record(s)
```

A freshly generated repository index matches `ledger.json` exactly.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 215 tests in 373.686s
FAILED (failures=1)
```

The other 214 tests passed, including all 71 V12 focused tests. The sole failure
is the pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V12 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V12 closes the demonstrated ordinary concurrent/reentrant state
corruption path, accidental direct semantic entry path, weak charge mutation,
and destination-overwrite race under the no-run boundary. It also makes the
B4/B6/B8 legacy-control scope explicit.

The exFAT fallback is no-overwrite but not atomically invisible: interrupted
partial output remains fail-closed. External immutable storage, executed-code
attestation, hard process limits, and role resource receipts remain future
runner obligations.

No current artifact establishes coordinate-family advantage, relation
generation, rank, linear algebra, target descent, fixed-curve preprocessing
crossover, rho improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

Commit the exact V12 snapshot and obtain fresh read-only theory, accounting, and
red-team review. Keep launch-plan design and execution `NO-GO` and
`maximum_runs=0`.
