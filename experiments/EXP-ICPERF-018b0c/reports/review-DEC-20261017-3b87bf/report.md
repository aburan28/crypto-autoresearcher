# Evidence review: bounded k11 solver-to-certificate pilot

**Decision:** DEC-20261017-3b87bf, inconclusive. **Evidence:** EV-ICPERF-54ac6b, strength inconclusive, descriptive medium tier. **Hypothesis:** H-ICPERF-195806. **Experiment:** EXP-ICPERF-018b0c. **Runs:** RUN-ICPERF-712e85 and RUN-ICPERF-1c8bfe. **Independent replacement review:** TASK-20261017-93d17d (J0) and TASK-20261017-b5d54d (J1–J4), archived by TASK-20261017-46f47f. This is one ordinary-binary GF(2^61) curve with a 60-bit prime subgroup, m=8 as seven chained S3 equations, and two B=316 bases.

## Observation

Both separately planted positive calls ended wall censored: weighted 300.0386098750023 seconds and local-random 300.0460652499969 seconds of call wall, one call per arm. The process-wall samples were 300.0156629999983 and 300.0213959590037 seconds, respectively. No executed accepted solver model or full-point certificate was recorded. The positive-stage driver wall was 601.2394865410024 seconds, including 0.7232824589955271 seconds of bundle packaging. The natural-stage driver spent 0.0026677079949877225 seconds; all 64 planned natural solver calls were gated and unattempted. The figure shows the two process-wall samples against the 300-second cap and the natural-call count against its planned 64. There is no statistical spread with n=1 per arm.

## Comparison

The frozen positive condition required both planted certificates within the cap and at least one certified natural row. The negative condition required passed positives and independently proved exhaustion of all 64 natural calls. Neither condition was observed. J0 independently reproduced the planned counters 0–7 and 66 labels only after choosing gamma=x([r]P_source)=70364449406991; that definition was omitted from the frozen specification and permitted fixture, and an alternate literal pole value changes admission. J1 matched prepared points and formula constants under the natural interpretation but could not inspect an executed natural call. J2 saw no accepted solver model. Its altered objects failed exact point checks in both arms, but the planned complete CNF/XOR/field checks were unavailable. J3 and J4 hold only for bounded cost classification and inference. Old TASK-20261017-dfdf05 review remains advisory because its independence check failed.

## Inference

The finite-cap instrument and natural relation-feasibility predictions remain unresolved. A wall-censored call is neither verified UNSAT nor evidence of absent point relations. Natural relation yield is unmeasured. No degree of regularity, useful rank, linear algebra, target solve, complete index-calculus S, candidate-versus-control E2E delta, or matched-rho gap was measured. The established index-calculus baseline is unchanged by this pilot.

## Limitation and next action

The specification must bind gamma by field definition and numeric value before another blind admission check or solver panel. A separate problem record should name this ambiguity without modifying the frozen evidence. A future instrument panel needs complete prepared Boolean false-object models in reviewer scope and independent CNF/XOR/field as well as exact point checks. Runtime dirty-tree state and runtime lock were not recorded; see `problems/execution-proof-chain-not-enforced.md`. Historical binary assertions and high host load further limit wall interpretation.

The earlier observation-only report is [run-20261017T1437Z](../run-20261017T1437Z/report.md). Raw snapshot TASK-20261017-da78be, run-report snapshot TASK-20261017-bbccbb, and replacement-review snapshot TASK-20261017-46f47f bind the source bytes. No canonical performance graph changes: the run graph remains an immutable observation plot, and no baseline or frontier row is justified by this decision.
