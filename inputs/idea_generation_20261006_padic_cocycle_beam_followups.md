# Prime-field ECDLP controlled mechanism follow-ups — 2026-10-06

## Intake status

- Source type: user-directed external follow-up experiments.
- Scope: classical ECDLP in prime-order subgroups of short-Weierstrass curves over prime fields.
- Exclusions: no Pollard-rho collision walk and no index-calculus relation collection.
- Evidence tier: deterministic toy experiments, external to this repository's contract and run-receipt system.
- Canonical status: none. This file allocates no IDEA, hypothesis, experiment, evidence, or decision identifier and changes no official research state.
- Bottom line: five earlier frozen successors failed their gates, then seven structured addition/spectral measurements continued the path. Denominator clearing exposed an exact constructible rank-four numerator; a quotient/remainder rectangle represents the complete quadratic-character orbit with two singular corrections. Target translation recovers every toy log through a labelled square-root point collision, explicitly identifying the resulting decoder as signed, shifted baby-step/giant-step rather than a new method.
- Import rule: treat these measurements as deduplication, control, and stop-rule priors until reproduced under a frozen repository experiment.

The originating code and JSON remain in a separate local repository. Reported provenance locators are:

| Artifact | SHA-256 or commit |
|---|---|
| p-adic decision-rule commit | `d27a568` |
| p-adic implementation commit | `4d06b69` |
| `padic_cocycle_lab.py` | `740dbe3078cbd246b5134944b5aee9073e241fd3541bc22467be4d39dfcabc95` |
| `tests/test_padic_cocycle_lab.py` | `1da80b4c43cb4ed51b1c8a6946dec24f138369011a11ef30616c996c65f59b8b` |
| `results/padic-cocycle.json` | `3c71a839f6e81f09a1903dc7aac94842a5137a78e05670b4d4b8a94db507502f` |
| beam decision-rule commit | `387b958` |
| beam implementation commit | `efbec7d` |
| `beam_exponent_lab.py` | `3e10208bd4f955f8432e51c364d96cadce9531ec77d42c4901ad0c69fde71719` |
| `tests/test_beam_exponent_lab.py` | `f4da6de0276fac21c181a2d2c821c2e5527487ae8123672104ad01f839aa3d3d` |
| `results/beam-exponent.json` | `b9a15961813afe9c8ee5d5830ab9876441d66661fafb8e2654d648faa9c79f7e` |
| sparse-defect decision-rule commits | `cd8939f`, `1249bb8` |
| sparse-defect implementation commit | `df744b2` |
| `translation_defect_lab.py` | `e7239dadc9380404326c66c710a1bc3de72937b6c0b05618251b7a2180c65f12` |
| `tests/test_translation_defect_lab.py` | `ceb2485aa64ad901604582254279f50268cb39958c6e804bd9a76217bfab39fb` |
| `results/sparse-translation-defect.json` | `7314973c8a820cf56f74b633719089074d8dcbbef625d69a621d9c5f3296d7c2` |
| block-Hankel decision-rule commit | `bc973a3` |
| block-Hankel implementation commit | `aa7c91c` |
| `block_hankel_lab.py` | `997bcce5994dda04e4bf775d1396487f55c2a5133364f551618138514a78c801` |
| `tests/test_block_hankel_lab.py` | `8e5b2f84a4a1d3c08b1e373a17c822f67f10eb64f51c98cffb95708ff788276f` |
| `results/block-hankel-state.json` | `6acd64cdf432c65c892969bb0d83158a02b2f99cb960b96bd5b1385a4058eb44` |
| generator-blind decision-rule commits | `d0bb017`, `50df5ab` |
| generator-blind implementation commit | `9be8ee9` |
| `generator_blind_lab.py` | `1b5f9d1b3766c940d504cf099f1420ab5f0b16c8142548be87dce7fe8fce5d74` |
| `tests/test_generator_blind_lab.py` | `9bcdb24e5c80a4725221368acc7d9176767532ab17318e44b12e5651f2be82d3` |
| `results/generator-blind-grammar.json` | `9134f6d0114ca22d4a40b6299250a9775c56f782ae70577bc4f153c4a780f835` |
| addition-kernel decision-rule commit | `d376c7d` |
| addition-kernel implementation commit | `a9fb5d0` |
| `addition_kernel_lab.py` | `eb141c6ed713e85f415a5f3b8b7b5f29fef490db722eb638b5dd15a62485ff86` |
| `tests/test_addition_kernel_lab.py` | `9586bbd995bb5f415b26998209740235cb2f4d766ffeb30e045ef6c014bb6776` |
| `results/addition-kernel-rank.json` | `c97d206dd03c60dd776fd8caca55ed6929213974253779e43bd5050a3f11ad6b` |
| rational-addition decision/layout commits | `2bbaa1d`, `b5ca515` |
| rational-addition implementation commit | `04c592b` |
| `rational_addition_lab.py` | `e4a54969b5b88481b88a96d1872a36f28a32cfac838cde511372a4a1f58fd824` |
| `tests/test_rational_addition_lab.py` | `cfbb3a28693a996e0111e65e6a133696ef038d5aba89874c62910fcf83f63131` |
| `results/rational-addition-structure.json` | `6f3a68202efcce5d2f2c8af03f31fa85245ce9f70c302a4ecf02a80b9802cd7c` |
| Gauss-expansion decision-rule commit | `faf037a` |
| Gauss-expansion implementation commit | `5fb2c97` |
| `gauss_expansion_lab.py` | `8fc4ea1c1ae78533df2a25d1d5e174c7d04d6fb503775a99ef6092f4244f71ab` |
| `tests/test_gauss_expansion_lab.py` | `9415147685f938a4192e5a4e0cce99b93b687ff829cad9c53f36ad6e833a0a12` |
| `results/gauss-character-expansion.json` | `ceac60648d389a6897941534e94a9dd197a34bff66b4bcab32f0984abd356b2c` |
| direct-factor decision-rule commit | `168b34b` |
| direct-factor implementation commit | `22510a9` |
| `four_factor_summation_lab.py` | `1792310cafadc56530387656ce3e808f264399996cebb0281b2cdf62c3c15eb3` |
| `tests/test_four_factor_summation_lab.py` | `6d7c33207ab575d1bc67f759ffb88862a802833be5cf5ac8ee65158cac178a6f` |
| `results/direct-four-factor-summation.json` | `0850b12efe96ab7c5c076ffdcea02f3227a6e517736a4c5b59f6da7ad2fdf6f1` |
| joint-transform decision-rule commit | `ccc20f0` |
| joint-transform implementation commit | `792206b` |
| `joint_transform_lab.py` | `497493d2753386956062d9ef4bd311ed58d3614bd89ca919c35830bac29d1713` |
| `tests/test_joint_transform_lab.py` | `cbe4007b5ace3fc8f6baf69000c67fe6268f1d0002eb42a14b08e6ad966857f8` |
| `results/joint-residue-scalar-transform.json` | `172eaa16734f46b303df5e9e488564eb739a44c0f199b56da510268e07a6a2fb` |
| full-coverage decision-rule commit | `3bcd12e` |
| full-coverage implementation commit | `9fd6f69` |
| `full_coverage_correction_lab.py` | `d291b00ba03122514b7f95b72351fb949ea27e89e66693984c9da2aba93c1222` |
| `tests/test_full_coverage_correction_lab.py` | `140b2d28a1a6aa1a64aeaa7736753cbd724d9849f147d6b6850a86761674f036` |
| `results/full-coverage-sparse-correction.json` | `8f29bd3e30e14aa03f7bfcca30477024af343b1a9aa41baf40abf8c992de5382` |
| translated-target decision-rule commit | `a4770aa` |
| translated-target implementation commit | `331c439` |
| `target_translation_lab.py` | `bc51cb42e2adad6da9c6d958d37e1f602283886c5e675b20f0d798451305f2ea` |
| `tests/test_target_translation_lab.py` | `eb40cc33b23e67a028e60782bdaed3841ff645d9038cad29e9e2ea8989b10fbc` |
| `results/target-translated-collision-decoder.json` | `9b52c7ef77f5b01806fcf68ca5cf820aa646528c43e1ef4351a83f5c5760e3ef` |
| streaming-resultant freeze/audit commits | `18f0d70`, `67a90f3` |
| streaming-resultant implementation/audit commits | `275c0ce`, `1b5991f` |
| `streaming_resultant_lab.py` | `612eb4613a4284cbc75bc6dc0b97616f2ea73f41c9517dab2ffe2ec54c313eb8` |
| `tests/test_streaming_resultant_lab.py` | `64385af442cca70c34d0e54813ab85138ce2f23c81fab201f3603dc92093ae01` |
| `results/streaming-resultant-decoder.json` | `281d5002a9dd7a6a3c8ba99e1d147ec5f7690b1d6ddb1a808f667562caf3d8b7` |
| hashed-moment freeze commit | `3a8699c` |
| hashed-moment implementation commit | `779cd75` |
| `hashed_moment_lab.py` | `e95429d25b20daf0fd77d2d7139d5378690c82b0a25002e6ddd9b331643a3386` |
| `tests/test_hashed_moment_lab.py` | `e79bc65a4db1335c60ff570b0ac0de3add1b28a3ead87d4b19b8928565e5b4c0` |
| `results/hashed-moment-sketch.json` | `49c2a83cc049821f3ccbdae47e05b8174d2e30c3a485456aec7a812349bb24ff` |

