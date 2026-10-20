#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set heading(numbering: none)

= Formal and evidence validation slice
2026-10-20 · Scoped audit of committed cryptanalysis and crypto-autoresearcher material

This is a review of historical evidence and source code. No scientific trial or new performance measurement was run. The main revisions inspected were `cryptanalysis` `5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14` and `crypto-autoresearcher` `18f0d9613a3b7ad575b190941a26b826312e4bc3`.

== Inventory and exact scope

The main trees contain 326 and 2,750 tracked experiment directories respectively. In the autoresearcher, 66 formal target specifications name 61 present theorem files and five undischarged files. Presence is not a successful proof build. The cryptanalysis main tree has 91 tracked Lean files. This audit checked selected high-impact links, not every experiment or theorem.

== Semaev first-fall discrepancy

The archived eight-cell toy summary records 70 of 80 Semaev draws at first-fall degree 2 and ten at degree 3. The historical note says the degree is pinned at two in every cell. The frozen formal target describes a universal first-fall proof. The Lean file itself proves annihilation of quadratic coefficients and explicitly says that the nonzero lower-degree residue is unproved. A zero combination would not be a nontrivial fall. Individual target abscissas were not retained in the eight-row summary, so the degree-three exceptions cannot be attributed from that artifact.

#figure(image("fall_counts.svg", width: 100%), caption: [Archived toy outcomes. Source: `research/verification/ffd_semaev_results.json`; 10 Semaev draws per cell.])

The valid conclusion is the conditional trace-cancellation identity and the measured toy distribution. A universal first-fall theorem, solving-degree consequence, and ECDLP cost claim remain open. The precise bridge and replay obligations are in `problems/semaev-degree-two-fall-nonzero-bridge.md`.

#pagebreak()

== Proof boundary in the orbit-summation experiment

The new Lean declaration `OrbitQuotient.triple_matches_iff_pair_lookup` proves an exact modular equivalence between direct three-slot matching and pair-index lookup over already enumerated scalar lists. Lean 4.34.1 compiled it; its axiom printout contained only `propext` and `Quot.sound`. Four Python unit tests passed, including a small-modulus direct-enumeration comparison for both representative policies. The theorem does not certify the curve/orbit enumeration, Boolean degree, four-slot counts, or performance.

#figure(image("proof_boundary.svg", width: 100%), caption: [The measured table and Lean lemma are separate evidence. Dashed arrows mark unproved jumps.])

== Benchmark dashboard refresh

The nine-row primary N13 toy benchmark snapshot was regenerated from committed `cryptanalysis` main. The source archive SHA-256 is `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973`; the exported snapshot SHA-256 is `4cc3b31ab805b34d9f2d1103e574f8130a6902d09703d49337c467257568ae5e`. Catalog and comparison receipt pins were updated together. Candidate IDs and recorded online timings differ from the prior import. “Recorded verified” is the archive’s status, not an independent replay performed here.

No canonical scientific graph data changed: no new experiment result was produced. The benchmark reader now points to the current primary archive, while other historical archives remain outside this dashboard view.

== Reproduction limits

The cryptanalysis candidate analyzer accepted all nine archive rows; four orbit tests and the new Lean module passed. The autoresearcher Lean smoke project built, six benchmark reader tests passed on the new main-based branch, and 145 focused UI tests passed on the complete `8b77d405...` checkout after the snapshot update. A complete static UI build emitted 55,152 files (519.9 MB), with all nine refreshed rows in `data/comparisons.json`. Node/npm were absent, so DOM tests did not run. The smoke build does not build the Semaev Mathlib theorem. A complete formal-workspace build and independent semantic review of all 66 targets remain outstanding.

Sources and exact commands: `report.md` beside this PDF. Visual source: `render.py`.
