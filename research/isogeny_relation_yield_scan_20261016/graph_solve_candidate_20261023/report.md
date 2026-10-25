# Candidate complete-solve path: bounded implementation controls

Date: 2026-10-22. Conductor task T-4795. This is source and execution-control
evidence for a candidate Sage modular solver, not a scientific graph-wide
relation-yield or ECDLP timing result.

The [replayed small-group controls](controls/attempt-2/manifest.json) bind the
current `solve.py` and `check.py` source hashes, binaries, commands, logs and
outputs. Both complete 19-point cases recovered and independently replayed
the public scalar: Q in the factor base had rank 2/2 and scalar 7; Q outside
the base had rank 3/3 and scalar 2. Each separate checker verified three base
orbits, 18 targets and 56 reported triples. The one-target input had rank 0/2
and remained censored. A copied scalar changed from 7 to 8 was rejected.

The [P37 control](controls/attempt-3/control-manifest.json) used the archived
public `u2_transport` prepared input at vertex 1 with eight targets and 1,600
factor-base x-orbits. The graph wrapper completed `input_verify`, Rust
collector, independent C++ ordered count and Python rank replay under its
8 GiB/1,800-second control guards. The candidate solver constructed 1,601
unknown columns, computed rank 2 and retained `censored_insufficient_rank`;
the separate checker accepted the censored record. Its exact commands,
source/output digests, phase times and sampled RSS are in the wrapper receipt
and control manifest. This bounded check exercises P37 field arithmetic and
matrix layout, not full discovery quota or solve completion.

The diagram [rank_summary.svg](rank_summary.svg) and inspected
[report.pdf](report.pdf) show only these recorded ranks. The solver JSON's
internal phase timings exclude Sage startup, graph construction, point
transport, base/table setup, repeated targets and matched rho. No timing
comparison or graph-wide curve ordering follows from these controls.
