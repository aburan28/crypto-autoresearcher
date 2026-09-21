# Cluster 01 — BASELINE — Draft Goals G30-001..G30-003

Filename note: the assigned full-cluster-description filename exceeded the filesystem
name limit (ENAMETOOLONG, 255-byte component cap, multi-byte chars); this file uses the
shortened name `cluster_01_BASELINE_G30-001..003.md`.

Source cartography: coordination/goals30/cartography_closed.md, cartography_active.md, cartography_harness.md (all 2026-07-23).
All three goals are measurement/infrastructure goals that protect the program from the two recurring failure modes of the closed record: uncharged-cost partial wins (closed failure reason #3) and adverse-scaling claims presented as crypto evidence (closed failure reason #7, AGENTS.md rule 7).

---

## G30-001: Fully-charged group-op-equivalent cost standard for algebraic attack stages

- **Cluster:** 01 BASELINE
- **Type:** infrastructure
- **Long-term chain:** Any claimed sub-rho algebraic attack (open frontier KN-OPEN-001/003/006, PO-transfer-007, RT-1476-SUBRES-A1) is only meaningful against a fully charged comparator. This goal enables a certified cost model, which gates every future end-to-end attack claim, which gates whether any crypto-relevant break claim can ever be accepted instead of collapsing like the closed 5x–115,000x-rho partial wins.
- **Mechanism:** Commission harness module `costmodel.py` implementing an explicit group-op-equivalent (GOE) ledger: one GOE = one prime-order group addition as executed by the harness rho implementation on the same instance. Convert Gröbner-basis seconds, sparse/structured LA work, relation collection, descent, memory, and preprocessing into GOE via per-machine calibration constants measured on fixed toy workloads, with each constant carrying a measured error bar and a conservative rounding rule (all conversions rounded UP by 1 sigma). Validate the model by replaying existing immutable runs (RUN-SEMAEV-{rho,gb}-b{8..14}-s{1..4}, EXP-SEMAEV-001) and checking that the GOE-converted cost of the S_3 decomposition path lands within the predicted GOE band of its wall-clock-derived estimate.
- **Quantified prediction:** GOE conversions reproduce measured rho group-operation counts within ±15% at 8–14 bits; the charged S_3 decomposition path costs ≥10x matched rho on the existing 16-run corpus (consistent with closed-record oracle floors >100x rho at slightly larger sizes), i.e., the model does not manufacture an artificial algebraic win.
- **Test boundary / scope:** Toy tier only: prime fields 8, 10, 12, 14 bits (optionally extended to 16 bits); seeds 1–4; factor base size 14 (matching EXP-SEMAEV-001); rho = existing Teske 32-branch walk; algebraic side = existing semaev.py S_3 ideal plus one sparse-LA microbenchmark. No claims above 16 bits.
- **Primary metric:** GOE conversion error |GOE_estimated − GOE_measured| / GOE_measured on held-out calibration cells. / **Secondary metrics:** charged-cost ratio algebraic/rho per cell; calibration-constant variance across repeated runs; memory charge (peak RSS → GOE) sensitivity.
- **Controls:** Matched rho baseline on identical (curve, seed, subgroup) instances from harness/rho.py; calibration cells and validation cells are disjoint seeds (seeds 1–2 calibrate, 3–4 validate); trivial-ideal control retained to separate "no decomposition" from cheap solve; no equating op types without the published conversion constants.
- **Falsification criteria:** Conversion error >25% on held-out seeds at any bit size in 2+ consecutive cells, or calibration constants non-stationary (drift >2x across reruns on identical workload) — the cost model is rejected as unreliable, not patched in place.
- **Negative-outcome value:** If GOE conversion cannot be made reliable at toy scale, the Coordinator freezes ALL end-to-end cost-ratio claims program-wide (no attack probe may report "x× rho" numbers) until a revised model passes — this directly prevents recurrence of closed failure reason #3 (full charging kills partial wins discovered only post-hoc).
- **Budget:** wall_clock 8h, memory 8 GiB, max_runs 40
- **Stopping rule:** Stop when (a) validation cells (8 cells: 4 bit sizes × seeds 3–4, both rho and algebraic side) all report within ±15% GOE error, or (b) falsification triggers, or (c) budget exhausted with status inconclusive.
- **Harness dependency:** Capability gap #4 (end-to-end cost model converting Gröbner/LA cost into rho-comparable group-op equivalents + sparse/structured LA benchmark module) — must be commissioned; builds on existing runner.py manifest v2 (peak-RSS, wall/CPU already captured).
- **Claim tier:** infrastructure
- **Dependencies:** none

---

## G30-002: Corrigan-Gibbs–Kogan S·T² preprocessing/advice accounting gate

- **Cluster:** 01 BASELINE
- **Type:** governance
- **Long-term chain:** Fixed-curve preprocessing is the only generic route by which "advice" could undercut per-instance rho, and CGK gives the generic lower-bound frontier S·T² ≳ p for any preprocessing DLP method. This goal enables a machine-checkable gate that any preprocessing/amortization claim (including active direction A2 isogeny-class-amortized advice and any reverse-index/table amortization revival) must clear, which gates whether preprocessing ideas can ever contribute to a below-Shoup end-to-end break rather than re-crediting table work (closed failure reasons #1, #3).
- **Mechanism:** Implement `preprocess_gate.py` as a ledger-side validator: for any run claiming a multi-instance or fixed-curve advantage, it extracts (i) preprocessing cost S in GOE (via the G30-001 cost model), (ii) per-instance online cost T in GOE, (iii) number of instances N actually solved, (iv) memory footprint. It then checks the fully-amortized per-instance cost T_eff = (S + N·T)/N against both matched rho (≈ c·p^{1/2} GOE) and the CGK-style generic floor implied by the measured S (an S·T²-vs-p accounting check at toy scale). The gate is exercised on a deliberate adversarial fixture: a rainbow-style precomputed table at 10–14 bits that wins per-instance online time, plus one fresh-window uniform control, to confirm the gate correctly classifies it as NO-GO once S is charged.
- **Quantified prediction:** The precomputed-table fixture shows online T ≈ 10–100x below rho while the charged T_eff ratio T_eff/rho ≥ 1 for all N ≤ 64 instances at 12–14 bits; the gate emits NO-GO with S·T² accounting within ±20% of the hand-computed frontier value.
- **Test boundary / scope:** Toy tier: 10, 12, 14 bits; seeds 1–4; N ∈ {1, 4, 16, 64} instances per curve from a seeded instance pool; advice restricted to curve-public data (no per-target leakage). No cross-curve advice claims (A2's toy-scale weakening is respected: cross-curve transfer is out of scope).
- **Primary metric:** Gate classification accuracy on labeled fixtures (adversarial-table = must-fail, matched-rho multi-instance = must-pass-neutrality). / **Secondary metrics:** S·T² accounting error vs hand computation; charged T_eff/rho ratio as function of N; memory charged vs manifest peak-RSS.
- **Controls:** Matched rho on identical instances with zero preprocessing; fresh-window uniform-instance control (anti-duplication rule iii: no selector without regime predictor + fresh-window uniform control); multiplicity crediting disabled (anti-duplication rule ii: each instance counted once); held-out seed 5 curve for final gate check.
- **Falsification criteria:** The gate passes the adversarial table fixture (false GO), or its S·T² accounting deviates >25% from hand computation in 2+ cells, or charging S flips fewer than expected classifications (gate insensitive to preprocessing cost).
- **Negative-outcome value:** If the gate cannot reliably distinguish charged from uncharged preprocessing wins at toy scale, no preprocessing/amortization direction (A2, reverse-index batching, PO-transfer-007 reusable-rank claims) may be dispatched as an attack probe — all such proposals are deferred to methodology repair first, removing an entire false-positive channel from the queue.
- **Budget:** wall_clock 6h, memory 8 GiB, max_runs 32
- **Stopping rule:** Stop when all labeled fixtures classify correctly and held-out seed-5 check agrees, or falsification triggers, or budget exhausted (status inconclusive).
- **Harness dependency:** Existing runner.py/manifest v2 (preprocessing runs already immutable) plus G30-001's `costmodel.py` for GOE conversion; new validator registered alongside tools/autoresearch_focus.py as a claim-gate (gap #4 dependent).
- **Claim tier:** infrastructure
- **Dependencies:** G30-001

---

## G30-003: Toy-to-crypto extrapolation and claim-tier-elevation protocol

- **Cluster:** 01 BASELINE
- **Type:** governance
- **Long-term chain:** The program's only honest route from toy experiments to a cryptographically relevant break is disciplined extrapolation; the closed record shows toy exponents n^1.19–n^1.69 vs required <n^0.5 (failure reason #7, "toy evidence MODEL-BOUND"). This goal enables a written, testable protocol for which trend statistics may be scaled and when a claim tier may rise, which gates every future tier-elevation decision, which protects the final break claim from being toy-scale overreach.
- **Mechanism:** Author `EXTRAP-PROTOCOL-001` (a review-required experiment record) plus a checker script `extrap_check.py`. The protocol pins: (a) the whitelist of extrapolatable statistics (per-instance GOE cost median and IQR across seeds, GOE cost exponent from ≥4 bit sizes with R² and residual diagnostics, memory exponent) and the blacklist (best-run values, single-size ratios, uncharged components, dreg proxy as d_reg); (b) minimum ladder: ≥4 bit sizes spanning ≥6 bits with ≥4 seeds per size, plus the 40–64-bit curated-table ladder (harness gap #6) before any "medium" tier elevation; (c) tier-rise rule: claim_tier may rise one level only if the fitted exponent's 95% CI lies strictly below the rho boundary exponent AND the CI width is <25% of the point estimate AND all runs valid/certified. Validate the protocol by applying it to two historical datasets: EXP-SEMAEV-001 + the 16 fresh-seed runs (expect: tier stays toy) and the rho ladder 6–14 bits (expect: exponent ≈ 1/2 recovered, demonstrating the protocol can recognize a genuine 1/2 exponent when one exists).
- **Quantified prediction:** On the rho 6–16-bit ladder the protocol recovers exponent 0.5 ± 0.08 (95% CI) and permits internal "matches generic boundary" labeling; on the Semaev corpus it refuses any tier elevation (exponent CI does not clear the <0.5 boundary). Protocol decisions agree with hand analysis on 100% of the validation datasets.
- **Test boundary / scope:** Measurement scope: bit sizes 6–16 for the rho ladder (extendable to curated 24–32-bit tables if gap #6 lands), seeds 1–4, existing immutable runs reused wherever available. The protocol text itself governs future claims but its validation stays at toy tier.
- **Primary metric:** Protocol-vs-hand-analysis agreement rate on validation datasets. / **Secondary metrics:** recovered rho exponent and CI width; Semaev exponent estimate with CI; number of statistics rejected by the whitelist filter per dataset.
- **Controls:** Matched rho ladder as the positive control (known-true exponent 1/2 must be recovered); Semaev corpus as the negative control (must NOT elevate); all statistics computed from run manifests only (no hand-edited numbers); protocol frozen before seeing validation outcomes (sealed-schedule discipline per GOAL-ECDLP-001 next_action).
- **Falsification criteria:** Protocol recovers a rho exponent CI not containing 0.5, or elevates the Semaev corpus tier, or whitelist/blacklist distinction cannot be implemented mechanically (requires human judgment per case) — protocol rejected and redrafted as a new record.
- **Negative-outcome value:** If no mechanical extrapolation rule validates, the Coordinator adopts a standing rule that NO claim tier ever rises above toy within this program until a successor protocol passes — closing the "toy result presented as scaling evidence" decision path entirely rather than adjudicating case-by-case.
- **Budget:** wall_clock 6h, memory 4 GiB, max_runs 24
- **Stopping rule:** Stop when both validation datasets produce protocol verdicts matching hand analysis, or falsification triggers, or budget exhausted (status inconclusive).
- **Harness dependency:** Existing runner manifests (exponent fitting from recorded GOE/seconds); optionally harness gap #6 (40–64-bit curated tables) for the extended ladder — not blocking for toy-tier validation; requires G30-001 GOE conversion for the algebraic-side statistic.
- **Claim tier:** infrastructure
- **Dependencies:** G30-001
