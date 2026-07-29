# Experiment Contract: Affine Secant-Slope Representative Compiler

## Protocol status

Status: `HYPOTHESIS`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`.

Execution status: `review_required`.

Active resource budget: zero. Maximum runs: zero. No implementation or
execution is authorized.

## Hypothesis

On at least two of three generated seven-bit ordinary prime-order curves, an
actual affine line-invariant rule for choosing one witness inside each
nonidentity `2F` output class produces exact retained eight-term support above
the empirical 95th percentile of 31 within-class hash-ranked controls under the
same factor base, witness classes, cap, and exact optimizer.

## Null hypothesis

Conditioned on the curve, factor base, two-sum output classes, witness
multiplicities, cap, and optimizer, affine secant/tangent parameters do not
improve recursive closure. Any observed candidate score is consistent with the
finite matched representative-choice controls.

## Parameters

- Field and curve family: generated short-Weierstrass curves over seven-bit
  prime fields.
- Curve rejection: singular, composite group order, trace `0` or `1`, or
  `j`-invariant `0` or `1728`.
- Curve seeds: `731001`, `731002`, `731003`.
- Factor base: one frozen sign-complete random-x set of size `B=6` per curve.
- Recursive structure: the exact SGCP degree-two representative table,
  degree-four conflict graph, cap `C=floor(q/2)`, and retained eight-term
  support objective inherited from `EXP-SGCP-EMBED-001/002`.
- Candidate and controls see affine points and public source indices only.
  Scalar indices are prohibited.

## Candidate compiler

For every `R` in `2F \ {O}`, define

```text
W_R = {{P_i,P_j}: P_i + P_j = R and i <= j}.
```

For each nonvertical witness compute:

```text
secant: lambda = (y_j-y_i)/(x_j-x_i)
tangent: lambda = (3*x_i^2+a)/(2*y_i)
intercept: nu = y_i-lambda*x_i
```

Inverse or vertical pairs produce the identity and remain outside the
nonidentity representative table. The candidate chooses the lexicographically
least tuple `(lambda,nu,i,j)` inside each `W_R`.

## Matched controls

1. Formal-lex: choose the lexicographically least `(i,j)` inside each `W_R`.
2. Hash nulls: for control indices `0..30`, rank every witness inside each
   `W_R` with domain-separated SHA-256 and select the least digest.

Every compiler uses the identical curve, factor base, output classes,
multiplicity profile, degree-four universe, cap, and exact optimizer. Hash
controls are a finite deterministic null, not a random-oracle theorem.

## Metrics

Charge each compiler separately:

- unordered pair enumeration and identity, inverse, secant, and tangent
  branches;
- field additions, subtractions, multiplications, squarings, and inversions;
- EC additions;
- hash calls and input bytes;
- `|2F|`, all `|W_R|`, the multiplicity histogram, representative entries,
  and canonical bytes;
- degree-four candidates, eligible maxima, conflict edges, constrained labels,
  public edges, and exact `|4F|`;
- retained maxima, exact eight-term support, support divided by `q`, and
  support per constrained label;
- optimizer nodes, bound evaluations, proof nodes, and unresolved gap;
- logical bytes read and written, CPU time, wall time, and externally measured
  peak RSS.

## Positive control

The formal-lex compiler must reproduce the frozen `EXP-SGCP-EMBED-001`
semantics on its registered fixture before any new curve result is accepted.

## Negative control

The 31 within-class hash controls hold all output classes and multiplicities
fixed while removing the affine line ordering.

## Success criterion

Promote only if the candidate:

- exceeds the empirical 95th percentile of retained eight-term support among
  the 31 hash controls on at least two of three valid curves;
- differs from formal-lex on at least 10 percent of nonsingleton witness
  classes;
- passes exact replay of the public source table, injectivity, associativity,
  unique factorization, acyclicity, final-edge exclusion, and witness lift;
- has a complete independently reproduced cost and optimizer ledger.

## Falsification criterion

Narrow the hypothesis if the candidate fails the percentile gate on every
valid curve, the witness classes are effectively all singletons, or any exact
semantic check fails. Optimizer exhaustion, resource refusal, a partial
control matrix, or infrastructure failure is `INCONCLUSIVE`.

## Interpretation boundary

A passing result would be a coordinate-specific structured-embedding signal at
toy scale. It would not establish relation generation, matrix rank, individual
logarithms, a compiled index-calculus attack, an exponent improvement, or a
Pollard-rho break. A later study must test admissible coordinate rescaling,
larger sizes, advice bytes, online work, rank, and descent.

## Next concrete action

Obtain independent theory and red-team reviews of this zero-run contract and a
dedicated literature check before implementing either producer or verifier.
