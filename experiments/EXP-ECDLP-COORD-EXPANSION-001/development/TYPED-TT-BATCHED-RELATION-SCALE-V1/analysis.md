# Analysis: TYPED-TT-BATCHED-RELATION-SCALE-V1

## Handoff: 12-bit fixed-curve relation scale

### Claim or task

Replicate the shared-source-sum relation transcript on the next committed
ordinary curve and retain family-specific rank failures.

### Status

OBSERVATION, TOY-EVIDENCE, MODEL-BOUND

### Evidence

- At `p=4027`, `q=4129`, and dimensions `[7,8,8,8,8]`, all four families
  preserve exact direct references, witnesses, D4 support, and held-out
  expected-witness coverage.
- Row-space ranks are `36,36,35,36` for `random_x`, `source_prf_x`,
  `x_interval`, and `rational_union`.
- Quotient ranks are `9,8,9,9`; the quotient width is `9`. The `source_prf_x`
  row is therefore a genuine rank-deficient negative control, while the other
  three reach full toy rank.
- Diagnostic solution digests match for `random_x`, `x_interval`, and
  `rational_union`; `source_prf_x` has no full solution and correctly fails
  that digest check.
- Width-13 source point additions are `0.08157x` of the separated control for
  `random_x`, `source_prf_x`, and `rational_union`, and `0.08174x` for
  `x_interval`.
- Shared cache sizes are `3.75-3.85 MB` measured Python bytes and
  `67,244-68,992` logical point-payload bytes.

### Limitations

- One 12-bit curve is not a scaling law. The p16267 run was not attempted in
  this bounded package after the dense predicted-suffix cost became excessive.
- Full quotient rank on three toy rows does not establish target descent,
  relation independence at cryptographic sizes, or an ECDLP improvement.
- Source additions are only one part of the cost; row-space reconstruction,
  predicate fields, matrix, memory bandwidth, advice construction, and rho
  remain to be charged end-to-end.

### Next concrete action

Design a larger-dimension sampled/transposed locator that avoids the full
predicted suffix scan, then repeat this exact family/rank/held-out protocol and
add independent sparse linear algebra and descent.

### Artifact paths

- `development/TYPED-TT-BATCHED-RELATION-SCALE-V1/RUN-001/raw-result.json`
- `development/TYPED-TT-BATCHED-RELATION-SCALE-V1/RUN-001/verification.json`
- producer: `src/typed_tt_batched_relation_transcript.py`
