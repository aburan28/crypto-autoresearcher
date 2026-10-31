# Missing results parent in cloud worker bootstrap

Attempt001 reached the unchanged driver after archive verification, then failed before trials because `/work/results` was absent. See [failure report](../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-worker-cloud-failure-001/report.md).

The fix is bootstrap creation of the parent before the driver. Exit criterion: a new frozen source attempt actually runs and passes all six controls, followed by three distinct-pod restore controls. A directory edit alone does not qualify the worker. No mathematical bound follows from this failure.

## Corrected attempt evidence

Protocol002 passed all six source controls and all three distinct-pod restore
controls. The corrected bootstrap creates the parent before invoking the
unchanged worker. See [cloud report](../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-worker-cloud-002/report.md).
Both jobs succeeded; all 556 archived file hashes verify and the nine-row
export validates with zero findings. This resolves the missing-parent
integration failure. Frontier resource admission and mathematical search
remain separate obligations.
