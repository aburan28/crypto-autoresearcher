# Implementation note — EXP-BINSTD-f9a860 / TASK-20261001-af8338

## Protocol followed

Stages 0–3 of `experiments/EXP-BINSTD-f9a860/specification.yaml` (approved
by `DEC-20261001-8570c3`). Observations only; no hypothesis/status edits.

## Deliverables

| Stage | Artifacts |
| --- | --- |
| 0 | `stage0/schema-outline.yaml`, `stage0/methodological-note.md`, gitignore for generated view, `tools/validate_reachability_table.py` scaffold→full |
| 1 | `stage1/seed-policy.yaml`, `stage1/fidelity-report.yaml`, 61 per-cell shards under `analysis/binstd-curve-audit/reachability/` |
| 2 | live checks + `--emit-view`; `stage2/validator-smoke.yaml` |
| 3 | `stage3/battery-report.yaml` (6/6) |

## Seed policy (deviations documented)

- **ABSENT preferred** over inventing ~175 `NOT_YET_ASSESSED` shards.
- `phi_stable_subspace_base`: HOLD-F text said STRUCTURALLY_EMPTY on all
  prime-degree rows; applied `IDEA-20260922-9e5383` correction —
  STRUCTURALLY_EMPTY only when `ord_m(2)=m-1`; otherwise COMPUTED `ord`
  arithmetic. Documented in `seed-policy.yaml`.
- No COMPUTED cells from unrepaired `IDEA-20260922-77bf31` prose.
- ECC2K-130 hand-seeded from `KN-LIT-661e97` + Weil recursion (`h=4`,
  `l=680564733841876926932320129493409985129`).
- `matched_rho` pins `rho_convention: CORR-20260922-81aeab`.

## Runs

| Run ID | Stage |
| --- | --- |
| RUN-BINSTD-f464e4 | 0 |
| RUN-BINSTD-239252 | 1 |
| RUN-BINSTD-4d4944 | 2 |
| RUN-BINSTD-82416b | 3 |

All manifests use `certificate.kind: none`.

## Battery

6/6 on scratch copies. Cases 2–6 never mutate the live ledger or live
reachability shards.

## Not done (by contract)

- CI workflow edits (Stage 4 / later DEC)
- Any break or curve attack-cost claim
- Committing the generated table view
