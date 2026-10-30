# Blocked producer cloud source is waiting for a schedulable node

Observed 2026-10-30 after submission at 18:58:52 UTC. Job
`semaev-blocked-worker-source-20261030-1700` has UID
`bdc12f87-0151-4308-8b80-942db349b6ec`; pod UID
`59c73561-3a17-49cb-a267-31d94dba1cd2` remains Pending.

The retained [status](../analysis/semaev-degree-five-quotient-lift/runs/blocked-worker-cloud-source-pending-001.json)
reports Unschedulable: one node fails pod anti-affinity, two fail the
node selector or affinity, and three have untolerated taints. These are
scheduler observations. They do not identify why additional capacity has
not appeared, prove a worker failure, or establish a mathematical result.
No source controls have executed in this pod. No dependent restore is
permitted until the source has successfully published all six control
results and their checkpoints.

The original n47 random00 job remains active with its original pod and
zero restarts. It has priority and has not been cancelled or replaced.
The new candidate already has 28 passing native controls and nine passing
actual local worker controls, with separate committed evidence. Those do
not substitute for the pending cloud check.

Next test: poll this exact job and retain its terminal state or its
successful source evidence. Do not submit a duplicate on an observation
timeout. Preserve the frozen one-attempt, 3600-second watchdog. If the
source fails, retain that outcome and diagnose capacity before freezing a
new attempt. Do not remove affinity, taints, caps, or the independent
checker to obtain a passing job.

Exit condition: the actual source pod executes all six fixed controls,
records successful original-checker and fresh-count results, and leaves
verified checkpoints for the separate restore pod. The degree-six search
still requires an accepted D5 codimension strictly exceeding the exact
solution count on a frontier input; cloud qualification alone is not that
result. Forty unfinished original high-memory inputs remain in scope.
