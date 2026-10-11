# Analysis — EXP-BINSTD-9d67ed Stages 0–1

Hypothesis: `H-BINSTD-d460e5`
Experiment: `EXP-BINSTD-9d67ed` (v1, approved `DEC-20261003-5c1347`)
Producer: `TASK-20261003-8c5337`
Review: `TASK-20261004-b86fea` / `REVIEW-BINSTD-9d67ed-20261004`
Evidence: `EV-BINSTD-461d48`
Decision: `DEC-20261004-98dcf7`
Execution code: `892923655e6807a3ae35844751f91c6407c3b4a6` (`code.dirty: false`)

This note is Coordinator review of archived observations. The Stage 1 replay ran from a copy under `/tmp/review-binstd-9d67ed` and did not rewrite the archived stage files. Scope is the toy n=17 encoding-residue instrument. The card records `certificate.kind` none. It does not advance an exponent and it does not speak to n≥131.

---

## Observation

Two runs. Both receipts are `output_validated` with `returncode` 0 and `check_returncode` 0. Both manifests are `completed_valid`, `code.dirty` false, and `certificate.kind` none. Both raw `claims.break` and `claims.exponent_move` are false. `claims.n_ge_131` is absent from both run manifests and both raw-result claim objects; the Stage 0 prediction freeze records it as false. Checker stdout is `OK` on both. Amazon Bedrock is `NOT SELECTED`. No Magma, Sage, or AUXIN.

| Run | Stage | Outcome | Receipt | Manifest |
| --- | --- | --- | --- | --- |
| `RUN-BINSTD-c87287` | 0 | `O-STAGE0-OK` (`twin_ok: true`) | `output_validated` | `completed_valid` |
| `RUN-BINSTD-4c79f8` | 1 | `O-SUPPORT` | `output_validated` | `completed_valid` |

`RESULTS.md` carries the single label `O-SUPPORT`, matching `RUN-BINSTD-4c79f8` raw `outcome`.

Stage 0 (`RUN-BINSTD-c87287`): outcome `O-STAGE0-OK`, `twin_ok` true. The freeze pins α = 3, the encoder, the seeds, and the Karabina transform.

Stage 1 panels, twenty rows on each cell. Blind medians, recomputed from `stage1/panels.json` rows before `implementation/` was opened. Each stored density equals `C_nl/N_var`.

| Cell | n | ell | completed | median treated | median null | treated ≤ 3 | null ≥ treated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `n17_l3` | 17 | 3 | 20 | 5/3 = 1.6666666666666667 | 17/6 = 2.8333333333333335 | true | true |
| `n17_l4` | 17 | 4 | 20 | 7/4 = 1.75 | 17/8 = 2.125 | true | true |

Controls on the archived control table: twin meters, the unsymmetrised null encode (`null_unsymmetrised_encode: true`), and frozen α = 3 (`frozen_alpha: 3`, `n_targets: 20`, shared encoder pin).

Temp Stage 1 replay (`/tmp/review-binstd-9d67ed`, that copy's stage1 json files and `RESULTS.md` deleted): outcome `O-SUPPORT`. Treated medians 1.6666666666666667 and 1.75. Archived repo stage files were not overwritten.

---

## Comparison

Producer `RESULTS.md` label `O-SUPPORT` agrees with `RUN-BINSTD-4c79f8` and with the temp replay.

Panel headers match the blind medians: treated 1.6666666666666667 and 1.75, null 2.8333333333333335 and 2.125. Both treated medians sit at or under the frozen α = 3. Both null medians sit at or above the treated median on the same cell.

`decide_outcome` emits `O-ARTIFACT` when a panel is artifact or `twin_ok` is false. A zero-`N_var` leftover (`N_var` = 0 with `C_nl` > 0) sets the meter artifact flag and clears `twin_ok`, so that leftover is `O-ARTIFACT`. Fewer than 20 completed targets is `O-INCONCLUSIVE`. Treated median above 3 is `O-FAIL-BAND`. A treated band with null median below the treated median is `O-FAIL-NULL`. Only the remaining conjunction is `O-SUPPORT`. Archived completed counts are 20 and 20. `band_holds` is read after the artifact and count gates.

The twin meter is an internal control inside this one package. It is not a second experiment.

---

## Inference

`O-SUPPORT` is the pre-registered conjunction on both Stage 1 cells: twin agreement, 20 completed targets, treated median ≤ 3, and null median ≥ treated. Stage 0 is `O-STAGE0-OK`.

Direction: **supports**. Decision: **support**. Strength: **preliminary**. `claim_tier`: toy. `proof_status`: empirical_only.

Hypothesis moves `approved` → `supported`. Experiment moves `approved` → `analyzed`. The idea text is unchanged. The goal head is not edited.

Stage 2 (`n` in {19, 23}) is not authorized from this package. A later contract would be a new experiment. One package is not a replication. No `KN-FIND`: preliminary strength is below the promotion bar, and this toy band is not a durable attack boundary.

Review-plan prior vs outcome: matched on J1, J2, and J3. No prior overturn. `PD-1` (one coordinator task owns all three joints; no separate validator or red-team) is the recorded procedure deviation.

---

## Limitation

- Toy n=17 only, cells (17, 3) and (17, 4), frozen α = 3, one package.
- `certificate.kind` none. No discrete-log solve.
- No exponent. No n≥131 result.
- The twin meter is an internal control, not a replication.
- Coordinator-direct review (`PD-1`). No independent validator and no red-team session.
- Amazon Bedrock not used. No AUXIN, Magma, or Sage.
