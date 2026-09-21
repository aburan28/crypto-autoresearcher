# Protocol design note — TASK-20260725-631

## Purpose

Freeze a **review-only** D≥6 support-matched null re-derivation protocol
(`SIG-D6-NULL-RECAL-v1`) that repairs the invalidated EXP-SIG-005 D6 axis before
any new SIG cascade measurement. Binding YAML:
`d6_null_protocol.yaml`.

## Inference

- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001

Fallback is infrastructure/policy metadata, not mathematical evidence.
Equivalence to research-sol-max is not claimed.

## Authorization

No rank / syzygy / residual measurement is authorized in BATCH-001. Independent
review PASS unlocks only *scheduling* of a later executor calibration task under
a fresh write_scope; a separate Coordinator ledger authorization is still
required before measurement. Protocol PASS is not cascade evidence and does not
change H-SIG-001 status.

## What failed (pinned)

At n=9 seed 1 D=6 (`RUN-EXP-SIG-005-k` vs `RUN-h`):

| arm | ncols | rank | shared sr_pred | deficit | residual_6 |
|---|---:|---:|---:|---:|---:|
| sem | 29332 | 27292 | 28068 | 776 | 2615 (retracted) |
| null | 31180 | 31179 | 28068 | −3111 | 4986 (C5 fail) |

Null is semi-regular through D≤5 and breaks only at D6: unequal column supports,
sr_pred matches neither arm, null extra/residual ≠ 0. Per DEC-20260720-001 /
EV-SIG-005 / KN-FIND-027, cascade claims remain admissible only for D≤5 until
repair. Legacy D6 magnitudes are quarantined.

## What this protocol freezes

1. **Invalidation** of `LEGACY-T11-D6-SHARED-SRPRED` — no reuse of the broken
   unaligned D6 baseline as structural evidence.
2. **Primary construction `ALIGN-SEM-SUPPORT`** — keep EXP-SIG-005 builders;
   at each D∈{3,4,5,6} restrict the null Macaulay matrix to exact `sem_cols`
   before calibrated rank/Koszul/residual analysis; hash
   `restricted_support` and `deleted_set = null_cols\\sem_cols`.
3. **Recalibrated prediction `sr_pred_calib`** — must match the aligned null
   ranks with null extra=0 and residual_D=0 through D=6 (Froberg-if-fit, else
   empirical null baseline labeled as such; else `CALIB_NO_GO`).
4. **Calibration gates that would have caught the D6 ncols mismatch:**
   - **CG-NCOLS** — calibrated arms share `|sem_cols|`; native
     `ncols_null ≠ ncols_sem` at D≥6 marks the legacy baseline invalid
     (trips 31180≠29332).
   - **CG-SRPRED** — forbids a shared prediction that matches neither arm.
   - **CG-NULL-ZERO** — repaired C5 (aligned null extra/residual = 0 at D≤6).
   - **CG-D5-CONTINUITY** — must not break the already-valid D≤5 null.
   - **CG-SUPPORT-HASH** — blocks ncols-only wrong-column deletions.
   - **CG-LEGACY-QUARANTINE** — blocks structural reuse of RUN-h D6 magnitudes.
5. **Cells** — primary calibration n=12 seed 2; regression witness n=9 seed 1.
6. **Admissibility split** after later `CALIB_PASS` + Coordinator measurement
   authorization: residual_6 / birth-law test, extra_6 + closures A3_6/A4_6/A5,
   deficit_6 vs `sr_pred_calib` under equal ncols (toy only). Still
   inadmissible: EXP-SIG-005 D6 magnitudes, d_reg comparisons, sub-rho /
   crypto claims, DREG `deficit_genuine` via this card.
7. **Already admissible without this protocol** — D≤5 cascade package
   (2n/3+1 D4 law through n=24; residual_5 through n=18 non-monotone; D5
   cross-instrument continuity).

## Separation from DREG CTRL-B

CTRL-B admits `deficit_genuine` on the DREG rank channel. This card recalibrates
the SIG signature / non-rewritable residual baseline. Shared diagnosis (D6
support confound); different metrics and admission predicates. Neither PASS
discharges the other.

## Outcomes (later executor, not this batch)

| Outcome | Meaning |
|---|---|
| `CALIB_PASS` | Equal-ncols semi-regular null baseline admitted for declared cells |
| `CALIB_NO_GO` | Instrument cannot host such a null — degree axis stays closed (not cascade falsification) |
| `failed_infrastructure` | ENOSPC/OOM/timeout — never evidence (rule 5) |

## Novelty / prior art

Adaptation of the already-demonstrated D6 support confound (EV-SIG-005,
DREG support probes) into an explicit SIG calibration contract with
ncols/sr_pred/null-zero gates. Not claimed as a new algebraic theorem.
