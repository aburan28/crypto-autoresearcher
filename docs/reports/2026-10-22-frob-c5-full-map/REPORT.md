# FROB C5 full quotient Frobenius map certificate

The [editable proof graph](proof.dot), [SVG](proof.svg), [PNG](proof.png),
[figure PDF](proof-figure.pdf), and [two-page report](report.pdf) show the
mathematical map result and the remaining historical boundary. No scientific
trial or timing run was repeated.

## Exact source and theorem

The prior [quotient-basis certificate](../2026-10-22-frob-c5-quotient-matrices/REPORT.md)
proves all 75 q-power image coordinates in the three frozen polynomial
quotients. The new [Lean source](../../../formal/CryptoResearch/FrobTrace/QuotientFrobeniusMap.lean)
has SHA-256 `369725d67c556ae7ed62f3bd318b02e8a5d8bbf41e5408516df03f0bafc589b7`
at source commit `1993b13e4a245b5e92ac8748198d2e9d0013e885`. Its
[formal target](../../../formal/targets/frob-c5-quotient-frobenius-map.yaml)
has SHA-256 `3cceac121b441df16cc2e9c6f790025daf95af8a59b85072e77c2dc5b9476a10`.
The aggregate theorem is
`CryptoResearch.FrobTrace.QuotientFrobeniusMap.all_full_frobenius_matrices`.

Mathlib's `FiniteField.frobeniusAlgHom` maps every element of each `AdjoinRoot`
quotient to its q-th power and is an algebra homomorphism over `ZMod q`; its
`toLinearMap` is therefore base-field linear. Lean proves each modulus has
degree five, uses the `AdjoinRoot` power basis, and rewrites every `toMatrix`
entry as the q-power image coordinate of a basis monomial. The earlier
certificate identifies that coordinate with the exact frozen matrix entry.
The theorem checks all 25 entries for each of q=11, 13 and 19. This is a
full-linear-map matrix equality, beyond a list of basis image calculations.
It does not require quotient-modulus irreducibility.

## Verification

The [exact-source verifier receipt](proof-verification.json) has SHA-256
`4837fb2da283983f24ba691c106ad8c8296ca12965dc512f40f78e24850be8c5`.
It records pinned Lean 4.35.0-rc1, a successful 8,975-job full workspace build
and 3,093-job target build, no forbidden constructs, and a passing global
audit of 667 theorem declarations using standard axioms only. The requested
theorem's axiom audit passed. Status is `machine_verified`; independent
semantic review remains pending. The recorded unrelated linter warnings do
not affect this source.

## Interpretation limit

The separate [exact matrix-kernel certificate](../2026-10-22-frob-c5-quotient-matrix-kernels/REPORT.md)
proves the C5 factor-kernel sums and trace dimensions for the matrices. An
additional [quotient-kernel certificate](../2026-10-22-frob-c5-quotient-kernel-transport/REPORT.md)
proves the corresponding C5 controls for the actual q-power endomorphisms.
The historical Sage field and kernel paths are not proved to refine the mathematical
map; original execution-source custody and independent code/semantic review
remain open. The three moduli are not proved irreducible in Lean, although the
[source-bound replay](../2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json)
checks them executably. The [open problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md)
tracks these checks. C8, the complete experiment gate, and performance claims
remain open. No performance dashboard value changed.
