# Independent verifier-root preparation control

Date: 2026-10-22 (America/Los_Angeles). Conductor tasks T-4770, T-4772,
and T-4774. Status: fixed public implementation control, outside scientific
discovery and confirmation.

The prospective graph protocol specifies an independent verifier root for the
unknown `Q` scalar. Previously the preparer derived that scalar from the target
root. The scientific CLI now requires three distinct 256-bit roots: base,
target, and verifier. Its version-2 commitment binds their SHA-256 digests.
The target root draws `(alpha,beta)` while the verifier root draws `Q`'s
nonzero scalar. Historical small controls remain replayable under their
original two-root mode; scientific execution rejects that mode.

[The retained control](control/receipt.json) used the fixed **public** byte
strings `B`×32, `T`×32, and `V`×32. It prepared the source P29 `low_x` arm at
the full 8,192-target discovery quota. The exact [prepare](control/prepare.command)
and [verify](control/verify.command) commands, stdout, stderr, root files,
commitment, [prepared input](control/prepared/prepared.txt), and manifest are
retained with hashes in the receipt. Both commands exited zero. The verifier
reported `pass` on 8,192 group-law targets, 512 signed base points, and
deterministic replay from all three roots. The [diagram](seed_flow.svg) shows
the separate derivation paths; an [inspected PDF](report.pdf) preserves the
same scope and result.

The 26-case small-control suite passed after the code change. An archived
eight-target two-root fixture still replayed exactly. The graph executor's
eight-target fixed public control passed its four phases, while its scientific
invocation rejected the historical input before creating an output directory.
These checks establish preparation and gate behavior on their tested inputs.
They do not measure relation yield, rank, a completed ECDLP solve, or runtime
advantage. The public roots are test values, not the post-freeze scientific
roots; no scientific commitment or Coordinator admission is issued here.

The [candidate 8,206-arm schedule](../graph_schedule_20261023/report.md)
remains separate. The next admission step binds this three-root source version,
collector binaries, full target commitments, output custody, and fixed
stopping rules in an approved runnable `EXP-*` contract.

Provenance: source code, archived graph and earlier fixed controls are
`internal`; this control's commands, data, and replay receipt are `internal`.
