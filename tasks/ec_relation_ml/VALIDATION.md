# Executed engineering pilots

2026-10-11 UTC. Frozen implementation commit:
`3e02da06533b7664a168d5dae1c493a5dd6421aa`. Python, NumPy 2.3.5 and SymPy 1.14.0;
actual platform/Python versions are in each manifest. CPU-only, sequential jobs.
These are software observations, with no independent scientific review or
hypothesis-status changes.

| Profile | Fields | Curves | Targets | Solver jobs | Completed / censored |
|---|---:|---:|---:|---:|---:|
| quick | 12 | 24 | 24 | 96 | 96 / 0 |
| standard | 48 | 96 | 192 | 768 | 768 / 0 |

The quick fields overlap the standard profile; these counts must not be summed
into an independent sample size. All fields lie between 7 and 233, and subgroups
are only 3–8 bits. Standard jobs have two internal timed solves, quick jobs one.

Executed commands from the repository root:

```sh
/workspace/solinas-runtime/report-venv/bin/python -m unittest discover -s tasks/ec_relation_ml/tests -v
/workspace/solinas-runtime/report-venv/bin/python tasks/ec_relation_ml/run.py run --output tasks/ec_relation_ml/examples/pilot-20261011
/workspace/solinas-runtime/report-venv/bin/python tasks/ec_relation_ml/run.py verify tasks/ec_relation_ml/examples/pilot-20261011
/workspace/solinas-runtime/report-venv/bin/python tasks/ec_relation_ml/run.py run --profile standard --output tasks/ec_relation_ml/examples/standard-20261011
```

All 13 mathematical/leakage checks passed. Both complete pilots were replayed
by the report builder: original roots, signed point equations, rank, scalar
recovery, fitting, choices, controls, metrics and hashes passed. Verification
receipts are in the [report directory](../../docs/reports/ec-relation-ml-20261011/).
These are deterministic software replays, not independent research review or
authentication of timings. The report builder writes into a fresh study
directory; it refuses to overwrite its existing JSON receipts.

On the standard test's 48 targets over 12 fields, per-target matrices have a
rank sum of 56 and recover 18 logs, including 7 already-known G/-G targets:
**11 newly identified logs**. Post-hoc combination of the same measured roots
within each exact curve gives a sum of joint ranks of **39** and identifies
**13 new logs**, plus those 7 initially known. This batch accounting is derived
from retained roots and checked against points and the verified BSGS scalars;
it supplies no new learning result or full batch-cost claim. BSGS recovers all
48 test targets. Every completed solver has the same relation pool.

Standard held-out mean action-process costs were 0.504 s for the best fixed
training action, 0.535 s for ridge and 0.521 s for the bandit. Learned selection
did not beat that strong baseline on this run. Process startup dominates these
tiny problems. Both profiles together took 465.3 s, including all acquired
labels; no amortized attack speedup or confidence interval is claimed.

The earlier number-field dataset audit found 104 cohorts, 24 source fields,
six finite curves and three primes, with 1,664 repeated target attempts. It
cannot provide simultaneous independent source-field and finite-curve train,
validation and test sets. Those already-inspected rows remain exploratory.

The [report and theory](../../docs/reports/ec-relation-ml-20261011/report.md)
provide the pipeline diagram, exact identity CSV, source hashes, controls,
limitations and a proposed wider confirmation design with multiplicity-adjusted
99.9% joint nominal coverage. That confirmation campaign was not run here.
