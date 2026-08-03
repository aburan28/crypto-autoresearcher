# EXP-SGCP-EMBED-002 development test log v4

## Scope

No V4 curve-family row, canonical matrix, runner, or launch plan was authorized
or created. This log covers unit fixtures, abstract graphs, generated-curve
provenance, factor-base checks, a complete synthetic canonical envelope, one
frozen `p=19,a=2,b=9,q=23,B=4` density row, and one in-memory frozen document.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `6f293f3bd64480d19bcc1ab136b87a846e961eda388c8daa427aefd5bbe68ae5` |
| `src/verify_sgcp_embed_family.py` | `a0daaeebc10937b00f8d658253637f491337ffac87ab6c3294d3cf50cc7be780` |
| `tests/test_sgcp_embed_family.py` | `fb183edbad2c690e9fda97bfb2e88168d954703669cb8dea17221a4a6d1f41d7` |
| `hypothesis.json` | `56d6512013b5f17b1aeb5ae4b7dd140b827ef7d4a5bf050f94d84f9193981424` |
| `specification.json` | `dd8c0f4d81ebc04c54fb5eb7b4a2a9a680d3c00ea8d38852a3ca543c7eb6302a` |
| `contract.md` | `a0ed546ef1e70fe50153949445f6b9d749c44b6c6fce65e40f1dc97bff0b7442` |
| `protocol-amendment-v4.json` | `927e097515b3449de47f8587ee87328ef95d433f6d4fdec1c1f1eede08495a53` |
| `revision-response-v4.md` | `454565ba8fc4fd9b9af69266d475a1dc60c5e0b9985dc442d52c1577bd1a9836` |
| `source-self-review-v4.md` | `0ca66b8ce1596a79c13998259ce5db1ea78a9f72572add79c663c1e7bf2a2cac` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Observed on 2026-07-20:

```text
Ran 25 tests in 0.809s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. Producer branch-and-bound and density objectives match exhaustive abstract
   optima, including all secondary ties.
2. A zero-node cap emits a valid nonzero interval and authenticated frontier.
3. Frozen predecessor values and pair-conflict/full-closure equivalence
   reproduce.
4. Generated curves satisfy every registered filter and full independent draw
   reconstruction.
5. Producer and verifier agree on every registered rejection reason, all
   duplicate combinations, and a duplicate candidate with four simultaneous
   mathematical reasons.
6. Predicates remain deterministic, cardinality matched, sign symmetric, and
   independently reconstructed.
7. Mobius, replicate, expansion, energy, graph, source, structural-work, byte,
   representative, objective, and scalar-material mutations fail closed.
8. V4 rejects integer zero changed to Boolean false or negative float zero,
   integer counts and ratios changed to equal floats, Boolean axioms changed to
   integers, and wrong exact types for masks, node caps, wall times, summaries,
   claim status, and byte receipts.
9. The independent ordering contract rejects a self-consistent label-convention
   mutation.
10. Producer and verifier reject missing, extra, duplicate, reordered,
    wrong-cap, wrong-node-cap, inconsistent-curve, and cross-seed-duplicate
    canonical matrices.
11. Both family gates agree on the complete synthetic 168-row matrix and reject
    every independent mutation of primary/full flags, bounds, gap, remaining
    nodes, frontier contents, frontier digest, or termination.
12. A third exhaustive oracle enumerates every independent frozen B=4 subset
    and matches support, constrained labels, public edges, retained maxima, and
    lexical witness at all four caps without invoking branch-and-bound or
    deterministic replay.
13. A frozen V4 document passes the exact-type closed envelope; malformed
    document scalar types and an empty canonical document fail. The top-level
    router uses the strict V4 path and rejects a legacy V3 canonical claim.
14. The producer CLI still refuses development family-row and canonical modes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002/hypothesis.json \
  experiments/EXP-SGCP-EMBED-002/specification.json
```

Observed result:

```text
VALID hypothesis experiments/EXP-SGCP-EMBED-002/hypothesis.json
VALID experiment experiments/EXP-SGCP-EMBED-002/specification.json
validated 2 record(s)
```

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests
```

Observed result:

```text
Ran 169 tests in 78.778s
FAILED (failures=1)
```

The other 168 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The run directory was
preserved. This is not a V4 assertion failure, but the repository-wide suite is
reported as failed.

## Interpretation

`OBSERVATION`: V4 closes the specific exact-type, duplicate-provenance,
ordering, gate, canonical-envelope, and frozen-secondary-oracle failures found
in V3 review.

This does not establish canonical feasibility, a coordinate-family advantage,
a relation generator, rank, descent, preprocessing crossover, rho improvement,
or ECDLP result. Fresh independent review remains mandatory before even a
launch-plan design.
