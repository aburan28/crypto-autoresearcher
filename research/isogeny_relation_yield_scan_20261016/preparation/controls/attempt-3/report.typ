#set page(margin: 18mm)
#set text(font: "Helvetica", size: 10pt)

= Two-edge transported-base control
16 October 2026 — implementation evidence, task T-3327

The source `low_x` base was mapped through the first two saved degree-7 edges of each P29/P37 walk. The four fixed targets were planted sums of three points from the first 16 signed base points. These controls test map and base arithmetic; they are not relation-yield samples or ECDLP cost measurements.

#image("control_graph.svg", width: 100%)

== Recorded checks

#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  [Stratum], [Signed base], [Edges], [Independent target counts],
  [P29], [512], [1, 2], [[1, 1, 1, 1] at source and both vertices],
  [P37], [3,200], [1, 2], [[1, 1, 1, 1] at source and both vertices],
)

For each edge, the saved kernel selected one Sage isogeny, the raw and canonical codomain models matched, the saved image generator matched, all transported base points were distinct and nonidentity, and 21 direct dual identities held. Independent short-Weierstrass arithmetic recomputed the target counts. Exact point digests, curve identities, edge timings, Sage version and graph digests are in `result.json`.

== Scope and next check

The first all-point dual replay was interrupted during its larger P37 work; its stderr was retained as attempt 2. Attempt 3 evaluates each forward map once per point and checks the dual on a fixed sample. P29's internal elapsed time was 1.93 s and P37's 360.79 s; these are control execution times, with no matched performance baseline. The next step is fixed check-vertex transport across the full paths with precommitted discovery targets and independent exact counts. Full relation collection, rank and same-point solving remain outside this control.

Source and evidence: `transport_two_edges.py`, `controls/attempt-3/result.json`, `controls/attempt-3/stderr.log`, and the archived P29/P37 graph walks bound by SHA-256 in the result. The prose report `insight.md` records the exact command, missing resource fields, and censored predecessor.
