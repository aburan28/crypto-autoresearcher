# Panel worker a2 correction

The first remote pilot `semaev-panel-n42-rand03-20261029-1600`
failed before controls/counting/checking because the new wrapper incorrectly
restricted a2 to zero. The fixed original input has a2=1. Retain the failed
job and protocol v1 unchanged; this attempt yields no mathematical result.

The equation used in code/s3sys.py and the standalone checker is
S3=(X1 X2+X1 z+X2 z)^2+X1 X2 z+a6, independent of a2.
The native counter uses precisely this equation. The checker receives a2
for its group-law self-test, not to modify the descended S3 equations.

`run_panel_worker_v2.py` removes only the erroneous a2 gate. The frozen v1
source remains intact. Five new full-worker controls passed: the three
original reference inputs at a2=1 give identical certificate bytes and
exhaustive counts3,1,1; an odd-degree n7 fixture at a2=0 and1 gives identical
certificate bytes and count1, exercises the group-law self-test, and matches
full Boolean enumeration. Receipts: panel-worker-v2-20261029/summary.json.

Exit condition for this obstruction: the same original n42 input must pass
worker startup and reach its exact count/checker under a prospectively frozen
v2 protocol, with durable S3 results. Software controls alone do not establish
that condition. Retry retains the same original identity and a distinct job.
