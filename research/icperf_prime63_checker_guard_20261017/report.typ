#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "New Computer Modern", size: 10pt)
#set par(leading: 0.65em)

= Prime63 planted-positive contradiction guard

GOAL-ICPERF-e6b6a4  •  2026-10-17  •  engineering control

The archived producer flags a planted positive whose solver response is
`certified_no_solution` as an invalid control and stops the panel. A
self-consistent raw archive with that response, however, passed the archived
independent checker as a censored positive. That is a checker acceptance
defect at the evidence boundary.

The additive `guard.py` first runs the archived checker, then independently
evaluates every planted witness against the exact polynomial, base,
signed-lift and full-target-point conditions. It reads the canonical raw
archive and rejects a planted `certified_no_solution` response. A model-cap
response remains censored. Archived sources remain byte-for-byte unchanged.

#figure(image("diagram.svg", width: 92%), caption: [Additive contradiction
guard. The red response is rejected after independent witness replay.])

== Engineering control

A synthetic Git fixture over a 101-element prime field used no Sage calls.
The forged, internally consistent unit-ideal response passed the old checker
as censored and was rejected by the guard. The model-cap control remained
censored. The exact command in `command.txt` ran eight tests, including the
archived admission and raw-custody controls. Logs and hashes are retained in
this directory. An unrelated existing `ResourceWarning` appears in stderr.

The result is a scoped checker fix. No full-width solve, relation yield,
degree of regularity, useful rank, target work, matched rho or complete
index-calculus runtime was measured. The scientific experiment remains
`review_required` until the successor source and execution protocol are
hash-bound and pass preapproval.
