# FROB C5 finite-field trace proof audit — 2026-10-22

**Scope.** This is a proof review of the finite-field core of frozen
`EXP-FROB-91ee9c` control C5, not a rerun or a research-state transition. The
source is [FiniteFieldTrace.lean](../../../formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean)
at commit `0600270bcf4a49edfb65d0fe838ab5fa4442216c`, with the exact
[target specification](../../../formal/targets/frob-c5-finite-field-trace.yaml).
The [diagram](proof.svg) shows the checked math and the remaining run bridges;
the [PDF](report.pdf) embeds that visual.

## Exact theorem and why it matches a C5 slice

Let `K ⊂ L` be finite fields with `finrank K L = 5`, and let `F` be the
`K`-linear `|K|`-power Frobenius. The target theorem assumes `(5 : K) ≠ 0` and
proves four conclusions:

1. For every `x : L`, `(1+F+F²+F³+F⁴)(x)` equals the image in `L` of the
   field trace `Tr_{L/K}(x)`.
2. The five-term polynomial and field trace have the same kernel.
3. The field-trace kernel has `K`-dimension **4**.
4. That kernel equals `range(F−1)`.

The proof uses Mathlib's explicit finite-field trace sum, Frobenius power
law, trace surjectivity for separable finite-field extensions, and
rank-nullity. The fourth conclusion also uses the previously verified
[OrderFive.lean](../../../formal/CryptoResearch/FrobTrace/OrderFive.lean)
identity and the fact that degree-five Frobenius has order five. The file
instantiates the dimension conclusion for `GaloisField 11 5`,
`GaloisField 13 5`, and `GaloisField 19 5`, corresponding to the three
archived base primes.

The frozen [specification](../../../experiments/EXP-FROB-91ee9c/specification.yaml)
and [analysis](../../../experiments/EXP-FROB-91ee9c/analysis.md) ask whether
the nontrivial Frobenius factor kernels form the trace-zero space of dimension
four. This proof establishes the trace polynomial and dimension on the
mathematical finite fields. It does **not** prove the factor-kernel direct-sum
decomposition or bind the archived `F_q[z]/(g)` basis and executable Frobenius
to the Lean model. Those exact obligations are in the
[open problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md).

## Verification and provenance

- `lake env lean CryptoResearch/FrobTrace/FiniteFieldTrace.lean` compiled the
  committed source on the pinned Lean `4.35.0-rc1` workspace without a proof
  error.
- The exact-source [formal verifier receipt](proof-verification.json) is
  produced separately from the theorem source and binds target
  `TASK-20261022-a855e0`, commit
  `0600270bcf4a49edfb65d0fe838ab5fa4442216c`, Lean `4.35.0-rc1`, and the
  dependency manifest. Its SHA-256 is
  `2545572af3cf8225ff110033cf70e6a45cd07b681c80154fdc5d470af28942cb`.
  The full workspace build passed **8,970 jobs**; the target axiom audit
  passed, and the workspace audit found **584 theorem declarations** using
  only standard axioms. No forbidden constructs were found. Independent
  semantic review remains pending; the hosted `lean-verification.yml` workflow
  is manually disabled, so this local exact-source receipt is the available
  proof-gate evidence.
- The [editable graph](proof.dot), [SVG](proof.svg), [PNG](proof.png), and
  [standalone figure PDF](proof-figure.pdf) are derived communication
  artifacts. No experiment values or performance graph changed because this
  work produced no new measurement.

## Boundary and next check

The archived checker and all-core object replay report dimension four in the
three core cells, but that is executable evidence about recorded inputs. A
general finite-field theorem cannot certify the historical quotient-field
implementation or the missing factor CRT step. C5 as a frozen run control,
C8, the experiment success gate, and any ECDLP performance conclusion remain
unestablished by this proof alone.

Next, formalize the exact q11 split-four-linear, q13 single-quartic, and q19
two-quadratic factorizations of the nontrivial part of `X^5−1` and prove their
kernel direct sum. Then bind the archived quotient-field bytes and Frobenius
matrix to that formal field, with a characteristic-five countercontrol and
independent semantic and code review.
