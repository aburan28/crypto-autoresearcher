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

![Recorded outcomes: arms 1–24 of all 48](arm-outcomes-panel-1.png){height=145mm}

![Recorded outcomes: arms 25–48 of all 48](arm-outcomes-panel-2.png){height=145mm}

Graph: RUN-ECDLP-a11661; each complete arm has 120 base/view groups and 1560 target cases; incomplete arm counts remain in the table. Units are counted target cases. All 48 arms are shown; zero bars remain labelled. No stochastic uncertainty interval applies.

## Immutable input bindings

Official protocol body SHA-256: `31d6425d88c3217ddab47fe3fbc295a6ec6b0af3513942f0fc2a9156ccea7d3d`.

Screen-plan byte SHA-256: `2152978af8dfe1f86b6225d14f0e587b030339a3fe6e948fdc7480a480d2bed3`.

Source manifest SHA-256: `b54ed025f45355dbc73f38cc08c19b5b08a44ca4c43b16318800d023755ef5fd`.

Exact input paths and file hashes are in report-inputs.json; publication paths may differ from the original execution paths.

## Recorded known-false controls

- {"case_id": "u1:x2:y7:wrong_root:anchored_power_root:target9", "control": "anchored_wrong_root_at_three_seedP", "pass": true}
- {"alpha_integer": 0, "case_ids": ["u1:x2:y7:fiber:a0:b0:target4", "u1:x2:y7:fiber:a0:b0:target8"], "control": "fiber_collision_at_five_six_seedP", "pass": true}
- {"alpha_integer": 1, "case_ids": ["u1:x2:y7:fiber:a1:b0:target4", "u1:x2:y7:fiber:a1:b0:target8"], "control": "fiber_collision_at_five_six_seedP", "pass": true}
- {"alpha_integer": 2, "case_ids": ["u1:x2:y7:fiber:a2:b0:target4", "u1:x2:y7:fiber:a2:b0:target8"], "control": "fiber_collision_at_five_six_seedP", "pass": true}
- {"alpha_integer": -2, "case_ids": ["u1:x2:y7:fiber:a-2:b0:target4", "u1:x2:y7:fiber:a-2:b0:target8"], "control": "fiber_collision_at_five_six_seedP", "pass": true}
- {"alpha_integer": -3, "case_ids": ["u1:x2:y7:fiber:a-3:b0:target4", "u1:x2:y7:fiber:a-3:b0:target8"], "control": "fiber_collision_at_five_six_seedP", "pass": true}

## Recorded verifier integrity errors

No recorded integrity errors.

## Separate recorded operation families

