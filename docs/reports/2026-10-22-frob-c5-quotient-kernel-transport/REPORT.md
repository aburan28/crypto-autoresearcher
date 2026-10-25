# FROB C5 controls for the actual quotient Frobenius maps

The [editable proof graph](proof.dot), [SVG](proof.svg), [PNG](proof.png),
[figure PDF](proof-figure.pdf), and [two-page report](report.pdf) show the
new mathematical result and the remaining historical boundary. No scientific
trial or timing run was repeated.

## Exact source and theorem

The [Lean source](../../../formal/CryptoResearch/FrobTrace/QuotientKernelTransport.lean)
has SHA-256 `d423507c9e82e2aafa3f203880e556b576c73d82644a5d55aa28a657be4be5d5`
at source commit `20982d9a84d87ca7a1013f4e35739366eccebaaf`. The
[formal target](../../../formal/targets/frob-c5-quotient-kernel-transport.yaml)
has SHA-256 `45c704365656aa2bd905c1f7d135995f19ce56927719fbf5ef0ac0aec1404810`.
The aggregate theorem is
`CryptoResearch.FrobTrace.QuotientKernelTransport.all_quotient_C5_controls`.

The earlier [full-map certificate](../2026-10-22-frob-c5-full-map/REPORT.md)
identifies the q-power endomorphism of each archived polynomial quotient with
the frozen 5×5 matrix in its power basis. This source uses that algebra
equivalence to transport the exact matrix trace rank and fifth-power identity
to each map. It applies the checked factor-polynomial identities to the maps
themselves, proving the q=11 four-linear, q=13 one-quartic and q=19
two-quadratic factor-kernel sums equal the five-term trace kernels. Lean also
proves each trace kernel has dimension four, each fixed kernel has dimension
one, and the fixed and trace kernels are disjoint. No quotient-modulus
irreducibility assumption is used for these ring-level statements.

## Verification

The [exact-source verifier receipt](proof-verification.json) records pinned
Lean 4.35.0-rc1, successful 8,976-job full workspace and 3,099-job target
builds, no forbidden constructs, and a passing global audit of 686 theorem
declarations using standard axioms only. The requested theorem's axiom audit
passed. The receipt has SHA-256
`c8e678daf13c2a08b2a94f76b6da0039e448b739780cf62d9bfdd0cbc65593da`
and status `machine_verified`; independent semantic review remains pending.
Six local style warnings recommend `have`
over `haveI` for proposition-valued finite-dimensional instances and do not
change the theorem or its assumptions.

## Code-path check and interpretation limit

The frozen Sage [core](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/core.py)
chooses a monic irreducible modulus and converts q-power images to
constant-first coefficient vectors. The [lattice helpers](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/lattice.py)
evaluate factor polynomials in that matrix and take right kernels. The
[driver](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/implementation.py)
checks directness, trace-kernel equality and dimensions. Its `T_equals_hM`
flag compares two constructions of the same matrix polynomial, so that flag
alone is only a consistency check. The separate
[source-bound replay](../2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json)
recomputes the frozen C5 matrices and rejects a matrix mutation, but does not
prove that the original Sage execution refined this Lean quotient model.

The original run manifest records source hashes for final post-bugfix files
that were untracked at execution start. The execution-time bytes therefore
remain unbound to a committed source tree. Historical Sage-to-Lean refinement,
original execution-source custody and independent code/semantic review remain
open. The three quotient moduli are not proved irreducible in Lean, although
the source-bound replay checks that property executably. C8, the complete
experiment gate and performance claims remain open. The
[problem record](../../../problems/frob-c5-factor-kernel-and-model-bridge.md)
tracks the remaining checks. No performance dashboard value changed.
