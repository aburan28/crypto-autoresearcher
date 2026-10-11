# RESULTS — EXP-BINSTD-591d28 Stages 2–3 (repl)

**Outcome:** `O-NEGATIVE`

Hypothesis: H-BINSTD-5fdceb. Approved: DEC-20261002-397fcd. Task: TASK-20261003-154cfb.

master_seed=2026100391; sample_e_budget={4: 262144, 5: 65536, 6: 16384}.

Stages 0–1 RESULTS.md and prior stage2/stage3/RESULTS-stages2-3.md left immutable.

## P1 fill-in (sampled e-space, Stage 2)

- l=4: est_spurious=None predicted=3072.0 e_hits=22/2621440
- l=5: est_spurious=1706.6666666666667 predicted=24576.0 e_hits=4/655360
- l=6: est_spurious=0.0 predicted=196608.0 e_hits=0/163840

## P3 random-subspace null

- l=4: dims=[4, 10, 17] P3_ge_poly=None est_spurious=None lift=1.0
- l=5: dims=[5, 15, 17] P3_ge_poly=True est_spurious=1747626.6666666667 lift=1.0
- l=6: dims=[6, 17, 17] P3_ge_poly=True est_spurious=6331024.905660378 lift=1.0

## P4 Frobenius arm

- Koblitz orbit_closure_ratio_mean=1.0
- Ordinary null mean=1.000134418850509
- p4_null_holds=True

## Scope

Stages 2–3 replication under artifact_tag='repl' / TASK-20261003-154cfb. No Magma/Sage/AUXIN/Bedrock. No ECDLP break. No exponent claim.
Amazon Bedrock: NOT SELECTED.
