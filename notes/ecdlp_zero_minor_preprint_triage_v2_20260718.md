# Zero-minor ECDLP preprint triage v2, 2026-07-18

## Handoff: corrected enumeration and theorem audit

### Claim or task

Audit arXiv:2607.09814v1 using its actual outer-choice, signature-hash, and
completion counts; test the printed zero-minor theorems; and compare expected
total work with rho.

### Status

`NEGATIVE RESULT`, scoped to the explicit enumerative attack and its stated
`Theta(1/p)` marginal-success model. `preprint_triage_20260718.md` at SHA256
`335286cd9561e0d5d9c9b68fd867d72b41eb5317b29d6dba5703ffadf73f181f`
is preserved as the historical first pass; this v2 supersedes its simplified
single-count analysis.

The preprint does not establish a polynomial-time or below-rho ECDLP
algorithm. Its literal Theorem 1 has a small counterexample, and a later proof
has a dimension mismatch. A genuinely non-enumerative zero-minor algorithm is
not ruled out.

Primary source:

- Ayan Mahalanobis, [A Guess and Determine Attack on the Elliptic Curve
  Discrete Logarithm Problem](https://arxiv.org/abs/2607.09814),
  arXiv:2607.09814v1, 2026.

### Assumptions

- Put `L=log2(p)`, with the paper's `ell=Theta(L)` and
  `ell'=ell/2 approximately 1.5*L`.
- Every outer choice, small-kernel computation, signature hash, completion,
  storage word, retry, and parallel worker is charged.
- The paper's marginal completion probability is accepted as

  ```text
  q0=(p-2*ell'+1)/(p*(p-ell'+1))=(1+o(1))/p.
  ```

- Rho's `Theta(sqrt(p))` group operations are the single-target classical
  baseline.

### Evidence so far

#### Correct count separation

For defect `d`, the attack has three different counts:

```text
N_b = binom(ell',d)
```

outer fixed-`b` choices,

```text
H_d = binom(ell'+d,d-1)
```

`(d-1) by d` kernel/signature hash entries per `b`, and

```text
C_d = binom(ell'+d,d)
```

possible `d by d` completions per `b`. They satisfy

```text
H_d/C_d=d/(ell'+1).
```

The preprint conflates these surfaces: choosing `ell'-d` elements from
`[ell']` yields `N_b`, not `C_d`, while Algorithm 1's `(d-1)`-row subsets have
count `H_d`, not `C_d`.

The paper estimates one-`b` success by

```text
1-(1-q0)^C_d.
```

The required independence is unproved and overlapping completion subsets are
dependent. The rigorous union bound is enough:

```text
Pr[one b succeeds] <= C_d*q0=(1+o(1))*C_d/p.
```

For fixed `d`, `C_d=Theta(L^d)` and success is `p^(-1+o(1))`. If `d=o(L)`,

```text
log C_d <= d*log(e*(ell'+d)/d)=o(L),
```

so nonnegligible one-`b` success requires `d=Theta(L)`. The regime in which
the determine step is polynomial for fixed `d` is therefore the regime in
which its success is negligible.

One full pass over all `b` values performs

```text
N_b*H_d
```

small-kernel computations and covers at most `N_b*C_d` completions. For fixed
`d`, these are `Theta(L^(2d-1))` and `Theta(L^(2d))`. Even optimistically
treating all completions as distinct independent trials, repetition to success
costs expected kernel work

```text
(p/(N_b*C_d))*(N_b*H_d)
  = p*d/(ell'+1)
  = Theta(p/L)  for fixed d,
  = Theta(p)    for d=Theta(L).
```

Pooling success across all `b` choices does not rescue the exponent. The most
optimistic entropy balance `log_p(N_b)+log_p(C_d)>=1` occurs near
`d approximately 0.09122*L`, where the two factors are approximately
`p^0.496` and `p^0.504`; kernel/minor traffic remains `p^(1-o(1))`, far above
rho. Gray codes, rank-one updates, hashing, and parallelism can change
polynomial factors or latency, not this charged candidate volume.

#### Literal theorem defects

Theorem 1 is false as printed. Over any field, take

```text
K = [[1,1,0,1],
     [1,1,1,0]].
```

The final two columns are the required anti-diagonal block, and the first two
dense columns form a zero `2 by 2` minor. But selecting only the first dense
column gives `K'=(1,1)^T`, which has no zero `1 by 1` minor. Thus

```text
K has a zero maximal minor
```

does not imply that every selected dense submatrix `K'` has a zero maximal
minor. The valid direction is narrower: a zero minor already found in the
selected `K'` can be extended with appropriate sparse columns.

Theorem 4's printed proof also states `|Upsilon|=ell` where the construction
needs `|Upsilon|=ell-d`; only then does adjoining `d-1` hyperplanes produce a
penultimate intersection of `ell-1` hyperplanes. The intended statement may
be repairable, but the printed proof does not establish it.

These correctness issues are independent of the scaling negative. Even a
repaired zero-minor implication leaves the explicit attack at
`p^(1-o(1))` enumerative work under its own success model.

### Failure modes

- Treating the overlapping-completion probability as an exact independence
  formula.
- Using `C_d` interchangeably for outer choices, hashes, and completions.
- Holding `d` fixed in work while allowing it to grow for success.
- Reporting the integer-only probability simulator as an ECDLP run.
- Omitting retries and total work when parallelizing.
- Extending this negative result to every zero-minor formulation.

### Next concrete action

Before any implementation claim, repair the zero-minor theorems, prove a
first/second-moment bound for target-sum `d`-subsets, and restate runtime using
`N_b,H_d,C_d`; require expected total work `o(sqrt(p))` for a below-rho claim.
The only potentially live successor is a genuinely sublinear, non-enumerative
search over the signature family.

### Artifact paths

- `notes/ecdlp_zero_minor_preprint_triage_20260718.md`
- `notes/ecdlp_zero_minor_preprint_triage_v2_20260718.md`
