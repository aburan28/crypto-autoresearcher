# EXP-CERTBIN-ec9d83 Stages 0–1

## Observation

RUN-CERTBIN-004f53 is the Stage 0 freeze. Its receipt status is `output_validated`, `check.stdout.log` is `PASS`, and `raw-result.json` records outcome `O-FREEZE`. The frozen-table SHA-256 is `8cdc12335fd1bcafed42e3f114ebb9506a2b268cc2b2e186d27b6f978b9fc7fa`.

RUN-CERTBIN-664bda is the Stage 1 dual-route comparison. Its receipt status is `output_validated`, `check.stdout.log` is `PASS`, and `raw-result.json` records outcome `O-IDENTITY`, with `implementations_agree`, `matches_printed`, and `pair_gib_ok` true. `certificate.kind` is `none` and `verified` is true. `n_ge_131_solve` is false. Both manifests name code commit `694fac27c5c39b5e8c8d189b661ba8af62e87c4f` with `dirty: true`.

The Stage 1 raw cells, one row each, all have `routes_agree` true:

| row | M_k | M_pair | R_mem | pair_gib |
| --- | --- | --- | --- | --- |
| n83-m3 | 52544464 | 1380460322251416 | 3.806300199509128e-08 | 20570461.78357923 |
| n83-m4 | 380881628445 | 380880755655 | 1.0000022915045905 | 5675.565535649657 |
| n131-m4 | 6390139590932159161 | 6390139587357207528 | 1.000000000559448 | 95220500042.3969 |
| n83-m7 | 25179796775 | 14175150 | 1776.3337089907338 | 0.2112261950969696 |
| n131-m7 | 39274997426201940 | 190756570278 | 205890.66666990466 | 2842.494402498007 |

The n83-m7 raw cell also records complementary `C(B+3, 4) = 33539489304300` and `fold_gib = 375.20821057260036`.

A blind recomputation with `k = floor(m/2)`, `M_k = C(B+k-1, k)`, `M_pair = B(B-1)/2`, `R_mem = M_k/M_pair`, and `pair_gib = M_pair*16/2^30` produced those same integers and the same float ratios. It was written into the review report before any file under `implementation/` was opened.

A later Stage 1 replay from a copy at `/tmp/review-certbin-ec9d83` into `/tmp/review-certbin-ec9d83-run` printed outcome `O-IDENTITY` and exited 0. `check.py` on that directory printed `PASS` and exited 0. The repository directory `experiments/EXP-CERTBIN-ec9d83/runs/` gained no new files.

## Comparison

Each recomputed `M_k` and `M_pair` equals the Stage 1 raw cell, and the two route floats in each cell are equal.

Degree-83 m=7 `R_mem` is 1776.3337089907338. The absolute difference from 1776.33 is 0.0037089907338, which is at most 0.1.

Degree-83 m=4 `R_mem` is 1.0000022915045905. The absolute difference from 1.000002 is 2.915045905e-7, which is at most 5e-7. The margin under 5e-7 is 2.084954095e-7.

Degree-83 pair-GiB values 20570461.78357923, 5675.565535649657, and 0.2112261950969696 match the printed figures 20570462.6, 5675.6, and 0.211 at three significant figures: 2.06e7, 5.68e3, and 0.211.

The Stage 0 freeze tolerances hold on the remaining rows. For n83-m3 the absolute difference from 3.806e-8 is 3.00199509128e-12, at most 5e-11, and the relative difference is 7.8875330827143e-5, at most 0.0005. For n131-m4 the absolute difference from 1 is 5.59448e-10, at most 5e-7. For n131-m7 the relative difference from 205890.7 is 1.6188247134346564e-7, at most 5e-7.

The four manifest source SHA-256 values equal the SHA-256 of the blobs of those files at `694fac27c5c39b5e8c8d189b661ba8af62e87c4f`.

The specification success sentence is the conjunction of route agreement, the three degree-83 pair-GiB figures, the m=7 band of 0.1, and the m=4 band of 5e-7. Those four comparisons hold. The hypothesis outcomes `O-COUNTEREXAMPLE`, `O-ARTIFACT`, and `O-IMPEDIMENT` stay unmet: the routes agree, the printed bands hold, and both receipts are `output_validated` with the freeze file present.

## Inference

The frozen success sentence licenses `O-IDENTITY` on the five printed-B rows. That licenses support of the integer identity `R_mem = C(B+k-1, k) / (B(B-1)/2)` at those printed `(degree, m, B)` values, at strength preliminary, claim tier toy, and proof status empirical_only.

`H-CERTBIN-e50e56` moves from approved to supported on that identity. `EXP-CERTBIN-ec9d83` moves from approved to analyzed. Degree 131 is closed-form arithmetic at a printed B.

## Limitation

The campaign is one deterministic dual-route package. Preliminary strength on that package does not meet the replicated or strong promotion gate, so no knowledge finding is promoted. `HEUR-CERTBIN-e50e56-H1` remains untested. This package authorizes no Stage 2. `certificate.kind: none` records the integer-identity check. The tested scope is the five printed-B rows in the frozen table. Degree-131 m=3 and m=10 stay outside the contract.
