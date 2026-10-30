---
id: KN-OPEN-57907f
type: open_problem
title: "Does omega <= 9/4 (openai/math family 107) hold over GF(2^k)?"
tags: [matrix-multiplication, omega, characteristic-2, asymptotic-spectrum, groebner, cost-model, openai-math]
confidence: unverified
source:
  citation: "openai/math family 107; KN-LIT-0b036e"
  url: "https://github.com/openai/math/blob/main/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/paper.pdf"
internal_refs: []
proof_status: not_applicable
proof_refs: []
added: 2026-10-27
superseded_by: null
---

## Question
Does the proof of `ω(ℂ) <= 9/4` in
`Matrix-Multiplication-Nine-Fourths-October-2-2026` transfer to fields of
characteristic 2?

## What is known here
- The primitive-root-of-unity separation transfers. Take any odd
  `L | 2^k − 1`. This is tested in `crypto/src/cryptanalysis/matmul_exponent.rs`.
- Appendix A's stated tools do not depend on the field on their face:
  separation, compactness, fixed point, and Strassen's asymptotic spectrum.
- The corpus formalizes `9/4` only over `ℂ`. Over every field it claims only
  `2.371054886…`. No reason is given for the gap.

## What would decide it
Check, over `F = GF(2^k)`, the two remaining steps of the paper:
- the shared-leg entropy inequality (Corollary `cor:entropy`);
- the detecting-characters lemma (Lemma `lem:existence`, Appendix A).

A failure in either step should name the characteristic-0 ingredient it
needs.

## Why it matters
Characteristic-2 summation-polynomial cost models evaluated at
`ω = 9/4`:
- `2^68.96` at `n = 131`;
- turning point `n = 227`, below the deployed binary fields `233`–`571`.

Today those rows are conditional on this question. They would also still
be existence-only exponents under a contested first-fall-degree model.
