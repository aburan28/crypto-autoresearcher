# Missing results parent in cloud worker bootstrap

Attempt001 reached the unchanged driver after archive verification, then failed before trials because `/work/results` was absent. See [failure report](../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-worker-cloud-failure-001/report.md).

The fix is bootstrap creation of the parent before the driver. Exit criterion: a new frozen source attempt actually runs and passes all six controls, followed by three distinct-pod restore controls. A directory edit alone does not qualify the worker. No mathematical bound follows from this failure.
