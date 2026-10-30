# Equivalent encodings and certified coefficient pruning

This continuation implements the two follow-ups the user selected after the
five-lead study. The earlier partial-matrix and fixed two-bit backdoor sweeps
are not expanded. Scientific execution requires the frozen native contract in
`experiments/EXP-PNEXT-624f41/`; software integrity tests are separate.

## Two-summand encoding

On a nonsingular curve `y²=x³+ax+b` over an odd prime field of characteristic
greater than three, fix `R=(r,s)` with `s != 0`. Define

```
N = x1*x2 - r*(x1+x2) - 2*r² - a.
N² - 4*s²*(x1+x2+r) = S3(x1,x2,r).
```

The quadratic equations `lambda²=x1+x2+r` and `2*s*lambda=N` have a unique
field witness exactly when the quartic vanishes. The witness lifts to
`Pi=(xi, lambda*(xi-r)-s)`, with `P1+P2=R`. Canonical binary encoding of lambda
requires explicit `lambda<p` clauses. Equal abscissas are permitted. The
non-two-torsion assumption and the restriction to two summands matter.

`encoding.py` compares the quartic, extra curve-membership predicates, the
quadratic lift and a reverse-generator-order quadratic A/A arm. All use the
same bounded polynomial-calculus learner and MiniSat backend. Learned clauses
require multiplier identities in the Boolean quotient. Complete independent
coordinate and auxiliary-variable censuses are checked against actual point
addition after the search; neither census steers search. Bounded search may
be censored even when this independent encoding-equivalence check completes.

The input degree falls from four to two by adding variables. This identity
does not establish lower intrinsic regularity, lower solving degree, a faster
solver, or an ECDLP algorithm. The PC strategy is incomplete; a stalled search
cannot certify non-refutability.

## Shared coefficient branch explanations

`coefficients.py` implements the other selected mechanism: construct a common
divisor polynomial from shared line coefficients, require its roots to lie in
a declared multiplicative coset, and explain rejected SAT branches with exact
finite-field polynomial identities. `check_coefficients.py` verifies the
certificates and full finite model/relation coverage independently. Exceptional
chart fallback and its costs remain explicit.

## Cost boundaries and custody

Construction, search, certificate checking, witness reconstruction and
independent census/checking have separate counters. Primitive field arithmetic
and procedural events are not summed into an unsupported universal work total.
Search failures, caps and A/A differences are retained. Producer RSS and CPU
telemetry do not provide an isolated timing comparison.

`driver.py` appends and fsyncs completed cells, binds the config by hash,
refuses existing output, and requires the native launch receipt. The post-run
checker also compares every journal row with the aggregate payload. Prior
observations informed this design: these public fixtures are not held-out
performance data.

Primary sources inspected before design: [Kosters and Yeo, Notes on summation
polynomials](https://arxiv.org/html/1503.08001), Proposition 2.1, and [Hader et
al., MCSat-based finite field reasoning in Yices 2](https://arxiv.org/html/2402.17927v1),
Sections 4–5. The latter motivates polynomial conflict explanations; this is
not a Yices implementation or a reproduction of its performance results.