All fourteen result payloads omit timing fields and reproduced byte-for-byte. The expanded external suite passed 62/62 tests. These are provenance statements, not repository run receipts.

## H9 — p-adic section-defect cocycle cancellation

### Mechanism

For a public lift section `s:E(F_p)->E(Z/p^2)`, compute the formal-kernel coordinate

```
C(A,B) = t(s(A)+s(B)-s(A+B))/p mod p,
```

where `t=-x/y` is the formal parameter at the identity. The hypothesis was that signed two-point combinations might cancel the arbitrary section contribution that defeated the earlier one-point ordinary-curve lift quotient.

Four public sections were frozen. They shift the lifted x-coordinate by `p*d(x,y)` for `d=0`, `x`, `y`, and `x^2+3y+17`, then solve for the y correction modulo `p`.

Six constant-work formulas were frozen before execution:

1. `C(Q,P)`;
2. `C(Q,Q)`;
3. `C(Q,P)-C(Q,-P)`;
4. the signed parallelogram `C(Q,P)+C(-Q,-P)-C(Q,-P)-C(-Q,P)`;
5. `C(Q,Q)+C(2Q,2Q)`;
6. `C(Q+P,P)-C(Q,P)`.

Each formula could use only public normalization by its values at `O` and `P`. No target labels were fitted.

