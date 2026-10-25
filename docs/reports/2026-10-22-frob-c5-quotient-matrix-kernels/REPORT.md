# FROB C5 exact quotient matrix factor-kernel certificate

The [editable proof graph](proof.dot), [SVG](proof.svg), [PNG](proof.png),
[figure PDF](proof-figure.pdf), and [two-page report](report.pdf) show the
mathematical matrix result and its historical boundary. No experiment was
rerun and no measured performance value changed.

## Exact source and claim

The three frozen C5 matrices are checked entry by entry in the earlier
[quotient-basis certificate](../2026-10-22-frob-c5-quotient-matrices/REPORT.md).
The [new Lean source](../../../formal/CryptoResearch/FrobTrace/QuotientMatrixKernels.lean)
has SHA-256 `c4608b079baf94bd7def305d1171e61c4057ee6e3dad4d4b08eb3d14bc9605dc`
at source commit `458c91dbdcb8b0116173014e421da852333e4e1a`. Its
[formal target](../../../formal/targets/frob-c5-quotient-matrix-kernels.yaml)
has SHA-256 `d82b5d3437067ab43dc8c848e904b3c501f4e3c6acc5c56c7c6d9c80f73d0fda`.
The aggregate theorem is
`CryptoResearch.FrobTrace.QuotientMatrixKernels.all_matrix_C5_controls`.

| Base field | Exact matrix calculation | Factor-kernel statement |
| --- | --- | --- |
| `ZMod 11` | `M^5=I`; trace rank one; kernel dimension four | Four distinct linear factor kernels are successively disjoint and sum to the trace kernel. |
| `ZMod 13` | `M^5=I`; trace rank one; kernel dimension four | The quartic factor kernel equals the trace kernel. |
| `ZMod 19` | `M^5=I`; trace rank one; kernel dimension four | Two quadratic factor kernels are disjoint and sum to the trace kernel. |

Lean computes each five-term trace matrix and factors it as a rank-one
diagonal matrix times an upper-triangular matrix with nonzero determinant.
Rank-nullity proves the kernel dimension. The exact factor-kernel identities
follow by instantiating the previously checked polynomial factorization and
coprimality theorems with `Matrix.toLin'` of the frozen matrices. The aggregate
theorem conjoins all three factor-kernel claims and all three dimensions.

## Verification

Direct `lake env lean` compilation and target-spec validation passed. The
[exact-source verifier receipt](proof-verification.json) has SHA-256
`5b2f59c4e9748afac49326348f7d7baaf94d249099e8fe44f81cda5fa6d3fdd1`.
It records pinned Lean 4.35.0-rc1, a successful 8,973-job full workspace build
and 3,097-job target build, no forbidden constructs, and a passing global
audit of 647 theorem declarations using standard axioms only. The requested
theorem's axiom audit passed. Status is `machine_verified`; independent
semantic review remains pending. The unrelated linter warnings recorded in
the build log do not affect these declarations.

## Interpretation limit

This is a Lean result about the three linear maps defined by the exact
recorded matrices. The preceding certificate proves that their columns equal
the q-power images of the quotient-basis monomials, and a
[full-map certificate](../2026-10-22-frob-c5-full-map/REPORT.md) proves the
q-power endomorphism has that exact matrix. Explicit Lean transport of the
kernel theorem to the quotient endomorphism, historical Sage refinement,
original run source custody, and independent code/semantic review are still
needed before calling the frozen C5 run control proof-backed. The
[open problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md)
tracks those obligations. C8 and the complete experiment success gate remain
open. No dashboard performance curve is changed by this mathematical proof.
