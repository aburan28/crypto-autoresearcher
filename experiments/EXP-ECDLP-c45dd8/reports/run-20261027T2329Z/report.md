# Fixed constructor-screen observations

EXP-ECDLP-c45dd8 / RUN-ECDLP-a11661: fixed constructor-screen observations

Observations only; interpretation and scientific decisions require a separate evidence review.

Operational status: completed; verifier integrity pass: True; recorded verifier errors: 0.

Actual case records: 74880; accepted: 74880; planned: 74880; missing cases: 0.

Producer candidate/control cases: 62400 / 12480; recorded statuses: {"aa_replay:BIT:None": 1400, "aa_replay:UNDEFINED:ZERO_NUMERATOR": 160, "candidate:BIT:None": 58080, "candidate:UNDEFINED:ZERO_NUMERATOR": 4320, "fiber:BIT:None": 7280, "fiber:UNDEFINED:ZERO_NUMERATOR": 520, "invalid_anchor:UNDEFINED:ZERO_ANCHOR": 1560, "wrong_root:BIT:None": 1560}.

Actual recovery group records: 5760; missing groups: 0; fresh predicate calls: 3900; verified fresh recovery targets: 780.

Public gate outcomes: {"IDENTITY_OR_TWO_PULSE_FAILURE": 3620, "UNDEFINED_COVERAGE": 2080, "gate passed": 60}.

Derived count of passing finite template fields (sum of recorded indicators): 0/40; all outcomes are shown below.

Exact A/A case pairs checked: 1560; recovery A/A group pairs: 120; covariance pairs: 67392; generator-reindex checks: 74880.

Validator-only truth-half positive controls: 120; ordering passes: 120; retained-bit reduction passes: 120; predicate evaluations: 0.

Counts in the tables and graph are copied from retained producer/verifier reports. Totals explicitly labelled as sums are simple sums of recorded indicators. No statistical intervals were registered for this exhaustive fixed screen.

## All 40 fixed templates

| Arm | alpha | beta | Complete | Groups | Ordering groups | Fresh recovery groups | Undefined cases | Truth mismatches | Finite gate |
|---|---|---|---|---|---|---|---|---|---|
| candidate | 0 | 1 | pass | 120 | 0 | 0 | 160 | 480 | fail |
| candidate | 0 | 2 | pass | 120 | 0 | 0 | 120 | 600 | fail |
| candidate | 0 | 3 | pass | 120 | 0 | 0 | 120 | 400 | fail |
| candidate | 0 | 4 | pass | 120 | 0 | 0 | 160 | 720 | fail |
| candidate | 0 | -1 | pass | 120 | 0 | 0 | 120 | 720 | fail |
| candidate | 0 | -2 | pass | 120 | 0 | 0 | 40 | 680 | fail |
| candidate | 0 | -3 | pass | 120 | 0 | 0 | 80 | 440 | fail |
| candidate | 0 | -4 | pass | 120 | 0 | 0 | 40 | 560 | fail |
| candidate | 1 | 1 | pass | 120 | 0 | 0 | 120 | 720 | fail |
| candidate | 1 | 2 | pass | 120 | 0 | 0 | 200 | 440 | fail |
| candidate | 1 | 3 | pass | 120 | 0 | 0 | 40 | 520 | fail |
| candidate | 1 | 4 | pass | 120 | 0 | 0 | 120 | 480 | fail |
| candidate | 1 | -1 | pass | 120 | 0 | 0 | 120 | 760 | fail |
| candidate | 1 | -2 | pass | 120 | 0 | 0 | 120 | 560 | fail |
| candidate | 1 | -3 | pass | 120 | 0 | 0 | 120 | 520 | fail |
| candidate | 1 | -4 | pass | 120 | 20 | 20 | 80 | 400 | fail |
| candidate | 2 | 1 | pass | 120 | 0 | 0 | 0 | 600 | fail |
| candidate | 2 | 2 | pass | 120 | 0 | 0 | 120 | 720 | fail |
| candidate | 2 | 3 | pass | 120 | 0 | 0 | 120 | 480 | fail |
| candidate | 2 | 4 | pass | 120 | 0 | 0 | 160 | 400 | fail |
| candidate | 2 | -1 | pass | 120 | 0 | 0 | 40 | 520 | fail |
| candidate | 2 | -2 | pass | 120 | 0 | 0 | 80 | 640 | fail |
| candidate | 2 | -3 | pass | 120 | 0 | 0 | 120 | 680 | fail |
| candidate | 2 | -4 | pass | 120 | 0 | 0 | 160 | 400 | fail |
| candidate | -2 | 1 | pass | 120 | 0 | 0 | 120 | 560 | fail |
| candidate | -2 | 2 | pass | 120 | 0 | 0 | 80 | 640 | fail |
| candidate | -2 | 3 | pass | 120 | 0 | 0 | 120 | 440 | fail |
| candidate | -2 | 4 | pass | 120 | 0 | 0 | 120 | 600 | fail |
| candidate | -2 | -1 | pass | 120 | 40 | 40 | 120 | 360 | fail |
| candidate | -2 | -2 | pass | 120 | 0 | 0 | 0 | 640 | fail |
| candidate | -2 | -3 | pass | 120 | 0 | 0 | 320 | 440 | fail |
| candidate | -2 | -4 | pass | 120 | 0 | 0 | 40 | 760 | fail |
| candidate | -3 | 1 | pass | 120 | 0 | 0 | 120 | 720 | fail |
| candidate | -3 | 2 | pass | 120 | 0 | 0 | 120 | 520 | fail |
| candidate | -3 | 3 | pass | 120 | 0 | 0 | 40 | 680 | fail |
| candidate | -3 | 4 | pass | 120 | 0 | 0 | 80 | 480 | fail |
| candidate | -3 | -1 | pass | 120 | 0 | 0 | 200 | 600 | fail |
| candidate | -3 | -2 | pass | 120 | 0 | 0 | 200 | 400 | fail |
| candidate | -3 | -3 | pass | 120 | 0 | 0 | 0 | 640 | fail |
| candidate | -3 | -4 | pass | 120 | 0 | 0 | 80 | 560 | fail |