### Predeclared gates

The arithmetic gate required zero failures of the abelian cocycle identity and commutativity over 128 deterministic triples per curve/section, plus exact recovery by the existing Smart trace-one positive control.

The mechanism gate required one fixed formula to give identical normalized predictions under all four sections and exact canonical logs on at least five of seven ordinary curves.

### Result

The arithmetic gate passed:

- zero cocycle or commutativity failures across nine curves and four sections;
- Smart's known anomalous quotient recovered 96/96 sampled logs on both A163 and A367.

The mechanism gate failed:

- every formula had **0/7** ordinary-curve support;
- no usable formula produced section-invariant predictions;
- best per-section canonical accuracy declined from at most 6.48% on the smallest curves to 0.53% at order 947, consistent with accidental field-sized matches.

This matches the expected obstruction. The formal kernel is the additive group of `F_p`, while the ordinary subgroup has prime order `r != p`; an additive homomorphism between these coprime-order groups is trivial. The anomalous case `r=p` is precisely where Smart's nontrivial linear observable exists.

Disposition: preserve the arithmetic/control harness and scoped negative. Do not expand the formula grammar unless a successor first explains how it evades both section coboundaries and the coprime-order obstruction. Allocate no canonical ID from this packet.

## H10 — scalar-balanced inverse-doubling beam exponent

### Mechanism

The earlier fixed-width beam percentages did not answer whether the correct branch survives in sub-square-root width. This follow-up measured the first power-of-two width reaching 90% recovery for the already frozen height and lifted-carry rankings.

The protocol used:

- every nonidentity target;
- generators `[u]P` for `u in {1,2,3,5}`;
- widths through the complete binary frontier;
- the original deterministic random score;
- a matched permutation of each coordinate score table over nonzero scalar indices;
- complete accounting of equivalent inverse-two multiplications, subtractions, score evaluations, and final candidate verifications.

