# EXP-SGCP-EMBED-002 development test log v6

## Scope

No V6 curve-family row, canonical matrix, runner, launch plan, or execution
budget was authorized or created. This log covers bounded input handling,
registered-envelope preflight, source-owned work ceilings, actual phase
receipts, unit and abstract fixtures, generated-curve provenance, one frozen
`p=19,a=2,b=9,q=23,B=4` density row, a full standalone B4 transcript, and
hand-derived family-gate boundaries.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `cf93669c05ac348fa8e67e7ed58ba440bb74cb686b7d530e58f5f27870da8528` |
| `src/verify_sgcp_embed_family.py` | `ba4df4b5c268b72fd5f28da039ef020882b682136c5df432b53acb610d473dd2` |
| `tests/test_sgcp_embed_family.py` | `43513bafd0c8f6db909e2739e4781c203bb797cbe9868da36ee74d1625576b52` |
| `hypothesis.json` | `d2a6ea2b21b7383c4b9175bd65134163b2fa391e636c1aea889012bf4cf93f82` |
| `specification.json` | `3df924d0e5374dadcd2dd87b010057d5da157f376d9c6c14b0fbc8e097005cea` |
| `contract.md` | `b2e24adab572673be501362f8ae616eb4d50c8a6b4ef99365ddc4ad9258bd37a` |
| `protocol-amendment-v6.json` | `4317a079db4edf75326f3ccbd447013438f9a8f5a3535016fd93056537021a89` |
| `revision-response-v6.md` | `4acbd6c30396f66ed5394893c035d3f1846a02f82129c59ae2c942bcc3f64f8f` |
| `source-self-review-v6.md` | `667fc3b8f81f870df5662333a97022b6ae66d1e00104c50f47d42c3821b741aa` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Observed on 2026-07-20:

```text
Ran 41 tests in 2.101s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. File-path verification requires one `O_NOFOLLOW` regular-file descriptor,
   bounds the read at 256 MiB, checks identity and metadata before and after the
   read, and hashes and parses the same immutable byte snapshot.
2. Changing-path, directory, and symlink inputs fail before JSON semantics.
3. JSON traversal is bounded by two million nodes, depth 64, and eight-MiB
   strings or keys. Unsupported V1-V5 schemas are rejected explicitly.
4. Generated curves are independently derived from registered bit and seed
   schedules; emitted draw counts are never followed as semantic instructions.
5. Document scope, matrix grid, exact scalar types, curve provenance,
   source-owned caps, row digests, and ordering fail before row semantics.
6. Frozen scope accepts only `B=4` with node cap 100,000. Canonical scope accepts
   only `B in {4,6,8}` with node cap 2,000,000. Direct row verification requires
   an explicit scope and its exact source-owned cap.
7. Huge bit sizes, unregistered B values, malformed repeated rows, and bad row
   digests invoke zero curve or row semantic calls.
8. Static reservation bounds curve draws, expansion and graph cells, primary
   and replay nodes, both replay caches, both primary caches, retained-model
   calls, and retained-model cells before semantic work begins.
9. Per-row and aggregate overbudget inputs fail before row semantics, including
   a twelve-row invalid-amplification fixture.
10. Receipts list only phases reached by actual control flow and separately
    report reserved and actual work. Invalid parse, schema, envelope, legacy,
    budget, and valid-document routes have exact phase-ledger controls.
11. Replay and proof counters, cache occupancy, and retained-model calls are
    measured from execution rather than copied from the input.
12. The standalone frozen-B4 oracle hardcodes only the public curve seed inputs,
    independently derives group order and caps, and reconstructs the complete
    factor-base, rejection, representative, conflict, graph, mask, formal
    family, label, edge, source-table, digest, axiom, and winner transcript.
13. The standalone oracle calls neither producer nor verifier semantic helpers.
14. Duplicate-null values `[8,8,10,12]` distinguish multiset median 9 from
    deduplicated median 10.
15. Exact one-tenth support is noncollapse; every coordinate family must be
    below one tenth across the required strata for `COLLAPSE`.
16. Existing provenance, exact-type, ordering, optimizer, graph, expansion,
    canonical-grid, and forbidden-material controls remain green. The producer
    CLI still rejects development family-row and canonical modes.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher.cli --repo . validate \
  experiments/EXP-SGCP-EMBED-002/hypothesis.json \
  experiments/EXP-SGCP-EMBED-002/specification.json
```

Observed result:

```text
VALID hypothesis experiments/EXP-SGCP-EMBED-002/hypothesis.json
VALID experiment experiments/EXP-SGCP-EMBED-002/specification.json
validated 2 record(s)
```

The generated experiment index exactly matched `ledger.json`.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 185 tests in 82.860s
FAILED (failures=1)
```

The other 184 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The run directory was
preserved. This is not a V6 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V6 closes the demonstrated V5 snapshot-binding, registered-scope,
trusted-budget, actual-phase, incomplete-oracle, and gate-discrimination defects
under the focused test boundary.

This does not establish parser peak-memory containment, canonical B6/B8
feasibility, actual family runtime, a coordinate-family advantage, a relation
generator, rank, descent, preprocessing crossover, rho improvement, or ECDLP
result. Fresh independent exact-commit review remains mandatory before even a
launch-plan design.
