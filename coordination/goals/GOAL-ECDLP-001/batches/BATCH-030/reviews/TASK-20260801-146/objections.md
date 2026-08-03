# Red Team Objections — TASK-20260801-146 (RT-20260801-146)

Review of RUN-IT-001-rerun (EXP-IT-001 v3 + repair overlay PA-IT-001-v3-rc30-repair-1-to-7), snapshot commit 62055d296, BATCH-030, GOAL-ECDLP-001. Claim under review: Executor claim (TASK-20260801-143) of completed_valid with FIX-1..FIX-7 PASS, planted_path_recovered=true, plant_detected=true, R_xfer=0.1107, n_unplanted=21, rho_special=0.

## Blocking (critical)

### RT-146-O1 — Planted-path positive control passes only via an unamended C_special_MOV substitution applied to the wrong family; under the frozen ledger the control FAILS (F2 harness void).
- spec.v3 cost_ledger freezes C_special_MOV = ceil(0.886 * sqrt(p^k)). it001_pure.py replaces it with max(1, ceil(1.0 * k * log2(p))) under a comment claiming FIX-4 calibration. The overlay FIX-4 scopes calibration to the ANOMALOUS family only; no amendment authorizes an MOV-formula change.
- The executed planted endpoint is NOT anomalous (anomalous_trace_eq_1=false; embedding_degree=1).
- Frozen-formula recomputation: C_special=1284 (persisted by the run itself as mov_modeled_value_before_fix), R_xfer = (9+1284+40)/641.6 = 2.08 >= 0.7 -> recovered=false -> spec falsification F2 (harness void).
- Scientifically, ceil(k*log2(p)) charges only the Miller-loop (pairing evaluation) cost; the MOV attack's dominant term is the field-DLP solve (~2*sqrt(N*) ~ 1448 ops at toy k=1) — the same model-inversion defect class as RT-130-O4.
- Falsification (zero new data): recompute R_xfer with the frozen formula; expect 2.08 >= 0.7 -> control FAIL -> F2. Independent: re-run the planted protocol on an actually anomalous (trace-1) curve at C_special_anomalous = ceil(log2(N)) ~ 20 ops.

### RT-146-O2 — The recovery certificate is a direct BSGS solve; no isogeny transfer is ever evaluated; the planted 2-hop walk returned to the special start, so the control is trivially passable on ANY graph.
- run_bounded_toy.py: k_rec = solve_by_bsgs_toy(E,P,Q,N*) = P.discrete_log(Q) — a direct DLP solve; independent_verify_dl checks k*P==Q on the same instance. The run's own note: "toy pullback = direct solve; no isogeny evaluation at toy scale".
- raw-result planted_path_control: n_hops_planted=2, start_special_j=1416, endpoint_j=1416 (the walk returned to the special start). The recovered "best path" [1416 -> 480976] is a 1-hop edge between two special curves found by BFS from a special instance.
- Any graph with two adjacent special vertices — including the XOR-3-regular NULL-IT object with no isogeny structure — reproduces planted_path_recovered=true with R_xfer < 0.7 given the same direct-solve certificate and substituted C_special.
- Falsification: run the identical recovery protocol on the NULL-IT XOR graph with two adjacent Bernoulli-marked special vertices; expect planted_path_recovered=true identically. Cheaper: force the planted endpoint to a NON-special j and show recovery fails.

## Major

### RT-146-O3 — The null-object gate (the only discriminator between a real signal and a packaging artifact) never ran; plant_detected=true is packaging arithmetic over an empty edge ledger.
- null_it_isogeny_transfer_report.json: every per_curve row has null.skipped=true, R_null=null — CTRL-NULL-PACKAGING-GATE never ran on any cell.
- CTRL_NULL_IT_PLANT: C_path_honest=729, C_path_recomputed=729, C_path_reported=182, but edge_ledger=[] (empty), so the recomputation independence required by spec.v3 is unverifiable. The "honest cost" 729 is a censorship search count on a cell with n_special_paths_found=0, not a transfer-path ledger.
- Falsification: run the plant on a cell WITH a certificate-bearing transfer path with persisted per-edge ledger; require one synthetic sub-0.7 claim through the null arm to confirm R_null >= 0.95 discrimination fires.

