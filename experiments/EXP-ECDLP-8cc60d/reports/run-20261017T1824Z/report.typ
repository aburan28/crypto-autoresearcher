#set page(paper: "a4", margin: 16mm)
#set text(size: 9pt)
= G2 full-grid observations
#text("Observations only. This report does not review or promote any hypothesis. The supervisor recorded invalid_output; corrected metadata must not be described as retroactive output validation.")

#text("Experiment EXP-ECDLP-8cc60d; hypothesis H-ECDLP-281dd6; goal GOAL-ECDLP-001. Run RUN-ECDLP-2ac930. Launch commit 37315eaa955d97dfe4609e76e846d3f94c92de96.")

#text("One full-grid trial ran. The scientific process exited 0 and the checker exited 0. Its check log reports {\"cells\": 24, \"part_b_cells\": 12, \"part_c_rows\": 4, \"part_d_samples\": 96, \"rows\": 144} with no reported problems. The checker checks retained samples; that is not independent review of every row.")

#text("The saved output contains 1532 part-A rows in 24 cells, 12 part-B cells, 4 public-parameter part-C rows and 3 part-D boxes. Raw data, controls, seeds 1,2,3, exact argv, source digests and environment are retained under ../../runs/RUN-ECDLP-2ac930/. No sieving or key recovery was performed.")

#text("The required manifest schema failed: manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'. Scientific raw output and checker success remain observations, with output_validated coverage zero and scientific review absent.")

#image("embedding-ratios.svg", width:100%)

#image("small-order-counts.svg", width:100%)

#text("Start 2026-10-17T18:24:22.299947+00:00; finish 2026-10-17T18:26:21.473327+00:00. CPU usage is not recorded by this supervisor. The legacy producer manifest records its elapsed wall time. Dirty-tree state and detailed hardware are unavailable in this receipt. The process ran within the frozen 7,200-second / 1,024-MiB envelope.")

#text("Graph 1 plots the arithmetic ratio k/l from recorded rows; graph 2 plots already recorded counts and model means without new estimation. No confidence interval is inferred. Model mismatches stay visible and are not a scientific rejection. Part-D values are polynomial norm diagnostics, not completed DLP or sieve performance.")

#text("Artifacts: execution-receipt.json, launch.json, command.txt, environment.json, manifest.yaml, raw-result.json and all stdout/stderr and checker logs in the run directory. Missing structured run-manifest provenance is tracked by problems/ready-plans-lack-supervisor-archive-coverage.md. Original bytes remain immutable.")