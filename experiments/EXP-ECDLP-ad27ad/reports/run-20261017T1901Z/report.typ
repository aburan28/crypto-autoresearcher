#set page(paper:"a4", margin:16mm)
#set text(size:9pt)
= Frozen-grid run observations
#text("Observations only. This is a descriptive run report, not hypothesis review, scientific promotion, or an execution-proof claim.")

#text("Experiment EXP-ECDLP-ad27ad; goal GOAL-ECDLP-001; run RUN-ECDLP-a5281a. Source-at-launch commit 82cc1338b982c401002f77dc4c19cb2c10a04989. All source bindings and literal argv are in environment.json and command.txt.")

#text("One frozen full-grid trial produced 90 saved cells. Producer return code 0; checker return code 0; supervisor outcome invalid_output. Detail: manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'.")

#text("Start 2026-10-17T19:01:24.555135+00:00; finish 2026-10-17T19:50:31.449523+00:00. The producer manifest records available wall timing. CPU usage, detailed hardware, and dirty-tree state are not recorded by this legacy supervisor. The exact memory/watchdog envelope and seeds are in the frozen trial plan and command.txt.")

#image("observations.svg",width:100%)

#text("Execution-time checker output (observed): {\"checked\": {\"cells\": 90, \"closure_pairs\": 6480, \"decomposition_triples\": 6480, \"exhaustive\": 18}, \"experiment_id\": \"EXP-ECDLP-ad27ad\", \"ok\": true, \"problems\": []}")

#text("Closure statistics are bounded finite measurements. Recorded one-standard-error bars omit uncertainty in the estimated density denominator and target clustering; no new significance test or asymptotic inference is made. The frozen hash and size thresholds use density about 2^-m, while the rotation arm unions rotated intervals; these controls are not generally density matched. Point sampling excludes O and y=0. These design limitations prevent treating this grid as a matched-density test or a DLP cost measurement. Unrelated software installation and builds overlapped this run on the same host; its wall time is not an isolated performance benchmark. See problems/rotation-factor-base-controls-not-density-matched.md.")

#text("All cells, controls, failed/censored outcomes and null values remain in raw-result.json. A checker pass does not independently review every mathematical claim. Schema/accounting corrections preserve the original supervisor receipt and cannot retroactively change invalid_output into output_validated.")

#text("Graph plots recorded observations only. No performance or attack-cost claim is made. Scientific source digests are frozen at launch; unrelated control-plane commits while the process runs do not change those source bytes. Producer end-of-run git HEAD, if different, is separate from execution source identity.")

#text("Artifacts: ../../runs/RUN-ECDLP-a5281a/ (launch.json, environment.json, command.txt, raw-result.json, manifest.yaml, execution-receipt.json, stdout/stderr and checker logs). No deployed-key recovery or NFS sieving occurred.")