# Zero-minor ECDLP preprint triage, 2026-07-18

## Handoff: guess-and-determine success/work coupling

### Claim or task

Triage Ayan Mahalanobis, *A Guess and Determine Attack on the Elliptic Curve
Discrete Logarithm Problem*, arXiv:2607.09814v1, submitted 2026-07-10, against
its stated success model and rho.

### Status

`NEGATIVE RESULT`, scoped to the preprint's enumerated-candidate algorithm and
success approximation; `REVIEW_REQUIRED` for its signature theorem.

The fixed-defect path is polynomial in `log p` only when its success is
negligible. Constant success forces `Theta(p)` enumerated candidates under the
paper's own model, already worse than `Theta(sqrt(p))` rho. This does not rule
out a different sublinear search over the signature space.

Primary source:

- Ayan Mahalanobis, [A Guess and Determine Attack on the Elliptic Curve
  Discrete Logarithm Problem](https://arxiv.org/abs/2607.09814),
  arXiv:2607.09814v1, 2026.

### Assumptions

- The subgroup order is the paper's prime `p` and `ell=Theta(log p)`.
- The determine stage uses the paper's candidate count
  `C=binom(ell'+d,d)` in its displayed success approximation. Minor indexing
  variants elsewhere in the pseudocode do not change the argument when `C` is
  the number of independently tested candidate signatures.
- The paper's approximation

  ```text
  Pr[success]=1-(1-1/p)^C
  ```

  is accepted for this cost audit.
- The stated algorithm explicitly constructs/tests those `C` candidates, so
  it spends at least one operation or record event per candidate.

### Evidence so far

The elementary union bound gives

```text
1-(1-1/p)^C <= C/p.
```

Therefore success at least a fixed `epsilon>0` requires

```text
C>=epsilon*p.
```

For fixed defect `d`,

```text
C=binom(ell'+d,d)=Theta(ell'^d)=poly(log p),
Pr[success]<=poly(log p)/p.
```

Thus the regime in which the determine step is polynomial in `ell` is not a
constant-success ECDLP algorithm.

Conversely, because `ell'=Theta(log p)`, obtaining `log C=Theta(log p)` from
the binomial coefficient requires `d=Theta(ell')`. Indeed, for
`delta=d/ell' -> 0`,

```text
log binom(ell'+d,d)
  <= d*log(e*(ell'+d)/d)
  = ell'*delta*log(e*(1+delta)/delta)
  = o(ell').
```

So `d=o(ell')` cannot supply nonnegligible success. Once `d=Theta(log p)`, the
paper's fixed-`d` polynomial claim no longer applies. More directly, any
implementation that explicitly constructs/tests all `C` candidates spends
`Omega(C)=Omega(p)` work at constant success, before kernel, minor, hash,
memory, retry, or verification costs. This is asymptotically worse than rho's
`Theta(sqrt(p))` group-operation baseline.

The paper's Table 1 covers only group sizes from 40 through 60 bits and already
shows that a fixed defect loses success as the bit size rises. It explicitly
states that the large-field success probability and the relation between `p`
and `d` are unknown, which is consistent with the bound above.

There is a separate correctness concern. The preprint warns that its theorem
connecting duplicate signature vectors to ultimate intersections may be wrong
because normalized generators need not be unique and two intersections may
share a vector. That warning requires an independent theorem audit; it is not
used in the asymptotic rejection above.

### Failure modes

- Calling `poly(ell)` work a polynomial-time ECDLP attack without multiplying
  by the inverse success probability.
- Holding `d` fixed in the work analysis while allowing it to grow in the
  success table.
- Reporting the fast integer-only probability simulator as an ECDLP run.
- Omitting outer guesses, kernel computations, maximal-minor enumeration,
  signature hashes, memory, and retries.
- Treating the paper's admitted theorem uncertainty as a proved flaw.
- Extending this scoped negative result to every zero-minor or algebraic attack.

### Next concrete action

Prove or disprove the duplicate-signature implication with normalized
one-dimensional kernels, then ask whether the `C=Theta(p)` candidate family has
a coordinate-specific sublinear search that is not already another DLP oracle;
without such a mechanism, do not implement the fixed-defect attack as an ECDLP
candidate.

### Artifact paths

- `notes/ecdlp_zero_minor_preprint_triage_20260718.md`