The frozen primary statistic was equal-weight macro accuracy across scalar bit-length buckets. Width scaling was fit as `W_90=r^alpha` with 2,000 deterministic curve-level bootstrap replicates.

### Predeclared gate

Height or carry could advance only if:

1. the one-sided 99% upper bound on `alpha` was below `1/2`; and
2. its `W_90` was strictly below both its matched score permutation and the random control for every generator on at least five of seven curves.

### Result

| score | primary W90 exponent | one-sided 99% upper bound | curves beating both controls on every generator |
|---|---:|---:|---:|
| height | 0.730762 | 0.974538 | 0/7 |
| carry | 0.621314 | 1.379280 | 0/7 |
| random control | 0.417010 | 1.588964 | n/a |
| permuted height | 0.588414 | 1.342833 | n/a |
| permuted carry | 0.687135 | 1.657458 | n/a |

Both candidates failed both gates. Generator sensitivity was large: within one curve, the first tested `W_90` often varied by a factor of four or eight.

A post-run methodology audit found that equal bucket weighting still gives easy tiny-scalar buckets disproportionate influence. The frozen primary decision was retained. A stricter, non-rescuing largest-bit-length-only diagnostic increased the height and carry exponent estimates to 0.970037 and 0.938425, with upper bounds 1.161027 and 1.279711. This strengthens the negative.

Complete toy orbit tables accelerated the measurement simulator, but were not credited as an attack resource. The scalar-state simulator was tested against the original group-operation solver.

Disposition: retire the frozen height and carry rankings. A successor needs a generator-invariant branch statistic and a predicted sub-square-root survival exponent before another beam sweep. Allocate no canonical ID from this packet.

## H11 — sparse translation-defect equation

### Mechanism and obstruction

For `f` in the Riemann--Roch space `L(mO)`, the frozen proposal sought

```
f(Q+P) - f(Q) = 1
```

outside an explicitly stored exception set. The residual
`g(Q)=f(Q+P)-f(Q)-1` has poles only at `O` and `-P`, with total pole degree at
most `2m`. It is not identically zero on an ordinary order-`r` cycle: summing
over `r` translations would imply `r=0` in `F_p`, but `r != p`. Thus at most
`2m` affine edges agree.

The two edges touching `O` are mandatory exceptions. With the constant
coefficient removed because it cancels under translation, there are `d=m-1`
useful coefficients and

```
e >= max(2, r-2m),
d+e >= ceil(r/2).
```

This is an undercharged linear lower bound before storing exception locations
or correction values. It is scoped to the explicit-exception representation;
it is not a general ECDLP lower bound or a novelty claim.

### Frozen audit and result

The audit used all seven ordinary toy curves, generators `[u]P` for
`u in {1,2,3,5}`, pole orders `2,3,4,8,16,32`, fixed deterministic consensus
samples, permuted-point controls, random-label-difference controls, and a
planted one-defect positive control. The rule and exact secondary comparison
were committed before implementation.

| curve | order | optimized lower bound on `d+e` | bound / `sqrt(r)` | generators beating both controls |
|---|---:|---:|---:|---:|
| E101 | 83 | 42 | 4.610 | 2/4 |
| E127 | 109 | 55 | 5.268 | 2/4 |
| E149 | 139 | 70 | 5.937 | 1/4 |
| E211 | 223 | 112 | 7.500 | 3/4 |
| E283 | 281 | 141 | 8.411 | 2/4 |
| E503 | 499 | 250 | 11.192 | 1/4 |
| E907 | 947 | 474 | 15.403 | 2/4 |

Every arithmetic and planted-defect audit passed. Every EC witness respected
the `2m` divisor ceiling and every required complete system was inconsistent.
No curve beat both matched controls on all four generators, so the empirical
gate scored **0/7**. The timing-free JSON reproduced byte-for-byte.

Disposition: retire the explicit sparse-exception representation. A successor
must derive a compact dense correction rule and an online evaluator before
examining scalar-labelled data. Allocate no canonical ID from this packet.

## H12 — block-Hankel shared state and index inversion

### Mechanism and obstruction

