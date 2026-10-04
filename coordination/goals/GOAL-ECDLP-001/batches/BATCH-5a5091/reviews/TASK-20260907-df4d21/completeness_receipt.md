# TASK-20260907-df4d21 — completeness of the Stage 2 occupancy protocol

Recorded: 2026-09-07. Role: coordinator. Goal: GOAL-ECDLP-001. Experiment: EXP-ECDLP-5cad48.

## Object checked

The four-cell occupancy and CS-ingredient audit ranked by `DEC-20260907-42e24f`. Text:

- `experiments/EXP-ECDLP-5cad48/amendments/v1_stage2_occupancy_audit.yaml`

This receipt does not authorize the computation. It does not classify W. It does not fit a.

## Verdict: complete enough to file, not authorized

The protocol names:

- four frozen floor cells only (S2-P8219 at M=9, 20, 37 and S2-P32779 at M=13)
- label definition floor_h = (xs * M) // p on dlog-table x-coordinates
- required outputs q, n_empty_before_remap, M_eff, max_q, min_q, dstar, pi_c, max_pi_c, and the five exact scalars
- independent bucket_stats with import_forbidden of the S2G, S2CS, S2, S2FL, and S2DX producers
- match to archived S2G after independent compute
- interpretation that occupancy contrast is not a W class
- refuse-until-authorized (occupancy_execution_authorized false)
- proof_search_map
- certificate kind none
- claim-changing review plan path review_plan_s2oc.yaml owning the occupancy-vector joint and a blind re-derivation of q, n_empty_before_remap, and M_eff on the miss and next-tightest hold

Predecessor SHA of `v1_stage2_slack_census_authorized.yaml` is `6c81e1134fa5c87853b56b78c97d9d999f8c4b05247de7c5858ee14982cfdd30`. Execution authorized is false.

## What this receipt does not do

- Does not authorize `RUN-ECDLP-5cad48-S2OC`.
- Does not classify W.
- Does not classify the S2-P8219 miss as SMALL-W or LARGE-W.
- Does not fit a.
- Does not authorize Stage 5 of EXP-ECDLP-a98ea9.
- Does not change H-ECDLP-07c7c6.
- Does not claim occupancy is an official supported bound.

Cited: DEC-20260907-42e24f, DEC-20260907-c02be0, RUN-ECDLP-5cad48-S2DX, RUN-ECDLP-5cad48-S2G, RUN-ECDLP-5cad48-S2FL, H-ECDLP-2ade73, EXP-ECDLP-5cad48, IDEA-20260904-f7d47d.
