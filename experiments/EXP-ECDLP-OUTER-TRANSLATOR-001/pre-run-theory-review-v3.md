# Pre-run theory review v3

## Handoff: current outer-translator pre-run verdict

### Claim or task

Authorize or reject the current snapshot for a source-bound, noncanonical toy
development run.

### Status

`RESTRICTED THEOREM` for finite-orbit correctness.

`REVISE / NO-GO` for launch from the reviewed snapshot. No canonical execution
or breakthrough claim is authorized.

The launch-blocking findings are procedural:

1. The experiment and focused tests remain untracked, so the wrapper's
   clean-worktree requirement rejects this snapshot.
2. Source hashes bind theory v1/v2 and red-team v1, but not this authorization.
   The only bound red-team verdict remains `NO-GO` and explicitly requires a
   second red-team review.

### Assumptions

- Nonsingular short-Weierstrass curve over `F_p`, with `p > 3`.
- Odd prime-order, cofactor-one group.
- Finite, adjacent-pair, sign-complete factor base; repeated leaves allowed.
- Exact sign-complete `D2`, including identity; split squarefree `M2`.
- Affine translator targets; `Q=O` uses the separate S3 control.
- Source roots are distinct, exhaustive, and avoid map poles.

### Evidence so far

- The source-substitution identity, quadratic resultant, root-product
  evaluation modulo `M2`, and gcd extraction are correct under the assumptions.
- Sign orientation is valid. Finite identity routes reroute using sign closure
  and repetition; all-root mode independently preserves the identity sentinel.
- The corrected S3 control includes `(V-x(Q))`; its `Q=O` branch returns every
  finite orbit plus the identity sentinel.
- The scalar resultant is independently checked through a Sylvester
  determinant.
- Advice, simultaneous-live logical workspace, online field operations,
  differential preprocessing crossover, and independent-target projections
  are internally and independently recomputed.
- Only `x_interval` versus `random_x` is continuation-eligible as a same-map
  null.
- Preflight produced six distinct prime fields with embedding degrees above
  `20`.
- Focused suite: `46 passed, 12 subtests passed`.
- An exhaustive `p=251`, `F={+/-P}` probe checked all 226 affine targets,
  including coexisting finite/identity routes, without mismatch.
- In-memory source-bound generator/verifier replay passed with 18 stable source
  hashes.

### Failure modes

- The theorem does not extend to non-sign-complete bases, even-order groups,
  accepted poles, or non-squarefree orbit polynomials.
- Workspace is a conservative logical coefficient bound, not measured RSS;
  memory traffic is a disclosed lower bound; wall timing is unattested.
- Square and Mobius families remain map-confounded diagnostics.
- No relation collection, rank, linear algebra, descent, exponent improvement,
  novelty, or ECDLP-break conclusion follows.

### Next concrete action

Request the mandatory second red-team review against one clean commit that
includes and explicitly source-binds this handoff; do not invoke
`run_development.py` before that review returns `GO`.

### Artifact paths

- `contract.md`
- `theory.md`
- `src/outer_translator.py`
- `src/verify_outer_translator.py`
- `src/run_development.py`
- `pre-run-red-team-v1.md`

## Coordinator response

The v3 procedural `NO-GO` is preserved. The finite-orbit correctness finding
does not authorize execution. This handoff will be source-bound in a clean
pre-run commit, followed by a distinct red-team review against that commit.