The frozen channel family was `x`, `y`, `x^2`, `xy`, `chi(x)`, and
`chi(x-1)`. If a `d`-dimensional autonomous linear state obeys
`z_(k+1)=A z_k`, Cayley--Hamilton makes every linear output satisfy a
recurrence of degree at most `d`. Therefore the joint state dimension is at
least the maximum scalar-channel complexity. Conversely, any period-`r` vector
sequence has an `r`-state cyclic realization.

The protocol measured Berlekamp--Massey complexity on two periods for all seven
curves and generators `[u]P`, `u in {1,2,3,5}`. Two shared scalar-position
permutations preserved full observable tuples; two independent per-channel
permutations preserved every marginal. A synthetic three-state generator was
the positive control. State-to-index lookup entries and bits were charged
separately.

### Result

The positive control measured complexity three. On all 28 curve/generator
pairs, `x`, `x^2`, and both character channels had complexity exactly `r`,
while `y` and `xy` had `r-1`. Hence the minimum joint autonomous linear-state
dimension was exactly `r`, from 83 through 947. Both control families also had
exact dimension `r` everywhere, so strict control support was **0/7**.

A generic state-to-index table needs `r` entries (581 to 9,470 bits on the toy
ladder), and the hypothesis supplied no sub-square-root decoder. The state gate,
control gate, and independent index-decoder gate all failed. The timing-free
JSON reproduced byte-for-byte.

Disposition: retire the frozen autonomous linear-state model. A successor must
preregister a nonlinear state representation and a direct target-to-index
algorithm with complete advice accounting. Allocate no canonical ID from this
packet.

## H13 — generator-blind coordinate-bit grammar

### Frozen model and controls

The model used a fixed 172-term grammar: centered `x,y`, six public interval
tests, quadratic characters of eight low-degree functions, two character
ratios, all pairwise products, and an intercept. A ridge linear classifier was
trained leave-one-curve-out with no curve identifier, generator multiplier, or
fitted field constant. A point-invariant public hash split scalar-training from
scalar-held-out points.

Each fold trained on generators `[u]P`, `u in {1,2,3,5}`, then evaluated the
fully unseen curve under all four generator relabelings. Thirty-two balanced
random-label and 32 scalar-permutation refits used the same feature matrices,
class weights, coefficient budget, and supplied-label count. The frozen gate
required every generator's one-sided 99% lower advantage to reach 0.05 and its
accuracy to exceed every matched refit, on at least five of seven curves.

### Result

Across all 28 unseen curve/generator evaluations, accuracy ranged from 27.8% to
58.8%. Every 99% lower advantage was negative; the best was -5.1% on the
largest curve. No EC accuracy beat all 64 matched refits, so support was
**0/7**. The fits consumed 824--1,340 known base logs per fold and stored 172
float64 coefficients. Recursive peeling was neither authorized nor run. The
timing-free JSON reproduced byte-for-byte.

Disposition: retire the frozen grammar without feature tuning. A successor
needs a mathematical generator-covariance mechanism derived before another
labelled sweep. Allocate no canonical ID from this packet.

## H14 — baby/giant addition-kernel separation rank

The scalar orbit was reshaped as `k=a+m*b`, `m=floor(sqrt(r))`, and analyzed as
a two-variable addition kernel. Raw `x` matrices had full finite-field row rank.
Complex phase matrices needed 78%--93% of row rank for 99% energy, overlapping
shuffled and random-field controls. At rank `ceil(r^(1/4))`, median separable
Fourier-query error increased from 0.489 to 0.689 and top-16 mode recall fell
from 0.688 to 0.281 over the ladder. All full-rank reconstruction controls
passed. This measurement motivated exact displacement structure rather than a
stop.

## H15 — exact rational-addition factor and displacement

For affine `A=(u,v)`, `B=(s,t)`, direct rearrangement of the addition law gives

```
(s-u)^2*x(A+B) = a(u+s)+2b-2vt+u*s^2+u^2*s.
```

All 28 curve/generator cases verified exact denominator-cleared rank four and
rank-one second Cauchy displacement. Raw output, inverse-square denominator,
and first displacement remained full rank. Both output-control families made
the cleared matrix full rank again. The constructible four-factor storage
fraction fell from 0.844 to 0.258 along the ladder. This is an exact positive
algebraic structure, not an ECDLP solution or novelty claim.

