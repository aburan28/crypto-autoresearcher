# TASK-20260813-e04ebc — Independent validation of ROUTE-I2

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            validator
    policy          review-adversarial     independent_session_required
    state           queued
    depends_on      TASK-20260813-415c21, TASK-20260813-5d1920
    review_required false
    archived_by     PENDING (ledger archive, TASK-20260813-fe3dec)
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## What this task must do

Audit whether `measure_route_i2.py` **genuinely** satisfies `PREREG-4`
§2.2's independence requirements (diff it against `measure_relvar.py`,
`measure_am4.py`, `replicate_l7l8.py` yourself — do not trust the
producer's self-certification), confirm basis fidelity to `PREREG-4` §2.1's
frozen `F0` specification, re-derive obligations 0-2 from the frozen text
(including a sample of the arithmetic without importing the producer's
module), and re-derive the fired termination branch. Verify `RC-3`'s carry
against the Red Team's own committed probe output.

## Primary targets, in order of priority

1. Is the claimed algorithmic difference genuine, or a relabelled copy of
   `hkz_profile`'s pipeline?
2. Does `ROUTE-I2`'s basis match `PREREG-4` §2.1's frozen construction
   exactly? A mismatch here voids the whole comparison.
3. Re-derive obligation 0 (the `G_REL2` coverage check) independently.
4. Re-derive a sample of obligation 1/2's arithmetic independently.
5. Confirm the `RC-3` carry against `probe_coverage_beta_mismatch_output.json`.
6. Confirm no reduction above `d = 40` was performed anywhere.

## Deliverables

    reviews/TASK-20260813-e04ebc/validation_report.yaml
    reviews/TASK-20260813-e04ebc/probes/*   (every probe built, with output)

**List every probe path explicitly in the report** — declared gap `G-1`;
these paths extend the ledger archive's declared set before it stages.

## Constraints

Independent session. Commit nothing — your report and probes sit
uncommitted until the ledger archive commits them (`PD-4`, open and
inherited). Do not restate `KN-FIND-9b5df0`/`KN-FIND-7d098b`/`KN-FIND-9d44b4`
as new. Claim tier stays TOY. A timeout, crash, or missing dependency is
infrastructure signal, never negative mathematical evidence.
