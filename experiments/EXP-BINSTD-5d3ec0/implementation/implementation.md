# Implementation notes — EXP-BINSTD-5d3ec0 / TASK-20261001-eaf0c5

## Protocol adherence

- Stage 0 artifacts written and committed (`8eee0ef17`) **before** any Stage 1
  run directory existed.
- Write scope limited to `experiments/EXP-BINSTD-5d3ec0/{runs,implementation,stage0,stage1,stage2}/`.
- Amazon Bedrock not selected/configured/probed/contacted/used.
- No AUXIN edits; no H/EXP/IDEA status edits.
- RUN ids minted via `tools/allocate_id.py --next run --area BINSTD` and
  `--check`ed before use.
- Optional SAT arm skipped (`sat_arm: skipped_optional_missing_engine`).

## Code provenance

Field/curve arithmetic lifted from `experiments/EXP-CERTBIN-e94b27/impl/` into
`implementation/` (gf2n.py, curve.py) and parameterised for n=19. Certificate
re-verification uses a fresh `Field` schoolbook object in `verify_cert.py`,
independent of the TableField hot path.

## Stage 0

- Product-law upper bounds at n=131; `|Gamma_13|` log2 ≈ 71.011 (within 0.5 of 71).
- n=19 order measured 523492 = 4×130873; 130873 prime; unique 2-torsion (0,1);
  2-Sylow cyclic; μ = 41811 with ord=19.
- Preregistered predictions frozen before Stage 1.
- Exact `|Gamma_1|=38`, `|Gamma_2|=608` at n=19 (upper bounds 38 and 684).

## Stage 1 deviations / observations

1. **Scalar-mult accounting** includes two multiplications to form each random
   walk step `R=αG+βT` plus `|Gamma_w|` trial multiplications per target.
2. **Ordinary control** uses the spec curve (A=46693,B=306147); measured order
   523646 = 2×261823 (ell ≠ Koblitz ell). Same V' construction over the same
   field; random scalar set size-matched to `|Gamma_w|`.
3. **Relabelled control** operates in additive `Z/(4·130873)` with generator
   `4` (order ell) and a random representative set of size `2^{l'}`. This is
   slightly richer than curve `|F_{V'}|` (trace-zero filter), which can bias
   Koblitz costs upward vs the additive control — disclosed, not “fixed”.
4. **Prediction band exceptions** (documented, not retuned): several cells have
   `mean_over_prediction < 1/1.5`, especially large-`|Gamma|` / large-`l'` toy
   cells. Frozen Stage-0 bands unchanged.
5. **Genericity ratios**: w=2 cells fall in [0.67,1.5]; w=1 Koblitz/control
   means sit near/slightly above 1.5 (≈1.53–1.60). Recorded as DO-3-shaped
   observation for Reviewer/Coordinator — Executor draws no conclusion.
6. Every completed seed carried `certificate.kind: discrete_log` with
   independent re-check; relation hits re-verified as `decomposition`.
   Cell manifests use `kind: none` as metric aggregates (per-seed certs in
   `raw-result.json`).

## Stage 2 deviations / observations

1. Work unit = Boolean GE pivot work on the D=2 linearisation of Weil-descended
   S_3 bit equations **plus** ANF monomial support size for deg≤4 (proxy for
   closure/Macaulay effort). Not CaDiCaL conflict counts.
2. One-hot system embeds per-pattern linear equations into `(v_i o_j, o_j)`
   columns with `sum o_j = 1`; does **not** double-count per-pattern GE into
   the one-hot numerator.
3. Ratios ≈ 2.5–2.8 ≥ 1.0 on all three `l'` cells; DO-2 not triggered.
4. No extrapolation to n=131.

## Non-claims (binding)

No break, no matched-rho competitiveness, no exponent improvement from the
tau-adic object, no deployed-curve attack cost.
