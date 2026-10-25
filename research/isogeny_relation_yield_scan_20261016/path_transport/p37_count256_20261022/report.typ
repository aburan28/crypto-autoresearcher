#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Arial", size: 9pt)
= P37 endpoint-256 public targetwise count control
#text(size: 8pt)[Observation-only implementation control, 2026-10-22. The 128 public targets are excluded from discovery and confirmation.]

== Exact pair and result
The source and endpoint-256 bases each contain 1,600 x-orbits with both signs over $F_81640512137$, group order 81640511861. The 256-edge saved map chain passed independent replay for 819,200 signed-base images. The same 128 public scalar targets were prepared on both endpoints with matching coefficient labels. The ordered-count files are byte-identical, SHA-256 `f799d1cd80cdacd125d4ad0e1681ce5e704da836c569b3e12b11763ba144d473`.

Seven of 128 targets have an ordered three-point representation, with 48 ordered representations total. The comparison record reports pass. These counts are the same as the earlier index-4 and index-24 public controls.

#figure(image("counts.svg", width: 100%), caption: [Recorded ordered triples for the same 128 public targets on the source and transported endpoint-256 bases. Task T-4739.])

== Scope
This is a targetwise transport-consistency check on fixed public controls. It does not measure graph-wide native-base yield, useful rank, or complete ECDLP cost. The accompanying Markdown report binds the exact inputs, commands, source and binary hashes, raw logs, and limitations.
