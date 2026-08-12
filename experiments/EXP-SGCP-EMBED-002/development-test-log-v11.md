# EXP-SGCP-EMBED-002 development test log v11

## Scope

No V11 generated density row, canonical matrix, runner, launch plan, or run was
authorized or created. This log covers transcript-derived completed
provenance/predicate equality, interrupted predicate accounting, one-buffer
input snapshotting, lexical preflight, one frozen
`p=19,a=2,b=9,q=23,B=4` density row, and inherited finite mathematical controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `42e77b58419c2e5e1d1df4fc9e21a1ecc736863f2cff2bb6eda0bad8c25f0282` |
| `src/verify_sgcp_embed_family.py` | `a0bab9d018ea12af5bfbfa9f80d7ac55094cc2355f7367ad330f91c8fd8d093b` |
| `tests/test_sgcp_embed_family.py` | `45b2665b44fd0bc3ca0c7feac7c86df24ea2c85390ff3f7defa19801acb5afef` |
| `hypothesis.json` | `31bf9007fb61e85e01db9ec1bb51885d1f9c5a2b8875b7d3c75f3ab5d37ac1a8` |
| `specification.json` | `d2d63fedabed0ea5f220ea002628e9c2a8871059c736513261f21cc40e8ae17f` |
| `contract.md` | `3ac4bc7265f767736d4070f196fca5f9399b83e61da638abeb85d4de035a3ee5` |
| `protocol-amendment-v11.json` | `4a101b1e8eccf2ca4f460d4d0c92e98bde8cdefb40514e2bbab07df52041cda9` |
| `revision-response-v11.md` | `59412b0a01db07688b4107e35f547dae28d26c8875c2fe5928b3599249b602df` |
| `source-self-review-v11.md` | `69104e98e690beb0ed4009c0fcd52e5f37131fdc155760e578f32f15d3314fb0` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-20:

```text
Ran 65 tests in 23.215s
OK
```

The transient duration includes repeated in-memory transcript controls and is
not a cryptanalytic cost metric.

## Passing controls

1. V11 accepts only its current schema and rejects V1-V10 without row
   verification. Public producer and direct-verifier construction gates remain
   closed; only frozen B4 density construction is admitted.
2. A transient public curve/factor-base control reconstructs all 168 canonical
   row transcripts without constructing any density row or optimizer. The exact
   completed counts are 480 prime candidates, 112 draws, 336 curve hashes, 218
   registered-curve point enumerations, and 4,218 predicate hashes.
3. Undercharging and overcharging each of those five dimensions by one produces
   exactly one completed-work mismatch while `actual_work_complete=true`.
4. Injected predicate interruption preserves its one charged hash, invalidates
   the row, omits completed equality, and sets `actual_work_complete=false`.
5. Completed equality is evaluated only after every row's curve provenance and
   factor base have passed semantic reconstruction. Frozen expectations for all
   five dimensions are zero.
6. Snapshot admission allocates one exact-size bytearray after the regular-file
   and initial-size checks, fills only that backing buffer, hashes the same
   bytes, and rejects the first over-ceiling byte before reading.
7. The verifier requires unchanged file identity and exact length, preserves
   same-byte hash/parse binding, strictly decodes ASCII, clears the snapshot
   buffer, and only then calls the duplicate-key and nonfinite-number rejecting
   standard parser.
8. Lexical preflight rejects excessive token count, nesting, raw string length,
   scalar-token length, insignificant whitespace, and non-ASCII bytes before
   JSON object construction. Directory, final symlink, FIFO, and disclosed
   parent-symlink controls continue to pass.
9. All inherited exact graph/expansion, replay, proof, cache, retained-model,
   closed-schema, bounded-diagnostic, phase-closure, frozen-B4 oracle, and family
   gate controls continue to pass.
10. Producer development-row and canonical modes remain disabled. No generated
    density row or run budget was consumed.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 13 record(s)
```

A freshly generated repository index matches `ledger.json` exactly.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 209 tests in 418.855s
FAILED (failures=1)
```

The other 208 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V11 assertion failure, but the repository-wide suite
is reported honestly as failed.

## Interpretation

`OBSERVATION`: V11 closes the demonstrated V10 deterministic-counter
false-valid path under the focused no-run boundary and materially reduces
explicit source-copy and pre-object lexical amplification. It also makes
predicate interruption semantics consistent with other partial-work paths.

This does not establish a peak-RSS or parser-object bound, CPU or wall-time
feasibility, a standalone B6/B8 complete oracle, canonical B6/B8 runtime,
coordinate-family advantage, relation generation, rank, linear algebra, target
descent, fixed-curve preprocessing crossover, rho improvement, an exponent, or
an ECDLP break.

## Next action

Commit the exact V11 snapshot and obtain fresh independent theory, accounting,
and red-team review. Keep `maximum_runs=0`; do not design a launch plan without
three explicit scoped `GO` decisions.
