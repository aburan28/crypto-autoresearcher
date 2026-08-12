# Independent Theory Review

Reviewer task `019fafb4-7445-73e2-8c2a-a46653b91276` analyzed the exact
left-associated complete RCB circuit after the norm-rank result.

## Status

- `RESTRICTED THEOREM`: central ranks satisfy
  `rank_2|3(h)<=48` and `rank_3|2(h)<=24`.
- `RESTRICTED THEOREM`: for every integer `e>=1`,
  `rank_2|3(h^e)<=48e` and `rank_3|2(h^e)<=24e`, subject to ambient
  dimensions.
- `RESTRICTED THEOREM`: low rank alone reduces zero localization to
  finite-field orthogonal vectors or projective point-hyperplane incidence;
  it does not provide a zero-reporting algorithm.
- `RESTRICTED NEGATIVE RESULT`: explicitly generating or scanning all central
  factor vectors costs `q^(3/5+o(1))`.
- `CONJECTURE`, `NOVELTY-UNVERIFIED`: implicit coordinate geometry may still
  permit a batched incidence algorithm outside the explicit-factor model.

## Circuit-Prefix Rank Theorem

Let `S_k` be the projective point after the first `k` inputs. There are `5-k`
complete additions after `S_k`. The norm locator is quadratic in the final
output and each following RCB addition doubles degree in its left state, so
its homogeneous degree in `S_k` is

`d_k = 2 * 2^(5-k) = 2^(6-k)`.

For a smooth plane cubic, the degree-`d` homogeneous coordinate-ring piece
has dimension `3d` for `d>=1`. Reducing the locator modulo the cubic equation
and expanding in a basis of that piece gives an exact separated expression

`h(left,right) = sum_j phi_j(S_k(left)) c_j(right)`.

Therefore, for source shape `[M,B,B,B,B]`,

| cut | exact upper bound |
|---:|---:|
| 1 | `min(M,B^4,96)` |
| 2 | `min(MB,B^3,48)` |
| 3 | `min(MB^2,B^2,24)` |
| 4 | `min(MB^3,B,12)` |

Replacing `h` by `h^e` multiplies the degree by `e`, yielding

`rank_k(h^e) <= min(left_k,right_k,3e*2^(6-k))`.

This explains the observed `h^2` ranks `96/48`. At `e=8`, the bounds
`384/192` exceed the tested central ambient dimensions, so the observed
saturation is permitted. Applying the bound to the Fermat indicator
`1-h^(p-1)` is asymptotically useless.

## Algorithmic Boundary

At cut 2, the factor sides have sizes

`MB=q^(2/5+o(1))` and `B^3=q^(3/5+o(1))`;

cut 3 reverses them. Explicit vector generation or scanning therefore already
costs at least `q^(3/5+o(1))`. Testing all pairs costs `q^(1+o(1))`.

A rank-only zero finder would solve arbitrary orthogonal-vector instances in
`F_p^24` or `F_p^48`. Known small-characteristic finite-field methods do not
directly help when `p` grows with `q`.

The negative is restricted to explicit factors. It does not cover implicit
coordinate multipoint evaluation, resultants, nonlinear selectors, alternate
addition trees, sparse support methods, or target-amortized algorithms.

## Next Proof And Experiment

Symbolically reduce the frozen circuit at cuts 2 and 3 into fixed bases of the
degree-16 and degree-8 coordinate-ring pieces. Emit the 48- and 24-coordinate
factors directly, without constructing the five-axis tensor, and verify
`U V^T=h` on every frozen cell.

Then determine whether target dependence acts through a fixed low-degree
transformation and whether the factor images have basis-invariant nonlinear
geometry supporting an incidence index below the explicit `q^(3/5)` floor.
