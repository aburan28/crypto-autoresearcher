#set page(paper: "a4", margin: 14mm)
#set text(font: "DejaVu Sans", size: 9pt)
#text(size: 17pt, weight: "bold")[Fixed-base targets in toy index calculus]

Observations only; independent evidence review determines any claim.

#text("EXP-ICPERF-3065f9 / H-ICPERF-a2284c / GOAL-ICPERF-e6b6a4")

#image("measurements.svg", width: 100%)

#text("RUN-ICPERF-842b51: 162 workers, 54 matched pairs. Derived ratio 1.0880; clustered 95% interval [1.0614, 1.1183]; A/A factor 1.0264.")

#text("All 162 workers completed; no failures/timeouts/censored records. Nine public prime-order curves at 12/14/16 bits; curve seeds 0/1/2, solver seeds 0/1, target seed 0, three repetitions, m2, small_x, mitm, scalar decomposition, harvest off, window 4.")

#text("Timer: entire native solve, including factor base, all table setup, misses, elimination and final verification. Excludes public-instance generation, process startup, trace hashing and independent checker. Each arm pays its own setup. Wall/CPU/group operations are not summed.")

#text("Independent checker: point counts and subgroup/order; recovered kP=Q; every seeded target; paired factor-base points/signs, relation digests and deterministic counters. Known-false log and zero-advantage controls rejected. Source bfc2e0b4c25ff1748872a3d4dd9af2d040ec3699. Launch source files unchanged. Command and raw receipts are in the run directory; detailed source/provenance is in report.md.")

#text("Limits: one host; scalar-decomposition toy workload. Candidate remains optional. No vectorized/default-pipeline, Pollard-rho, deployed-curve, asymptotic or official-frontier claim. Process peak RSS includes Python overhead; coordinate payload 304–480 bytes does not. CPython 3.12.14, NumPy 2.3.5, Linux x86_64, five visible CPUs on AMD EPYC 9V74.")

#text("Independent review found C-target not isolated: the candidate always occupies the middle execution slot. The observed timing ratio is descriptive only; it cannot support a causal wall-time speedup claim. A separately frozen balanced-slot successor on unseen curves is required.")
