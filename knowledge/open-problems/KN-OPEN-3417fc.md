---
id: KN-OPEN-3417fc
type: open_problem
title: "Is there a computable non-group-theoretic invariant on the canonical prime-to-p torsion lift E(Q_p)[n] whose value separates [k]S by k at sub-rho amortised cost?"
tags: [lifting, local-torsion, p-adic, valuation, coordinate-invariant, formal-group, ecdlp, prime-field, open-problem, kn-tech-06bb4e]
confidence: reported
status: open
source_refs: [KN-LIT-6935a1, KN-TECH-73630e, KN-TECH-06bb4e, KN-OPEN-019]
added: 2026-08-09
superseded_by: null
---

## The question

Let `E/F_p` have good reduction lift `E/Q_p`, let `S` have prime-to-`p` order `n`,
and let `Ŝ ∈ E(Q_p)` be its unique order-`n` lift. `KN-TECH-73630e` shows
`red : <Ŝ> → <S>` is a group isomorphism, so every group-theoretic invariant is
constant across the lift and Silverman's face F2 (`KN-TECH-06bb4e`) is closed at
that level.

What remains: the `p`-adic **coordinates** of `[k]Ŝ` are genuine additional
symbols even though they carry no additional information. Is there a computable
functional

```
inv : <Ŝ> --> (some ordered or metric target)
```

built from coordinates and valuations rather than from group structure — for
instance the profile `v_p(x([k]Ŝ) - x([j]Ŝ))`, coordinate digit statistics at
fixed precision, or a `p`-adic distance to a fixed subvariety — that is
non-constant in `k` and **efficiently invertible**, so that recovering `k` from
`inv([k]Ŝ)` costs less than `n^{1/2}` amortised over the whole attack including
the precision needed to evaluate `inv`?

## Why it is not already answered

- It is not answered by `KN-TECH-73630e`, which is deliberately restricted to
  group-theoretic invariants.
- It is not answered by `ECDLP-IDEA-004` / `ECDLP-IDEA-160`, which closed the
  *additive-logarithmic* and *ramification-break* families respectively. A
  coordinate/valuation profile is neither a formal logarithm nor a ramification
  filtration invariant.
- Information-theoretically the answer must be "no gain": `Ŝ` is a deterministic
  function of `S`. So the question is strictly computational — whether the
  `p`-adic presentation makes some structure *cheap* that is expensive in `F_p`.
  A negative answer is expected; the value is in fixing which functional families
  have been measured rather than assumed.

## Falsification / resolution criteria

Resolved **negatively (scoped)** by measuring a stated family of coordinate
functionals at toy `p` and showing each is either constant in `k`, or requires
precision growing so that per-query cost times query count exceeds `n^{1/2}`.
Resolved **positively** by exhibiting one functional with a measured non-constant,
efficiently invertible profile and a charged end-to-end cost below rho and BSGS.

Neither outcome is a break; a positive outcome would be a first non-trivial
computational handle in face F2 and would require independent replication before
any status change.

## Status

`OPEN`. No experiment run. Made falsifiable as `ECDLP-IDEA-436`
(proposed, unapproved).
