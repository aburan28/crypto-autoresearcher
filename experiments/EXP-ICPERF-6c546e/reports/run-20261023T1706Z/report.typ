#set page(paper: "a4", margin: 14mm)
#set text(font: "DejaVu Sans", size: 9pt)
#text(size: 17pt, weight: "bold")[Held-out balanced index-calculus run]

Observations only; independent review determines any performance claim.

EXP-ICPERF-6c546e / H-ICPERF-a2284c / RUN-ICPERF-d566af

#image("measurements.svg", width: 100%)

#text("162 completed workers; 54 pairs. Derived geometric ratio 1.1606; clustered 95% interval [1.1268, 1.1977]; A/A factor 1.0442. Frozen numerical gate met; not an independent verdict.")

#text("Nine unseen public curves: bits12/14/16; curve seeds3/4/5; solver seeds0/1; three repetitions, m2, small_x, mitm, scalar decomposition, harvest off, window4. Each arm occupies every slot once within each exact target cell; all six permutations occur. First confounded grid is retained separately.")

#text("Timer: entire native solve, including per-solve setup, misses, elimination and final verification. Startup/imports, public-instance generation, telemetry, hashing and independent checker excluded. All failures would be retained; none occurred. Arithmetic and schedule checkers passed; wrong-log, zero-advantage and original middle-slot controls rejected.")

#text("Environment bound before run: 166 dependency entries, CPython3.12.14, AMD EPYC 9V74 80-Core Processor, five visible CPUs. Every worker pinned to CPU0; per-arm load and process CPU context retained. Context is not proof of host-wide isolation. RSS28.37–29.87 MiB; coordinate payload304–440 bytes excludes Python overhead.")

#text("Source e9f89202f5977ad5e39cc42311cfa781a24d41f7; raw snapshot ed0d34e276149b30d137448f22b0fb17cdd4cf28. Command, seeds, exact parameters, provenance and limitations:report.md. One-host toy scalar workload only; no default/vectorized, rho, production-curve, asymptotic or official-frontier statement.")
