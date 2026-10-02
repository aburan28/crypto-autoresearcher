# Analysis: EXP-BINSTD-9d1b8e (H-BINSTD-128789)

Review plan: `experiments/EXP-BINSTD-9d1b8e/review/review-plan.yaml`
(`REVIEW-BINSTD-9d1b8e-20261001`), written before this analysis.
Producer: TASK-20261001-0fc34d. Decision target: `replicate` preferred over
`support` for this first positive arithmetic / certificate package.

## Observation

**Validity (J1).** 9 run directories under `runs/` (plus `.gitkeep`);
execution_report lists the same 9 completed IDs, `invalid: []`,
`failed: []`. Every run has `manifest.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`. All
`status: completed_valid`, `termination_reason: completed`. Stage split:
1 Stage 0 (`RUN-BINSTD-1ee50c`), 1 Stage 1 (`RUN-BINSTD-82b5eb`), 7 Stage 2
(cells (4,5)/(4,7), pi2 aggregate, k1, null, degenerate, composite search).
Within `maximum_runs: 30`. No Bedrock in manifests/environments.
`break_claim: false` on every raw result and stage artifact.

Raw metrics agree with stage summaries: Stage 0 `all_rows_pass=true`; Stage 1
`a3_discharge_status=discharged`; Stage 2 ord matches 5 and 7 with
`certificate_verified=true`; controls and composite outcome match YAML
reports. Protocol deviations disclosed: SIGMA+Washington equivalents (not
Silverman full text); composite not-found-within-budget; (4,7) group order
via Weil recursion; manifests `dirty=true` at write time.

**Stage 0 (J2).** Five-row certificate (`all_rows_pass: true`):

| curve | k | gcd | t_odd | Weil | corrected ρ bits | frozen | Δ |
|-------|---|-----|-------|------|------------------|--------|---|
| c2pnb176v1 | 11 | 1 | true | pass | 78.097641 | 78.10 | <0.01 |
| c2pnb208w1 | 13 | 1 | true | pass | 93.980388 | 93.98 | <0.01 |
| c2pnb272w1 | 17 | 1 | true | pass | 125.784774 | 125.78 | <0.01 |
| c2pnb304w1 | 19 | 1 | true | pass | 141.706932 | 141.71 | <0.01 |
| c2pnb368w1 | 23 | 1 | true | pass | 173.565554 | 173.57 | <0.01 |

Dual inherited column present and labeled separately. `ord_mu_stated=k` via
k-prime + μ≠1 argument on each row. Attack-ceiling sentence present
(sqrt(k) rho vs up to k/k² IC). No break.

**Blind re-derivation (J2).** From audited `r_from_dump` and `k` alone,
`log2(sqrt(π·r/(4k)))` recovers producer recomputed bits exactly and stays
within ±0.01 of frozen expected on all five rows.

**Stage 1 (J3).** `a3_discharge_status: discharged`, `provenance: retrieved`,
`verified_by: TASK-20261001-0fc34d`. Sources: SIGMA 13 (2017) 083 (sha256
recorded) + Washington §2.8 (sha256 recorded); Silverman Appendix A full
text not opened (disclosed). a=0 on c2pnb208w1 marked red herring. Odd
traces on all five → ordinary → j≠0 under classification.

**Stage 2 (J4).** `ord(π_q)=5` on (4,5), `=7` on (4,7); certificates
`verified: true`. π₂ off-curve on 100/100 sampled x∉F₂ for both cells.
Controls: k1 embedding ord=1 / symmetry order 2 with negation; null
(50/50 π₁₆ off-curve) reports no endomorphism; degenerate (50/50 π₂
on-curve) detects π₂ endomorphism. Composite search:
`not-found-within-budget` after 64 curves (HEUR-H2 incomplete). Certificate
pass rate 1.0. No break.

## Comparison

Matches DO-1 (ledger-certified under stated scope): Stage 0 arithmetic
passes; Stage 2 prime cells return ord=k′ with π₂ failing; Stage 1
discharges A3 with retrieved provenance. Does not light DO-2 (Aut>ℤ/2),
DO-3 (ord≠k′), DO-4 (π₂ endomorphism on B∉F₂), or DO-5 (instrument
invalid). Composite miss matches HEUR-H2 falsification branch
(control incomplete, not (A) refutation) and the proves-too-much object
that forbids forcing proper-divisor ord.

Blind rho re-derivation agrees with producer. Null/degenerate polarity is
correct (proves-too-much objects hold). No path files break / attack-cost /
exponent.

## Inference

First Stages 0–2 package is **valid** and **supports** the scoped control-
certificate claim of H-BINSTD-128789 (DO-1 shape) at strength
**preliminary**: five-row gcd/Weil/corrected-rho arithmetic; A3 discharged
via retrieved Aut classification; toy ord(π_q)=k′ certificates with
passing controls. Standing preference and review-evidence rule: prefer
**replicate** over **support** on first positive arithmetic certificates.
Do not promote to KN-FIND. Composite nearby-object control remains
incomplete within budget 64. No break / exponent / attack-cost claim.

Official decision target: `replicate`; hypothesis `approved` → `analyzed`.

## Limitation

- First unreplicated observation; no independent validator/red-team (PD-1).
- Stage 2 toys only (dk′≤28 on prime cells; composite search dk′=24).
- Stage 0 is arithmetic recomputation on deployed identities — not a crypto-
  scale group-walk measurement; transfer of toy ord instrument to deployed
  k∈{11..23} is group-theory extrapolation, not empirical at those k.
- Silverman Appendix A full text not opened; A3 rests on SIGMA+Washington
  equivalents (disclosed).
- Composite search incomplete (HEUR-H2).
- Manifests recorded `code.dirty=true` at write time (pre-commit tree).
- Constant-factor bookkeeping only; time exponent unchanged (1/2).
- No break; no attack-cost; no exponent-moving claim.
