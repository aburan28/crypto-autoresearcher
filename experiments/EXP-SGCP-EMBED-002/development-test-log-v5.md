# EXP-SGCP-EMBED-002 development test log v5

## Scope

No V5 curve-family row, canonical matrix, runner, launch plan, or execution
budget was authorized or created. This log covers unit and abstract fixtures,
generated-curve provenance, factor-base checks, synthetic canonical envelopes,
one frozen `p=19,a=2,b=9,q=23,B=4` density row, in-memory frozen documents,
malformed-input receipts, a standalone frozen-B4 semantic implementation, and
hand-derived family-gate boundaries.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `d9cf9eeb5cda649956e3b8b1b6a754909869e53fd053c7ef2da14809b94c81dc` |
| `src/verify_sgcp_embed_family.py` | `053c11426031e53df5ef7c11cd4d652fa65c7effed3411924a6b4016d18cf776` |
| `tests/test_sgcp_embed_family.py` | `2900c3bad72096e2d12bca5720d2eb5fb26937af9867841cd07ca4d7602da903` |
| `hypothesis.json` | `b9514323c1ab5aa1c4e2046b810306e04d937bb0714ec6efc0e2eaade3ad1597` |
| `specification.json` | `0e4390d1e4cc726b86d830426ad8d06debcb438a2d4295d78c516ddb2e3445f1` |
| `contract.md` | `714ff8d09d1e45c3c0b04bf4b7cf23cd1a31e4e7f1a173beaaa1e2e74202d992` |
| `protocol-amendment-v5.json` | `43fc0af4a834e2b8e036dcb5b36f8c088c890fdc791711e1a9670dc3148ae04f` |
| `revision-response-v5.md` | `d76d68c518fa17fea48d49923dd8d1bfc5adc1a40a6f494b37f7a22c3a2bdebb` |
| `source-self-review-v5.md` | `45f5028b173c7d10fd944a95cfb1d2d985caf7f1b316eec8f39d53537625ae86` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Observed on 2026-07-20:

```text
Ran 33 tests in 1.902s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. Every V4 red-team crash mutation returns an equal deterministic invalid
   receipt on repeated calls and consumes zero independent primary-proof nodes.
2. Truncated cap schedules are rejected before cap indexing; negative caps and
   cap associations are rejected before replay.
3. Selected maxima must be degree-four, sorted, in-range, unique, ordered, and
   independently eligible. Optimizer indices and masks receive corresponding
   checks.
4. V1-V4 schemas are explicitly rejected with zero row reports. Relabeling a
   complete V5 body cannot enter a legacy verifier.
5. Legacy and unknown receipts list only parsing and routing checks; they do not
   claim graph, gate, optimizer, source, or accounting reconstruction.
6. Malformed JSON, duplicate keys, nonobject roots, malformed schema types,
   and wrong/out-of-range verifier budgets return invalid receipts.
7. Exact scalar-type mutation traverses every scalar leaf in the frozen row;
   every wrong Boolean/integer/float/string/null substitution is rejected.
8. The standalone frozen-B4 oracle independently reconstructs affine EC
   addition, all points, least-x fibers, degree-two representatives,
   degree-four candidates, individual eligibility, conflicts, retained-model
   costs, pair support, and the complete five-field objective at all four caps.
9. The standalone oracle matches factor points, candidate/eligible/conflict
   counts, selected indices, lexical witnesses, constrained labels, public
   edges, and objective values.
10. Hand-derived duplicate-null values `[8,10,10,12]` exercise the exact
    middle-two median without deduplication.
11. Exactly 18/24 positives with three passing strata passes; 17/24 with three
    strata and 18/24 with two strata both fail.
12. A half-cap 18/24-two-strata signal cannot splice with a three-quarter-cap
    17/24-three-strata signal.
13. An all-pair FAIL with every family below `1/10` in four strata emits
    `COLLAPSE`; a noncollapse FAIL emits `WEAKEN_OR_REJECT`.
14. The prior provenance, exact-type, ordering, optimizer, graph, expansion,
    source-table, canonical-grid, and forbidden-material controls remain green.
15. The producer CLI still rejects both development family-row and canonical
    modes.

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
Ran 177 tests in 73.050s
FAILED (failures=1)
```

The other 176 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The run directory was
preserved. This is not a V5 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V5 closes the demonstrated V4 verifier exceptions and legacy
routing defects, adds a genuinely separate frozen semantic reconstruction, and
tests the registered family-gate decision boundaries with hand-derived counts.

This does not establish canonical feasibility, a coordinate-family advantage,
a relation generator, rank, descent, preprocessing crossover, rho improvement,
or ECDLP result. Fresh independent exact-commit review remains mandatory before
even a launch-plan design.
