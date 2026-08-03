# Pre-run theory review v2

## Handoff: repaired finite-orbit translator launch decision

### Claim or task

Determine whether the repaired finite-orbit translator and exact `D2+D3`
comparator are ready for a source-bound, noncanonical toy development run.

### Status

`RESTRICTED THEOREM` for the finite-orbit construction under the assumptions
below. `REVISE / NO-GO` for the reviewed development launch snapshot.

This decision concerns incomplete controls and accounting. It is not a
refutation of the coordinate-translator hypothesis. A later `GO` would permit
toy development evidence only, never an exponent or ECDLP-break claim.

### Assumptions

- Nonsingular short-Weierstrass curve over `F_p`, with `p > 3`.
- Odd prime-order, cofactor-one subgroup.
- Nonempty sign-complete factor base in adjacent sign pairs.
- Repeated leaves are allowed.
- `D2=F+F` includes identity, is sign complete, and retains exact witnesses.
- `M2` is the split squarefree polynomial of nonidentity D2 x-orbits.
- Translator targets are affine; `Q=O` is a separate control.
- Source branches cover every factor x-root exactly and have no accepted poles.
- Advice, audit-only data, target workspace, and replay remain segregated.

### Evidence so far

For `R=X(D2 minus {O})`, define

```text
G_Q(V,W) = product_{u in X_F} f4(u,V,W,x(Q))
H_Q(V)   = product_{w in R} G_Q(V,w) mod M2(V).
```

For every `v in R`, `H_Q(v)=0` iff some accepted factor x-root and finite D2
x-root satisfy the configured `f4` relation. Rational coordinates plus sign
closure lift this to an exact signed five-leaf route. A missing finite-side
identity route can be rerouted using

```text
Q = A + f = A + (-f) + (2f).
```

This uses sign closure, odd order, and repeated leaves. The `A=O` route has no
x-coordinate: first-witness mode may stop at a finite witness, while all-root
mode must report the identity sentinel iff `Q` lies in D3. The repaired
implementation and coexisting-route regression enforce this distinction.

The corrected affine S3 control is

```text
(V-x(Q)) product_{w in R} f3(V,w,x(Q)) mod M2(V).
```

The `F={+/-G}, Q=2G` regression shows that the uncorrected product misses the
identity half and the corrected control returns it.

For the symmetry-compressed D3 comparator, one x key and one canonical
orientation witness are sufficient. Query orientation is derived from the
computed complement y-coordinate, and the negative witness is obtained by
toggling every adjacent sign index with `index xor 1`. No hidden y-coordinate
advice is required.

The reviewed cost boundaries include:

```text
D2 build attempts                  = B(B+1)/2
D3 build attempts                  = B*|D2|
deg_V(G_Q), deg_W(G_Q)             <= 4*(B/2)
dense coefficient bound for G_Q   <= (4*(B/2)+1)^2
unreduced deg_V(H_Q)               <= 4*(B/2)*|R|
reduced deg(H_Q)                   < |R|
target-symbolic dense bound        = |R|*(4*(B/2)*|R|+1)
```

These are explicit-root-product bounds, not lower bounds for implicit
resultants, product trees, modular composition, or shared multipoint methods.

Focused tests at the reviewed snapshot passed:

```text
42 passed, 12 subtests passed
```

### Launch-blocking findings in the reviewed snapshot

1. Source binding was impossible because `pre-run-red-team-v1.md` did not yet
   exist, and the generator bound theory v1 but not this v2 decision.
2. Peak target workspace counted only the largest retained polynomial instead
   of simultaneously live source, product, and reduction state.
3. The mandatory `Q=O` S3 control was stated but neither executed nor emitted.
4. Independent verification did not yet invoke its coordinate compatibility,
   source-map, advice, and workspace recomputations.
5. Coordinate families and `random_x` used different supported targets, so the
   matched comparison was not actually target matched.
6. Translator batch/amortized totals were not emitted, preprocessing crossover
   used translator preprocessing rather than the nonnegative differential over
   the comparator, and continuation aggregation was per-row rather than
   conjunctive over both seeds and every size.

Any one of findings 1 or 2 invalidated a source-bound cost run. Findings 3-6
prevented a claim that every contract control and continuation gate had run.

### Failure modes

- Treating finite-orbit correctness as complete identity semantics.
- Losing an all-root identity sentinel when finite routes coexist.
- Comparing x-orbit advice with duplicated affine D3 keys.
- Undercharging simultaneous polynomial state.
- Comparing coordinate families on different targets.
- Reporting amortization without translator batch rows.
- Letting replay substitute for independent coordinate and accounting checks.
- Promoting a toy functional pass without relation quality, rank, linear
  algebra, or target descent.

### Next concrete action

Repair and source-bind all six findings, then request a distinct v3 theory
review before any evidence-bearing development run.

### Artifact paths

- `contract.md`
- `theory.md`
- `implementation.md`
- `pre-run-theory-review-v1.md`
- `src/exact_floor.py`
- `src/polynomial_engine.py`
- `src/outer_translator.py`
- `src/verify_outer_translator.py`
- `tests/test_outer_translator.py`
- `tests/test_outer_translator_floor.py`
- `tests/test_outer_translator_polynomial.py`

## Coordinator response

The v2 `REVISE` decision is preserved. During the review, the coordinator had
already begun repairing findings 2 and 4; those changes do not retroactively
turn this snapshot into a `GO`. Findings 1, 3, 5, and 6 remain launch blockers,
and a separate v3 review is required after all repairs and tests.
