#set page(margin: 0.65in)
#set text(font: "Libertinus Serif", size: 10pt)
#set heading(numbering: none)

= P29 same-conductor control schedule supplement

Status: `candidate_unapproved`. This versioned supplement retains the frozen
8,206-arm graph schedule unchanged and adds four secondary P29 controls:
native `low_x` and `random_x` bases on each of P29-E2 and P29-E3, with 8,192
distinct targets per arm. Both endpoints use the graph discovery coefficient
domain (`P29`, `discovery`) and the same committed base, target, and verifier
roots. Target points are curve-specific; the paired $(alpha,beta)$ sequence
is shared and was independently checked with public control roots.

#figure(image("p29-secondary-floor.svg", width: 100%), caption: [E2/E3 are descriptive controls and do not enter graph finalist selection.])

== Identity and control scope

The endpoint labels, models, generators, field size, subgroup order, and
conductor factor come from the frozen source specification
`experiments/EXP-ECTD-0cf008/specification.yaml`. Its exact SHA-256 is bound in
`p29-secondary-floor-manifest.json`. Independent checks verify group membership
and the prime-order generator certificate for each endpoint.

The schedule has four arms and 32,768 target probes total. The control test
replays the common `P29/discovery` coefficient sequence for all four arms.
This establishes schedule identity and domain compatibility only. There are
no relation counts, rank measurements, or ECDLP trials in this supplement.

The P29-E1 floor remains primary. E2/E3 cannot enter graph finalist selection.
The full experiment contract, candidate plan, and Coordinator admission must
bind these controls before any scientific run.

Schedule SHA-256: `d01f15b92ebd250b9f90cbc278f55d13cc023046da268d96597ec6ddf72ec02a`\
Verification manifest SHA-256: `802d326963cee7e04b3cccc0b513ac18f005deb3b18dea8250a42d4d16154dee`
