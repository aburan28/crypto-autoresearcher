# Elliptic-Net Block Zero V1 Analysis

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`REVISE INTERPRETATION`.

No family passes the recurrence-signal gate. This is not an ECDLP
impossibility result and does not rule out nonlinear elliptic-net,
function-field, divisor, implicit circuit, or projective-gauge-invariant
representations.

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
- same-code deterministic normalized rerun: exact.

The sequence length is diagnostic. It is longer than the attack `A` source
and must not be treated as free relation support.

## Main Observation

Every root sequence has Berlekamp-Massey order exactly `L/2`:

| q | B | L | progression planted | random-A planted | progression held-out |
|---:|---:|---:|---:|---:|---:|
| 953 | 5 | 40 | 20 | 20 | 20 |
| 3919 | 8 | 64 | 32 | 32 | 32 |
| 15583 | 10 | 80 | 40 | 40 | 40 |

The values are identical across all four coordinate families for the frozen
raw RCB projective representation. This is the generic finite-sample profile,
not evidence of a short recurrence.

A recurrence trained on the first two-thirds of each planted progression
root misses `13-14`, `22`, and `27` held-out terms at the three sizes. The
planted root annihilator fails on the held-out-target root in exactly
`20`, `32`, and `40` positions. No target pair shares an exact connection
polynomial.

For every tested raw node sequence, the linear system for fixed raw Somos-4
coefficients is inconsistent. Thus neither linear recurrence fitting nor a
direct rank-one elliptic-divisibility/Somos-4 identity compresses these
frozen projective-gauge root products.

The raw result's `violations` value is an inconsistency sentinel equal to the
number of available equations when no exact fit exists. It is not the
minimum residual over all coefficient pairs and must not be read as “every
equation fails under a best fit.”

## Level-by-Level Result

The negative begins at the leaves in the frozen representation. For every
curve, family, target, and progression/random variant:

- median leaf BM order is `L/2`;
- median BM order remains `L/2` at every dyadic level;
- held-out-exact fraction is zero at every level;
- sibling exact-annihilator fraction is zero at every nontrivial level;
- sibling cross-recurrence exact fraction is zero.

A fixed raw tuple locator

`i -> h_Q(P0+iD,r1,r2,r3,r4)`

therefore already looks random to the tested linear recurrence model.
Multiplying raw leaves does not create a shared linear state.

This is stronger than a root-only miss, but it remains finite-sample and
model-bound. It is not invariant under projective rescaling.

## Controls

For every field:

- the planted order-four linear sequence is recovered at order four and
  predicts every held-out term;
- the functional division-polynomial elliptic divisibility sequence has zero Ward
  residual and an exact induced Somos-4 fit;
- the deterministic random sequence has BM order `L/2` and no exact
  Somos-4 fit;
- the product of six independently planted order-two sequences also has BM
  order `L/2`.

The EDS control validates the fitter but is not matched to a translated,
gauge-dependent rank-two net slice. The last control shows that pointwise
products can rapidly expand linear complexity even when each factor has
compact linear state.

## Exact Zero Semantics

Canonical representatives preserve witness support because the affine group
sum is symmetric in the four identical `R` slots and the norm locator is zero
exactly on equality. They do not preserve raw nonzero locator values or
ordered multiplicity.

Every planted root has at least one zero. Balanced-tree descent reaches a
zero leaf, and the recovered complete-addition point equals the target.
Observed planted-root zero counts range from 2 to 8.

An independent permutation probe on the first random-x cell found that all
24 permutations of tuple `(0,1,2,3)` have one affine point sequence and one
zero mask but 24 distinct raw locator-value sequences. The RCB projective
scale is therefore an active representation confounder: nonzero rescaling
multiplies the quadratic locator by a nonzero square while preserving every
zero.

## Charged Cost

Logical packed payload per reported target tree:

| q | leaves | nodes | field elements | bytes | state / B^2.5 |
|---:|---:|---:|---:|---:|---:|
| 953 | 70 | 143 | 5,720 | 11,440 | 102.32 |
| 3919 | 330 | 664 | 42,496 | 84,992 | 234.76 |
| 15583 | 715 | 1,434 | 114,720 | 229,440 | 362.78 |

Across the three points, the fitted slopes against `q` are approximately:

- canonical leaves: `0.833`;
- materialized tree state: `1.074`;
- complete-addition construction calls: `1.081`.

These byte counts are not peak resident memory. They omit Python objects,
simultaneously live target state, memory traffic, and BM analysis workspace,
and may alias carried nodes. The measured RSS is process-wide and does not
validate the packed table.

These slopes are toy diagnostics. Symbolically, canonical leaves are
`Theta(B^4)`, and evaluating or storing length-`Theta(B)` sequences is
`Theta(B^5)`. The explicit construction is therefore much worse than rho and
cannot be reclassified as preprocessing-free.

## Strongest Valid Conclusion

Under the frozen left-associated RCB projective gauge, tested curves, factor
bases, targets, sequence length `L=8B`, and the homogeneous-linear plus raw
direct-Somos-4 models:

> No order-at-most-`2B` annihilator exists for the raw root prefixes; tested
> sibling minimal polynomials are distinct; and explicit block-product
> construction remains a `Theta(B^5)` diagnostic.

This rules out the frozen raw-RCB-gauge homogeneous-linear/direct-Somos gate
on these toy rows. It does not establish a zero-set-invariant recurrence
negative and does not rule out elliptic nets themselves.

## What Remains Open

Ward's elliptic-net structure is nonlinear. The functional positive control
shows that exact nonlinear recurrence can coexist with BM order `L/2`.
Therefore the most useful successor is not a longer BM sweep by itself.

The next experiment must first remove the projective confounder. It should
compare raw, scale-stripped or intrinsic, randomly rescaled, permuted, and
reparenthesized locator sequences at `L in {8B,16B,32B}` and solve a joint
bounded-order annihilator system. The verifier must independently reconstruct
the zero masks and recurrence claims.

After that invariant preflight, represent each fixed locator as a divisor or
rank-two elliptic-net slice and ask whether a block product can be composed
by adding compact divisor data before specialization. A concrete formulation
uses the rank-two net polynomial for `(D,T_t)`, where
`T_t=P0+S_t-Q`, and forms a block norm over the coordinate algebra of the
four-sum divisor. It must charge:

- divisor degree growth under block multiplication;
- target dependence of the divisor and normalization constants;
- state needed to evaluate a block at one progression index;
- exact zero descent and multiplicity;
- comparison to explicit `B^4` leaves and generic fixed-base preprocessing.

If divisor degree grows linearly with block size and no cancellation or
quotient exists, that becomes the reusable nonlinear obstruction. If a
target-independent quotient keeps degree sublinear, it would be a genuinely
new compiler lead.
