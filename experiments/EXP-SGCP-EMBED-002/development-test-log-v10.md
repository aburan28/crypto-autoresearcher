# EXP-SGCP-EMBED-002 development test log v10

## Scope

No V10 generated density row, canonical matrix, runner, launch plan, or run was
authorized or created. This log covers the public producer surface, frozen-only
legacy controls, exact completed graph/expansion deltas, preserved interrupted
work, one frozen `p=19,a=2,b=9,q=23,B=4` density row, and inherited finite
mathematical controls.

Claim boundary: no-run implementation preflight only; `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. `maximum_runs=0` remains unchanged.

## Frozen source snapshot

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `0e6e5b444ae18b426926098a1563bb002808779baaa8c4d281e86630bfba1f24` |
| `src/verify_sgcp_embed_family.py` | `540ef51e311114524946b5c87c8399e7353dc418dabddfa8f3d0bec9b013dde9` |
| `tests/test_sgcp_embed_family.py` | `be2f5e8edacc6299c20d58f9a6a1a74682f611efc0331ebf622c088d6cba9008` |
| `hypothesis.json` | `bcda153c81bd967864479a7bda11caf7f3e565820d796dcc4c709de9d9d12d59` |
| `specification.json` | `303e249db0131620fbdb407de21a22652c0d87fbd52c34641a5238d82ed2fc89` |
| `contract.md` | `3d020f814f4eb900e7b34a581351164aceffe6a8e36db8d32dbc6f357eac4501` |
| `protocol-amendment-v10.json` | `4e4a73cc9dfa3bb81ba39d6997ebd71f555e06c34132f2acca259dc2a574ba21` |
| `revision-response-v10.md` | `a2093b1977ec0ac93dfe6a475a22683687337e6ab0e26404017014372b3129da` |
| `source-self-review-v10.md` | `1c5cac118cef83731439530f44ff5806e2cc1469821c29ade2c944d2da4edccc` |

The eventual Git commit is recorded separately because this log is part of the
commit being formed.

## Focused command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_sgcp_embed_family.py
```

Observed on 2026-07-20:

```text
Ran 60 tests in 2.738s
OK
```

The transient duration is not a cryptanalytic cost metric.

## Passing controls

1. Public `generated_curve` and `build_legacy_row` reject before private or
   factor-base work. Public legacy calls reject both frozen and non-frozen
   associations without changing operation counters.
2. `_build_frozen_legacy_control_row(B)` validates exact integer
   `B in {4,6,8}` before constructing the frozen curve and reproduces all
   predecessor optima. There is no arbitrary-curve legacy control interface.
3. Public `build_density_row` rejects non-frozen associations before
   factor-base work and rejects a wrong-length point list before scanning point
   contents. Only the exact frozen B4 control is admitted.
4. The successful frozen path reports 31 graph-candidate evaluations, 66
   eligible conflict checks, 144 eligible pair-output cells, and 214 expansion
   cells. Each completed row equality-checks those dimensions against its
   independently reconstructed candidate, eligible, and factor-base counts.
5. Suppressing each of the four completed charges produces an exact zero-versus-
   expected mismatch. Overcharging one candidate evaluation produces 32 versus
   31. Every case invalidates the row with `actual_work_complete=true` and a
   failed graph/expansion unit.
6. In-loop failure after the second matching charge still preserves exact value
   2, the trusted reservation, a failed graph/expansion unit, and
   `actual_work_complete=false`.
7. The rest of the frozen actual-work vector remains one frozen, one semantic,
   and four primary point enumerations; 218 replay nodes; 250 primary nodes;
   268 entries in each replay cache; 56 primary-support and 129 primary-
   constrained cache entries; 401 retained-model calls; and 41,404 retained-
   model cells.
8. V1-V9 schemas reject without V10 row verification. Exact document, row,
   nested, summary, gate, accounting, and report schemas remain closed.
9. Source-sized admission, nested authentication, summary/gate reconstruction,
   phase closure, actual-to-reservation dominance, bounded diagnostics,
   single-snapshot input, and all inherited standalone frozen-B4 semantic
   controls continue to pass.
10. Producer development-row and canonical modes remain disabled. No generated
    density row or run budget was consumed.

## Record validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate \
  experiments/EXP-SGCP-EMBED-002
```

Observed result:

```text
validated 12 record(s)
```

A freshly generated repository index matches `ledger.json` byte-for-byte.

## Repository-wide suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Observed result:

```text
Ran 204 tests in 76.100s
FAILED (failures=1)
```

The other 203 tests passed. The sole failure is the pre-existing immutable-run
guard `test_locked_runner_stdout_roles_compose_without_descendants`, which
refused to overwrite
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001`. The directory was
preserved. This is not a V10 assertion failure, but the repository-wide suite
is reported honestly as failed.

## Interpretation

`OBSERVATION`: V10 closes the demonstrated V9 public legacy-producer and
completed graph/expansion equality defects under the focused no-run test
boundary. It also narrows the private predecessor control to the frozen curve
and preserves all incremental exception receipts.

This does not establish parser or allocator containment, CPU/RSS or memory-
bandwidth feasibility, a standalone B6/B8 complete oracle, canonical B6/B8
runtime, coordinate-family advantage, relation generation, rank, linear
algebra, target descent, fixed-curve preprocessing crossover, rho improvement,
an exponent, or an ECDLP break.

## Next action

Commit the exact V10 snapshot and obtain fresh independent theory, accounting,
and red-team review. Keep `maximum_runs=0`; do not design a launch plan without
three explicit scoped `GO` decisions.
