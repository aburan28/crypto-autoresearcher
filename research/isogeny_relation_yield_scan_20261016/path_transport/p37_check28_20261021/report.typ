#set page(paper: "us-letter", margin: 0.8in)
#set text(font: "Arial", size: 10pt)
= P37 source-base transport: check vertex 28
#text(size: 9pt)[Observation-only report, 2026-10-21. This control checks saved map and base arithmetic; no relation targets were collected.]

== Inputs
P37 over $F_81640512137$, prime group order 81640511861, 1,600 x-orbits (3,200 signed points). Archived walk SHA-256: ` 523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281 `. Sage 10.10.rc0.

== Observations
The producer wrote edges 25–28 with timers 6.127, 3.754, 4.120 and 3.586 s. Edge 28 has $j=22296417885$; checkpoint SHA-256: ` 0432bfb7e7d60f0d19e6641a6d7fd0ae51434eb5010ef978b76cf73160c7123a `. Producer wall 40.94 s; verifier wall 5.76 s. Independent replay: status pass, 28 edges and 89,600 point images; terminal hash matches checkpoint.

#figure(image("edge_times.svg", width: 100%), caption: [Checkpoint-recorded edge times. Edges 25–28 were produced in this session; edges 1–24 are earlier controls.])

== Scope
The verifier independently checks the saved edge and full signed-base map chain. Edges 29–256 and all discovery-stream relation-yield, rank, and ECDLP measurements remain open. Exact commands, logs, model identity, and source script are in the accompanying Markdown report.
