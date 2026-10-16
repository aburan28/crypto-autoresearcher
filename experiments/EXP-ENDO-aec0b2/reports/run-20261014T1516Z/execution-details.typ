#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Execution details appendix
== Status
#text("Observations only. One trial requested and completed; zero failed or timed out. Supervisor status output_validated; process and replay-check return codes both zero. Certificate kind: none. This appendix adds recorded provenance to report.md; no new trial or research review.")

== Recorded timing
#text("Driver wall time: 3.099779952 seconds. Driver process CPU time: 3.099138084 seconds. Measurement scope: driver arithmetic and raw-result assembly; checker/supervisor costs separate. These recorded times are not a performance comparison. Supervisor and checker CPU/resource totals were not recorded.")

== Environment and inputs
#text("Experiment EXP-ENDO-aec0b2; run RUN-ENDO-4d758c. Platform linux; Python 3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]. Hostname, CPU model and runtime lock were not recorded. Full-tree dirtiness is unknown. Parameters copied from manifest.yaml: {\"D_K\": [-3, -4, -7, -8, -11, -15, -20, -23], \"conductors\": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], \"generator_scales\": [1, 2, 3], \"module_primes\": [2, 3, 5, 7]}. Seed list: [1729].")

== Provenance
#text("Immutable run directory: experiments/EXP-ENDO-aec0b2/runs/RUN-ENDO-4d758c. Manifest SHA256 1b649202da7b29d9efbc19c82eb2c9efb511e798be164208ca3093cc9725d24d. Exact command and source bindings are retained in manifest.yaml and launch.json. The replay checker is implementation integrity, not independent mathematical validation.")

