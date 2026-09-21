---
id: KN-FIND-007
type: internal_finding
title: Decomposition-yield conservation — factor-base geometry cannot change mean yield, only redistribute it
tags: [index-calculus, factor-base, decomposition-yield, coverage, point-decomposition, conservation, ecdlp, toy-scale]
confidence: established
proof_status: derivation
proof_refs:
  - experiments/EXP-FB3-001/conservation.md
  - experiments/EXP-FB3-001/analysis.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-232/validation_notes.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-233/objections.md
internal_refs: [H-FBG-001, RQ-FBG-001, EV-FBG-001, DEC-20260724-007, RUN-FB3-001-N18]
claim_tier: toy
added: 2026-07-24
superseded_by: null
---

## Statement

Let `G` be a finite abelian group of order `N` and `D ⊆ G \ {0}` a factor base of
`B` distinct elements. For `m ≥ 1` and `r ∈ G`, let `c_D(r)` be the number of
size-`m` multisets from `D` summing to `r`. Then

```
sum over r in G of c_D(r)  =  binomial(B + m - 1, m)
```

exactly, because every size-`m` multiset sums to exactly one target. Hence the
mean per-target decomposition yield is

```
E_r[c_D(r)] = binomial(B + m - 1, m) / N
```

for **every** base of size `B`, independently of how `D` is chosen.

## Consequences (all confirmed against measurement in EXP-FB3-001)

1. **Mean yield is not a design lever.** The yield ratio of any structured base
   against a matched random base of the same size is exactly 1. Measured over
   144 cells at `N ~ 2^14/2^16/2^18`, the maximum absolute deviation of the exact
   cell mean from `binomial(B+2,3)/N` was exactly 0.
2. **Any "growth with N" clause on mean yield is identically satisfied at slope
   zero.** A hypothesis of the form "some geometry's mean-yield advantage grows
   with N" is refuted by arithmetic before any experiment runs.
3. **Only the distribution is free.** Coverage (the fraction of targets with at
   least one decomposition) obeys `coverage ≤ min(1, mean)`, with equality iff no
   target has two decompositions. Additive structure that creates repeated sums
   therefore *lowers* coverage at matched size: the H017 small-multiples base
   collapses to a coverage ratio of 0.0021 at `2^18` while its concentration
   statistic reaches 1224x.
4. **Typing is a fixed penalty, not a lever.** For typed decompositions with
   sub-base sizes `B1 + B2 + B3 = B`, the total is `B1·B2·B3 ≤ (B/3)^3 = B^3/27`,
   strictly below the untyped `binomial(B+2,3) ≈ B^3/6`. Measured penalty at a
   balanced split: 4.817x.

## What this does not say

- It does **not** say structured bases cannot beat random bases. Coverage headroom
  up to `min(1, mean)` is real and reachable: a Bose–Chowla `B_3` (Sidon) base
  attains it exactly, with a measured coverage ratio of 1.1071, and a whole-group
  low-collision greedy reaches 1.0269 at the parameters of the tested battery.
  The headroom ceiling is about +54%.
- The cost benefit of that headroom is bounded. Under a harvest-all solve, the
  relations obtained per solve equal the mean and are exactly geometry-invariant.
  Under one-relation-per-target, the gain is at most
  `min(1, μ)/(1 − e^{−μ}) ≤ 1.582`, maximised at `μ = 1`.
- It says nothing about the **cost of finding** a decomposition (the
  summation-polynomial / point-decomposition solve) or about the linear-algebra
  stage — which is where the index-calculus cost actually sits.
- It is **consistent with index calculus working**: the Gaudry–Diem `1/n!`
  decomposition probability over extension fields *is* this conservation mean.
  The extension-field advantage lives in the solve, not in the yield.
- Relation rank and independence are not captured: the mean scores a
  rank-deficient base as tied with a random base of the same size.

## Why it is worth recording

The identity is a one-line double count, but the repository had budgeted 24 CPU
hours and 96 runs for a battery (`EXP-FB3-001`, approved by `DEC-20260717-002`)
whose primary metric it makes vacuous, and the earlier scoped negative
`EV-FB-001` reported "yield tracks the combinatorial `|FB|³/N`" as an empirical
observation without noting that it cannot do otherwise. Recording it converts a
recurring empirical null into a screening rule: **a factor-base proposal that
promises higher mean yield at matched size is refuted on sight; only proposals
that argue about coverage, relation rank, recognizability, or solve cost are
worth measuring.**

## Provenance

Pre-registered in `experiments/EXP-FB3-001/amendment-001.yaml` and committed in
the protocol snapshot (`81d9e9f`) *before* any cell was measured, then confirmed
by the battery (`68e375f`), independently recomputed by the validator without
importing executor code, and bounded by the red team's Sidon and corrected-greedy
probes. Toy scale: `N ≤ 2^18`, 12 generated prime-order curves, `m = 3`.
