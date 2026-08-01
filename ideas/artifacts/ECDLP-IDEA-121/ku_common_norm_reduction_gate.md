# IDEA-121 KU/Common-Norm Reduction Gate

Status: `REVISE_INTRINSIC_GEOMETRIC_AND_GENERIC_SLP_ROUTES_CLOSED_KU_REDUCTION_OPEN`

This theorem receipt executes the one action authorized by IDEA-121 and P1513
v2. It screens two additional circuit-level routes. It is not a lower bound for
arbitrary arithmetic circuits and does not authorize an elliptic run.

## Frozen Degree Regime

Write `B=N^(1/5)`. The shared source-marked circuit has `Theta(B^2)`
constant-degree leaves and semantic bidegree `Theta(B^2)`. The selector
polynomials `T(U)` and `F(V)` have degree `Theta(B)`. Each norm has degree
`D=Theta(B^3)` in `W`, while a favorable batch has only `Theta(B)` accepted
common roots. Pollard rho is `Theta(B^(5/2))`.

The common roots can be written without either norm as the overdetermined fiber
system

```text
T(U)=0,
F(V)=0,
H(U,W)=0,
H(V,W)=0.
```

The small final accepted degree does not by itself make this an intrinsic-degree
geometric-resolution instance.

## Route A: Intrinsic-Degree Geometric Resolution

Giusti, Heintz, Morais, Morgenstern, and Pardo solve a square radical regular
sequence given by a straight-line program in nonuniform arithmetic-network size
polynomial in the input length and the *maximum degree of the prefix
varieties*. Their construction uses linear algebra on matrices of size at most
`2*d*delta`, where `d` bounds the semantic equation degrees and `delta` is that
geometric-degree parameter.

IDEA-121 has four equations in three variables. On the squarefree generic
control, every literal three-equation subsystem already has a large degree:

| omitted equation | square subsystem degree |
|---|---:|
| `H(V,W)` | `deg(T)*deg(F)*deg_W(H)=Theta(B^4)` |
| `H(U,W)` | `Theta(B^4)` |
| `F(V)` | `deg(T)*deg_W(H)*deg_V(H)=Theta(B^5)` |
| `T(U)` | `Theta(B^5)` |

For example, `T=F=H(U,W)=0` chooses `B` target roots, `B` independent
factor-start roots, and `Theta(B^2)` endpoint roots. The fourth equation is the
cut that collapses this ambient fiber to the planted `Theta(B)` intersection;
a square solver cannot credit that final cut while ignoring the degree of the
square system it must first represent.

Generic linear combinations do not supply a certified smaller prefix degree,
and the cited theorem does not cover an arbitrary overdetermined circuit by the
final accepted degree alone. Even under the unrealistically favorable
substitution `delta=Theta(B)`, its stated matrix dimension is

```text
2*d*delta = Theta(B^3),  d=Theta(B^2),
```

already above rho. With an admitted square subsystem, `delta` is at least
`Theta(B^4)` on the generic control. The theorem is also nonuniform over
algebraic parameters and gives only an unspecified polynomial exponent, so it
does not establish the required finite-field base-operation or bit recurrence.

**Decision:** classical intrinsic-degree geometric resolution is a scoped
negative for this formulation. A new overdetermined solver whose complexity is
output-sensitive in the final cut, not in square-subsystem or prefix degree,
would be a mechanism-new operation and is not ruled out.

## Route B: Generic Straight-Line GCD And Factor Extraction

Kaltofen's generic GCD and factorization algorithms accept straight-line
programs plus total-degree bounds and return straight-line programs for the GCD
or factors with controllable randomized correctness. Their complexity is
polynomial in the circuit input and the input total degrees represented as unary
parameters. The factorization construction is likewise polynomial in total
degree; published summaries give factor-program length terms
`O(D^2*L + D^(3+epsilon))` for input circuit length `L` and total degree `D`.

For IDEA-121, merely applying this theorem to the two norms requires both:

1. straight-line programs for `N_T` and `N_F`, whose construction from the
   bivariate product circuit is exactly the unresolved common-norm conversion;
2. the norm degree bound `D=Theta(B^3)` in the generic algorithm's unary-degree
   input and running-time parameter.

Thus the cited generic GCD/factor result is not a certified sub-`B^(5/2)`
algorithm in this regime even before multiplicity and source recovery. It also
returns polynomial factors, not the target/start/four-transition inverse.

**Decision:** generic straight-line GCD/factorization is a scoped negative as a
solver substitution. This does not rule out a specialized low-output-degree
common-factor extractor whose recurrence depends on the `Theta(B)` common
factor rather than the `Theta(B^3)` norm degrees.

## Surviving KU Obligation

Kedlaya-Umans remains an open reduction target only in the following strict
form:

```text
(T,F,H product circuit)
    -> O(1) degree-Theta(B^2) KU-compatible operations
    -> common factor, multiplicities, and exact source jets,
```

with no norm circuit, `B^3` unary degree object, square-subsystem geometric
resolution, specialization family, dense coefficient vector, or post-hoc
source table. Every lifting, multimodular, extension-field, FFT, failure, output,
rank, factor-log, blind-descent, and memory cost must be converted to
`lambda,mu<=0.45` in the IDEA-121 model.

No checked source supplies this reduction. The KU branch therefore remains
deferred, not positive.

## Exact Controls For The Runnable Gate

For each `B` in `{4,6,8,12,16,24,32}`, independently verify:

- shared circuit size `B^2`, norm degree `B^3`, and planted output degree `B`;
- literal square-subsystem degrees `B^4,B^4,B^5,B^5`;
- optimistic geometric-resolution matrix size `2*B^3` and its ratio to
  `B^(5/2)`;
- admitted square-prefix degrees and their ratios to rho;
- generic SLP GCD/factor input degree `D=B^3` exceeds the rho proxy;
- the derivation preserves the distinction between a scoped route negative and
  an unconditional arithmetic-circuit lower bound.

## Primary References

- Giusti, Heintz, Morais, Morgenstern, and Pardo,
  [Straight-Line Programs in Geometric Elimination Theory](https://arxiv.org/abs/alg-geom/9609005).
- Kaltofen,
  [Greatest Common Divisors of Polynomials Given by Straight-Line Programs](https://users.cs.duke.edu/~elk27/bibliography/88/Ka88_jacm.pdf).
- Kaltofen,
  [Factorization of Polynomials Given by Straight-Line Programs](https://users.cs.duke.edu/~elk27/bibliography/89/Ka89_slpfac.pdf).
- Kedlaya and Umans,
  [Fast Polynomial Factorization and Modular Composition](https://doi.org/10.1137/08073408X).

## Decision Boundary

The intrinsic-degree and generic-SLP routes are closed only in the stated
models. IDEA-121 remains deferred behind the direct KU-compatible
circuit/common-norm reduction. No relation collection, factor-log system, blind
descent, or generic ECDLP speedup has been produced.
