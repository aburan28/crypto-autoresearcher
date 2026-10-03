# Analysis — EXP-BINSTD-f9a860 / H-BINSTD-0514c3

Review plan: `experiments/EXP-BINSTD-f9a860/review/review-plan.yaml`
(`REVIEW-BINSTD-f9a860-20261001`). Producer: `TASK-20261001-af8338`
(package ~`f9115cf00`). Evidence: `EV-BINSTD-813422`. Decision:
`DEC-20261001-93ce58`.

Class: **tooling**. No ECDLP attack, no break, no curve attack-cost claim,
no CI wire-up in this package.

---

## Observation

**Validity.** Four runs, all `status: completed_valid`, `result.valid:
true`, `certificate.kind: none`, `termination_reason: completed` (S3) /
equivalent completed termination on S0–S2:

| Run | Stage | Primary metrics |
| --- | --- | --- |
| `RUN-BINSTD-f464e4` | 0 | stage0_complete; schema outline + methodological note + gitignore + validator present |
| `RUN-BINSTD-239252` | 1 | `cells_seeded_count=61`; `transcription_fidelity_fraction=1.0` |
| `RUN-BINSTD-4d4944` | 2 | `schema_unmutated_pass=true`; `generated_view_gitignored=true`; `write_once_layout_pass=true`; `error_count=0` |
| `RUN-BINSTD-82416b` | 3 | `battery_pass_count_out_of_6=6`; peak RSS ≈22.3 MiB; wall ≈4.16 s |

Raw-result metrics agree with manifests and with stage1/2/3 YAML reports.
`n_runs=4 ≤ maximum_runs=12`. Required artifacts present
(`stage0/`, `stage1/`, `stage2/`, `stage3/`,
`tools/validate_reachability_table.py`, 61 shards under
`analysis/binstd-curve-audit/reachability/`). Generated view path is
gitignored (`.gitignore:339`) and not tracked. Live validator re-run this
session: `cells=61 errors=0 rc=0`. No Bedrock. Every artifact reviewed
carries `no_break_claim: true`.

**Stage 0.** Schema outline documents HOLD-F fields and verdict enum
including `NOT_YET_ASSESSED`. Methodological note states no-break,
`certificate.kind: none`, CI out of scope. Validator scaffold present
(later filled for Stage 2).

**Stage 1.** `seed-policy.yaml`: `grid_choice: ABSENT_preferred` (no
invented ~175 `NOT_YET_ASSESSED` files); `phi_stable_policy`:
`STRUCTURALLY_EMPTY` only when `ord_m(2)=m-1` (9e5383 correction);
ECC2K-130 hand-seeded from `KN-LIT-661e97`; `rho_convention:
CORR-20260922-81aeab` on matched_rho; forbidden 77bf31 COMPUTED prose not
used. `fidelity-report.yaml`: `n_compared=39`, `n_pass=39`,
`transcription_fidelity_fraction=1.0` (threshold 0.01 bit). Spot check
this session: ECC2K-130 `l` bit-length 130; decomposition_m2 cell carries
continuous-product formula with `floor_bits=89.25` matching fidelity
recompute within threshold.

**Stage 2.** Checks implemented: schema, hash, supersession,
liveness_informational. Unmutated smoke pass; generated view rebuildable
to gitignored path.

**Stage 3 battery (scratch copies).**

| Case | Name | Expect | Actual | Named cell / pointer |
| --- | --- | --- | --- | --- |
| 1 | valid_unmutated_seed | PASS | PASS | — |
| 2 | one_byte_certificate_flip | FAIL | FAIL | `ECC2K-130/GHS_cover` / README.md (sha256 mismatch) |
| 3 | missing_input_record_id | FAIL | FAIL | `ECC2K-130/decomposition_m2` / missing IDEA id |
| 4 | synthetic_supersession | FAIL | FAIL | `ECC2K-130/decomposition_m2` / superseded `IDEA-20260922-6028ed` |
| 5 | bad_missing_quantity_vocab | FAIL | FAIL | `ECC2K-130/QSP` / `missing_quantity` |
| 6 | unrelated_new_idea_false_positive | PASS | PASS | unrelated IDEA id (control) |

