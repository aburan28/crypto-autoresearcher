# Larger classical ECDLP solver validation

The 48-curve, 768-target validation batch is complete. [Report](../../experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/HEADER.md), [six-page PDF](../../experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/report.pdf), [observations](../../experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/observations.md), and [sealed records](../../experiments/EXP-ECDLP-9f7772/runs/RUN-ECDLP-dba66e/parts-manifest.json).

The objective is a correct working algorithm followed by improvement against an explicit baseline. This batch uses fresh 12/14/16/18-bit prime-order subgroups, six curves per size/stratum, and sixteen public targets per curve. The fixed 192-target core is nested in the full panel. Everything is classical and outside index calculus.

| Method | Checked recoveries | Recorded setup + target CPU across the full panel |
| --- | --- | --- |
| Upstream AutoRho | 768/768 | 0.308699 s |
| Bernstein–Lange precomputation | 768/768 | 0.185001 s |
| BSGS | 768/768 | 0.0589784 s |
| Fixed candidate followed by rho | 768/768 | 1.26832 s |

These are sums of recorded solver-API intervals, with setup paid once per curve and reused over sixteen targets. They exclude common input certification, serialization, orchestration and final teardown. The report separately gives the registered equal-curve paired geometric means, A/A variability, reconstructed cold totals, nested-core reuse and operation/memory scopes. Timings and operation counts are different units.

The primary x-mod-7/exact-prefix/beam-8 candidate alone recovers 3/768; rho supplies the remaining 765 hybrid answers. Every fallback has the same primitive-work vector as its paired rho reference. AutoRho A/A answers and deterministic work agree on every target. The complete hybrid's correctness does not establish candidate-alone completeness. BSGS has the lowest measured CPU cost among these implementations at these parameters; that finite-size result is separate from asymptotic time/memory exponents.

Actual AutoRho and Bernstein–Lange source is vendored unchanged from `aburan28/cryptanalysis` commit `379faa0f1e38facd9c8fdfc527f0b89518cf2e70`, using the same arithmetic backend as the candidate. See [baseline details](baselines/README.md), [candidate details](candidate/README.md), [cohort and custody](cohort/README.md), and [execution operations](admission/OPERATIONS.md).

The genuine supervisor records one output-validated successor batch, six successful jobs and 15,360 rows. Its total envelope is 55.178581 seconds, including builds, development controls and checking. Raw commit `c4b940ac5360e17cb221772f968bab20f67266c3` preceded analysis. The unchanged repository verifier checked the actual snapshot commit `1822ae0b7247c08dd9062eba62358b8bf19ff728` for 2,884 bound paths. Both task claims are released as completed.

The [earlier compiler-stopped attempt](../../experiments/EXP-ECDLP-381959/reports/run-20261025T1906Z/HEADER.md) has its own immutable records and report. It produced no confirmation measurements. The [approved build-only successor](../../experiments/EXP-ECDLP-381959/amendments/20261025-build-only-successor.json) preserves its failure and the unchanged cohort, rather than rewriting that run.

[Publication provenance and post-seal target reveal](../../experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/PROVENANCE.md) and six machine-readable local comparison records accompany the report. Their structural validation is separate from independent scientific review. The existing committed-ref progress exporter automatically counts the new claim records; the registered report estimator remains distinct from dashboard statistics.

For the preserved run's status:

```sh
python3 tools/experiment_execution.py status \
  --plan experiments/EXP-ECDLP-9f7772/trial-plan.json
```

Do not overwrite or retune this confirmation run. A new candidate revision uses fresh prospective source binding and a fresh confirmation cohort, while explicitly retaining this working baseline and its cost model.
