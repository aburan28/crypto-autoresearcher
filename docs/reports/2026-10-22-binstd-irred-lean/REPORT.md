# Lean irreducibility of the BINSTD degree-eight factors

The frozen n=17 BINSTD Stage-1 files list bitmask polynomials 313
and 471 and label each degree eight. The parent
[factorization proof](../2026-10-22-binstd-factor17-lean/REPORT.md)
binds those exact constants to Lean and proves their product with
`X+1` is `X^17+1` over `F₂`. This follow-up proves that both
degree-eight factors are irreducible in `(ZMod 2)[X]`.

The [Lean source](../../../formal/CryptoResearch/Binstd/Irreducibility.lean)
first cancels `X+1` against Mathlib's prime-cyclotomic identity to
show `factor8a * factor8b = Φ₁₇`. It checks that 2 has order 8 modulo
17 and computes each factor's degree as 8. Mathlib's cyclotomic
factor-degree criterion then proves
`factor8a_irreducible` and `factor8b_irreducible`; the
[formal task](../../../formal/targets/binstd-x17-degree-eight-irreducible.yaml)
targets their conjunction `factor8_irreducible_pair`.

The [verification receipt](proof-verification.json) reports
`machine_verified` under Lean 4.35.0-rc1: the full build passed, the
625-theorem audit found standard axioms only, and the target axiom
audit passed. Independent semantic review is still pending. The
[editable graph](irreducibility.dot), [SVG](irreducibility.svg),
[PNG](irreducibility.png), [figure PDF](irreducibility-figure.pdf)
and [report PDF](report.pdf) show the proof chain and its remaining
scope boundary.

Irreducibility and the product do not by themselves identify the
archived field's `x↦x²` map with the cyclic normal-basis module or
prove that its invariant-subspace dimensions are exactly
`{0,1,8,9,16,17}`. The
[open bridge problem](../../../problems/binstd-frobenius-invariant-dimension-lean-bridge.md)
tracks that remaining mathematical step. The archived hit counts
and toy yield decisions remain empirical; no performance dashboard
value, attack cost or deployed-security claim changes.
