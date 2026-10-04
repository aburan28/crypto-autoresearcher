# TASK-20260909-a4da3d execution report

All four frozen run records are terminal. R1, R2, and the corrected R3 package are valid run records; R4 is terminal with an explicit infrastructure gap for the HA-2 permutation replay.

- R1: exact committed control regression passed; order-8 and order-16 subgroup counts were 11,811; C7 synthetic controls passed.
- R2: 4,064 attempts, 2,670 completed, 1,394 timed out; P1 total_mult 20 and P4 total_mult 31; both certificate exact verifiers returned zero errors.
- R3: 320 attempts at each comparison alarm; at 30 seconds 212 completed and at 240 seconds 306 completed.
- R4: fresh process, zero new descents, all recomputed non-HA2 statistics matched the R2 statistics; HA-2 permutation replay is recorded as failed infrastructure because its frozen 755,904-coset by 2,000-shuffle workload was not rerun.

The YAML execution report contains observations, anomalies, exact artifact paths, and the rerun assessment. It does not change hypothesis or experiment status.