## All eight control arms

| Arm | alpha | beta | Complete | Groups | Ordering groups | Fresh recovery groups | Undefined cases | Truth mismatches | Finite gate |
|---|---|---|---|---|---|---|---|---|---|
| invalid_anchor | -1 | 1 | pass | 120 | 0 | 0 | 1560 | 0 | fail |
| fiber | 0 | 0 | pass | 120 | 0 | 0 | 0 | 600 | fail |
| fiber | 1 | 0 | pass | 120 | 0 | 0 | 0 | 600 | fail |
| fiber | 2 | 0 | pass | 120 | 0 | 0 | 280 | 440 | fail |
| fiber | -2 | 0 | pass | 120 | 0 | 0 | 0 | 560 | fail |
| fiber | -3 | 0 | pass | 120 | 0 | 0 | 240 | 480 | fail |
| wrong_root | — | — | pass | 120 | 0 | 0 | 0 | 600 | fail |
| aa_replay | 0 | 1 | pass | 120 | 0 | 0 | 160 | 480 | fail |

## Scope and accounting

These are recorded observations, not an evidence-review verdict. The scope is the fixed F11 model y²=x³+x+6, subgroup order 13, twelve nonidentity public bases and ten coordinate views. The views are covariance checks, not independent statistical samples. The 40 integer templates and eight control arms remain visible, including incomplete, failed and undefined outcomes. A false finite gate with integrity errors is not a mathematical counterexample. A finite gate result applies only to this registered template and fixture; no global ordering, novelty, complexity improvement, universal circuit obstruction or scientific status transition follows.

The validator-only truth-half positive control uses O(r) scalar enumeration. It tests the validator and retained-bit reduction; its zero predicate-evaluation count is not an executed candidate recovery. Actual fresh candidate recovery is reported from its separate trace stream. Failed public gates retain their not-attempted reasons and do not become successful recoveries.

Counter families are source-instrumented operations with separate setup, evaluation, public gate, fresh setup, fresh evaluation, reduction, census and validator work. No field/group price, prorating of global census/validator work, complete machine cost, qualified timing, memory measurement or attack speedup is inferred. Model/point scaling, Python container/control work, serialization, hashing, I/O and runtime/source checks include unmetered harness work. Candidate counters are not independently replayed. The full campaign includes the linear all-point gate and public census.

Producer unmetered harness work: ["public model/point coordinate scaling uses raw modular integer arithmetic", "Python container/control operations outside named counters", "JSON serialization, hashing, file I/O and runtime/source checks"]

Every retained group, undefined target, first counterexample, residual vector and failed-gate reason is listed in group-diagnostics.csv. The full verifier source retains all exact mismatches and traces. Validator-only positive controls, known-false controls and verifier errors are retained in validator-controls.json.

Operation counts are copied without prices into operation-families.csv. Global two-pass census and validator costs remain separate and are not allocated across arms.

![Recorded undefined and truth-mismatch cases for every arm](arm-outcomes.svg)

Graph: RUN-ECDLP-a11661; each complete arm has 120 base/view groups and 1560 target cases; incomplete arm counts remain in the table. Units are counted target cases. All 48 arms are shown; zero bars remain labelled. No stochastic uncertainty interval applies.

## Immutable input bindings

Official protocol body SHA-256: `31d6425d88c3217ddab47fe3fbc295a6ec6b0af3513942f0fc2a9156ccea7d3d`.

Screen-plan byte SHA-256: `2152978af8dfe1f86b6225d14f0e587b030339a3fe6e948fdc7480a480d2bed3`.

Source manifest SHA-256: `b54ed025f45355dbc73f38cc08c19b5b08a44ca4c43b16318800d023755ef5fd`.

Exact input paths and file hashes are in report-inputs.json; publication paths may differ from the original execution paths.
