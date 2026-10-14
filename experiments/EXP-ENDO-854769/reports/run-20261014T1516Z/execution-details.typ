#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Execution details appendix
== Status
#text("Observations only. One trial requested and completed; zero failed or timed out. Supervisor status output_validated; process and replay-check return codes both zero. Certificate kind: none. This appendix adds recorded provenance to report.md; no new trial or research review.")

== Recorded timing
#text("Driver wall time: 0.009882722 seconds. Driver process CPU time: 0.009869388 seconds. Measurement scope: driver arithmetic and raw-result assembly; checker/supervisor costs separate. These recorded times are not a performance comparison. Supervisor and checker CPU/resource totals were not recorded.")

== Environment and inputs
#text("Experiment EXP-ENDO-854769; run RUN-ENDO-910c24. Platform linux; Python 3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]. Hostname, CPU model and runtime lock were not recorded. Full-tree dirtiness is unknown. Parameters copied from manifest.yaml: {\"D_K\": [-3, -4, -7, -8, -11, -15, -20, -23], \"conductors\": [1, 2, 3, 6], \"module_primes\": [2, 3, 5, 7], \"primary_generator_coefficients\": [6, 10, 15]}. Seed list: [1729].")

== Provenance
#text("Immutable run directory: experiments/EXP-ENDO-854769/runs/RUN-ENDO-910c24. Manifest SHA256 d6278bfda20ff82d9eaf8deceafd9dee3e391987aff7965720ebc07dd639b8e3. Exact command and source bindings are retained in manifest.yaml and launch.json. The replay checker is implementation integrity, not independent mathematical validation.")

