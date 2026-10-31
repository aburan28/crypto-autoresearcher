# Cloud source qualification: scheduling deadline

Job `semaev-blocked-worker-source-20261030-1700`, UID
`bdc12f87-0151-4308-8b80-942db349b6ec`, started its job deadline at
18:58:52 UTC and received a Failed condition with reason
`DeadlineExceeded` at 19:58:53 UTC on 2026-10-30. Every observed pod state
was Pending/Unschedulable. No retained pod, log output, or S3 output was
found by the post-terminal checks.

The planned six source-pod cases and three separate-pod restore cases
remain unqualified. No dependent restore was launched. No completed trial
rows or successful experiment export are fabricated for this operational
failure. The existing 28 native and nine local-worker controls do not
substitute for cloud qualification. This outcome proves no LFD bound and
does not establish a defect in the candidate producer.

Evidence: [terminal status](../../runs/blocked-worker-cloud-source-terminal-001.json),
[output check](../../runs/blocked-worker-cloud-source-output-check-001.json),
[earlier scheduler status](../../runs/blocked-worker-cloud-source-pending-001.json).
Frozen protocol SHA256:
`691181aa857920db5e544da5838a9163e811e18ad5a56ae2d704a73c0a283efe`.

Next: reconcile capacity after the existing priority frontier job ends;
any retry needs a new identity and prospective execution record. Placement
guards and resource caps remain intact. Forty unfinished original
high-memory inputs and nine unfinished panel inputs remain in scope.
The live n=47 and n=45 scientific producers are separate from this failure.

The operational flow diagram records this attempt only. No mathematical
edge in the canonical evidence graph changes because no control executed
successfully and no scientific certificate was produced.
