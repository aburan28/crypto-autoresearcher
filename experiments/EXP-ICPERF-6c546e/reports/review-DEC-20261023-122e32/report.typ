#set page(paper: "a4", margin: 14mm)
#set text(font: "DejaVu Sans", size: 8.5pt)
#text(size: 16pt, weight: "bold")[Reviewed balanced index-calculus improvement]

#text("DEC-20261023-122e32 accepts EV-ICPERF-92c130: moderate empirical, toy scope. EXP-ICPERF-6c546e / RUN-ICPERF-d566af; independent TASK-20261023-6562b0. Historical reference default unchanged.")

#text("Observation:162 complete workers,54 pairs,9 unseen12/14/16-bit public curves,18 target/relation streams. Seeds3/4/5; solver seeds0/1;3 repetitions; m2/small_x/mitm, scalar, harvest off, window4. Every arm crosses every slot; all six permutations occur.")

#image("measurements.svg", width: 100%)

#text("Comparison: paired geometric full-solve ratio1.160582; A/A1.044171; pooled95% interval[1.126752,1.197661],5000 stratified curve-cluster resamples. Frozen point gate1.05 and interval lower>1 pass. Blind floor upper1.197412 and linear upper1.197418 also retained; percentile rounding was unspecified. Five pairs are slower.")

#text("Inference: independent integrity and inference joints hold in this scope. Nine orders exhaustively counted;162 certificates and18 streams replayed. Wrong-log/config/target/row/environment/affinity/load controls and original middle-only schedule reject; identical-time gate fails. Prior blind algebra and unchanged-worker audit reused explicitly.")

#text("Boundary: complete instrumented native API call includes all per-solve setup, misses, relations, LA/recovery and final verification; startup/imports, fixtures, telemetry, hashing and checker excluded. Setup is not double-counted. Full group-op sums200856 versus50490 per54 solves; no addition of unlike or overlapping costs.")

#text("Limit: one CPython3.12.14/EPYC9V74 CPU0 host/session;9 curves, not54 independent curves. No known competing scientific producer; census cannot prove global isolation. RSS28.37–29.87MiB; packed payload304–440 bytes excludes Python objects. No default/frontier, rho/BL, deployed-curve, asymptotic or execution-proof claim.")

#text("Next: publish optional implementation and structured claim; keep goal active. Original confounded timing remains preliminary. Raw snapshoted0d34e276149b30d137448f22b0fb17cdd4cf28; sourcee9f89202f5977ad5e39cc42311cfa781a24d41f7. Full methods, controls, citations and limits:report.md.")
