# EXP-ECDLP-e36df2 independent review (Coordinator, TASK-20260912-85eb3e)

Reviewer: coordinator (single-reviewer; prior disclosed non-blind per handoff,
`blind_rederivation` performed genuinely before reading `pooled-summary.json`).

## 1. Blind rederivation (statistical_construction_validity, joint 1)

Performed BEFORE opening `pooled-summary.json`, `design_note.md` section 4b, or
`driver/pooled_summary.py`, reading only the 24 main `raw-result.json` files
(RUN-ECDLP-e36df2-001..024).

**n_agree sums (s_x):** 11+18+13+26 (curve0) +19+23+27+21 (curve1)
+16+26+21+26 (curve2) +16+23+20+25 (curve3) +27+25+17+18 (curve4)
+23+13+23+10 (curve5, positive control) = 487.

**n_agree sums (s_y):** 19+22+20+22 +20+14+17+25 +13+20+22+22 +10+23+20+22
+19+20+21+24 +16+17+21+22 = 471.

**n_agree sums (s_rand):** 16+19+17+19 +25+23+22+23 +21+17+26+25 +25+21+22+25
+23+22+20+21 +14+29+15+24 = 514.

**mu0 sums** (summed per-instance `mu_0_i`, using the section-specific value
where an exclusion occurred — curve2 and curve5 each have one x-excluded
instance, `n_excluded_x=1`, `n_excluded_y=0` throughout): mu0_x = 479.27839,
mu0_y = mu0_rand = 479.27926 (worked curve-by-curve: curve0 79.96290,
curve1 79.68713, curve2(x) 79.79556 / curve2(y) 79.79609, curve3 79.88146,
curve4 79.96858, curve5(x) 79.98276 / curve5(y) 79.98309).

Result: **rho_hat_x = 487/479.278 = 1.01611, rho_hat_y = 471/479.279 =
0.98273, rho_hat_rand = 514/479.279 = 1.07244.**

**Comparison against `pooled-summary.json`:** k_x=487/mu0=479.2783891773381/
rho_hat=1.0161109096446341; k_y=471/mu0=479.2792567294617/
rho_hat=0.9827256101464557; k_rand=514/mu0=479.2792567294617/
rho_hat=1.0724436594804208. Exact match on k for all three sections; mu0
matches to displayed precision (my hand sums land at 479.27839 / 479.27926,
identical to 10+ significant figures). **No mismatch.**

**CI construction check.** The CI is claimed exact-Poisson on k, divided by
mu0. I checked this via the chi-square/gamma-quantile relationship (Garwood
interval): L = 0.5*chi2^{-1}(alpha/2, 2k), U = 0.5*chi2^{-1}(1-alpha/2,
2k+2), alpha=0.05, applied to s_x (k=487, mu0=479.278). Using the
Wilson-Hilferty cube-root approximation to the chi-square quantile
(chi2_p(df) ~ df*(1 - 2/(9df) + z_p*sqrt(2/(9df)))^3):
- df=974 (=2k), z_0.025=-1.95996: term=1-0.0002281-0.029600=0.970172,
  cubed=0.913263, chi2=889.52, L=444.76 -> L/mu0 = 444.76/479.278 = 0.9280.
- df=976 (=2k+2), z_0.975=1.95996: term=1-0.0002277+0.029573=1.029345,
  cubed=1.090699, chi2=1064.52, U=532.26 -> U/mu0 = 532.26/479.278 = 1.1105.

Reported CI: [0.9278577, 1.1104949]. My hand approximation lands at
[0.9280, 1.1105] — matches to the precision the Wilson-Hilferty
approximation supports (~3-4 significant figures). This is a legitimate
exact-Poisson CI construction, not a mislabeled normal-approximation
interval. **Joint 1: PASSED**, both sub-checks (recomputed k/mu0/rho_hat,
and CI construction legitimacy).

## 2. Outcome classification (joint 2)

