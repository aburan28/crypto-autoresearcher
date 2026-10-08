# Analysis: EXP-BINSTD-6211a9 (H-BINSTD-4c31d1)

Review plan: `experiments/EXP-BINSTD-6211a9/review/review-plan.yaml`
(`REVIEW-BINSTD-6211a9-20261001`), written before this analysis.
Producer: TASK-20261001-a76432. Decision target: **inconclusive**
(preregistered DO-E / N2 fail) preferred over support on this first pass;
replicate successor under repaired N2 instrument.

## Observation

**Validity (J1).** 13 run directories under `runs/`; execution_report lists
the same 13 completed IDs, `invalid: []`, `failed: []`. Every run has
`manifest.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`command.txt`. All `result.valid: true`, `termination_reason: completed`,
`status: completed_valid`. Stage split: 4 Stage 0, 6 Stage 1, 3 Stage 2.
Within `maximum_runs: 30`. Required stage0/1/2 artifacts all present.
Amazon Bedrock not selected. Sampled Stage 1/2 decomposition certificates
report `verified: true` / `certificate_pass_rate: 1.0` where claimed.
Producer disclosures retained: Stage 2 `class_bit_proxy`, Stage 2 M3
`n_instances=8` (vs Stage 1's 20), `m_a=3` instrument_ceiling, N1 exact-GE
noise floor identically 0.

**Stage 0 (J2).** FIPS 186-4 Appendix D.1.3.1 re-derived from frozen corpus
PDF (`provenance: retrieved`, `verified_by: executor:TASK-20261001-a76432`);
sect163k1/r2 share field poly exponents `[163,7,6,3,0]`, `a=1`, cofactor 2,
order bit-length 163; differ in `b` only; `fips_single_variable_pair_verified:
true`. Symbolic P1: `b_only_in_degree_0`, `a_absent_from_S3`,
`symbolic_P1_pass: true`. M1: both b=1 cells weight 1; b-generic weights in
Binomial band; `instrument_ok: true`. Trimoska n=17: `#E=131174`, `r=65587`,
`Fb=[204,238]`, rho rounds 227/55 — exact integer match. Ownership note cites
`RQ-NISTBIN-06157b`.

**Stage 1 (J3).** Top-degree identity passes on all four cells. M3 aggregate
ranks (20 instances, dmax=3) identical across C-KK/C-GK/C-KG/C-GG at every
degree: d1=23, d2=254, d3=1794 (min=max=median). Blind re-derivation of
cross-cell disagreement from the published aggregate table: delta=0 at each
degree → `HB2_2_holds: true`. N1: M3_rank_delta_max=0, pass. Known-false:
`n_G_decompositions=0`, pass. Pattern verdict: `E1` with label
`observation only` / `E1_compatible_M3_invariant_M2_no_hard_a_zero`.
Measured M2 lambda_x: C-KK=C-GK=0.06067, C-KG=0.06214, C-GG=0.11284
(dual-cite RQ-NISTBIN-06157b). No hard a-contrast zero/non-zero separation
at even m_a=2 (E3 not triggered under this arity; known-false used odd m_a=1).

**Stage 2 (J4).** n=29 top-degree identity pass; `HB2_2_holds: true` on 8
instances (labeled reduction vs Stage 1). M2 uses `G_membership_mode:
class_bit_proxy` (and `class_bit_proxy_h_gt_2` where h>2). N2 two C-KG
draws: curve_1 h=822 r=653143 vs curve_2 h=2 r=268427513; fb_ratio=0.993
inside [0.85,1.18]; lambda_x_ratio=405.4 outside band →
`N2_agreement: false`. M5 C-KK: Fb abscissae 1031 measured; U≈17.78 derived;
rho modeled `sqrt(pi r/(4n))`. `no_deployed_curve_break_claim: true`.
m_a=3 instrument_ceiling. No M4 artifacts claimed in-scope.

## Comparison

- Stage 0 matches preregistered FIPS / P1 / M1 / Trimoska predictions.
- Stage 1 HB2-2 zero-variance prediction holds under dense Macaulay dmax=3
  at n=23,l=11,m_a=2 — consistent with DO-A's M3 half and incompatible with
  DO-C (no cross-cell rank disagreement).
- Stage 1 pattern E1 is producer-labeled observation only; M2 shows C-KK≈C-GK
  (orbit-blind algebra compatible) with C-GG highest yield — not a hard E3
  zero/non-zero split at even arity.
- Stage 2 HB2-2 hold replicates the Stage 1 M3 invariance direction at n=29
  with reduced instance count.
- Stage 2 N2 fails the preregistered agreement band on lambda_x under a
  disclosed non-comparable instrument (class_bit_proxy + cofactor drift).
  Per H-BINSTD-4c31d1 DO-E / falsification: the 2x2 cannot attribute cell
  differences; honest output is a power / instrument calculation, not an
  E1/E2/E3 verdict.
- Proves-too-much controls: known-false stayed at zero; no support of E1
  while N2 is lit.

## Inference

The run set is valid for review. Stage 0–1 deliver a clean first observation
that HB2-2 holds at the tested toy scope and that M3 is E1-compatible, but
Stage 2 lights DO-E (`N2_agreement=false`) under `class_bit_proxy` with
large cofactor mismatch. Under the frozen protocol, DO-E makes cell
attribution unreadable — therefore the official decision is **inconclusive**
on the E1/E2/E3 identification claim, not support, not reject_scoped (HB2-2
was not refuted; no counterexample certificate against degree invariance).
HB2-2 holds and Stage 0 gates remain scoped observations for a successor
replication with cofactor-matched C-KG draws and strict (or otherwise
comparable) G-membership. No deployed-curve security claim; no M4; no
exponent move.

## Limitation

- Stage 2 M2 / N2 lambda_x under class_bit_proxy is not comparable across
  cofactors h=822 vs h=2; N2 fail is instrument-contaminated DO-E.
- Stage 2 M3 uses 8 instances (vs ≥20 planned) and dmax=3 dense GE, not full GB.
- Stage 1 M3 likewise dmax=3 dense ranks — preprocessing-immune relative to
  WDSat but not a full first-fall Groebner profile.
- N1 noise floor is identically 0 (deterministic exact GE) — does not estimate
  solver stochasticity.
- m_a=3 not run (instrument_ceiling); M4/WDSat deferred (IMP-WDSat-M4).
- Toy n∈{17,23,29} only; no transfer to m≥163; no deployed break.
- No independent validator/red-team this round (review-plan PD-1).
- Producer manifests record `code.dirty: true` at run time.
