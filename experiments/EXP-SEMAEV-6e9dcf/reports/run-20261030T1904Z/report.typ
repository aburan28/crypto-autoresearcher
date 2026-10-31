#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
#set heading(numbering: none)
= EXP-SEMAEV-6e9dcf: run observations
#text("RUN-SEMAEV-0e5876 | H-SEMAEV-94dab2 | GOAL-ECDLP-001")

#text("This report describes execution only. No mathematical conclusion, performance advantage or hypothesis verdict is inferred.")

== Outcome
#text("One frozen trial launched; zero output-validated trials; one infrastructure error; zero watchdog timeouts. Both arms exited 1 because the launch environment lacked NumPy. The checker was not executed. Comparison and both arm result objects are null. The certificate is not established.")

#image("diagram.svg", width: 100%)
#text("Diagram of this single failed trial: no comparable mathematical measurements exist to plot. Source: execution-receipt.json, raw-result.json and both arm stderr logs.")

== Execution and scope
#text("Cell mtic-010b. Both legacy and repaired s4_expr arms were launched concurrently using the frozen parent implementation and archived seeds/instances. Dependencies: parent RUN-SEMAEV-2a8498 (mtic-007) and RUN-SEMAEV-fcd67c (mtic-008). Controls: CTRL-LEGACY-REPRO, CTRL-ARM-FINGERPRINT, CTRL-REEXTRACT and CTRL-IMMUNE-BY-IMPORT. No overall control verdict is available from this failed trial.")

#text("Code commit: f1a804657b38be2222bc2414dd8bedc896eeb47f. Python: 3.11.17. Platform: linux. Driver manifest dirty flag: false; architecture x86_64; 32 logical CPUs. CPU time is not reported. Driver-recorded wall time: 66.116450548172 seconds; this differs from the supervisor interval below. Native plan SHA-256: 6fe1fc2c2156f451267a95b5744a4c5518c1e76a3c83e0277ca9737a29838599.")

#text("Recorded start (UTC): 2026-10-30T19:04:16.761191+00:00; finish: 2026-10-30T19:05:25.528039+00:00. Derived elapsed interval: 68.766848 seconds (finish minus start; includes supervisor overhead). Frozen limits: 5400-second watchdog, 8192 MB, one trial, two arm workers.")

== Exact command and records
#text("Supervisor: uv run --offline --no-project --with 'PyYAML>=6.0' --with sympy==1.14.0 --python 3.11 python tools/experiment_execution.py run --plan experiments/EXP-SEMAEV-6e9dcf/trial-plan.json --owner executor-run-20261030-01a179ee --epoch 2")

#text("Trial argv is preserved verbatim in launch.json and command.txt; data.json embeds the launch record and receipt. Raw directory: experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/.")

== Failure and preservation
#text("Both stderr logs report ModuleNotFoundError: No module named numpy at run_mtic.py line 35. The executor selected an environment with PyYAML and SymPy but omitted the NumPy import dependency. No frozen source or plan was changed, and this attempt was not retried. The first supervisor admission was refused before trial creation because the local origin tracking ref was stale; an exact branch fetch resolved that admission issue.")

#text("Sources checked: frozen specification.yaml and trial-plan.json; DEC-20261019-ebf1dc; TASK-20261019-212d85; parent launch.py and worker.py. These authorize a one-trial successor and preserve earlier interrupted attempts. No new literature or novelty claim is made. Raw measurements, checker results and scientific conclusions remain unavailable.")

