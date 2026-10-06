# Prime-field ECDLP controlled follow-ups: p-adic cocycles and beam exponents — 2026-10-06

## Intake status

- Source type: user-directed external follow-up experiments.
- Scope: classical ECDLP in prime-order subgroups of short-Weierstrass curves over prime fields.
- Exclusions: no Pollard-rho collision walk and no index-calculus relation collection.
- Evidence tier: deterministic toy experiments, external to this repository's contract and run-receipt system.
- Canonical status: none. This file allocates no IDEA, hypothesis, experiment, evidence, or decision identifier and changes no official research state.
- Bottom line: both frozen successors failed. P-adic cocycle arithmetic was correct but every proposed formula remained lift-section dependent; height/carry beams required width exponents above the square-root target and failed generator/control gates.
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

Both result payloads omit timing fields and reproduced byte-for-byte. The expanded external suite passed 22/22 tests. These are provenance statements, not repository run receipts.

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

## Remaining preregistered cards, not results

The external plan retains four unexecuted proposals. These have no positive evidence and are not canonical candidates:

- a generator-blind coordinate-bit grammar with whole-curve holdout and relabelled labels;
- a sparse-defect translation equation `f(Q+P)-f(Q)=1` outside a compact exception set;
- a theorem-first sparse spectral coefficient oracle, with no benchmark allowed before sub-square-root coefficient construction is derived;
- a block-Hankel multi-coordinate recurrence with mandatory state-to-index inversion.

They are included here only to prevent parameter-tuning regressions and to identify possible future mechanism gates. Nothing in this packet is a breakthrough or promotion.
