#set page(paper: "a4", margin: 16mm)
#set text(font: "Helvetica", size: 9pt)
#set heading(numbering: "1.")
= Prior P29 same-conductor native observations

2026-10-23. Descriptive audit of two archived arms from EXP-ECTD-0cf008.
This is not an evidence review or a graph-walk measurement. Values are copied
from output-validated receipts and their raw-result records. The source
experiment remains incomplete.

== Exact curve identities

All models use F_p, p = 320092037, subgroup order r = 320091991, and
f_E = 8209. E1, the primary P29 floor, is y² = x³ + 101186781x + 57596093,
G = (0, 112219098). E2 is y² = x³ + 64570613x + 54195252,
G = (0, 5368294). E3 is y² = x³ + 234001141x + 79995391,
G = (5, 53527325).

== Recorded observations

#set text(size: 7.5pt)
#table(
  columns: (1fr, 1.2fr, 1.2fr, 1.5fr, 1.8fr),
  inset: 4pt,
  stroke: 0.5pt,
  [*Endpoint*], [*Run ID*], [*Useful / attempted*], [*Exact 99.75% interval*], [*Rank at 512 / 2,048 / 8,192 / 32,768*],
  [E2 native], [RUN-ECTD-c769f1], [2,204 / 32,768], [[0.063148, 0.071545]], [37 / 143 / 256 / 256],
  [E3 native], [RUN-ECTD-f395a9], [2,191 / 32,768], [[0.062762, 0.071136]], [45 / 140 / 256 / 256],
)
#set text(size: 9pt)

#image("yield.svg", width: 96%)

The observed fractions are 0.0672607422 (E2) and 0.0668640137 (E3); their
derived difference is 13/32,768 = 0.0003967285, about 0.0397 percentage
points. The plotted exact intervals overlap. No equality or difference
conclusion follows. Both runs report an independent ordered-count match and
valid group-law replay and reached rank 256 of 256 by the 8,192-target prefix.

== Incomplete panel and graph-study scope

The E1 primary P29-floor-native run (RUN-ECTD-8231ef) failed with an
infrastructure error. The E2 and E3 random arms (RUN-ECTD-d14263 and
RUN-ECTD-45ca41) also failed with infrastructure errors. The registered
E2/E3-to-E1 panel is incomplete.

These valid native observations are prior secondary context. They do not use
the graph study's committed target stream and do not describe graph vertices
or transported bases. The frozen graph contract must state whether fresh E2
and E3 arms share its target root before any root is issued.

Source: [archived 20-arm run report](../../../../experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/report.pdf).
Graph implementation controls: [separate report](../report.pdf).
