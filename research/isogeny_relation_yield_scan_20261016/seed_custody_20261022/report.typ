#set page(paper: "a4", margin: 22mm)
#set text(font: "New Computer Modern", size: 10pt)

= Independent verifier-root preparation control

2026-10-22 · T-4770 / T-4772 / T-4774 · Fixed public control

The graph scientific preparer now requires three distinct 256-bit roots. The
base root chooses the factor base, the target root draws `(alpha,beta)`, and
the verifier root chooses the nonzero hidden scalar of `Q`. The version-2
commitment binds all three digests. Historical two-root controls remain
replayable; the scientific executor rejects that mode.

#figure(image("seed_flow.svg", width: 100%), caption: [Separate root derivations in the prepared-input control.])

The retained P29 source `low_x` control used fixed public roots `B`×32,
`T`×32, and `V`×32. It prepared 8,192 targets, the full discovery quota for
one P29 arm. Independent group arithmetic verified all 8,192 target equations
and 512 signed base points. Deterministic replay from all three roots passed.
The exact commands, stdout, stderr, root files, prepared input, manifest, and
hashes are in `control/`.

The 26-case small-control suite passed; an archived two-root fixture still
replayed. An eight-target four-phase graph control passed, and scientific
mode rejected an older two-root input before writing an attempt directory.

These are implementation checks. No relation collection, useful rank,
graph-wide inference, approved experiment, or complete ECDLP timing occurred.
The public test roots cannot serve as scientific target roots. The candidate
8,206-arm schedule and later fresh confirmation and solve stages remain open.