| Family / operation | Count |
|---|---:|
| producer. planning\_cost. coordinate\_enumeration. field\_add | 242 |
| producer. planning\_cost. coordinate\_enumeration. field\_equal | 121 |
| producer. planning\_cost. coordinate\_enumeration. field\_mul | 242 |
| producer. planning\_cost. coordinate\_enumeration. field\_reduce | 726 |
| producer. planning\_cost. coordinate\_enumeration. field\_square | 242 |
| producer. planning\_cost. coordinate\_enumeration. point\_membership\_call | 121 |
| producer. planning\_cost. parameter\_certification. certification\_discriminant\_check | 1 |
| producer. planning\_cost. parameter\_certification. certification\_trial\_division | 4 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. field\_add | 242 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. field\_equal | 121 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. field\_mul | 242 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. field\_reduce | 726 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. field\_square | 242 |
| producer. planning\_cost. plan\_description\_pass. coordinate\_enumeration. point\_membership\_call | 121 |
| producer. planning\_cost. plan\_description\_pass. parameter\_certification. certification\_discriminant\_check | 1 |
| producer. planning\_cost. plan\_description\_pass. parameter\_certification. certification\_trial\_division | 4 |
| producer. planning\_cost. plan\_description\_pass. point\_count | 13 |
| producer. planning\_cost. plan\_description\_pass. scalar\_orbit\_tables | 0 |
| producer. planning\_cost. point\_count | 13 |
| producer. planning\_cost. scalar\_orbit\_tables | 0 |
| producer. grid. evaluate. exception\_identity\_predicate | 5640 |
| producer. grid. evaluate. exception\_undefined\_setup | 1560 |
| producer. grid. evaluate. exception\_vertical\_addition | 66240 |
| producer. grid. evaluate. exception\_zero\_numerator | 5000 |
| producer. grid. evaluate. field\_add | 1065600 |
| producer. grid. evaluate. field\_equal | 1195920 |
| producer. grid. evaluate. field\_inverse | 264960 |
| producer. grid. evaluate. field\_mul | 1783560 |
| producer. grid. evaluate. field\_neg | 66960 |
| producer. grid. evaluate. field\_power\_call | 62680 |
| producer. grid. evaluate. field\_reduce | 5491680 |
| producer. grid. evaluate. field\_square | 724400 |
| producer. grid. evaluate. field\_sub | 1258560 |
| producer. grid. evaluate. group\_add\_call | 331200 |
| producer. grid. evaluate. group\_add\_nonvertical | 66240 |
| producer. grid. evaluate. group\_double\_nonvertical | 198720 |
| producer. grid. evaluate. inverse\_euclid\_iteration | 722016 |
| producer. grid. evaluate. miller\_chain\_add | 132480 |
| producer. grid. evaluate. miller\_chain\_double | 198720 |
| producer. grid. evaluate. miller\_coefficient\_call | 66240 |
| producer. grid. evaluate. point\_membership\_call | 73320 |
| producer. grid. evaluate. power\_bit | 186600 |
| producer. grid. setup. exception\_vertical\_addition | 5760 |
| producer. grid. setup. field\_add | 86520 |
| producer. grid. setup. field\_equal | 132120 |
| producer. grid. setup. field\_inverse | 40080 |
| producer. grid. setup. field\_mul | 127080 |
| producer. grid. setup. field\_neg | 5760 |
| producer. grid. setup. field\_power\_call | 120 |
| producer. grid. setup. field\_reduce | 455400 |
| producer. grid. setup. field\_square | 52080 |
| producer. grid. setup. field\_sub | 103680 |
| producer. grid. setup. group\_add\_call | 28800 |
| producer. grid. setup. group\_add\_nonvertical | 5760 |
| producer. grid. setup. group\_double\_nonvertical | 17280 |
| producer. grid. setup. inverse\_euclid\_iteration | 104724 |
| producer. grid. setup. miller\_chain\_add | 11520 |
| producer. grid. setup. miller\_chain\_double | 17280 |
| producer. grid. setup. miller\_coefficient\_call | 5760 |
| producer. grid. setup. point\_membership\_call | 5760 |
| producer. grid. setup. power\_bit | 240 |
| producer. recovery. evaluate. exception\_identity\_predicate | 300 |
| producer. recovery. evaluate. exception\_vertical\_addition | 3600 |
| producer. recovery. evaluate. field\_add | 57600 |
| producer. recovery. evaluate. field\_equal | 64800 |
| producer. recovery. evaluate. field\_inverse | 14400 |
| producer. recovery. evaluate. field\_mul | 97200 |
| producer. recovery. evaluate. field\_neg | 3600 |
| producer. recovery. evaluate. field\_power\_call | 3600 |
| producer. recovery. evaluate. field\_reduce | 298800 |
| producer. recovery. evaluate. field\_square | 39600 |
| producer. recovery. evaluate. field\_sub | 68400 |
| producer. recovery. evaluate. group\_add\_call | 18000 |
| producer. recovery. evaluate. group\_add\_nonvertical | 3600 |
| producer. recovery. evaluate. group\_double\_nonvertical | 10800 |
| producer. recovery. evaluate. inverse\_euclid\_iteration | 39240 |
| producer. recovery. evaluate. miller\_chain\_add | 7200 |
| producer. recovery. evaluate. miller\_chain\_double | 10800 |
| producer. recovery. evaluate. miller\_coefficient\_call | 3600 |
| producer. recovery. evaluate. point\_membership\_call | 3900 |
| producer. recovery. evaluate. power\_bit | 10800 |
| producer. recovery. fresh\_setup. exception\_vertical\_addition | 60 |
| producer. recovery. fresh\_setup. field\_add | 900 |
| producer. recovery. fresh\_setup. field\_equal | 1380 |
| producer. recovery. fresh\_setup. field\_inverse | 420 |
| producer. recovery. fresh\_setup. field\_mul | 1320 |
| producer. recovery. fresh\_setup. field\_neg | 60 |
| producer. recovery. fresh\_setup. field\_reduce | 4740 |
| producer. recovery. fresh\_setup. field\_square | 540 |
| producer. recovery. fresh\_setup. field\_sub | 1080 |
| producer. recovery. fresh\_setup. group\_add\_call | 300 |
| producer. recovery. fresh\_setup. group\_add\_nonvertical | 60 |
| producer. recovery. fresh\_setup. group\_double\_nonvertical | 180 |
| producer. recovery. fresh\_setup. inverse\_euclid\_iteration | 1098 |
| producer. recovery. fresh\_setup. miller\_chain\_add | 120 |
| producer. recovery. fresh\_setup. miller\_chain\_double | 180 |
| producer. recovery. fresh\_setup. miller\_coefficient\_call | 60 |
| producer. recovery. fresh\_setup. point\_membership\_call | 60 |
| producer. recovery. gate. exception\_identity\_addition | 17280 |
| producer. recovery. gate. exception\_vertical\_addition | 5760 |
| producer. recovery. gate. field\_add | 40320 |
| producer. recovery. gate. field\_equal | 368640 |
| producer. recovery. gate. field\_inverse | 80640 |
| producer. recovery. gate. field\_mul | 195840 |
| producer. recovery. gate. field\_neg | 5760 |
| producer. recovery. gate. field\_reduce | 950400 |
| producer. recovery. gate. field\_square | 97920 |
| producer. recovery. gate. field\_sub | 449280 |
| producer. recovery. gate. gate\_outcome\_inspection | 74880 |
| producer. recovery. gate. gate\_retained\_bit\_read | 155520 |
| producer. recovery. gate. group\_add\_call | 103680 |
| producer. recovery. gate. group\_add\_nonvertical | 63360 |
| producer. recovery. gate. group\_double\_nonvertical | 17280 |
| producer. recovery. gate. inverse\_euclid\_iteration | 218304 |
| producer. recovery. gate. point\_equal | 149760 |
| producer. recovery. gate. point\_negate | 5760 |
| producer. recovery. gate. scalar\_multiply\_bit | 17280 |
| producer. recovery. gate. scalar\_multiply\_call | 5760 |
| producer. recovery. reduction. exception\_identity\_addition | 1740 |
| producer. recovery. reduction. field\_add | 10200 |
| producer. recovery. reduction. field\_equal | 20880 |
| producer. recovery. reduction. field\_inverse | 4980 |
| producer. recovery. reduction. field\_mul | 20160 |
| producer. recovery. reduction. field\_reduce | 72240 |
| producer. recovery. reduction. field\_square | 10800 |
| producer. recovery. reduction. field\_sub | 21120 |
| producer. recovery. reduction. group\_add\_call | 6720 |
| producer. recovery. reduction. group\_add\_nonvertical | 600 |
| producer. recovery. reduction. group\_double\_nonvertical | 4380 |
| producer. recovery. reduction. inverse\_euclid\_iteration | 13506 |
| producer. recovery. reduction. point\_equal | 780 |
| producer. recovery. reduction. point\_membership\_call | 780 |
| producer. recovery. reduction. recovery\_scalar\_digit\_update | 3900 |
| producer. recovery. reduction. recovery\_scalar\_interval\_round | 780 |
| producer. recovery. reduction. scalar\_multiply\_bit | 2280 |
| producer. recovery. reduction. scalar\_multiply\_call | 780 |
| validator. actual\_fresh\_recovery\_trace\_checks. character\_calls | 3600 |
| validator. actual\_fresh\_recovery\_trace\_checks. equality | 659640 |
| validator. actual\_fresh\_recovery\_trace\_checks. field\_add | 62040 |
| validator. actual\_fresh\_recovery\_trace\_checks. field\_inverse | 106200 |
| validator. actual\_fresh\_recovery\_trace\_checks. field\_multiply | 260820 |
| validator. actual\_fresh\_recovery\_trace\_checks. field\_square | 121260 |
| validator. actual\_fresh\_recovery\_trace\_checks. field\_subtract | 573240 |
| validator. actual\_fresh\_recovery\_trace\_checks. group\_add | 117240 |
| validator. actual\_fresh\_recovery\_trace\_checks. group\_negate | 5760 |
| validator. actual\_fresh\_recovery\_trace\_checks. identity\_add | 12480 |
| validator. actual\_fresh\_recovery\_trace\_checks. scalar\_multiply\_calls | 6540 |
| validator. actual\_fresh\_recovery\_trace\_checks. slope | 99000 |
| validator. actual\_fresh\_recovery\_trace\_checks. vertical\_add | 5760 |
| validator. arithmetic\_record\_checks. character\_calls | 61240 |
| validator. arithmetic\_record\_checks. field\_add | 205800 |
| validator. arithmetic\_record\_checks. field\_inverse | 129040 |
| validator. arithmetic\_record\_checks. field\_multiply | 597240 |
| validator. arithmetic\_record\_checks. field\_square | 128480 |
| validator. arithmetic\_record\_checks. field\_subtract | 66240 |
| validator. oracle\_and\_laws. equality | 119326 |
| validator. oracle\_and\_laws. field\_add | 19470 |
| validator. oracle\_and\_laws. field\_inverse | 25321 |
| validator. oracle\_and\_laws. field\_multiply | 40330 |
| validator. oracle\_and\_laws. field\_square | 12778 |
| validator. oracle\_and\_laws. field\_subtract | 80924 |
| validator. oracle\_and\_laws. group\_add | 11063 |
| validator. oracle\_and\_laws. group\_negate | 780 |
| validator. oracle\_and\_laws. identity\_add | 1571 |
| validator. oracle\_and\_laws. identity\_slope | 3000 |
| validator. oracle\_and\_laws. input\_discriminant\_check | 61 |
| validator. oracle\_and\_laws. input\_primality\_trial\_division | 244 |
| validator. oracle\_and\_laws. oracle\_table\_entries | 923 |
| validator. oracle\_and\_laws. point\_check | 923 |
| validator. oracle\_and\_laws. primitive\_oracle\_queries | 780 |
| validator. oracle\_and\_laws. primitive\_oracle\_terms | 10140 |
| validator. oracle\_and\_laws. slope | 28981 |
| validator. oracle\_and\_laws. vertical\_add | 791 |
| validator. oracle\_and\_laws. vertical\_slope | 1440 |
| validator. retained\_bit\_reduction\_and\_obligations. equality | 659640 |
| validator. retained\_bit\_reduction\_and\_obligations. field\_add | 50940 |
| validator. retained\_bit\_reduction\_and\_obligations. field\_inverse | 99000 |
| validator. retained\_bit\_reduction\_and\_obligations. field\_multiply | 228120 |
| validator. retained\_bit\_reduction\_and\_obligations. field\_square | 114060 |
| validator. retained\_bit\_reduction\_and\_obligations. field\_subtract | 638760 |
| validator. retained\_bit\_reduction\_and\_obligations. group\_add | 117240 |
| validator. retained\_bit\_reduction\_and\_obligations. group\_negate | 74880 |
| validator. retained\_bit\_reduction\_and\_obligations. identity\_add | 12480 |
| validator. retained\_bit\_reduction\_and\_obligations. scalar\_multiply\_calls | 6540 |
| validator. retained\_bit\_reduction\_and\_obligations. slope | 99000 |
| validator. retained\_bit\_reduction\_and\_obligations. vertical\_add | 5760 |
| validator. truth\_half\_positive\_control. equality | 121200 |
| validator. truth\_half\_positive\_control. field\_add | 25680 |
| validator. truth\_half\_positive\_control. field\_inverse | 16920 |
| validator. truth\_half\_positive\_control. field\_multiply | 51840 |
| validator. truth\_half\_positive\_control. field\_square | 27480 |
| validator. truth\_half\_positive\_control. field\_subtract | 88200 |
| validator. truth\_half\_positive\_control. group\_add | 19440 |
| validator. truth\_half\_positive\_control. group\_negate | 1560 |
| validator. truth\_half\_positive\_control. identity\_add | 2280 |
| validator. truth\_half\_positive\_control. input\_discriminant\_check | 120 |
| validator. truth\_half\_positive\_control. input\_primality\_trial\_division | 480 |
| validator. truth\_half\_positive\_control. oracle\_table\_entries | 1560 |
| validator. truth\_half\_positive\_control. point\_check | 1560 |
| validator. truth\_half\_positive\_control. scalar\_multiply\_calls | 1680 |
| validator. truth\_half\_positive\_control. slope | 16920 |
| validator. truth\_half\_positive\_control. vertical\_add | 240 |
