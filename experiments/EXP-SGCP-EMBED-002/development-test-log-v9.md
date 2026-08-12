# EXP-SGCP-EMBED-002 development test log v9

## Scope

No V9 generated density row, canonical matrix, runner, launch plan, or run was
authorized or created. This log covers executed-dimension graph accounting,
incremental graph/expansion exception receipts, reflected-path totality, direct
producer construction guards, final phase closure, one frozen
`p=19,a=2,b=9,q=23,B=4` density row, and inherited finite mathematical
controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `6a16d1e136fdc2378f541da5f06bbed821ba475e393142129cf09db4967a9edf` |
| `src/verify_sgcp_embed_family.py` | `3c6e9852ffd58f79de3163895b81856abc1392ea5b00c663b6512739210fe492` |
| `tests/test_sgcp_embed_family.py` | `062d37f56591797453b00bb5345d1a6b57de24788ceeff9990ced5527ccac2c5` |
| `hypothesis.json` | `a4600104b4e3aa15ff29dabd7559bf3bd4ba9bdc534ce3cdbaead3cbdd8f8074` |
| `specification.json` | `a79507390cb57880bbc70f0a29f1150ec752ae057373e70635409c1d5b4933d6` |
| `contract.md` | `157b3f6b59d1717667ace216b351c6dd20195da482b844f83e02fe8896af97ae` |
| `protocol-amendment-v9.json` | `6155e6ecec22427d3e416d68d5b3d41757053a567153f1989fedc15f789ecd18` |
| `revision-response-v9.md` | `70566f684390a845d0063572336f43a13e53263c7b90a9b1cea93c6869143b2b` |
| `source-self-review-v9.md` | `d9bf7ba0ee1996c06078ecc3247b8502c3ed24b84ac28cafb58ac3b2bc25bca9` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-20:

```text
Ran 58 tests in 3.167s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. The successful frozen path reports 31 executed graph-candidate evaluations,
   66 eligible conflict checks, 144 eligible pair-output cells, and 214
   expansion cells. Their separate reservations are 35, 595, 1,225, and 214.
2. Graph candidates, eligible conflicts, expansion formals, and eligible
   pair-output cells are charged inside their executed loops. Failure after the
   second matching charge preserves exact value 2, the failed aggregate unit,
   the reservation, and `actual_work_complete=false`.
3. The rest of the frozen actual-work vector remains exact: one frozen, one
   semantic, and four primary point enumerations; 218 replay nodes; 250 primary
   nodes; 268 entries in each replay cache; 56 primary-support and 129 primary-
   constrained cache entries; 401 retained-model calls; and 41,404 retained-
   model cells.
4. An otherwise successful report must match the exact V9 phase sequence and
   close every expected unit. Suppressing one primary-proof update produces an
   invalid final closure receipt.
5. Reflected path metadata is limited to 4,096 ASCII bytes or a bounded omission
   marker. An invalid-budget call with a path longer than the 8 MiB complete
   report ceiling returns a bounded invalid receipt.
6. Public `generated_curve` raises before the private generated control. Public
   `build_density_row` rejects changed provenance, duplicate or exact-type-
   aliased points, noninteger node caps, and every non-frozen association before
   factor-base work.
7. V1-V8 schemas reject without V9 row verification. Exact document, row,
   nested, summary, gate, accounting, and report schemas remain closed.
8. Source-sized admission, nested authentication, summary/gate reconstruction,
   actual-to-reservation dominance, bounded diagnostics, single-snapshot input,
   and all inherited standalone frozen-B4 semantic controls continue to pass.
9. Producer development-row and canonical modes remain disabled. Generated
   controls stop at private curve-provenance and factor-base scope, so no row or
   run budget was consumed.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 11 record(s)
```

A freshly generated repository index matched `ledger.json` byte-for-byte after
the SGCP protocol changed from 8 to 9.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 202 tests in 97.334s
FAILED (failures=1)
```

The other 201 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V9 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V9 closes the demonstrated V8 executed-dimension, partial-work,
path-totality, direct-producer, phase-closure, and stale-diagnostic defects under
the focused no-run test boundary.

This does not establish parser or allocator containment, CPU/RSS or memory-
bandwidth feasibility, a standalone B6/B8 complete oracle, canonical B6/B8
runtime, coordinate-family advantage, relation generation, rank, linear
algebra, target descent, fixed-curve preprocessing crossover, rho improvement,
or any ECDLP result. Fresh independent exact-commit theory, accounting, and
red-team review remains mandatory before even a launch-plan design.
