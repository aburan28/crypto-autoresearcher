# EXP-SGCP-EMBED-002 development test log v13

## Scope

No generated V13 curve-family density row, canonical matrix, runner, launch
plan, or run was authorized or created. Historical V1 development artifacts
remain historical and are not V13 evidence. This log covers thread-owned and
explicitly closed verifier state, path-worker re-entry gating, descriptor-bound
two-object publication, one frozen `p=19,a=2,b=9,q=23,B=4` density document,
exactly three transient noncanonical frozen legacy semantic rows at B=4,6,8,
and inherited finite mathematical controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `bdab1fe6766553438932ae938cf6b33b5a2c56f32d1caccceaacbc4d3a177122` |
| `src/verify_sgcp_embed_family.py` | `a12d733ceb0faed254452891d73da5f53db53833013977694eac913e463d94dc` |
| `tests/test_sgcp_embed_family.py` | `6700ee5d44377b759a7e32040fa5a46cac6414b249e53a15e9f53a5c742c79a9` |
| `hypothesis.json` | `0cc2466c4fe132ff9f52261d080fec4bb1c370b0aa501e6c618c74269eff147a` |
| `specification.json` | `2d2363d94c1b16ffa12e071af75a8ad666f44f68e25f74c0d4f3205be80b2ce6` |
| `contract.md` | `c23a5a7cea1d131ad57d1d4c68f41dece506cacf6081ee33e48b7cf0469319ea` |
| `protocol-amendment-v13.json` | `639a2a85e67c6157948287eef87f9b2db13fe932bc795bb40f11f10d48217628` |
| `revision-response-v13.md` | `21b4584b2bff5c9064051351e2a3e912085ed105b455ae0d33f26fa10c4f46da` |
| `source-self-review-v13.md` | `830ecf7838ff1c827319e9a3e8e9a0697dd9a819538f34087b2eed78297058f9` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-23:

```text
Ran 75 tests in 23.787s
OK
```

The transient duration includes repeated in-memory semantic controls and is not
a cryptanalytic cost metric.

## Passing controls

1. V13 accepts only its current schema and rejects V1-V12 without row
   verification. Producer family-row and canonical execution remain closed.
2. Every public call receives fresh actual-work, reservation, and curve-cache
   state. The state is bound to its creating thread and closed before context
   restoration.
3. Concurrent and nested calls reproduce the serial frozen receipt. An
   escaping worker exception restores the exact outer state; direct worker
   re-entry, copied-context cross-thread use, and stale copied-context use
   reject.
4. Internal semantic entry points reject without the active identity-checked
   path permit, and the path-worker body also requires its invocation token.
5. Boolean, zero, negative, float, string, and null work charges reject before
   mutation. Exact completed undercharge and overcharge controls still detect
   one-unit mismatches.
6. Exactly three transient frozen legacy semantic rows are constructed at
   B=4,6,8 and receive a separate in-test digest receipt. They are noncanonical
   predecessor controls, not generated curve-family density rows.
7. Output parents are walked through no-follow descriptors below the
   development root. Data and canonical completion receipt paths are
   no-overwrite and independently size/hash validated.
8. Preexisting and race-created data paths are preserved. Interrupted direct
   data publication is an unaccepted orphan; interrupted direct receipt
   publication is an unaccepted invalid receipt; payload tampering causes an
   unaccepted receipt mismatch.
9. Injected directory-fsync failure and hard-link-success temporary-cleanup
   failure after content publication return accepted results with structured
   warnings and a matching receipt. No real-filesystem support observation is
   claimed from the forced `ENOTSUP` controls.
10. The exact canonical provenance/predicate vector remains 480 prime
    candidates, 112 draws, 336 curve hashes, 218 registered-curve point
    enumerations, and 4,218 predicate hashes.
11. All inherited exact graph/expansion, replay, proof, cache, retained-model,
    one-buffer parser, bounded-diagnostic, phase-closure, frozen-B4 oracle, and
    family-gate controls continue to pass.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 15 record(s)
```

A freshly generated repository index matches `ledger.json` exactly.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 219 tests in 63.445s
FAILED (failures=1)
```

The other 218 tests passed, including all 75 V13 focused tests. The sole
failure is the preserved pre-existing immutable-run guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V13 assertion failure, but the repository-wide suite
is reported honestly as failed.

## Interpretation

`OBSERVATION`: V13 removes the demonstrated publication terminal-state
ambiguity by making the completion receipt, rather than caller return or the
data path alone, the logical content commit. It also closes ordinary
exceptional, direct path-worker re-entry, copied cross-thread, and stale-context
state reuse.

The receipt is unkeyed and does not authenticate against a hostile same-user
filesystem actor. Receipt visibility is not proof that every durability syscall
succeeded. External immutable storage, executed-code attestation, hard process
limits, preserved publication warnings, and role resource receipts remain
future runner obligations.

No current artifact establishes coordinate-family advantage, relation
generation, rank, linear algebra, target descent, fixed-curve preprocessing
crossover, rho improvement, exponent, deployment relevance, or an ECDLP result.

## Next action

Commit the exact V13 snapshot and obtain fresh read-only theory, accounting, and
red-team review. Keep launch-plan design and execution `NO-GO` and
`maximum_runs=0`.
