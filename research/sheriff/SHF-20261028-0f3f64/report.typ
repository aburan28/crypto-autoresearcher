#set document(title: "Sheriff case SHF-20261028-0f3f64")
#set page(paper: "a4", margin: 1.8cm, numbering: "1")
#set text(size: 9.5pt)
#set par(justify: true)
#show heading.where(level: 1): set text(size: 16pt)
#show heading.where(level: 2): set text(size: 12pt)

= Sheriff case SHF-20261028-0f3f64

Independent re-audit of current main in crypto-autoresearcher, crypto and cryptanalysis. An audit record: it changes no research state and repairs nothing. The full text is in `REPORT.md`; verdicts are in `findings.yaml`, which passes `check-case`.

*Result: of 21 claims, 2 are upheld, 13 upheld with a narrower scope, 4 overclaimed, 2 not covered; none broken. There is no blocker; 7 major findings.*

#figure(image("sweep.svg", width: 100%), caption: [Deterministic sweep (tools/sheriff.py), canary 15/15.])

== Overclaimed
- *C-STARK-5:* the FRI fold check and the depth gate have no isolating negative test (S2N-1, S2N-2). `cargo test` was not run.
- *C-MAN-2:* `complete_manifest()` compares only id fields; 24 of 27 contradictions pass (LGN-2).
- *C-LED-1:* 143 to 126 is 141 to 124 at the PR tip and 115 to 100 as merged. The merge left duplicate keys in the supersession registry (LGN-1).
- *C-LEAN-2:* `translation_descends_iff_two_torsion` proves commutation, not descent (L-N9 still open).

== Held
- cryptanalysis\#1077: 150 of 150 SHA256SUMS verify; every quoted band number matches. S/rT is 0.0114, 29.0 and 115.5 at 0, 0.1 and 1 GAE: unresolved against rho, no improvement claimed.
- stark_v2 DEEP-ALI: transcript order, D(x) recomputation, degree bound and ε arithmetic read as sound (code reading only).

== Not covered
`cargo test`, the Lean build and axiom audit (no toolchain; install refused), workflow states, `analyze_v2.py` rerun, S3 objects.

== Prior findings
42 fixed, 6 partially fixed, 1 not fixed (L-N9), 1 not covered (CI1).
