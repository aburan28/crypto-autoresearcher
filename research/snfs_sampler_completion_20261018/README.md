# Completed sampler support and fixed-input variation

Observations only. EXP-ECDLP-00e491 records the remaining sampler follow-ups
from the earlier observation study: exhaustive finite coefficient support,
an interface separating search seeds from algebraic inputs, fresh-seed variation,
legacy controls, identical-seed replay and complete discovered-point traces.
Interpretation, relevance and usefulness calls remain with the owner.

- [Report and plots](../../experiments/EXP-ECDLP-00e491/reports/run-20261018T0110Z/REPORT.md)
- [PDF](../../experiments/EXP-ECDLP-00e491/reports/run-20261018T0110Z/report.pdf)
- [Observation YAML](../../experiments/EXP-ECDLP-00e491/reports/run-20261018T0110Z/observation.yaml)
- [Descriptive tables](../../experiments/EXP-ECDLP-00e491/reports/run-20261018T0110Z/observations.json)
- [Canonical protocol](../../experiments/EXP-ECDLP-00e491/specification.yaml)
- [Frozen trial plan](../../experiments/EXP-ECDLP-00e491/trial-plan.json)
- [Raw publication verification](../../coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7fde0/archives/TASK-20261018-70f7f2/publication-verification.json)

The two native trials completed with literal status `output_validated`:

| Run | Recorded scope |
| --- | --- |
| RUN-ECDLP-ee0d23 | 3,232 coefficient patterns; 29,088 prime-value checks |
| RUN-ECDLP-6bd7b4 | 102 searches: 84 fresh jobs, 11 legacy controls, 7 exact replays |

Built-in checkers replayed every support record and verified all 480 discovered
point events. All eleven legacy controls and seven identical-seed replay streams
matched. This is mechanical checking, not an independent scientific review.

The finite source irreducibility screen leaves 3 degree-eight and 21 degree-twelve
prime-eligible, Q-irreducible patterns unresolved. All twelve fresh jobs within
each input finish with identical counts, while two inputs show different
intermediate discovery counts. The report preserves ordinary results alongside
these patterns, with exact scope and proposed next checks.

`panel.json` fixes seven complete inputs, their auxiliary primes, job roles,
work ladder and exact search-seed strings before launch. `prepare_inputs.py`
selects them without running a search. `coefficients.json` enumerates the full
prescribed supports. The Rust driver accepts each fixed input directly;
`full_catalog.py` records the source screen separately from exact Sage results.
`execute_trial.py` and `check_trial.py` integrate the native producer/checker.
The native run manifests and indexed bundles retain commands, source hashes,
launch environment and uncapped discovered-point/checkpoint/shell event streams.
Rejected candidates are not individually logged.

Engineering validation before the runs: three Rust tests and seven Python
fixtures, including invalid reduction, trace corruption and partial-output
preservation after child failure. Published run trees and earlier reports remain
immutable. Hypothesis H-ECDLP-4da36f is lineage only; no scientific status changed.
This completes this sampler protocol, not all 23 original lead protocols.
