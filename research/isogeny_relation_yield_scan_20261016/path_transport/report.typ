#set page(margin: 18mm)
#set text(font: "Helvetica", size: 9.5pt)

= First check-vertex path transport
16 October 2026 — implementation control, T-3361 (successor to T-3350)

The archived P29 and P37 degree-7 walks carried the fixed source `low_x`
signed base to their first scheduled all-point check vertices. This report
records implementation observations; it assigns no scientific verdict.

#image("chain.svg", width: 100%)

#table(
  columns: (1fr, 1fr, 1fr, 2fr),
  [Stratum], [Edges], [Point images replayed], [Final checkpoint SHA-256],
  [P29], [8], [4,096], [`8b40a5c11de49dbf…`],
  [P37], [4], [12,800], [`4b529e7d45b6cc54…`],
)

The table shows SHA-256 prefixes for legibility. Complete hashes appear in
`insight-20261016.md` and the verifier stdout files.

The integer-arithmetic verifier exited 0 on both chains. It replayed all
stored base and generator images, the raw codomain identities, the source
base definition, the hash chain, and the fixed check-vertex schedule. P29
index 8 and P37 index 4 each retained the full number of distinct `x`
orbits. Evidence: `controls/p29-check1-verify.stdout`,
`controls/p37-check1-verify.stdout`, and the saved `edge-*.json` files.

#pagebreak()

== Diagnostic execution times

#image("edge_times.svg", width: 100%)

The times are single internal monotonic measurements made while preparing
each edge. Processor isolation, CPU time, RSS, complete shell wall time,
and uncertainty were not captured. These bars make no performance or
ECDLP cost comparison.

== Failure and next gate

The first P29 continuation exited 1 because the Sage launcher redirected
its cache to a protected directory. Its stderr is retained as
`controls/p29-resume-to-check1.stderr`. The corrected Sage-shell invocation
for P29 and the P37 continuation exited 0. Full-path transport, relation
collection, rank, and same-point solving remain next-stage work.

The dated prose report `insight-20261016.md` gives exact commands, input
hashes, source revision and dirty state, the independent checks, and limits.
The editable diagram source is `render_report.py`.
