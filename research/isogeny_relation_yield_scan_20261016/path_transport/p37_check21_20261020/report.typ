#set page(paper: "us-letter", margin: 0.8in)
#set text(font: "Arial", size: 10pt)
= P37 source-base transport: edge 21 control
#text(size: 9pt)[Observation-only report, 2026-10-20. This control checks saved map and base arithmetic; no relation targets were collected.]

== Inputs
P37 over $F_81640512137$, prime group order 81640511861, 1,600 x-orbits (3,200 signed points). Archived walk SHA-256: ` 523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281 `. Producer script SHA-256: ` 2829ef00e3727216f91bda4cccb386f3ea54db7fcdedf87954b5eab3362cc84e `. Sage 10.10.rc0.

== Observations
Edge 21 destination $j=49775280396$. Checkpoint SHA-256: ` d2e283edb3ab0cbb4078d8c01b587c8ab25b0dcf11194324d8e8eef7eb982f54 `. Per-edge timer: 7.393 s. Producer wall 25.83 s; verifier wall 5.56 s. Independent replay: status pass, 21 edges and 67,200 point images; terminal hash matches checkpoint.

#figure(image("edge_times.svg", width: 100%), caption: [Checkpoint-recorded edge times. Edge 21 was produced in this session; edges 1–20 are prior controls.])

== Scope
The verifier independently checks the saved edge and full signed-base map chain. Edges 22–256 and all relation-yield, rank, and ECDLP measurements remain open. Exact commands, logs and source script are in the accompanying Markdown report.