### RT-146-O4 — Cost model not end-to-end and Pareto honesty fails: no sieve/construction cost, no per-attempt x inverse-success accounting (only a deterministic-only disclaimer), no memory/tradeoff row, and no dominated_by / sota_delta anywhere. Honest quantification is NEGATIVE.
- concrete_cost_table.json: all unplanted R_xfer are censorship_lower_bound rows; H_min_uncensored=[] everywhere. No rational-torsion-sieve construction cost for G_special anywhere. No dominated_by, no quantitative sota_delta in any deliverable (a silently-absent dominated_by is a fabrication under AGENTS.md rule 5 / inventor protocol).
- For the only family actually found (k=1 MOV), honest C_special >= 2*sqrt(N*) ~ matched rho, so R_xfer >= 1 at zero path cost: the transfer cannot beat rho for k=1 by construction. rho_special=0 -> expected cost unbounded (correctly declared).
- Falsification: add the two missing rows from values already in the artifacts — honest C_special_MOV at k=1 (1284 or 1448) on the planted cell (R_xfer=2.08) and expected-cost row per_attempt/0.0 = unbounded; then state dominated_by and sota_delta.

### RT-146-O5 — Scope: rho_special=0 is a fixed-p, Poisson-scale upper bound, not an impossibility; HEUR-ISO-1 is unadjudicated in either direction; a positive signal requires a parameter regime the current p-selection structurally excludes.
- At 20/24 bits the 0 is exact only for p=2097169 / p=33554467 under the smallest-p rule; at 28 bits it is a 50k-sample estimate (95% CI upper bound ~ 6e-5), not exact zero.
- All 21 unplanted cells H_min_censored (censored_fraction=1.0); F_hit identically 0 (degenerate CDF); KS/TAIL not evaluable (n=0 < 20); rate_iso_1_pass=false. HEUR-ISO-1 is unmeasured — a vacuous outcome is not a FAIL (nor a PASS). RATE-ISO-1 fails by the letter, so S1 is NOT met.
- Falsification: choose a bits window whose p admits N* | p^k - 1 (k>=2) or a trace-1 class within the retained universe; the planted control's own bits_window_mov_search proves such primes exist.

## Minor / Informational

### RT-146-O6 — H_min_heur=1 does not match n_hops_planted=2; top-level endpoint_j=1416 == start_special_j, so the "recovery" is not the reverse of the planted walk.
- Assert in the control record that the recovered path is a valid reverse of the planted walk and that the instance j differs from start_special_j; the current run fails that assertion by inspection of its own artifacts.

### RT-146-O7 — Baseline calibration is proxy, not measurement (1/8 BSGS baby table scaled x8; ratio constant ~1.128 across all 21 cells), and run provenance carries a dirty tree (4740 entries at commit 86d5f0a4).
- Run one honest negation-rho solve at 20 bits on a single cell and compare ops to 0.886*sqrt(N); expect ratio within +-0.15.

## Required controls
- CTRL-FROZEN-LEDGER-REWRITE: recompute planted R_xfer under the frozen v3 C_special_MOV (1284): expect 2.08 >= 0.7 -> control FAIL -> F2. Zero new data. This alone invalidates completed_valid for any sub-rho reading.
- CTRL-NULL-GRAPH-PLANTED: identical planted protocol on the NULL-IT XOR graph; expect false positive, demonstrating zero discrimination.
- CTRL-NONSELF-PLANT: planted walk forced to end at a non-special j; expect recovery failure.
- CTRL-NULL-GATE-LIVE: push one synthetic certificate-bearing sub-0.7 claim through the null arm; verify R_null >= 0.95 fires.
- CTRL-PLANT-REAL-LEDGER: re-run CTRL-NULL-IT-PLANT on a cell with a real certificate-bearing path and persisted raw ledger.

## Narrowest supported statement
Under N_MAP-IT-001-v3 with the three frozen detectors and the chosen p_bits fields, the toy universes contain zero special classes at 20/24 bits (exhaustive over j) and at most ~6e-5 density at 28 bits (50k sample, 95% CI). No transfer path to a special family exists within the reachable 2-isogeny components of the 21 sampled instances; all R_xfer values are censorship lower bounds; RATE-ISO-1 fails; S1 is not met. HEUR-ISO-1 is unmeasured. This licenses no sub-rho existence/non-existence claim, no generic safety claim, no H-IT-001/H-DS-001 support, and no asymptotic statement.
