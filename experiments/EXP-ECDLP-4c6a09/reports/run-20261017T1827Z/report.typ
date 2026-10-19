#set page(paper:"a4", margin:16mm)
#set text(size:9pt)
= Frozen-grid run observations
#text("Observations only. This is a descriptive run report, not hypothesis review, scientific promotion, or an execution-proof claim.")

#text("Experiment EXP-ECDLP-4c6a09; goal GOAL-ECDLP-001; run RUN-ECDLP-e89532. Source-at-launch commit aefcb291f54dd1cb1e59487a70c11b910ec28b06. All source bindings and literal argv are in environment.json and command.txt.")

#text("One frozen full-grid trial produced 1395 saved cells. Producer return code 0; checker return code 0; supervisor outcome invalid_output. Detail: manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'.")

#text("Start 2026-10-17T18:27:36.970924+00:00; finish 2026-10-17T18:46:07.605308+00:00. The producer manifest records available wall timing. CPU usage, detailed hardware, and dirty-tree state are not recorded by this legacy supervisor. The exact memory/watchdog envelope and seeds are in the frozen trial plan and command.txt.")

#image("observations.svg",width:100%)

#text("Execution-time checker output (observed): {\"checked\": {\"cells\": 1395, \"sample_points\": 2367, \"shapes_checked\": 4, \"torsion_bound_cells\": 24, \"witnesses\": 796}, \"experiment_id\": \"EXP-ECDLP-4c6a09\", \"ok\": true, \"problems\": []}")

#text("Rank descent was explicitly skipped by the producer; independent generator sets and rank gains are not certified. New non-torsion-point counts are not substituted for rank. The recorded gamma values are finite covering diagnostics, not an ECDLP complexity exponent.")

#text("All cells, controls, failed/censored outcomes and null values remain in raw-result.json. A checker pass does not independently review every mathematical claim. Schema/accounting corrections preserve the original supervisor receipt and cannot retroactively change invalid_output into output_validated.")

#text("Graph plots recorded observations only. No performance or attack-cost claim is made. Scientific source digests are frozen at launch; unrelated control-plane commits while the process runs do not change those source bytes. Producer end-of-run git HEAD, if different, is separate from execution source identity.")

#text("Artifacts: ../../runs/RUN-ECDLP-e89532/ (launch.json, environment.json, command.txt, raw-result.json, manifest.yaml, execution-receipt.json, stdout/stderr and checker logs). No deployed-key recovery or NFS sieving occurred.")