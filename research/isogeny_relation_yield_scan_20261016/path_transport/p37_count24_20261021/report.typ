#set page(paper: "us-letter", margin: 0.78in)
#set text(font: "Arial", size: 10pt)
= P37 vertex 24 public targetwise count control
#text(size: 9pt)[Observation-only report, 2026-10-21. These fixed public targets are excluded from discovery and confirmation inference.]

== Identity and method
P37 over $F_81640512137$, prime group order 81640511861. The signed source base has 3,200 points and is transported through 24 saved degree-7 edges. The independent chain verifier replayed 76,800 point images. Both endpoints use the earlier fixed 128 public scalar labels and the same exact ordered-count oracle.

== Observations
All 128 targetwise counts agree. Seven targets are nonempty and have 48 ordered relations total. Source and transported count files have the same SHA-256: ` f799d1cd80cdacd125d4ad0e1681ce5e704da836c569b3e12b11763ba144d473 `. The same digest appears in the earlier first-check P37 source control. The saved destination checkpoint SHA-256 is ` ed74a5492453944588f3365e483cc28a634e39bf5be6b5ca48006ae2f751b93a `.

#figure(image("counts.svg", width: 100%), caption: [Exact ordered three-point counts for the same 128 public targets on source and vertex-24 transported bases. Bars coincide targetwise.])

== Scope
This is an implementation control for this fixed stream and endpoint. The admitted discovery stream, native-base comparison, useful-rank replay and full ECDLP cost measurements remain open. Inputs, commands, binary/source hashes, raw counts, meters, and a retained failed wrapper attempt are in the accompanying Markdown report.
