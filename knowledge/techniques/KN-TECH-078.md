---
id: KN-TECH-078
type: technique
title: Correlation and fast correlation attacks - linear cryptanalysis of stream ciphers as decoding
tags: [correlation-attack, fast-correlation-attack, siegenthaler, meier-staffelbach, lfsr, decoding, parity-check, ldpc, correlation-immunity, linear-cryptanalysis, stream-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "basic correlation attack: exhaustive search over one LFSR's initial state, 2^L for length L, using keystream correlated to that LFSR's output with bias eps and about eps^{-2} keystream bits. Fast correlation attacks replace the exhaustive search with iterative decoding, trading keystream and precomputation against time"
applicability: keystream generators built from LFSRs where the output function is correlated to a subset of the register outputs; the linear-family counterpart of the algebraic attacks in KN-TECH-072, and a design constraint that trades against algebraic immunity
source_refs: [KN-TECH-067, KN-TECH-068, KN-TECH-072, KN-LIT-3794, KN-LIT-3795, KN-LIT-3792, KN-LIT-3793, KN-LIT-3176, KN-LIT-1518, KN-LIT-2018, KN-LIT-4747, KN-LIT-3809]
added: 2026-07-31
superseded_by: null
---

## Method

**The divide-and-conquer observation** (Siegenthaler, 1985). Take a combiner
generator: several LFSRs feeding a Boolean function `f`. If the keystream `z_t`
is correlated to the output `a_t` of one register — `Pr[z_t = a_t] = 1/2 + ε` —
then that register can be attacked **alone**. Guess its initial state, generate
its output, and measure the correlation with the keystream; the correct guess
shows `ε`, the others show noise. Cost `2^L` for register length `L` and about
`ε^{-2}` keystream bits, instead of `2^{ΣL_i}` for the whole generator.

The design response is **correlation immunity**: choose `f` so that its output
is statistically independent of every small subset of inputs. Siegenthaler's
trade-off says this cannot be had for free — correlation immunity of order `m`
caps the algebraic degree of `f`, and a low degree is exactly what
`KN-TECH-072`'s algebraic attacks want. **Resistance to the two families pulls
in opposite directions**, and that tension is the central design problem for
this class of cipher.

**Fast correlation attacks** (Meier–Staffelbach, 1988) drop the exhaustive
search. Observe that the LFSR sequence is a codeword of a linear code determined
by the feedback polynomial, and the keystream is that codeword seen through a
binary symmetric channel of error rate `1/2 − ε`. Key recovery **is decoding**:

- find low-weight parity-check relations satisfied by the LFSR sequence, either
  from multiples of the feedback polynomial or by search;
- run iterative decoding — belief-propagation style, exactly as for LDPC codes —
  to recover the initial state.

The result is a family of algorithms trading keystream length, precomputation
and time against each other, with the classical treatments in `KN-LIT-3794` and
`KN-LIT-3795`. Later refinements push the same idea further: extension-field and
large-unit approximations (`KN-LIT-3793`), weak feedback-polynomial classes
(`KN-LIT-3176`), and the near-collision and revisited variants that reach
full-round Grain-family designs (`KN-LIT-3792`, `KN-LIT-3809`). Modern targets
include SNOW-V/Vi (`KN-LIT-2018`) and Bluetooth's E0 (`KN-LIT-4747`); the
survey-style treatment in `KN-LIT-1518` maps the family.

**Why this is linear cryptanalysis.** The correlation being exploited is a
linear approximation of the output function, its magnitude is a Walsh
coefficient of `f`, and combining several such approximations is the capacity
argument of `KN-TECH-068` in a different costume. The distinguishing feature is
what happens *after* the bias is found: block-cipher linear cryptanalysis counts
and ranks key guesses, stream-cipher correlation attacks decode.

## Program usage

- **The decoding reformulation is the transferable idea.** "Recovering the secret
  is decoding a noisy codeword" converts a search problem into a problem with its
  own mature algorithmic literature and its own thresholds. That is the same
  species of move the program values in `KN-TECH-056` — find the object under
  which the problem is already solved — and it is worth noting that the
  asymmetric side of this corpus has a direct analogue: LWE is decoding with
  errors (`KN-TECH-021`), and the primal/dual attacks (`KN-TECH-038`,
  `KN-TECH-039`) are the lattice reading of the same statement.
- **The Siegenthaler trade-off is a rare, provable "you cannot have both".** The
  program's Pareto-honesty requirement (`KN-TECH-056`: `dominated_by` and
  `sota_delta` in every deliverable) is about exactly this shape of constraint,
  and this is a clean external example where the trade is a theorem rather than
  an observation.
- **Precomputation is a cost.** Fast correlation attacks move work into
  parity-check search; under `KN-TECH-035` that is charged and reported, never
  discounted.

## Applicability limits

- **A correlation must exist.** Against a correlation-immune output function of
  sufficient order, the divide-and-conquer step has nothing to divide, and the
  algebraic route of `KN-TECH-072` is the relevant one instead.
- **Linear state update is assumed.** Designs with nonlinear update (Trivium,
  Grain's NFSR) do not fit the plain model; the published attacks on them work
  around this and their applicability is design-specific, not generic.
- **Decoding thresholds are real.** Iterative decoding succeeds only when the
  error rate is below a threshold set by the parity-check weight and density;
  above it, more keystream does not rescue the attack.
- **Keystream availability caps everything.** `ε^{-2}` bits under one key is
  often the binding constraint in practice.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The divide-and-conquer principle,
correlation immunity and its trade-off against algebraic degree, and the
decoding reformulation with iterative parity-check decoding are standard
published results, written from established knowledge and not re-derived or
measured here. Siegenthaler's and Meier–Staffelbach's originating papers are
named in prose; this corpus holds no `KN-LIT` entry for either and no identifier
was minted. All cited `KN-LIT` records are **title-level** per the family note —
that the Grain family, SNOW-V/Vi and E0 are targets is read from titles, and no
complexity figure from any of them is quoted or verified. The parallel drawn to
LWE-as-decoding and to the program's Pareto-honesty rule is this program's own
reasoning.
