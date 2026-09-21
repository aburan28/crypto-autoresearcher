# EXP-TRA-001 analysis — Transfer-operator (Koopman) spectral channel on the +P walk (candidate C1)

Run: RUN-TRA-001-a (`sage experiments/EXP-TRA-001/tra1_koopman.sage`, wall 27.08 s, stderr empty).
All numbers below are read from `runs/RUN-TRA-001-a/raw.json` and `runs/RUN-TRA-001-a/reversibility_check.json`.

## Protocol executed (frozen in specification.yaml)

- p ∈ {211, 1009, 4099}; C ∈ {8, 32, 128}; S ∈ {round(n^{1/4}), round(n^{3/8})}; seeds 20260717..20260722 (6 seeds).
- 18 prime-order instances (#E(F_p) = n prime; n ranges 191–233 / 977–1069 / 4021–4211), one hidden k per instance, paired across the grid.
- 108 charged configs (empirical operator from S i.i.d. +P transitions, T = S readout from Q), 54 exact-coarse oracle rows (M_exact, T = n), 108 negative-control rows (random permutations), 18 positive-control rows.
- Actual S: p=211 → 4 and 7–8; p=1009 → 6 and 13–14; p=4099 → 8 and 22–23. At S = n^{1/4}, only 3.7–7.8 matrix rows are visited out of 9–129 (fill recorded per config).
- Gate-relevant rows: S = n^{1/4} only (n^{1/4} ≤ n^{0.3} < n^{3/8}); 18 configs per size.

## Controls

- **Positive control: PASS.** Full resolution (C = n, exact shift): analytic readout recovers k_real = k exactly for all 18 instances; the explicit n×n matrix path (p ∈ {211, 1009}, 12 instances) recovers k with L = n, φ = 1/n (e.g. n = 199: k_real = 182 = k, L = 199). The channel exists in principle and the estimator is correct.
- **Negative control: PASS.** Random permutation operators: 50 hits vs chance expectation 50.35 (ratio 0.993); informative-only 23 vs 23.34 (0.985); per-size L_eff_mean vs chance floor: 1.082/1.362 (p=211), 1.555/1.602 (p=1009), 1.833/1.638 (p=4099). No estimator artifact.
- **Determinism: PASS.** Second identical invocation (`tra1_koopman_repro.sage`, differs only in output path) produced byte-identical content in all non-volatile fields (`raw-repro.json`).

## Measured L (gate rows, S = n^{1/4}, 18 configs per size)

| size | n_mean | threshold n^0.05 | hits | chance hits | L_claimed mean | L_eff mean | L_eff median | chance floor E[L_eff] | frac L_eff ≥ thresh |
|---|---|---|---|---|---|---|---|---|---|
| p=211 | 203.3 | 1.304 | 13 | 11.08 | 2.28 | 1.667 | 1.0 | 1.385 | 0.278 |
| p=1009 | 1028.3 | 1.414 | 15 | 12.53 | 2.06 | 1.555 | 1.0 | 1.304 | 0.278 |
| p=4099 | 4106.7 | 1.516 | 9 | 7.58 | 3.06 | 1.778 | 1.0 | 1.579 | 0.333 |

Growth of L_eff_mean vs n across the three sizes: fitted exponent δ = 0.0195 (L ∝ n^δ). L stays O(1): informative configs have w_step ∈ {2,…,6}, L ≤ 6 at all sizes, both S values, all C.

Informative-only hit/chance ratios (gate rows): p=211: 5/3.08 = 1.63; p=1009: 5/2.53 = 1.97; p=4099: 6/4.58 = 1.31. Counts are tiny (5–6 hits), the ratio does **not** grow with n (it falls from 1.97 to 1.31), and the negative control shows no such excess (0.985).

## Gate arithmetic (numbers, no verdict)

- Literal gate "L ≥ n^{0.05} at S ≤ n^{0.3} sustained across three sizes": per-size crossing fractions 0.278 / 0.278 / 0.333 — not sustained (needs ~1.0), and L_eff median = 1.0 at every size.
- The literal gate is **at/below the chance floor** at these toy sizes: thresholds 1.304–1.516 vs floor E[L_eff|chance] = mean(2 − 1/L) = 1.304–1.638. 23 of 108 negative-control rows also "cross" the literal threshold. Literal crossings therefore carry no signal at this scale; the discriminative statistics are hit-vs-chance and the growth exponent δ = 0.0195 ≈ 0 (super-constant growth required by the cost model).
- L_eff_mean exceeds the floor by +0.28 / +0.25 / +0.20 per size — small, hit-count-driven, and not replicated on the negative control.

## Charged cost

- Sampling+readout+spectral convention (2S + Cc³)/√n: means 51135 (p=211), 22705 (p=1009), 11358 (p=4099), dominated by the C³ eigensolve at C = 128 (129³ ≈ 2.1·10⁶ vs √n ≈ 14–64). Candidate cost model S·C²: means 23296 / 34944 / 46592 — also ≫ √n at toy scale. Sampling alone (2S ≈ 8–46 group ops) is the only sub-birthday component, and at that budget the empirical operator is near-empty (fill ≤ 8 of 129 rows).
- Finish-inclusive ratio (2S + Cc³ + √(n/L_eff))/√n: 51136 / 22706 / 11359 — no regime with total charged cost below √n.

## Unexpected observation (recorded per contract rule 8): the exact coarse operator is reversible — the phase channel is structurally absent

All 54 exact-coarse oracle rows returned "no non-stationary eigenvalue with positive imaginary part". Follow-up diagnostic (`reversibility_check.sage`, recomputed from the frozen instances): over all 54 exact lumped matrices,

- max |Im(λ)| = 3.7·10⁻¹⁶ (spectrum real to machine precision);
- detailed-balance residual max | |c|M[c,c'] − |c'|M[c',c] | / max|c| = 2.5·10⁻¹⁷ (exact reversibility w.r.t. cell sizes);
- leading non-trivial eigenvalue magnitude λ₂: mean 0.422, max 0.988 (real, sub-unit; the chain mixes, but every eigenphase ≡ 0).

Mechanism (executor's note, not a proved theorem): the x-interval partition is invariant under R ↦ −R (x(R) = x(−R)), and the involution gives #transitions(c→c') = #transitions(c'→c) exactly, so the lumped translation operator satisfies detailed balance and is self-adjoint in the size-weighted inner product — its spectrum is entirely real. For negation-symmetric (x-coordinate) coarse-graining there are **no eigenvalue phases at all**, at any sampling budget: the k-encoding character phases are destroyed structurally by the ±-fold, not merely statistically. Complex eigenvalues in the charged rows arise only from sampling noise breaking the symmetry; the readout on them performs at chance. This is sharper than the candidate's predicted "coarse-graining kills the phase" and suggests the barrier statement may be provable as a symmetry theorem (reversible lumping ⇒ real spectrum ⇒ no phase observable), complementing the character-orthogonality argument.

## Fitted L(S, C) law (archival ask)

Sampled, charged rows: L_claimed means stay in [1.5, 4.0] across the whole (p, C, S) grid with no monotone trend in p, C, or S (e.g. p=4099, S=n^{1/4}: C=8 → 2.33, C=32 → 3.67, C=128 → 3.17; p=211, S=n^{1/4}: 2.00–2.68; informative fraction 1/6–6/6 per cell). Exact-coarse oracle: L = 1 (non-informative) everywhere. Best summary law: L = O(1), δ ≈ 0.02 vs n; floor-limited.

## Deviations and infrastructure notes

1. Two initial invocations failed at the JSON dump step (Sage preparser `Integer`/`RealNumber` literals are not JSON-serializable; fixed with explicit casts + a default serializer). No experimental data was produced by those invocations; they are infrastructure failures, recorded here per rule 5 (not evidence either way).
2. Git HEAD moved during the task: 9cbe004 at first read, e111dd3 at run time (coordinator committed DEC records). Manifest records the run-time HEAD; dirty tree consists of untracked task files only.
3. `tra1_koopman_repro.sage` is a byte-copy of the main script with only the output path changed, used solely for the determinism check; `raw-repro.json` retained.
4. Estimator definition (single leading non-stationary eigenpair, smallest-positive-phase tie-break, gauge fix, combined matched-filter readout, T = S, O-cell convention Cc = C+1, uniform fill for unvisited rows) was pinned in specification.yaml before execution; the candidate text did not fix these choices.
5. No stopping rule triggered (27 s ≪ 600 s). Sage invocations used: 1 env probe + 3 main attempts (2 failed at dump) + 1 successful run + 1 diagnostic + 1 repro = 7 ≤ budget 8.

## Limitations (scope of any negative reading)

Toy prime fields (n ≤ ~4200); x-interval partitions only; single-eigenpair matched-filter estimator; S ∈ {n^{1/4}, n^{3/8}} only; 6 seeds. At these sizes C = 128 is not ≪ √n and the literal n^{0.05} gate sits at the chance floor, so the gate arithmetic is reported alongside the chance floor rather than as a standalone signal. A reversible-partition obstruction proved here for x-cells does not by itself exclude non-negation-symmetric partitions or higher-mode estimators; it does show the tested channel carries no phase observable.

## Files in this experiment

- `specification.yaml` — frozen protocol
- `tra1_koopman.sage` — experiment script (writes raw.json)
- `reversibility_check.sage` — analysis-side diagnostic on frozen instances
- `tra1_koopman_repro.sage` — determinism-check copy (output path only)
- `runs/RUN-TRA-001-a/{manifest.yaml, raw.json, raw-repro.json, reversibility_check.json, stderr.txt}`
- `analysis.md` (this file)
