# Canonical GF(2^17) Frobenius and the BINSTD factor product

The frozen BINSTD n=17 dimension files describe a normal-basis
circulant calculation using the factors of `x^17-1` over `F₂`.
The [Lean source](../../../formal/CryptoResearch/Binstd/CanonicalFrobenius.lean)
instantiates Mathlib's finite-field Frobenius theorems on the canonical
`GaloisField 2 17`: its extension degree and Frobenius order are 17,
and the Frobenius minimal polynomial is `X^17+1`. It rewrites that
polynomial using the [source-bound factor product](../2026-10-22-binstd-factor17-lean/REPORT.md)
to obtain `factor1 * factor8a * factor8b`.

The [formal task](../../../formal/targets/binstd-canonical-frobenius-minpoly.yaml)
targets the conjunction of the order and minimal-polynomial identities.
The [verification receipt](proof-verification.json) reports
`machine_verified` under Lean 4.35.0-rc1: the full build passed, the
630-theorem audit found standard axioms only, and the target axiom
audit passed. Independent semantic review is still pending. The
[editable graph](canonical-frobenius.dot),
[SVG](canonical-frobenius.svg), [PNG](canonical-frobenius.png),
[figure PDF](canonical-frobenius-figure.pdf) and [report PDF](report.pdf)
show the scope.

This theorem concerns the canonical field. It does not prove that the
archived runner's polynomial-basis modulus `t^17+t^3+1` or its
`x↦x²` implementation is isomorphic to this exact model in Lean.
It also does not classify all invariant subspaces or establish the
recorded admissible-dimension table from code. Those gaps remain in
the [open bridge problem](../../../problems/binstd-frobenius-invariant-dimension-lean-bridge.md).
Archived hit counts and relation-yield ratios remain empirical; no
performance, attack-cost, or security verdict changes.
