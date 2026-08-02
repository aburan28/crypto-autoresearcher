# Red-Team Review: Coordinate Energy Certificate V2

## Handoff: Verified computation with a failed mandatory control

### Claim or task

Determine whether the frozen V2 packet supports a coordinate-family signal or
a scoped negative result.

### Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `CONTROL-INVALID`.

### Assumptions

- the audited source commit is
  `17f004d97c883444319dd0b11cc97e209ce917f1`;
- scalar censuses exist only as generated-toy diagnostic ground truth;
- canonical random fibers are the registered null;
- the exact E4 and certificate families are interpreted only through their
  frozen multiple-testing procedures;
- all four control classes are mandatory.

### Evidence so far

- the producer launched from a clean source tree;
- nine generated prime-order curves and 18,423 null sets were evaluated;
- zero of 27 exact E4 tests and zero of 81 certificate tests were rejected
  after Holm correction;
- zero candidate predictors passed;
- literal AP, signed AP, and predictor-positive controls passed;
- the predictor-negative control failed;
- an independent implementation reconstructed all curves, candidates, nulls,
  target rows, predictors, controls, ranks, and family gates;
- direct ordered-four-loop D4 agrees with the producer's convolution result;
- all 14 registered mutations are rejected.

### Findings

1. **The packet is inferentially invalid despite valid arithmetic.** The
   contract makes all controls mandatory. A failed negative control prevents
   both positive promotion and a candidate-family negative.
2. **The negative-control failure is caused by rare-bucket selection.** The
   selected infinity bucket covers six training rows and three held-out rows.
   Two positive permuted labels among three predictions produce `0.333982`
   retained enrichment while recall is `0.000083` and the predictor's rank is
   `0.335938`.
3. **The current enrichment cap and learner eligibility rules are
   inconsistent.** The gate correctly prevents this predictor from passing,
   but the separate control cap assumes enough predictions for enrichment to
   be stable. The learner needs a training-coverage floor before bucket
   selection.
4. **Candidate predictors show the same weak learner behavior.** Their chosen
   buckets cover only four to eight training rows. All have zero held-out
   recall and rank one. These outcomes cannot be promoted into evidence
   because the negative control demonstrated that the selection surface is
   not calibrated.
5. **The exact energy and certificate paths remain useful.** Their arithmetic,
   multiple-testing order, public witnesses, and mutation resistance replay
   independently. The protocol defect is localized to predictor
   eligibility/control calibration.
6. **The smallest raw energy rank is not a signal.** The `0.034180` local rank
   is one of 27 preregistered tests and fails Holm correction. No
   post-selection emphasis is allowed.
7. **Finite toy evidence remains model-bound.** Factor bases contain only five
   or seven points, the largest subgroup order is 16,607, and diagnostic
   discrete-log indexing is unavailable in an attack. Nothing here implies a
   deployment result or scaling improvement.
8. **Pre-run implementation objections were substantially repaired.** The
   frozen producer gates on controls and strict configuration, constructs
   candidate sets without the diagnostic log map, evaluates all targets,
   stores public witnesses, charges major producer paths, binds source
   provenance, and has an independent verifier. The confirmatory control
   failure is a new empirical protocol finding, not a replay of those repaired
   issues.

### Strongest valid conclusion

> The frozen V2 computation is reproducible and independently verified, but
> its mandatory permuted-label control fails because the learner may choose a
> vanishingly rare training bucket. No candidate-family conclusion is valid
> from this packet.

### Failure modes

- relabeling the zero candidate gates as a scoped negative;
- reporting the negative predictor's rank failure while omitting its failed
  enrichment control;
- changing the learner and rerunning the already observed confirmatory seeds;
- choosing a coverage floor after examining fresh confirmatory outcomes;
- treating direct D4 replay as validation of the statistical protocol;
- extrapolating from `B<=7` to an index-calculus relation compiler.

### Next concrete action

Preregister and test a predictor successor with at least 1% pooled and
per-training-curve bucket coverage, calibrate it on development-only curves,
then freeze new source and run once on fresh seeds.

### Artifact paths

- `development/COORD-ENERGY-CERT-V2/contract.md`
- `development/COORD-ENERGY-CERT-V2/raw-result.json`
- `development/COORD-ENERGY-CERT-V2/verification.json`
- `src/coord_energy_certificate_v2.py`
- `src/verify_coord_energy_certificate_v2.py`
