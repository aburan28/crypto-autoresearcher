#set page(paper: "a4", margin: 18mm)
#set text(font: "Helvetica", size: 9pt)
#set heading(numbering: "1.")
= Full-quota P37 graph input preparation control

2026-10-22, Conductor task T-4822. Implementation control at P37 vertex 0
using public roots. This report records preparation and replay observations;
it makes no relation-yield, rank, ECDLP-cost or hypothesis-status decision.

#image("diagram.svg", width: 100%)

The independently checked candidate schedule contains 8,206 arms. The new
materializer selected three named P37 vertex-zero arms and prepared the full
discovery quota of 2,048 targets for each. Each arm contains 3,200 signed
base points. The native and graph-transport input bytes are identical at the
source vertex. The separate u=2 transported input matches the exact
(x,y) -> (4x,8y) map on all base and target points. The coefficient stream
digest agrees across all three arms. The existing group-law verifier passed
on every saved input; swapped-root, unscheduled-arm and changed-target controls
were rejected.

The raw inputs, manifests, bindings, measured preparation process durations,
and machine checks are retained in `control/`. The roots are public control
values and are excluded from scientific discovery. The group-law verifier did
not independently replay the seed stream; the materializer reconstructed
every coefficient from the three roots. Relation collection, rank, confirmation
and complete ECDLP costs remain unmeasured by this control.

Next: freeze scientific roots and the runnable experiment contract, issue a
Coordinator admission, and execute the fixed graph schedule through `run`.
