#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= EXP-CMFB-cea1d2: run observations
#text("RUN-CMFB-2373be | H-CMFB-9b2eed | TASK-20261015-1c0251")

#text("Execution observations only. The output is invalid under the native manifest schema; no hypothesis verdict or mathematical result is inferred.")

== Recorded outcome
#text("Eight frozen trials requested. One launched: t1-inventory. Process exit code 0; native receipt status invalid_output; zero output-validated trials. The checker did not execute. Seven trials remain waiting on dependencies; none was launched. No timeouts. No retry or frozen source edit.")

#image("diagram.svg", width: 100%)
#text("Diagram of the recorded execution and admission failure. No comparable validated measurements exist to plot. Source: execution-receipt.json and the supervisor coverage output.")

#text("Native detail: manifest.yaml fails the run schema (tools/validate_ledger.py) and cannot be completed from publish-time facts: run.result.certificate.kind must be one of discrete_log|decomposition|none. The driver manifest has no result.certificate field. Driver status completed and official=true do not override the supervisor rejection.")

== Frozen scope and controls
#text("Family small-x coverage and qr_window scan-efficiency observations at toy sizes; three arms FAM, other D=-19 curves (N-A), random curves (N-B). K=200, seeds 7001 through 7010 preserved. The inventory used one worker and 2048 MB. Instrument, sensitivity and measurement controls depend on the rejected inventory and were not executed. No conclusion about the 53-bit pair or ECDLP attack cost.")

== Environment and timing
#text("Code commit 7769e4dbf015ff20c8c93514dab6a96201d0f753; driver dirty flag false. Python 3.11.17, NumPy 2.4.6, PyYAML 6.0.3; Linux x86_64, 32 logical CPUs. Exact environment, source hashes and argv are embedded in data.json and preserved in the run directory.")

#text("Supervisor start UTC 2026-10-30T19:11:19.697572+00:00; finish 2026-10-30T19:11:21.696539+00:00. Derived elapsed interval 1.998967 seconds = finish minus start. Unvalidated driver-reported telemetry: wall 0.927 seconds, CPU 0.77 seconds, peak RSS 64237568 bytes. These values describe this inventory process and are not accepted benchmark results.")

== Exact commands and custody
#text("Supervisor: uv run --offline --no-project --with 'PyYAML>=6.0' --with numpy==2.4.6 --python 3.11 python tools/experiment_execution.py run --plan experiments/EXP-CMFB-cea1d2/trial-plan.json --owner executor-run-20261030-01a179ee --epoch 2")

#text("Trial: python3 experiments/EXP-CMFB-cea1d2/implementation/driver.py --trial t1-inventory --run-dir /home/ec2-user/crypto-coordinate-current-base-20261028/experiments/EXP-CMFB-cea1d2/runs/RUN-CMFB-2373be")

#text("Records: experiments/EXP-CMFB-cea1d2/runs/RUN-CMFB-2373be/. Receipt artifact hashes retain manifest.yaml, raw-result.json, command/environment/launch records and logs. Checker logs are empty and check_returncode is null.")

== Sources and limitations
#text("Read: frozen specification.yaml, trial-plan.json, TASK-20261015-1c0251, and declared driver/count/curves/analyze/check and parallel module. Those define eight serial trials, frozen seed streams and dependent gates. No new literature or novelty claim is made. Raw inventory remains available but unvalidated; all comparison, control and scientific conclusions are unavailable. No research-state transition is made.")

