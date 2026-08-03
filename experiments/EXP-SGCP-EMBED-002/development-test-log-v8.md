# EXP-SGCP-EMBED-002 development test log v8

## Scope

No V8 generated density row, canonical matrix, runner, launch plan, or run was
authorized or created. This log covers path-only evidence admission, closed
nested source shapes, exact actual-work accounting, validity-enforced resource
dominance, phase-local exception receipts, diagnostic/report ceilings, one
frozen `p=19,a=2,b=9,q=23,B=4` density row, and inherited finite mathematical
controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `ee0b0eecc067fdbb4e02bd147ff55b129fffa45a3c9d0d65020c45f1ee453963` |
| `src/verify_sgcp_embed_family.py` | `cb8478b0f74d5f5a6fc044213099bf66f564062a482868ac1940306a48543400` |
| `tests/test_sgcp_embed_family.py` | `ea818fd8a94c07918aed47b09d864e9a988b2c5786aa213e6154b8bd0565b7a0` |
| `hypothesis.json` | `ba83f51bf178743b3b57eb3ba0f7d237a939b7433782320cf2ba9d2a6d5c7c1a` |
| `specification.json` | `df7509e613b10fe8d4d57d6f538c5a541f4fef9c83f17b5231881a9eb01628d3` |
| `contract.md` | `477ef0b5db1f6881bc0f1b19f62929ed48d4da9a80c6c51af01e4684049fd52d` |
| `protocol-amendment-v8.json` | `761bb0c449cee4fbd18bb3b16cd6ce50aafdeaf987404e721107633cc910d54b` |
| `revision-response-v8.md` | `d3c05736e04d5c72a58799190d27d74861b87325710d0250bc214f9be67deabc` |
| `source-self-review-v8.md` | `3898b5461dd01ec16ede1f23154f8a33a19165335258c5c7b81fb6f18063f5f2` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-20:

```text
Ran 54 tests in 2.649s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. Path-based `verify_document` is the sole evidence-bearing API. Both public
   direct-row APIs reject before curve, graph, replay, or proof work.
2. V1-V7 schemas reject without V8 row verification. Exact document, row,
   nested, summary, gate, accounting, and report schemas remain closed.
3. Source-sized admission precedes the generic JSON walk. A 1,000-key nested
   factor-base amplification, one-over lists, malformed B/family values, and
   nested gate amplification all stop at `source_collection_bounds` without
   calling the generic walk or semantic verifier.
4. Major nested row objects have closed key sets. Map, reason, formal, edge,
   source-table, graph/expansion histogram, frontier, and byte-receipt
   containers have source-derived bounds.
5. Nested digests and byte accounting, plus reconstructed summary and family
   gate, are checked before reservation-dependent curve work.
6. The valid frozen path records exactly one frozen, one semantic, and four
   primary point enumerations; 214 expansion cells; 1,457 graph cells; 218
   replay nodes; 250 primary nodes; 268 entries in each replay cache; 56
   primary-support and 129 primary-constrained cache entries; 401 retained-
   model calls; and 41,404 retained-model cells.
7. Complete work must satisfy both upper-bound dominance and exact-by-
   construction cache/enumeration counts. Suppressing all four primary point-
   enumeration charges leaves the mathematics successful but makes the final
   receipt invalid with a failed dominance phase.
8. An otherwise valid path with a replay reservation reduced below observed
   work is invalid. Incomplete work is also invalid regardless of numerical
   dominance.
9. Replay/proof nodes and cache insertions are charged globally as executed;
   retained-model calls and cells are charged per evaluation. Injected failures
   after two nodes preserve the failing-cap lower bound.
10. Injected failures on frozen, semantic, and primary point enumeration are
    charged before the call and attributed to the owning aggregate phase with
    exact expected/completed/failed unit counts.
11. Aggregate curve, replay, retained-model, and primary phases pass only after
    every registered unit completes with zero failures.
12. Reflected digests are sanitized, nested errors are normalized to the
    bounded top-level list, key sampling avoids full sorting, and the complete
    report including size and hash fields is capped.
13. One immutable regular-file byte snapshot is hashed and parsed. Final
    symlinks, directories, FIFOs, initial oversized files, malformed JSON,
    duplicate keys, nonfinite numbers, and changing paths fail closed.
14. The standalone frozen-B4 oracle continues to exact-compare the complete
    candidate/eligible lists, recursive parents, graph, compiler, retained
    model, and five-field cap winners. Outside frozen B4, secondary objective
    fields remain replay-confirmed rather than independently proved.
15. Producer development-row and canonical modes remain disabled. Generated
    controls stop before density-row construction, so no row or run budget was
    consumed.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 10 record(s)
```

The generated experiment index exactly matched `ledger.json` after the SGCP
version changed from 7 to 8.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 198 tests in 83.245s
FAILED (failures=1)
```

The other 197 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V8 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V8 closes the demonstrated V7 path/API, admission, accounting,
phase, diagnostic, and secondary-claim defects under the focused no-run test
boundary.

This does not establish parser or allocator containment, CPU/RSS or memory-
bandwidth feasibility, a standalone B6/B8 complete oracle, canonical B6/B8
runtime, coordinate-family advantage, relation generation, rank, linear
algebra, target descent, fixed-curve preprocessing crossover, rho improvement,
or any ECDLP result. Fresh independent exact-commit theory, accounting, and
red-team review remains mandatory before even a launch-plan design.
