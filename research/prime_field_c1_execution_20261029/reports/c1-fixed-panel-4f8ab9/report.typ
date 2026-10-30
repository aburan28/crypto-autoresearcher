#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= C1 fixed P-256 run: observations
29 October 2026 · c1-fixed-panel-4f8ab9 · one physical panel

This descriptive report records the unchanged fixed F1 inputs and complete
finite oracle checks. It is not an independent claim review or a speedup claim.

#image("native.svg", width: 100%)

#table(columns: (1.8fr, 1fr, 1fr, 1fr), inset: 5pt,
  [Case], [States], [Signed solutions], [Oracle],
  [Depth3 positive], [1], [1], [matched],
  [Depth3 generator], [0], [0], [matched],
  [Depth4 positive], [1], [1], [matched],
  [Depth4 generator], [0], [0], [matched],
)

All five arity-four partitions [1,1,1,1], [2,1,1], [2,2], [3,1], [4] each had
one signed solution. Nonseparable and corrupted-certificate controls passed.
The historical corruption case removes the solution set; no additional native
root/sign mutation is implied. All triple coordinate partitions were checked;
the nonzero native triple states here are distinct-coordinate states.

The process exited0, no timeout, source unchanged: seven cases complete,
four complete triple cases, three control cases, zero unknown. The public
generator's zero solution count applies only to the fixed declared base/query.
The positives are constructed controls, not unknown-DLP recoveries.

== Frozen execution
Exact curve, generator, fibre terminals and targets: original
research/p256_factor_base_parallel_20261026/tracks/f1/inputs.json.
Seed2026102601, maximum operator dimension560, all multiplicity strata; one
compute process/thread;2GiB memory and3600s watchdog. Admission used the
unchanged real S3 gate, committed source/protocol/release and owner lease.

Source: #text(size: 8pt)[6164ec00d419cbe43520fbdda19f85f6bbde44cf].
Protocol: #text(size: 8pt)[da415e25dd20cae3d33abe90b1c6c9b6500063cfd7f7ad6dd78c97c49e7399d8].
Release commit: #text(size: 8pt)[9374c43ed538a91b62e3edc2b51d9f1ec1a6ccee].
Raw data snapshot: #text(size: 8pt)[e925f22610577ceae34ff0e9cff59b3b40de277a].

== Resources and limits
Diagnostic process wall321.665s; CPU user317.619s and system2.956s;
peak process RSS123,777,024 bytes. Shared host, wall_valid=false; no calibrated
timing or complete-cost claim. Solver-total events include their inner phases;
the separate oracle must not be hidden or double-counted. FLINT internal field
operation counts remain unavailable. The export's two method cells share one
physical process and one diagnostic cost record; do not add shared counts.

Raw cases, journals and exact command: ../../runs/c1-fixed-panel-4f8ab9/.
The export verifies with file hashes and0 findings. Analysis, supervision,
source locks and the literature/source review are in the parent study.
Reports/summaries add only labeled arithmetic on retained values. No failed or
censored scientific case occurred. No official scientific status is promoted;
model identity and independent scientific review remain unverified.
