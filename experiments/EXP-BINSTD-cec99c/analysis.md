# Analysis — EXP-BINSTD-cec99c Stages 0–1

Hypothesis: `H-BINSTD-d09592`
Experiment: `EXP-BINSTD-cec99c` (v1, approved `DEC-20261003-be1d8e`)
Producer: `TASK-20261003-ef1f84`
Review: `TASK-20261004-4cad32` / `REVIEW-BINSTD-cec99c-20261004`
Evidence: `EV-BINSTD-4d3c15`
Decision: `DEC-20261004-28dd8f`
Execution code: `b3921b2f015c908c20a1e10c0657a4c30ecaec67` (`code.dirty: false`)

This note is Coordinator review of archived observations. The Stage 1 replay ran from a copy under `/tmp/review-binstd-cec99c` and did not rewrite the archived stage files.

Review-plan prior (recorded before this analysis): expect **inconclusive** because `decide()` returns `O-ARTIFACT` on twin failure, `O-INCONCLUSIVE` when any cell's raw count is below its surplus floor, and only then reads the null and the `R ≥ 1/2` band. Archived raw is 3 against need_raw 4, 6, and 8. Twins agree. `band_holds` is true on the partial bags. The retention band is not the label.

---

## Observation

Two runs. Both receipts are `output_validated` with `returncode` 0 and `check_returncode` 0. Both manifests are `completed_valid`, `code.dirty` false, and `certificate.kind` none. Both `claims.break`, `claims.exponent_move`, and `claims.n_ge_131` are false. Checker stdout is `OK` on both. Amazon Bedrock is `NOT SELECTED`. No Magma, Sage, or AUXIN.

| Run | Stage | Outcome | Receipt | Manifest |
| --- | --- | --- | --- | --- |
| `RUN-BINSTD-3f972b` | 0 | `O-STAGE0-OK` (`twin_ok: true`) | `output_validated` | `completed_valid` |
| `RUN-BINSTD-d08b90` | 1 | `O-INCONCLUSIVE` (`surplus_met: false`, `band_ok: true`, `twin_ok: true`) | `output_validated` | `completed_valid` |

`RESULTS.md` carries the single label `O-INCONCLUSIVE`, matching `RUN-BINSTD-d08b90` raw `outcome`.

Stage 0 (`RUN-BINSTD-3f972b`): `fb_size_n17` 4, `null_identity_R` 1.0, conjugate probe `pass` true. Catalog seed `2026100311`, collect seed `2026100312`, ρ = 1/2.

Stage 1 panels, n=17, ell=3, `fb_size` 4, ρ = 1/2:

| Surplus | need_raw | raw | unique_a | unique_b | R | band_holds | null unique | null R = 1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1/1 | 4 | 3 | 2 | 2 | 2/3 | true | 3 | true |
| 3/2 | 6 | 3 | 2 | 2 | 2/3 | true | 3 | true |
| 2/1 | 8 | 3 | 2 | 2 | 2/3 | true | 3 | true |

Control-table: `twins_agree` true on all three cells, `null_R_is_one` true on all three.

Blind floors, computed from `fb_size` 4 and surplus pairs `(1,1)`, `(3,2)`, `(2,1)` before `implementation/` was opened: `1*4//1 = 4`, `3*4//2 = 6`, `2*4//1 = 8`. Archived raw 3 is strictly below each floor.

Temp Stage 1 replay (`/tmp/review-binstd-cec99c`, archived `stage1/panels.json`, `stage1/control-table.json`, and `RESULTS.md` deleted on the copy only): outcome `O-INCONCLUSIVE`, raw counts 3, 3, 3, need_raw 4, 6, 8. Repo hashes of those three archived files were unchanged after the replay.

---

## Comparison

Producer `RESULTS.md` label `O-INCONCLUSIVE` agrees with `RUN-BINSTD-d08b90` and with the temp replay.

`need_raw` on the archived panels is 4, 6, and 8, which is the same triple as the blind integer floors. Each archived raw count is 3.

`band_holds` is true on every partial bag (`unique_a` 2, raw 3, and `2 * 2 >= 3 * 1`). That band reading sits on bags that never reached the surplus floor. `decide()` emits `O-INCONCLUSIVE` on `surplus_met` false before it reads `band_ok`. `check.py` refuses `O-SUPPORT` and `O-FAIL-BAND` unless `surplus_met` is true. The true band flag does not replace the floor label.

Stage 0 twin freeze holds (`O-STAGE0-OK`), so the package is not `O-ARTIFACT` from a twin mismatch. Stage 1 twins also agree (`unique_a` = `unique_b` = 2 on each cell).

---

## Inference

`O-INCONCLUSIVE` is the unmet-surplus branch. Raw 3 is below need_raw 4, 6, and 8. Twins agree. `band_holds` true on the partial bags is not the label.

Direction: **neutral**. The surplus floor stopped the label before the retention band, so this package neither supports nor weakens `H-BINSTD-d09592`.

Decision: **inconclusive**. Strength: **inconclusive**. `claim_tier`: toy. `proof_status`: empirical_only.

Not support: the surplus floor was not met. Not weaken and not `reject_scoped`: the `R ≥ 1/2` branch was not the deciding branch, and one empirical-only package is not a scoped rejection.

Hypothesis and experiment move `approved` → `analyzed`. Stage 2 (`n` in {23, 31}) stays unauthorized. No discrete logarithm, no exponent, no ECC2K-130 result. No `KN-FIND`.

Review-plan prior vs outcome: matched on J1, J2, and J3. No prior overturn. `PD-1` (one coordinator task owns all three joints; no separate validator or red-team) is the recorded procedure deviation.

---

## Limitation

- Toy n=17, ell=3, `fb_size` 4, three surplus cells, one collect seed. Transfer to n=23, n=31, or ECC2K-130 is an unvalidated non-claim.
- `certificate.kind` none. This card claims no discrete-log solve.
- The retention ratio 2/3 is a reading of partial bags of size 3. It is not a surplus-met band result.
- One unreplicated package. Coordinator-direct review (`PD-1`). No independent validator and no red-team session.
- A later contract may raise the raw budget. This package does not, and Stage 2 is not opened from it.
- Amazon Bedrock not used. No AUXIN.
