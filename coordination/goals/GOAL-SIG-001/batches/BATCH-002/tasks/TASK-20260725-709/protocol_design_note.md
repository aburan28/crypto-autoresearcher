# Protocol design note — TASK-20260725-709

## Purpose

Repair freeze of **SIG-D6-NULL-RECAL-v2**, superseding
`TASK-20260725-631` / `SIG-D6-NULL-RECAL-v1` (snapshot `91d10c79cec0`) to
discharge red-team `RT-20260725-633` (REVISE) per `EV-SIG-009` /
`DEC-20260725-014`. Binding YAML: `d6_null_protocol.yaml`.

## Inference

- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001

Fallback is infrastructure/policy metadata, not mathematical evidence.
Equivalence to research-sol-max is not claimed.

## Authorization

No rank / syzygy / residual measurement is authorized in BATCH-002. Independent
review PASS unlocks only *scheduling* of a later executor calibration task under
a fresh write_scope; a separate Coordinator ledger authorization is still
required before measurement. Protocol PASS is not cascade evidence and does not
change H-SIG-001 status.

## What v1 failed (RT-20260725-633)

At n=9 seed 1 D=6 (`RUN-EXP-SIG-005-k` vs `RUN-h`), the legacy baseline remains
correctly invalidated (unequal supports 31180 vs 29332; shared sr_pred matches
neither arm). Authorization honesty held. Blocking REVISE reasons:

| ID | Defect | v2 repair |
|---|---|---|
| **OBJ-633-1** | Definition required identical column *sets*; CG-NCOLS checked cardinalities only; CG-SUPPORT-HASH was optional (`_pass_if_alignment_used`); secondary searched equal *counts* | CG-NCOLS = set equality; CG-SUPPORT-HASH unconditional on every CALIB_PASS path; secondary closed as CALIB_PASS path |
| **OBJ-633-2** | CG-D5-CONTINUITY "unaligned **or** aligned" | Explicit conjuncts: unaligned D≤5 C5 **and** aligned D≤5 null-zero/rank |
| OBJ-633-3 (nb) | No explicit fail if `sem_cols ⊈ null_cols` | CG-SUPPORT-SUBSET / `CALIB_FAIL_SUPPORT_SUBSET`; forbid padding |
| OBJ-633-4 (nb) | CG-LEGACY-QUARANTINE labeled `machine_check` | Relabeled `package_review_check` |

Cheapest mutation blocked by v2: keep `|null_cols|==|sem_cols|` while
`null_cols ≠ sem_cols` → `CALIB_FAIL_NCOLS` / `CALIB_FAIL_SUPPORT_HASH`.

## What this repaired protocol freezes

1. **Invalidation** of `LEGACY-T11-D6-SHARED-SRPRED` — unchanged quarantine of
   RUN-h D6 magnitudes.
2. **Primary construction `ALIGN-SEM-SUPPORT`** — sole CALIB_PASS-admissible
   construction; require `sem_cols ⊆ null_cols`, then restrict null to exact
   `sem_cols`; publish support/deletion hashes.
3. **Hard support-set admission (CTRL-SUPPORT-SET / CTRL-SUPPORT-HASH):**
   - **CG-NCOLS** — `calibrated_null_cols(D) == sem_cols(D)` as sets;
     cardinalities are derived only.
   - **CG-SUPPORT-HASH** — unconditional admission metric (no
     `_pass_if_alignment_used`); `sem_support_hash == calibrated_null_support_hash`.
   - **CG-SUPPORT-SUBSET** — fail closed if sem is not a subset of null.
4. **Secondary** renamed `REJECT-UNTIL-NATIVE-SUPPORT-MATCH`; requires native
   *set* equality if attempted; `calib_pass_admissible: false` (count-only
   path closed).
5. **CG-D5-CONTINUITY** — (a) unaligned D∈{3,4,5} C5 continuity **and**
   (b) aligned D≤5 null-zero / rank match under ALIGN.
6. **CG-SRPRED / CG-NULL-ZERO / CG-LEGACY-QUARANTINE** — retained; legacy gate
   is a package-review check.
7. **Cells** — primary n=12 seed 2; regression witness n=9 seed 1.
8. **Admissibility split** after later `CALIB_PASS` + Coordinator measurement
   authorization unchanged in spirit; still inadmissible: EXP-SIG-005 D6
   magnitudes, equal-ncols/unequal-support “calibration”, d_reg / sub-rho /
   crypto claims, DREG `deficit_genuine` via this card.

## Separation from DREG CTRL-B

CTRL-B admits `deficit_genuine` on the DREG rank channel. This card recalibrates
the SIG signature / non-rewritable residual baseline. Shared diagnosis (D6
support confound; ncols-only insufficient); different metrics and admission
predicates. Neither PASS discharges the other.

## Outcomes (later executor, not this batch)

| Outcome | Meaning |
|---|---|
| `CALIB_PASS` | Equal-*support-set* semi-regular null baseline admitted for declared cells |
| `CALIB_NO_GO` | Instrument cannot host such a null — degree axis stays closed (not cascade falsification) |
| `failed_infrastructure` | ENOSPC/OOM/timeout — never evidence (rule 5) |

## Novelty / prior art

Adaptation of the already-demonstrated D6 support confound (EV-SIG-005,
DREG support probes / CTRL-B set-hash discipline) into an explicit SIG
calibration contract with unconditional set-identity gates. Not claimed as a
new algebraic theorem.
