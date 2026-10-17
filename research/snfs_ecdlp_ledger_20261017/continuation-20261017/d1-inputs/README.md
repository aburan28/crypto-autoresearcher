# D1 candidate input reconciliation

The two fetched source pages now provide separate candidate lists of 30 and 31 rational points. [Fetch provenance](fetch-record.json) preserves the exact public URLs, timestamps, HTTP outcomes and body hashes. The source pages' rank and independence assertions remain source assertions.

`prepare_candidates.py` accepts only the two explicit equation formats, parses every indexed rational pair, checks the discriminant is nonzero, and checks all 61 pairs against their stated equations using exact `Fraction` arithmetic. The 31-point equation and list also agree exactly with the ICARM snapshot already archived by the rank campaign. Candidate JSON files retain the general Weierstrass models; no isomorphism or height scaling is silently introduced. The two parser refusal controls reject a changed coordinate and duplicate index without changing source bytes.

This closes the **location and exact equation-membership** gap for the rank-30 candidate. It supplies no independence proof, full Gram matrix, certified height-error bounds, saturated basis, new rank result, or D1 lattice-count measurement.

The existing rank campaign reports must be read together:

- [Executor observations](../../../../coordination/goals/GOAL-ECRANK-002/batches/BATCH-52b70c/tasks/TASK-20260905-cfce83/observations.md).
- [Run-integrity review](../../../../coordination/goals/GOAL-ECRANK-002/batches/BATCH-52b70c/tasks/TASK-20260905-b439f9/validation_report.yaml).
- [Mathematical red-team report](../../../../coordination/goals/GOAL-ECRANK-002/batches/BATCH-52b70c/tasks/TASK-20260905-0728c3/red_team_report.yaml).

Both reviews correct the executor's spurious factor-10^10 regulator discrepancy. The red-team report explicitly distinguishes a non-singular **numerical** regulator from a certified interval computation. This continuation adopts neither a new exact-independence claim nor an exact-rank assertion. The original source-index snapshot remains unchanged.

Next: bind a reproducible Gram-matrix constructor, error/precision treatment and the actual generated subgroup for both candidates; certify the needed positive-definiteness and determinant/covolume conventions. Freeze a finite enumeration workload and target-coverage measurement before the D1 run. A count over the generated sublattice must not be labeled a count over a saturated full MW basis.
