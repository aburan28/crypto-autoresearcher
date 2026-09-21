# EXP-JET-001 analysis — tangent-split summation (first-jet / dual-number decomposition) vs serial-S3 harvester

**Hypothesis:** H-JET-001 (candidate A1). **Valid run:** `RUN-JET-001-b` (`RUN-JET-001-a` retained, invalid — JSON
serialization defect, identical measurements; see its manifest). SageMath 10.9, git `9cbe004`, dirty tree.
Protocol: `specification.yaml` (frozen). m=3; ordinary prime-order curves; p ∈ {101, 211, 431} (+1009 stress);
seeds 20260717..20260722 (6 per prime, 24 instances); standard x-interval FB, B = {14, 20, 28, 40}.
Per candidate pair {P1,P2}: tangent screen = exact Cramer solve of the F_p-linear ε-block
(unknowns = jets (w, v3), RHS free in (v1, v2)) → C_lin, σ; exact zeroth-order test =
Sylvester resultant Res_u(S3(x1,x2,u), S3(u,X,x_R)) + Horner over FB_x → C_nonlin.
Charged cost = (B/p_m)·(per-candidate cost) + B² (LA toy proxy) + 0 (descent, complete FB), per the
frozen cost model. No stopping-rule deviations (8 s per invocation; cap 600 s). 2 runs used of 8.

## Measured numbers (per-size means over 6 seeds)

| p | n̄ | B | pairs | rel/pairs (p_m) | σ | σ_w | C_lin | C_nonlin | per-rel cost ratio (c/t) |
|---|---|---|---|---|---|---|---|---|---|
| 101  | 109.0  | 14 | 91  | 0.707 | 1.0000 | 0.0 | 113.83 | 388.40 | 0.7733 [0.771, 0.774] |
| 211  | 221.0  | 20 | 190 | 0.520 | 1.0000 | 0.0 | 113.82 | 436.32 | 0.7931 [0.792, 0.794] |
| 431  | 419.7  | 28 | 378 | 0.434 | 1.0000 | 0.0 | 113.94 | 502.39 | 0.8151 [0.815, 0.815] |
| 1009 | 1016.3 | 40 | 780 | 0.250 | 1.0000 | 0.0 | 113.96 | 599.06 | 0.8402 [0.840, 0.840] |

(ratio = classical per-relation cost / tangent-split per-relation cost at equal hit rate; σ = measured screen
survival; σ_w = fraction of relations with jet-degenerate solutions, the genuine-tangent-witness regime.)

Charged cost (F_p-ops, means): p=101: 7897 (c) / 10155 (t); p=211: 17319 / 21732; p=431: 33289 / 40661;
p=1009 (stress): 98661 / 117126. Relation yield per F_p-op is strictly lower for the tangent route at every size
(e.g. p=431: 8.64e-4 vs 7.04e-4).

## Controls

- **POS-1 (positive): PASS.** S3-chain vs sign-symmetric EC membership test: **0 mismatches in 3133 relation
  pairs / 9984 candidate pairs** (exact set agreement every pair). Every harvested relation carries an
  EC-verified witness (3133/3133). Branch-hit counts vs combinatorial law `pairs·4·B/((n−1)/2)`: ratio
  0.876–0.973 per size (inside the [0.5, 2] gate) — the standard harvester reproduces the ledger counting law.
- **NEG-1 (negative): PASS.** 200 EC-verified random non-relation tuples per instance (1200 total): screen
  survival 1.0000 = measured σ (screen has no filtering power to leak); full tangent-split pipeline claimed
  **0** relations on them; no true relation was killed by the screen (σ = 1 ⇒ no false negatives).
- Startup implementation self-checks: F1 expansion, jet partials vs symbolic derivatives, and the Sylvester
  determinant vs Sage's resultant all verified before measurement.

## Gate arithmetic (numbers, not verdict)

1. **Charged-cost exponent** (log-log OLS vs n, 18 points over the three gate sizes):
   classical slope **1.0616**, 95% CI [0.9984, 1.1249]; tangent slope **1.0240**, 95% CI [0.9615, 1.0865].
   (Stress-inclusive 24-point fits: 1.1197 [1.0750, 1.1644] / 1.0837 [1.0389, 1.1284].)
   The gate requires ≤ 0.49 with the 1/2 crossing excluded at 95%. Measured slopes are ≈ 1.0 with 0.49 and 0.5
   far below both CIs — the 1/2 crossing is excluded, but in the direction opposite to promotion.
2. **Per-relation cost ratio at equal hit rate**: 0.7733 / 0.7931 / 0.8151 (gate sizes), 0.8402 (stress).
   The gate requires ≥ 4× sustained; measured values are < 1 at every size (tangent-split is 16–23% *more*
   expensive per relation), sustained across all sizes and all 24 instances.

Neither promotion prong is crossed. The measured regime is the candidate's anticipated fatal obstruction #1:
**the ε-system is implied by the zeroth-order data** — σ ≡ 1 exactly, so `C_lin + σ·C_nonlin = C_lin + C_nonlin
> C_nonlin` for every candidate at every size (overhead C_lin/C_nonlin = 29.3% / 26.1% / 22.7% / 19.0%,
declining only because C_nonlin grows ∝ B via the Horner evaluations). The alternative witness regime is also
measured dead: σ_w = 0/3133 (no relation solution is jet-degenerate), so requiring genuine tangent witnesses
collapses the relation probability.

## Why the screen cannot filter (structural finding, verified per pair)

The ε-block is 2 equations in 4 jet unknowns (w, v3 | v1, v2), triangular with Cramer determinant
Δ = duF0·dx3F1. Its coefficients depend on the *unknown* zeroth-order solution (u, x3), so the only
a-priori-executable form is the formal consistency analysis; Δ was a nonzero polynomial for **every** candidate
(delta_deg = 3 in 100% of pairs), hence consistency for all tangent data and survival σ = 1. The linear block
carries no information beyond the zeroth-order equation — the information-conservation obstruction made concrete.

## Unexpected observations (recorded per rule 8)

1. Measured p_m (0.212–0.736) falls *below* the cost-model estimate B²/(2n) (0.754–1.036), by a factor
   1.18–3.66 growing with size — the aggregate law overestimates the per-pair hit rate at these toy sizes.
2. The EC-arithmetic membership route costs ≈ 116 op-equivalents/pair vs C_nonlin ≈ 388–599 for the
   polynomial S3-chain (context only — different operation types, per baseline discipline).
3. Charged-cost toy exponent ≈ 1.06 for the *classical* route itself (charged cost ∝ n at fixed B per size;
   LA/descent degenerate at toy scale) — the 0.5 bar is a crypto-scale asymptotic, not visible at toy sizes.
4. RUN-JET-001-a: JSON serializer truncated Sage RealNumber fields (ci95→[0,1], pos1b_ratio→0); run-a kept,
   marked invalid; run-b is the record of truth. An implementation failure, not evidence (rule 5).

## Scope

Toy prime fields p ≤ 1009 (≈ 2^10), m=3, x-interval factor bases, 6 seeds, op-counted schoolbook cost model.
A scoped negative over exactly this tested distribution; it does not address higher m, Weil-restriction
settings, or crypto-scale fields (rule 6, rule 7).