## H16 — Gauss expansion on the rank-four numerator

The quadratic character cancels the square denominator, and its nonzero
additive Fourier coefficients all had magnitude `sqrt(p)` exactly to recorded
precision. At `ceil(sqrt(p))` modes, retained energy fell from 11.0% to 3.4%,
median matrix error was 0.946--0.985, and median rectangle-spectrum error was
0.905--0.969. Deterministic truncation reached 90% sign accuracy near `p/2`
modes; matrix error below 0.25 used the full `p-1` budget. Random-mode and
balanced-function control distributions are retained in full. The next
experiment is direct summation of individual bilinear phase terms from H15's
four factors.

## H17 — direct four-factor phase summation

Direct cells, full-feature aggregation, residue/DFT batching, and a four-factor
Hadamard construction agreed exactly on 28 elliptic and 56 permuted-feature
cases. Full feature tuples never collided. Phase 99%-energy rank fractions had
the same median, `0.857143`, for elliptic inputs and controls; rank-capped tensor
recompression had median matrix error `0.815288` versus `0.807678` for controls.
The exact residue histogram still visited every cell once, but when all
additive modes were requested its modeled work ratio fell from 0.384 to 0.052
over the curve ladder.

## H18 — joint residue/scalar-frequency transform

A mixed-sign 2D transform exactly reconstructed every sampled `(t,q)` phase
and the complete all-`q` quadratic-character spectrum. Its joint support used a
median 96% of cells, dense state expanded from 93 to 895 entries per cell, and
dense 2D work was 1.91--1.96 times the repeated one-dimensional route. The
singular-free step-one rectangle covered only 21.7% down to 6.4% of scalar
sums, motivating a different layout rather than a denser transform.

## H19 — full-coverage sparse singular correction

The masked quotient/remainder layout covered every scalar exactly once. Across
all 28 curve/generator cases, the rank-four character formula held away from
exactly two cells: one doubling at scalar 2 and one inverse pair at scalar 0.
Adding those two explicit corrections reconstructed the full character orbit
and its DFT exactly. Correction relative L2 fell from 0.158 to 0.046 across the
ladder. This is an exact positive algebraic representation, not yet a fast
nonlinear evaluator.

## H20 — target-translated collision decoder

Translating the giant side by `Q=[k]G` makes a same/inverse point collision emit
`k=+/-a-o-m*j`. Every one of 9,096 nonidentity targets was recovered with
`floor(sqrt(r))` baby points and `ceil(r/m)` translated giant points; the
full-coverage mask guaranteed one inverse collision. Permuting the giant
points' scalar labels reduced median recovery to 11.1%, declining to roughly
6% on the largest curve. All 420 sampled translated rank-four/correction
systems were exact. This positive decoder is the standard signed, shifted
baby-step/giant-step meet-in-the-middle mechanism and is retained as a control,
not claimed as novel.

## H21 — streaming resultant decoder

An injective `F_(p^2)` point encoding supports a streaming characteristic
product, derivative, and label numerator. Their quotient at a root recovers the
giant label without a point-equality table. After a cross-ring audit added every
integer lift `g0+j*p<r`, all 9,096 targets still recovered with zero derivative
or subfield failures. The decoder used a 12-field-element working set and
10,636,080 total factor updates. It emitted 936 extra lifts, including 344
validated high-label roots. This is a constant-memory, linear-work
reformulation of the collision control, not an exponent improvement.

## H22 — hashed moment sketches

Exact singleton and two-item `F_(p^2)` moment buckets replaced pair streaming
with sketch inserts and baby probes. One full-size capacity-two sketch recovered
92.6% overall; two recovered 99.7% and missed 27 targets. Their median storage
was 146 and 292 field elements, versus 60 coordinate elements for the full H20
point table. The only configuration below that table size recovered 3.6%.
Complete recovery therefore did not accompany a storage reduction in the frozen
sweep; coupled peeling and seed search remain queued.

## Remaining preregistered cards, not results

The active continuation has one next proposal. It has no result and is not a canonical candidate:

- coupled-bucket peeling and seed search under the original point-coordinate
  storage cap.

They are included here only to prevent parameter-tuning regressions and to identify possible future mechanism gates. Nothing in this packet is a breakthrough or promotion.
