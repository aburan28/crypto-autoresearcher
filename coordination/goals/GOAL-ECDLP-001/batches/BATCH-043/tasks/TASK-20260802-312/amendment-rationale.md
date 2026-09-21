# TASK-20260802-312 — amendment rationale (PA-IT-001-v3-rc43-repair-3)

## Authority

DEC-20260802-232 opens BATCH-043 to discharge DEC-20260802-212 after
RT-20260802-244 returned REVISE on PA-IT-001-v3-rc36-repair-2.

## What changes

1. **B1:** Introduce `C_special_smart` as the sole anomalous pass threshold;
   demote `C_special_field_DLP` to MOV/comparator-only. This removes the
   model-inversion that made genuine Smart plants fail `R_xfer < 0.7` under
   field-DLP-scale charges (RT-146-O1 / RT-130-O4 class).
2. **B2:** Replace qualitative `sota_delta` prose with explicit three-axis
   fields. For this design-only overlay all three axes are `not_applicable`
   with a non-solver scope sentence.
3. **B3:** Bind a single entrypoint
   `experiments/EXP-IT-001/implementation/run_bounded_toy.py` and freeze exact
   smoke/measure command strings. Drop dual `.sage` primary entrypoint and any
   "may adjust CLI flags" language.
4. **M1:** Require `start_j_speciality: nonspecial` and
   `path_is_reverse_of_planted: true` on the transfer certificate.
5. **M2:** List `recompute_null_plant_from_ledger.py` in
   `implementation_archive_manifest`; absence invalidates the run package.
6. **M3:** Soften the MOV formula ban to pass-threshold-only; allow labeled
   comparator columns.

## What is not claimed

No implementation, experiment, ECDLP exponent improvement, novelty, SOTA,
support, rejection, closure, or breakthrough. H-IT-001 remains `specified`.

## Pareto

- `dominated_by`: Pollard rho at exponent 1/2
- `sota_delta` axes: all `not_applicable` (non-solver design overlay)
