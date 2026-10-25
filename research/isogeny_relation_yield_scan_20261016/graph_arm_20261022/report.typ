#set page(paper: "us-letter", margin: 0.72in)
#set text(font: "Helvetica", size: 9pt)
#set heading(numbering: none)

= Graph-transported factor-base arm
Fixed implementation control, 2026-10-22 PDT — Conductor T-4748, fence epoch 1.
Implementation and raw controls: commit `366dd01f19`.

This report records prepared-input checks. It makes no relation-yield, rank,
or ECDLP runtime inference. Source and raw values: `report.md`,
`control-metrics.json`, archived P29/P37 checkpoint chains.

== Exact tested objects
P29: $E / F_(320092037): y^2 = x^3 + 105931039 x + 284015384$,
prime order $320091991$, source $G=(0,50656410)$, check vertex 8.
P37: $E / F_(81640512137): y^2 = x^3 + 46677163888 x + 11713815639$,
prime order $81640511861$, source $G=(39752613976,79465703431)$,
check vertex 4. Both prefixes use archived degree-7 separable maps over
their respective prime fields.

#figure(image("diagram.svg", width: 100%), caption: [Archived graph transport and native-base comparisons. The two zero overlaps are fixed-input observations.])

== Fixed controls
The source graph base equals source native `low_x`. At P29 vertex 8, the
256-orbit graph and native bases share 0 x-orbits. At P37 vertex 4, the
1,600-orbit bases share 0. The same generator, Q, and eight public target
coefficients were used in each pair. The 26 small arm/vertex preparation
cases passed, including rejection of a noncheck vertex and a modified
checkpoint digest. Exact raw values and checkpoint hashes are in
`control-metrics.json`.

== Next obligation
Bind a runnable post-freeze collector and independent count/rank verifier,
then freeze the check-arm quotas and target roots under Coordinator approval.
This control does not enter the prospective discovery inference.
