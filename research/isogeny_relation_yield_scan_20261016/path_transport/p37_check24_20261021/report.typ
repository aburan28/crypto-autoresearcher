#set page(paper: "us-letter", margin: 0.8in)
#set text(font: "Arial", size: 10pt)
= P37 source-base transport: check vertex 24
#text(size: 9pt)[Observation-only report, 2026-10-21. This control checks saved map and base arithmetic; no relation targets were collected.]

== Inputs
P37 over $F_81640512137$, prime group order 81640511861, 1,600 x-orbits (3,200 signed points). Archived walk SHA-256: ` 523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281 `. Sage 10.10.rc0.

== Observations
The successful producer wrote edges 22–24 with timers 1.600, 1.162 and 1.261 s. Edge 24 has $j=27040562305$; checkpoint SHA-256: ` ed74a5492453944588f3365e483cc28a634e39bf5be6b5ca48006ae2f751b93a `. Producer wall 11.43 s; verifier wall 1.99 s. Independent replay: status pass, 24 edges and 76,800 point images; terminal hash matches checkpoint. A first launch failed on a missing sparse-checkout input before writing any checkpoint, and its logs are retained.

#figure(image("edge_times.svg", width: 100%), caption: [Checkpoint-recorded edge times. Edges 22–24 were produced in this session; edges 1–21 are earlier controls.])

== Scope
The verifier independently checks the saved edge and full signed-base map chain. Edges 25–256 and all relation-yield, rank, and ECDLP measurements remain open. Exact commands, logs, model identity, and source script are in the accompanying Markdown report.
