# Elliptic-Net Block Zero V1 Analysis

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

No family passes the recurrence-signal gate. This is not an ECDLP
impossibility result and does not rule out nonlinear elliptic-net,
function-field, divisor, or implicit circuit representations.

## Exact Run

- source commit: `560afccdb186664e7a98e544347d670c260c243b`;
- curves: `q in {953,3919,15583}`;
- families: random-x, source-PRF-x, x-interval, rational-union;
- `B in {5,8,10}`;
- sequence length: `L=8B in {40,64,80}`;
- canonical four-`R` leaves: `70,330,715`;
- 12 family rows, two `A` variants, two targets per variant;
- wall time: 21.15 seconds;
- peak RSS: 45,154,304 bytes;
- zero projective, affine-replay, locator, or planted-descent mismatch;
- independent normalized rerun: exact.

The sequence length is diagnostic. It is longer than the attack `A` source
and must not be treated as free relation support.

## Main Observation

Every root sequence has Berlekamp-Massey order exactly `L/2`:

| q | B | L | progression planted | random-A planted | progression held-out |
|---:|---:|---:|---:|---:|---:|
| 953 | 5 | 40 | 20 | 20 | 20 |
| 3919 | 8 | 64 | 32 | 32 | 32 |
| 15583 | 10 | 80 | 40 | 40 | 40 |

The values are identical across all four coordinate families. This is the
generic finite-sample profile, not evidence of a short recurrence.

A recurrence trained on the first two-thirds of each planted progression
root misses `13-14`, `22`, and `27` held-out terms at the three sizes. The
planted root annihilator fails on the held-out-target root in exactly
`20`, `32`, and `40` positions. No target pair shares an exact connection
polynomial.

All available Somos-4 equations fail:

- 36 of 36 at `L=40`;
- 60 of 60 at `L=64`;
- 76 of 76 at `L=80`.

Thus neither linear recurrence fitting nor a direct rank-one
elliptic-divisibility/Somos-4 identity compresses these root products.

## Level-by-Level Result

The negative begins at the leaves. For every curve, family, target, and
progression/random variant:

- median leaf BM order is `L/2`;
- median BM order remains `L/2` at every dyadic level;
- held-out-exact fraction is zero at every level;
- sibling exact-annihilator fraction is zero at every nontrivial level;
- sibling cross-recurrence exact fraction is zero.

A fixed tuple locator

`i -> h_Q(P0+iD,r1,r2,r3,r4)`

therefore already looks random to the tested linear recurrence model.
Multiplying leaves does not create a shared linear state.

This is stronger than a root-only miss, but it remains finite-sample and
model-bound.

## Controls

For every field:

- the planted order-four linear sequence is recovered at order four and
  predicts every held-out term;
- the division-polynomial elliptic divisibility sequence has zero Ward
  residual and an exact induced Somos-4 fit;
- the deterministic random sequence has BM order `L/2` and no exact
  Somos-4 fit;
- the product of six independently planted order-two sequences also has BM
  order `L/2`.

The last control identifies the likely mechanism: pointwise products rapidly
expand linear complexity even when each factor has compact linear state.

## Exact Zero Semantics

Canonical multisets preserve the ordered locator zero set because the
complete group sum and locator are symmetric in the four `R` inputs. The
root is zero at an index exactly when at least one canonical tuple is a
witness.

Every planted root has at least one zero. Balanced-tree descent reaches a
zero leaf, and the recovered complete-addition point equals the target.
Observed planted-root zero counts range from 2 to 8.

## Charged Cost

Per target tree:

| q | leaves | nodes | field elements | bytes | state / B^2.5 |
|---:|---:|---:|---:|---:|---:|
| 953 | 70 | 143 | 5,720 | 11,440 | 102.32 |
| 3919 | 330 | 664 | 42,496 | 84,992 | 234.76 |
| 15583 | 715 | 1,434 | 114,720 | 229,440 | 362.78 |

Across the three points, the fitted slopes against `q` are approximately:

- canonical leaves: `0.833`;
- materialized tree state: `1.074`;
- complete-addition construction calls: `1.081`.

These slopes are toy diagnostics. Symbolically, canonical leaves are
`Theta(B^4)`, and evaluating or storing length-`Theta(B)` sequences is
`Theta(B^5)`. The explicit construction is therefore much worse than rho and
cannot be reclassified as preprocessing-free.

## Strongest Valid Conclusion

Under the exact complete-addition locator, tested curves, factor bases,
targets, sequence length `L=8B`, and the linear-recurrence plus direct
Somos-4 models:

> No short, shared, target-independent annihilator appears at any dyadic
> block level. Explicit block-product construction and storage remain
> `Theta(B^5)` diagnostics.

This rules out the preregistered linear block-zero compiler in this regime.
It does not rule out elliptic nets themselves.

## What Remains Open

Ward's elliptic-net structure is nonlinear. The matched positive control
shows that exact nonlinear recurrence can coexist with BM order `L/2`.
Therefore the most useful successor is not a longer BM sweep by itself.

The next experiment should represent each fixed locator as a divisor or
rank-two elliptic-net slice and ask whether a block product can be composed
by adding compact divisor data before specialization. It must charge:

- divisor degree growth under block multiplication;
- target dependence of the divisor and normalization constants;
- state needed to evaluate a block at one progression index;
- exact zero descent and multiplicity;
- comparison to explicit `B^4` leaves and generic fixed-base preprocessing.

If divisor degree grows linearly with block size and no cancellation or
quotient exists, that becomes the reusable nonlinear obstruction. If a
target-independent quotient keeps degree sublinear, it would be a genuinely
new compiler lead.
