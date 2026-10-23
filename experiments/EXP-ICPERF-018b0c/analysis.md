# EXP-ICPERF-018b0c evidence analysis

Decision: DEC-20261017-3b87bf. Evidence: EV-ICPERF-54ac6b. Hypothesis: H-ICPERF-195806. Runs: RUN-ICPERF-712e85 and RUN-ICPERF-1c8bfe. Replacement review: TASK-20261017-93d17d (J0) and TASK-20261017-b5d54d (J1–J4), content-first archived under TASK-20261017-46f47f. This analysis is scoped to one certified ordinary-binary curve over GF(2^61), a 60-bit prime subgroup, m=8 represented by seven chained S3 equations, and two B=316 bases.

## Observation

The weighted planted call ended `wall_censored` after 300.0386098750023 seconds of call wall; the matched local-random planted call ended `wall_censored` after 300.0460652499969 seconds. Neither returned an accepted solver model or full-point certificate. The positive-stage driver recorded 601.2394865410024 seconds, including 0.7232824589955271 seconds of calls-bundle packaging. The natural-stage driver recorded 0.0026677079949877225 seconds and launched zero of its 64 planned solver calls because the positive gate did not pass. The two attempted solver processes consumed 600.037058959002 seconds of process wall and 514.72628992 seconds of sampled process CPU in aggregate, as independently reconciled by TASK-20261017-b5d54d. These are host observations; no controlled hardware-normalized speed comparison was made.

The seven replacement reviewer files match the SHA-256 values in the TASK-20261017-46f47f receipt. A reachable corrective marker repairs an archive commit-message ID omission without changing the original seven-file content or receipt. The replacement review plan's independence checker passed structurally.

## Comparison

The frozen success criterion requires **both** planted calls to return independently checked full-point certificates within 300 seconds and at least one distinct certified projected row from the common natural panel. The observed calls were censored, and the natural panel was gated. The negative criterion requires both positives to pass and all 64 natural calls to finish with independently proved exhaustion; none of that happened. Consequently neither a positive nor a negative mathematical result is scored.

J0 independently derived counters 0–7, 32 raw channels, and 66 planned call labels when gamma is interpreted as x([r]P_source)=70364449406991. The frozen specification and permitted fixture do not explicitly bind gamma, however; an alternative literal pole value changes target admission. J0 is inconclusive for unique blind schedule reconstruction. J1 matched prepared targets and formula constants under the derived gamma, but no natural call executed. J2 had no accepted solver model to test. Its two altered objects were rejected at the exact point interface for both arms; complete CNF/XOR/field rejection required by the plan was not established. J3 and J4 hold only for bounded cost classification and inference limits. Earlier TASK-20261017-dfdf05 review is preserved as advisory because it failed independence checks.

The fixed forbidden-value encoding has equal static clause and XOR counts across both arms; its membership sets differ. Thus this run contains no measured static formula-size reduction. No degree of regularity measurement exists.

## Inference

The Coordinator decision is **inconclusive** for the finite-cap instrument hypothesis. The two 300-second censored controls do not show verified UNSAT, absence of a relation, or solver incapacity outside the cap. The 64 natural calls supply no relation-yield sample. No useful rank, linear algebra, target-solve work, complete pipeline S, weighted-base advantage, or matched-rho gap can be computed. The frozen index-calculus baseline remains the comparison point with no new measured improvement from this pilot.

## Limitation and next check

The exact gamma admission rule must be bound in a prospective successor contract and independently regenerated from the specification and fixture before another solver panel. A separately scoped problem record is required for this ambiguity. A later solver-to-certificate test must carry complete Boolean false-object controls in an authorized reviewer scope and independently check accepted CNF, XOR, field, sign, raw-point and projected-row conditions. Runtime receipts lack a dirty-tree flag and runtime lock; see `problems/execution-proof-chain-not-enforced.md`. Output hashes and independent raw classification do not establish execution proof. The host load reported before the two sequential calls was about 23–24 in the one-minute sample, limiting wall-time comparability.

The existing run report is `experiments/EXP-ICPERF-018b0c/reports/run-20261017T1437Z/report.md`. The replacement reviewer reports and snapshot receipt, both raw-stage directories and their archive receipt, and the run-report receipt are the evidence for this analysis. The prior advisory review has no load-bearing joint in this decision.
