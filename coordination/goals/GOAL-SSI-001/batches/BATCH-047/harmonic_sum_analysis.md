# Harmonic Sum Analysis: The √N Barrier

**Verdict**: Sub-√N is NOT achievable by any known technique. Not provably impossible.

## The reduction chain (verified)

H(N,a) = Σ_{k=1}^N 1/(k-a) mod p = -P'(1-a)/P(1-a)
where P(T) = ∏_{k=0}^{N-1}(T+k)

Harvey's algorithm (2014): computes P(T₀) in O(√N · polylog(N)).
This is tight within the BSGS/polynomial-evaluation framework.

## Why √N appears (AM-GM barrier)

To compute ∏ of N linear factors:
- Build degree-D polynomial, evaluate at M = N/D points
- Cost: O((D + M) · polylog) ≥ O(2√N · polylog) by AM-GM with D·M = N
- Optimum: D = M = √N

Multi-level decomposition: same √N minimum at every level.
Recursive splitting: same √N at optimal parameter balance.

## Connection to √élu

√élu IS Harvey's algorithm applied to the isogeny kernel product.
The √N barrier for harmonic sums IS the √ℓ barrier for isogenies.
They are the same mathematical obstruction viewed from different angles.

## No known lower bound

- No Ω(√N) lower bound exists for H(N,a) or ∏(k-a) mod p
- The trivial bound is Ω(1) (O(log p) output bits)
- No reduction to any known hard problem
- The √N barrier is STRUCTURAL (AM-GM in polynomial BSGS) not PROVEN

## The one remaining gap

"Evaluation vs. Representation": could ∏(T₀+k) be computed WITHOUT
building an intermediate degree-√N polynomial? An algorithm maintaining
polylog(N) state and producing the answer in sub-√N steps?

No such algorithm exists. No impossibility proof exists.
The question is formally OPEN in algebraic complexity theory.

## Implications for GOAL-SSI-001

The √N barrier is now fully characterized:
- It IS the √élu barrier (same computation)
- It IS the shifted factorial barrier (same algorithm)
- It IS the AM-GM inequality in polynomial multi-point evaluation
- It is NOT proven as a lower bound
- Breaking it would simultaneously break √élu AND improve factorial computation

STATUS: OPEN CONJECTURE (C1/C2/C3 in the analysis).
No further algorithmic pursuit warranted within this program.
Monitor for external advances in algebraic complexity theory.
