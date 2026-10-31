#set page(paper: "a4", margin: 19mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(justify: false)
#text(size: 19pt, weight: "bold")[Classical ECDLP: failed transport attempt]

EXP-ECDLP-956f81 / RUN-ECDLP-c8d9b0

GOAL-ECDLP-e70832 / H-ECDLP-6674c9

This report records observations only. No mathematical verdict or performance comparison follows from this pre-candidate failure.


#text(weight: "bold")[What ran]

#text("One trial requested and attempted; zero completed, one infrastructure failure, zero timed out. Source commit: 3982e1a7626c11b4b57db544cf9548f25d658af0. One VM was created. The first pinned-image metadata read raised AttributeError because Sandbox.open is absent in the installed Modal SDK 1.6.2. The candidate engine was never invoked. Linux / Python 3.12.14; requested VM configuration: 2 CPU, 12288 MiB. These resource values are requested, not measured.")


#text(weight: "bold")[Recorded scope and missing data]

#text("The native controller records 0 engine executions, collection_complete=false, no collected output files and termination_ack=null. Scientific validity is not_assessed. No scientific nonce, curve, target or workload was generated. Calibration, confirmation, controls, solver verification, references and analysis did not execute. Recovery rates, candidate query counts, sample distributions, CPU time and peak RSS are unavailable. Missing scientific quantities are not zero-valued observations. No candidate evaluator export rows are created.")


#text(weight: "bold")[Operational timing]

#text("Supervisor start: 2026-10-29T21:53:39.045750+00:00. Finish: 2026-10-29T21:53:40.757379+00:00. Derived difference: 1.711629 seconds (finish minus start), an operational supervisor interval only. No qualified algorithm clock or counter replay. Driver return code 1. Supervisor check_returncode=null; the check was not executed.")

#image("pipeline.svg", width: 100%)

#text(size: 8pt)[Actual recorded stopping point; the later cleanup event is labeled separately. No scientific comparison was available.]

#pagebreak()

#text(weight: "bold")[Separate later cleanup]

#text("The original native receipt remains byte-exact with termination_ack=null. Later fixed public transport probes used only the same existing VM, no candidate code, no new VM and no scientific draws. All five passed. The separate cleanup receipt records actual termination acknowledgement at 2026-10-29T22:02:50.903688+00:00, provider return code 137 after requested termination. This is neither a candidate exit nor a candidate memory-exhaustion finding.")


#text(weight: "bold")[Preservation and limitations]

#text("All 29 original native files were captured exactly and stored with complete GET and member hash verification. Native records: experiments/EXP-ECDLP-956f81/runs/RUN-ECDLP-c8d9b0. Capture/cleanup controls: coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-19ba16/failure-captures/RUN-ECDLP-c8d9b0. The observations establish a pre-candidate infrastructure failure only; they do not measure any algorithmic comparison. The old EXP/RUN will not be retried. Transport repair, additive metadata and a fresh admitted successor are separate technical work.")


#text(weight: "bold")[Reproduction command]

#raw("/workspace/classical-ecdlp-endpoint-reuse/runtime-20261028/bin/python tools/experiment_execution.py run --plan experiments/EXP-ECDLP-956f81/trial-plan.json --owner controlled-candidate-executor --epoch 1", block: true)

Complete exact driver argv, parameters, input hashes, failure and environment are in report.md, observations.json and the native launch/environment/command records.
