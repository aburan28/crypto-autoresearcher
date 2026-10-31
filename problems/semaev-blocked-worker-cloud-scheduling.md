# Blocked producer cloud source reached its scheduling deadline

Update at 2026-10-30 19:59 UTC: the exact job below is terminal with
`DeadlineExceeded` (Failed condition at 19:58:53 UTC). The
[terminal status](../analysis/semaev-degree-five-quotient-lift/runs/blocked-worker-cloud-source-terminal-001.json)
and [output check](../analysis/semaev-degree-five-quotient-lift/runs/blocked-worker-cloud-source-output-check-001.json)
retain the evidence. No pod remains; the bounded log query returned empty,
and recursive listing of this job's S3 prefix returned no objects. All
observed pre-terminal states were unschedulable. The frozen cloud protocol
is unfulfilled; no successful source or restore controls are claimed.

The next action is capacity reconciliation after the priority frontier job
finishes, followed by a separately frozen attempt if an admissible slot is
available. Do not resubmit the terminal job name or remove placement guards.
The following records the original pending state and preserves its scope.

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

## 2026-10-30 continuation after capacity reconciliation
The priority n47 job terminated on node shutdown at20:43:47UTC; the cloud overview shows no active Semaev jobs. Version2 of the cloud-control protocol is separately frozen with the same bundle, three fixtures, original checker, 2CPU/4GiB limits, one-hour watchdog and zero retries. Source job semaev-blocked-worker-source-v2-20261030-2055 is prepared, not yet submitted. Its independent output identity preserves version1; all six source controls must pass before a distinct restore pod. Scheduler admission remains an observation to obtain.

## 2026-10-30 cloud qualification completed
Version2 source completed21:00:39UTC; distinct restore completed21:08:46UTC. Allnine actual controls passed. The original checker accepted allsix completed certificates, retained hashes matched, and all556 archived file hashes verified. The three restored controls loaded source checkpoints under the same frozen context. Report/export/PDF: analysis/semaev-degree-five-quotient-lift/reports/blocked-checkpoint-worker-cloud-002; export validation returnedzero findings. Sourcepod bbe03960-0d90-4ef8-805f-4dcc6a21854e andrestorepod f5b60284-7fc6-4621-9feb-4c251d1546a4 differ. The earlier scheduling failure remains preserved. This resolves the small cloud-qualification dependency; the next large input retains its actual memory/disk admission checks.
