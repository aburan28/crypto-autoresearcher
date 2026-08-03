# EXP-SGCP-EMBED-002 development test log v7

## Scope

No V7 generated density row, canonical matrix, runner, launch plan, or run was
authorized or created. This log covers source-bounded admission, partial work
receipts, nonblocking file handling, diagnostic ceilings, cache receipts, unit
and abstract fixtures, generated-curve and factor-base controls, one frozen
`p=19,a=2,b=9,q=23,B=4` density row, a complete standalone B4 transcript, and
hand-derived family-gate boundaries.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `de2bc61c2e2d1925a3ad266df4420799cb95a4ffa173af6d2299fd178d42fcad` |
| `src/verify_sgcp_embed_family.py` | `e36ac89056646cacbc8305adf8f8a9087eff2081cfb9695f791a6eda21d0b517` |
| `tests/test_sgcp_embed_family.py` | `70b8ca5a6e3a817ad4ffa7890764e248b0d4f84c4b99dfee6d8a6c6481fd7704` |
| `hypothesis.json` | `400bdbbe7c2cd98814f20908a95c1346dbe475802090f03468b64804d9fc7e13` |
| `specification.json` | `1fe9ba01acfb10feb763faf090feabf9913329acccd2ed448afbd9f99b1acdf0` |
| `contract.md` | `43d79e564fef989c4fc2c786f8a9bb5e5bcf3a7131c8149d68e1398be3b8f551` |
| `protocol-amendment-v7.json` | `1eb5fb0d7563eedbb643dadbb8a1395bc42838b61a4f78e8e7ee3645ea35dbbc` |
| `revision-response-v7.md` | `ab4ef87a4e5127e8bc27659bfc2457aafe84f0e793f5c6e33cc247b998653d47` |
| `source-self-review-v7.md` | `b022dd23dbfd4d88aa596a805997967db8be22d23fd9acf171ab82f08f5d3c93` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-20:

```text
Ran 46 tests in 2.086s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. Exact V7 types, row digest, protocol, validity, ordering, registered scope,
   source-owned caps, objective, empty frontier, masks, and B-derived transcript
   lengths pass before curve derivation.
2. Bad row digests, wrong objectives, nonempty frontiers, oversized masks, and
   oversized edge transcripts call no frozen/registered curve helper, replay,
   or primary proof.
3. The final input component is opened no-follow and nonblocking. FIFO,
   directory, final symlink, and initial sparse oversized-file controls fail
   before JSON semantics or reads. Parent-component symlink traversal is
   explicitly disclosed and tested.
4. One immutable byte snapshot is hashed and parsed. A later path mutation
   cannot alter parsed bytes or the input hash receipt.
5. JSON shape and diagnostics have independent source ceilings. An amplified
   malformed document stays within 256 messages, 65,536 total ASCII bytes, and
   2,048 bytes per item.
6. Reservation fields separate prime candidates, curve draws/hashes/point
   enumerations, predicate hashes, semantic and primary point enumerations,
   expansion/graph cells, replay/proof nodes, replay/primary caches, and
   retained-model calls/cells.
7. Producer optimizer and full-model cache entries are source-enforced and
   authenticated. Verifier cache occupancy is separately observed and remains
   below its reservation.
8. Injected second-cap replay and primary-proof failures preserve the resource
   reservation, first-cap nonzero work, two cap reports, nested diagnostic,
   failing phase, and `actual_work_complete=false`.
9. Phase status is emitted from actual call sites; a later failure overrides an
   earlier pass, and `independent_checks` includes only final passed phases.
10. Source SHA-256 is frozen at module load, is never recomputed while
    reporting, and is labeled diagnostic rather than executed-code attestation.
11. Generated controls stop at curve provenance and factor-base semantics. No
    generated density row is constructed.
12. The standalone frozen-B4 oracle exact-compares every candidate formal,
    point, recursive parent pair, and eligible item, plus the factor-base,
    representative, rejection, conflict, graph, model, and winner transcripts.
13. Exact `1/4` persistence passes while `999/4000` in one stratum fails.
    Duplicate-null, strict-collapse, comparison-count, stratum, and anti-
    splicing controls remain green.
14. Producer CLI development-row and canonical modes remain disabled.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 9 record(s)
```

The generated experiment index exactly matched `ledger.json` after its SGCP
version changed from 6 to 7.

The repository-wide record command is currently blocked by the unrelated
pre-existing unwrapped
`experiments/EXP-ECDLP-COMPRESSED-JOIN-001/hypothesis.json`. That file is
outside this change and was not modified.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 190 tests in 63.874s
FAILED (failures=1)
```

The other 189 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The run directory was
preserved. This is not a V7 assertion failure, but the repository-wide suite is
reported honestly as failed.

## Interpretation

`OBSERVATION`: V7 closes the demonstrated V6 fail-fast, nonblocking input,
partial receipt, diagnostic, source-hash, zero-row-control, candidate-list, and
source-bounded work-accounting defects under the focused test boundary.

This does not establish parser or allocator containment, canonical B6/B8
feasibility, actual family runtime, a coordinate-family advantage, a relation
generator, rank, linear algebra, target descent, preprocessing crossover, rho
improvement, or ECDLP result. Fresh independent exact-commit review remains
mandatory before even a launch-plan design.
