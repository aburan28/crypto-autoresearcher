# EXP-SGCP-EMBED-002 development test log v3

## Scope

No V3 curve-family row and no canonical run were authorized or created. This
log covers unit fixtures, abstract graphs, generated-curve provenance and
factor-base checks, one frozen `p=19,a=2,b=9,q=23,B=4` density row, and one
in-memory frozen document.

Claim boundary: implementation preflight only; `TOY-EVIDENCE`, `MODEL-BOUND`,
and `NOVELTY-UNVERIFIED`.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `849dea8d74529efa3213b46038ae971fac48c7b40648d33a68076e2dfb831aa1` |
| `src/verify_sgcp_embed_family.py` | `9d69344061c6507e3bb4972d9a73797c17297634269a78f93a7180303170994b` |
| `tests/test_sgcp_embed_family.py` | `f0bd8e93f41d0fddeba19c5868598d2268d7ab99a5e03d5ff3e3acf1b1d039a3` |
| `hypothesis.json` | `61a06d7f53d5c6129a8825dae1f718a4e3a00852f9f0fd8dafe82b33b9d921d1` |
| `specification.json` | `9ae11f5fe1f26b41ded91cb648d3a42fabad25967a4813bcb1d03a941b7de695` |
| `contract.md` | `10d4cc2968add106ae2c08d8950aae7ccbfcc713794a871099518627fba13b8d` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Observed result on 2026-07-20:

```text
Ran 19 tests in 0.543s
OK
```

The transient test-suite duration is not a cryptanalytic cost metric.

## Passing controls

1. Branch-and-bound matches exhaustive abstract graph optima.
2. Density objective and all tie fields match exhaustive capped optima.
3. A zero-node cap emits a nonzero gap whose interval contains the exact
   optimum; the frontier certificate and replay validate.
4. Frozen predecessor outcomes and the B=4 pairwise-conflict/full-closure
   equivalence reproduce.
5. Generated curves for all eight bit-seed pairs satisfy the registered
   filters and independent transcript derivation.
6. Singular, trace-zero, anomalous, `j=0`, and `j=1728` reason fixtures expose
   the expected reason; a scripted duplicate draw is retained explicitly.
7. Curve rejection-digest mutation fails independent provenance.
8. Every tested predicate is deterministic, cardinality-matched, and
   negation-symmetric.
9. Illegal coordinate and hash-null replicate bindings fail.
10. A Mobius nonce mutation fails after factor-base, row-byte, and row digests
    are refreshed.
11. Degree 1, 2, 4, and 8 expansion agrees with the independent implementation;
    formal and ordered witness totals match exact combinatorial counts.
12. The V3 frozen density row is exact at all four caps and passes independent
    graph, source, energy, structural-work, byte, replay, and depth-first
    verification.
13. Byte and structural-work mutations fail independently reconstructed
    receipts.
14. An appended scalar table fails both the closed schema and recursive
    forbidden-material scan.
15. An extra nested rejection field fails the closed graph transcript schema.
16. Representative-table, objective-order, source-table, and optimizer-gap
    mutations fail after enclosing receipts are refreshed.
17. A frozen V3 document passes the closed envelope; producer and verifier both
    reject an empty canonical matrix.
18. Producer and independent family gates agree exactly on a complete synthetic
    168-row matrix containing duplicate null support values.
19. Both gate implementations reject a missing row and an unresolved cell.
20. The producer CLI refuses both development family-row and canonical modes.

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
Ran 163 tests in 60.995s
FAILED (failures=1)
```

The other 162 tests passed. The sole failure was the pre-existing immutable-run
guard
`test_locked_runner_stdout_roles_compose_without_descendants`, which refused to
overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The run directory was
preserved. This is not a V3 assertion failure, but the repository-wide suite is
reported as failed rather than relabeled green.

## Interpretation

`OBSERVATION`: V3 rejects the mutation classes accepted by V2 and freezes one
complete exact family-gate interpretation.

This does not show that the 168-row canonical matrix is computationally
feasible, that any coordinate family wins, or that a structured embedding
produces ECDLP relations. Fresh independent review is required before any
launch-plan work.