`specification.yaml`'s `success_criterion` (read verbatim, not paraphrased),
outcome (1) SUPPORTED requires ALL of:
- **Stage 0 passes (0 mismatches).** `stage0_regression_transcript.json`:
  `"total_checked": 1340, "total_mismatch": 0, "passed": true` (1340 =
  20 instances x 67 m-values, matching `m_range_tested`'s length).
  CONFIRMED directly from the artifact.
- **Positive control flagged 4/4 at m=2.** `frozen_positive_control_curve.json`
  lists primes [11987, 12007, 12011, 12037]. Runs 021-024's
  `flagged_x_degenerate_m` each show `"2": {"<own prime>": <prime-1>}` for
  exactly these four primes. CONFIRMED directly from raw artifacts (not from
  `pooled-summary.json`'s `m2_flag_rate` field alone, though that field
  agrees: "4/4").
- **s_rand's CI contains 1.** [0.98172, 1.16929] contains 1.0. CONFIRMED
  (both from my blind-rederivation CI check above and from
  `pooled-summary.json`'s own `s_rand_ci_contains_1: true`).
- **Both rho_hat_x and rho_hat_y CIs contain 1 and exclude >=3.**
  s_x: [0.9279, 1.1105] contains 1, excludes 3. s_y: [0.8960, 1.0756]
  contains 1, excludes 3. CONFIRMED.

All four named conditions for outcome (1) SUPPORTED hold on direct
inspection. No other of the four disjoint outcomes (FALSIFIED,
SPLIT/INCONCLUSIVE, INSTRUMENT INVALIDATION) is text-consistent with these
numbers. **Joint 2: PASSED — outcome is SUPPORTED.**

## 3. Chi-square periodicity robustness (joint 3), third instance

The design note's periodicity explanation (section 4c) was previously
spot-checked on p=14821/n=415 and p=12853/n=12958. I independently checked a
**third, different instance**: curve_idx=2, p=7487, n=413 (RUN-ECDLP-e36df2-011,
one of the larger chi-square statistics in the pool).

- s_x chi-square: statistic=2694328.0330037023, dof=7486.
  ratio = 2694328.033 / 7486 = 359.92 (7486*359=2687474;
  remainder 6854.03/7486=0.9155; 359+0.9155=359.9155).
- Predicted ratio N_i/n, using the actual post-exclusion trial count
  (n_total_after_exclusion for s_x = 148952) over n=413:
  148952/413 = 360.66 (413*360=148680; remainder 272/413=0.6586;
  360+0.6586=360.6586).
- Ratio of ratios: 359.9155 / 360.6586 = 0.99794 — within **0.21%**, well
  inside the ~15% tolerance the joint's `breaking_artifact` allows.

**Joint 3: PASSED.** The periodicity explanation for the inflated chi-square
statistic tracks N_i/n closely on a third, previously-unchecked instance,
not just the two already spot-checked in `design_note.md`.

## 4. proves_too_much objects

- **s_rand (null-object control).** CI [0.98172, 1.16929], confirmed to
  contain 1 by the same recomputation as joint 1 above, directly from the 24
  raw-result.json `s_rand.n_agree`/`s_rand.mu_0_i` fields (k=514,
  mu0=479.27926). The method itself is not inflating agreement counts.
  **Required check: CONFIRMED.**
- **positive_control_curve (engineered m=2 trap).** Confirmed 4/4 directly
  from `frozen_positive_control_curve.json`'s 4 listed primes cross-referenced
  against `flagged_x_degenerate_m` in RUN-ECDLP-e36df2-021..024's own
  raw-result.json files (not merely `pooled-summary.json`'s summary field).
  **Required check: CONFIRMED.**

Neither `failure_signature` condition is triggered. Instrument validity holds.

## 5. Inference

All three joints pass, both proves_too_much objects confirm instrument
validity, and specification.yaml's own success_criterion text supports
outcome (1) SUPPORTED on direct inspection of the four named conditions,
independently reconfirmed from raw artifacts rather than from
`pooled-summary.json`'s classification. The repaired test design (tautology
removed, resolution-matched sample size, cross-prime degeneracy screen,
two independently-coded contrast sections, null and positive controls, one
sensitivity check at mu0_target=40) makes claim (3) decidable at toy scale
for the first time, and the decision is: no systematic linearity is
resolvable at this resolution. This closes DEC-20260911-74c9dc's carve-out.

Both rho_hat_x and rho_hat_y independently land inside the pre-registered
band (CI contains 1, excludes >=3), agreeing in verdict — not a split. The
sensitivity check at mu0_target=40 on curve_idx=1 reproduces the same
qualitative verdict (s_x=1.004, s_y=0.891, s_rand=1.073, all CIs containing
1), which is the tail-consistency check this campaign's roadmap bias
requires for a heuristic-validation pairing (H1/H2 are heuristics, validated
here, not a complexity claim — `asymptotic_claim: null` throughout).

## 6. Limitations

- Toy tier only: 6 curves (5 original + 1 engineered), 24 (curve,prime)
  instances, primes in [2^10,2^14). No transfer to cryptographic scale.
- This is a null/absence-of-systematic-effect result, at toy scale,
  consistent with (not a new proof of) KN-TECH-73630e's uniqueness theorem.
  The theorem is assumed, not re-derived, here.
- `H-ECDLP-6a9479`'s own `analyzed` status and claim-3 `refine` status_note
  are unaffected and immutable; only `H-ECDLP-09125b`'s own status changes.
- No attack, no exponent claim anywhere: every tested multiple m is known to
  the generator.
- The chi-square diagnostic column in `pooled-summary.json` is a secondary,
  non-load-bearing diagnostic; its apparent "anomaly" is a mechanical
  artifact of short point order n << N_i (now checked on three distinct
  instances, all tracking N_i/n within ~15%), and does not affect the
  primary rho_hat statistic, which does not share the short period (m *
  d(s(S)) mod p cycles through p distinct values over n periods of m, per
  design_note.md section 4c's argument, itself unchanged by this review).
- The Stage 3 falsification-bar wording ambiguity (point-estimate>=3 vs.
  CI-lower-bound>=3) noted in `design_note.md` section 5 does not affect this
  outcome: both readings agree (`not_falsified_by_this_bar` for both s_x and
  s_y under both interpretations).
- Single-reviewer coordinator review (no mutual blindness); mitigated by a
  genuine blind_rederivation performed before consulting `pooled-summary.json`,
  per the handoff's stated mitigation.
