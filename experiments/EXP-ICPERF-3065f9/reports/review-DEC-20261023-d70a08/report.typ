#set page(paper: "a4", margin: 14mm)
#set text(font: "DejaVu Sans", size: 9pt)
#text(size: 17pt, weight: "bold")[Independent review: timing confounded]

#text("DEC-20261023-d70a08 / EV-ICPERF-9bf9d7 / EXP-ICPERF-3065f9 / RUN-ICPERF-842b51")

#image("measurements.svg", width: 100%)

#text("Observation: all 162 certificates and 18 target/relation/elimination streams reconcile. Exact full group counts over 54 solves: 213501 reference vs52935 candidate, including final verification. Target counts include cache setup:205608 vs45042.")

#text("Comparison: observed scheduled wall-time contrast1.08798; clustered95% interval[1.06137,1.11827]. C-target is NOT ISOLATED: candidate always runs in slot1; references only0/2. A/A endpoint reversal cannot test a middle-slot effect. Evidence remains preliminary; no causal wall-time advantage is promoted.")

#text("Decision: revise. Preserve verified algebra and exact finite operation counts; keep the reference default. Freeze a balanced successor EXP-ICPERF-6c546e on unseen curve seeds3/4/5, with every arm in every execution slot within each cell. Bind dependencies and record host/affinity context.")

#text("Scope: nine12/14/16-bit public toy prime-field curves; m2, small_x, mitm, scalar decomposition, harvest off. One host; no vectorized-baseline, production-curve, rho, asymptotic or official-frontier result. Review owners TASK-20261023-5301b1 and TASK-20261023-18b489; independence checker passed. Detailed evidence and review provenance:report.md.")
