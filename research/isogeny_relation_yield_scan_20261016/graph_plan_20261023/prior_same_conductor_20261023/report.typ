#set page(paper: "a4", margin: 11mm)
#set text(font: "Helvetica", size: 8pt)
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
#set text(size: 8pt)

#image("yield.svg", width: 84%)

The observed fractions are 0.0672607422 (E2) and 0.0668640137 (E3); their
derived difference is 13/32,768 = 0.0003967285, about 0.0397 percentage
points. The plotted exact intervals overlap. No equality or difference
conclusion follows. Both runs report an independent ordered-count match and
valid group-law replay and reached rank 256 of 256 by the 8,192-target prefix.

== Target-stream audit

The source specification says endpoint arms share a target vector. I independently hashed all 32,768 ordered `(alpha, beta)` pairs in the committed native prepared inputs, excluding curve-dependent points. The streams differ, including their first coefficient pair:

#set text(size: 7.5pt)
#table(
  columns: (1fr, 1.6fr, 2fr),
  inset: 3pt,
  stroke: 0.4pt,
  [*Endpoint*], [*First `(alpha, beta)` pair*], [*Coefficient-stream SHA-256*],
  [P29 floor E1], [(264673044, 279640898)], [64cd3756f380...588c51ca],
  [P29-E2], [(306343046, 290671108)], [80d447c67d0d...0cd3cb3c5],
  [P29-E3], [(214677491, 24330666)], [2917b209cce2...be0fc7a3],
)
#set text(size: 8pt)

The archived E2/E3 observations are marginal, not paired with E1 or each other. The graph protocol must bind and independently verify identical ordered coefficient pairs across P29 endpoints within each stage before reporting paired contrasts. Full digests and the first three pairs are in the editable report source.

== Incomplete panel and graph-study scope

The E1 primary P29-floor-native run (RUN-ECTD-8231ef) failed with an
infrastructure error. The E2 and E3 random arms (RUN-ECTD-d14263 and
RUN-ECTD-45ca41) also failed with infrastructure errors. The registered
E2/E3-to-E1 panel is incomplete.

These valid native observations are prior marginal secondary context. Their
coefficient streams differ from E1 and each other; they do not use the graph
study's committed target stream and do not describe graph vertices or
transported bases. Fresh E2/E3 arms on the graph study's common P29 stream are
required for paired same-conductor controls.

Source: [archived 20-arm run report](../../../../experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/report.pdf).
Graph implementation controls: [separate report](../report.pdf).
