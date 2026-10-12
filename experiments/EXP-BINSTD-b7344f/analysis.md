# Analysis — EXP-BINSTD-b7344f (TASK-20261001-8c14b5)

Review plan: `experiments/EXP-BINSTD-b7344f/review/review-plan.yaml`
(written before this analysis). Evidence: `EV-BINSTD-2d34cb`. Decision:
`DEC-20261001-817681`.

## Observation

- **Validity.** Six `completed_valid` runs: Stage 0 `RUN-BINSTD-08f0ab`;
  Stage 1 `03a5cd` (unsat 386), `23a5c3` (sat 100), `1c1589` (N-AFF62),
  `a67dbf` (random_dense 100); Stage 2 `d310bd`. Every manifest uses
  `certificate.kind: none`. Stage 0 artifacts exist under `stage0/` before
  Stage 1 summaries. No Amazon Bedrock. No CDCL engine invocation. No edits
  under `EXP-CERTBIN-e94b27/`. Infra exclusions: 0.
- **Stage 0 (modeled).** Producer table reports
  `all_nonpositive_within_1e-9: true` with
  `max_V_across_grid ≈ -0.0254`. Product-law yaml marks m∈{2,3} as
  `exceeds_rho: true` under formula `n + log2(m)` (see Limitation).
- **Stage 1 (measured).** Unsat CV ≈ 0.0111; sat CV ≈ 0.0104; both < 0.1
  (HEUR-H1 null). N-AFF62 CV ≈ 0.0306. Random_dense CV ≈ 2.84 (different
  shape; not pooled). Hill α ≫ 1 on PDP sets (indicative-only at these N).
- **Stage 2.** `icperf-distribution-schema.yaml` + `portfolio-hold.md`
  name **DO-1**. Explicit refusals: break, exponent, CDCL heavy tails,
  positive portfolio authorization.

## Comparison

- Blind re-derivation of V(β) on the frozen grid (formula only; no producer
  table): max_β V = {-0.0254, -0.0526, -0.0526, -0.0526, -0.0526} for
  ρ∈{1,1.5,2,10,100}; all ≤ 0 within 1e-9. Agrees with producer.
- CV recompute from reported mean/std: unsat 97074.7/8708720 ≈ 0.01115;
  sat 90888.2/8702769 ≈ 0.01044. Agrees with producer.
- HOLD-U BRIEF floors (recalled-as-pointer then checked against review
  YAML numbers already in-repo): m=3 → 2^68.58 vs rho 2^60.81
  (ratio ≈ 2^7.77 ≈ 218 > 1); m=2 → 2^89.25 > rho. Qualitative
  "floors exceed rho at m≤3" holds under HOLD-U numbers even though the
  Stage-0 yaml used a coarser `n+log2(m)` formula (Limitation).

## Inference

- HEUR-BINSTD-32867d-H0 (V(β)≤0 for ρ≥1) is **supported** at the modeled
  Stage-0 grid (claim_tier: observational / conditional on the concentrated-
  IC exponential-rho model).
- HEUR-BINSTD-32867d-H1 (W4 CV < 0.1 on RC-1 sat/unsat) is **supported** as
  a **controlled null** only — not CDCL evidence (proves-too-much refusal
  held).
- Portfolio hold at m≤3 under HOLD-U arithmetic is the designed DO-1
  outcome. Does **not** authorize CDCL portfolio runs or deployed races.
- Random_dense CV≈2.84 shows the instrument can report high CV on a
  different shape; it does not contaminate the PDP null.

## Limitation

- Stage-0 `product-law-floors.yaml` uses `floor_log2 = n + log2(m)`
  (~132 at m=3), not the HOLD-U BRIEF 2^68.58 figure. Qualitative
  exceeds-rho still holds; numeric table should be amended in a successor
  if BRIEF-exact floors are required in artifacts.
- Unsat N=386 vs requested 400 (archive shortfall disclosed).
- Sat arm uses first 100 archived F-S3 sat, not freshly planted.
- Same-session Coordinator-direct review (PD-1): strength capped at
  preliminary.
- IMP-no-cdcl remains: missing WDSat/CryptoMiniSat/CaDiCaL/Macaulay2 is
  infrastructure, not thin-tail evidence about CDCL.
- No n=131 attack run; no break; no exponent move.

## Claim boundary (explicit non-claims)

No deployed-curve break, no rho competitiveness win, no CDCL heavy/thin
tail claim, no positive portfolio V(β*)>0 at cryptographic scale, no
Amazon Bedrock.