`scratch_copy_discipline: true`; `live_ledger_unmutated: true`. Case 5
battery-report lists `error_count: 0` / empty `first_errors` while `rc=1`
and case pass=true; independent reproduction this session yields
`error_count=1` with schema finding
`OPEN missing_quantity 'NOT_A_VALID_VOCAB_STRING_battery' not in controlled
vocabulary` at pointer `missing_quantity` — case outcome stands; report
field incompleteness noted under Limitations.

---

## Comparison

Against `specification.yaml` success criterion and
`H-BINSTD-0514c3` DO-1:

| Criterion | Required | Observed |
| --- | --- | --- |
| `schema_unmutated_pass` | true | true |
| `battery_pass_count_out_of_6` | 6 | 6 |
| `transcription_fidelity_fraction` | 1.0 | 1.0 |
| `write_once_layout_pass` | true | true |
| `generated_view_gitignored` | true | true |
| `certificate.kind` | none | none (4/4) |
| CI wire-up | not in scope | not done |
| Break / attack-cost claim | forbidden | absent |

Preregistered prediction (A)–(E) matched. Case 6 proves-too-much control
passed (unrelated ledger growth does not fail validation). Case 1
unmutated pass confirms validator is not a constant tripwire.

Documented deviations vs unrepaired HOLD-F prose:

1. **ABSENT preferred** over inventing `NOT_YET_ASSESSED` shards —
   explicitly allowed by contract seed policy.
2. **`phi_stable_subspace_base`**: STRUCTURALLY_EMPTY only when
   `ord_m(2)=m-1`; otherwise COMPUTED ord arithmetic — recorded in
   `seed-policy.yaml` as 9e5383 correction; not a silent fabrication.

Neither deviation lights DO-2/DO-3/DO-4.

---

## Inference

Stages 0–3 package is **valid**. Observations match DO-1-carrier-ready:
the HOLD-F-corrected per-cell write-once reachability layout plus
`validate_reachability_table.py` passes unmutated validation and the
named six-case Sigma_ledger battery, with transcription fidelity 1.0 on
seeded re-derived cells and a gitignored generated view.

Official reading: **support** the scoped tooling claim of
`H-BINSTD-0514c3` (HEUR-H0 battery exhaustiveness for named ops;
HEUR-H1 write-once + gitignored-view layout). Strength **preliminary** —
single unreplicated producer package; the six cases enumerate named
operations but are not an independent-implementation replication.
Therefore **no KN-FIND promotion** (support + preliminary is below the
replicated/strong promotion gate).

CI integration remains a **separate** Coordinator infrastructure
decision after 6/6; this support does **not** authorize workflow edits
and does **not** claim any curve's attack cost or a break.

Hypothesis: `approved` → `supported`. Experiment: `approved` →
`analyzed`.

---

## Limitation

- Tooling / observational claim only; no scientific ECDLP result.
- Seeded coverage is 61 cells; most of the ~30×13 grid remains ABSENT —
  absence is not STRUCTURALLY_EMPTY and is not progress toward a break.
- Validator certifies pointer consistency (schema/hash/supersession), not
  scientific truth of COMPUTED floors as attack costs.
- Case 5 battery-report omitted structured `first_errors` (rc-based pass
  still correct; reproduced independently).
- Scratch battery does not prove behaviour under real concurrent git
  races (disclosed optimistic assumption).
- OPEN-cell liveness is informational only; string-exact
  `missing_quantity` matching may miss semantic equivalents.
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Manifests record `dirty: true` at producer write; package later
  committed under `f9115cf00`.
- Single unreplicated package → strength preliminary, not replicated/
  strong.
- No CI; no Bedrock; no break; no exponent; no attack-cost claim.
