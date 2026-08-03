---
id: KN-FIND-c41ea9
type: internal_finding
title: The m=3 Semaev summation cover has cycle type governed by a quadratic character
  product, with monodromy S_2 for every non-singular curve; and on the factor-base
  locus the summation fibre splits completely at every m, so a generic-fibre
  Frobenius census measures a quantity that is constant where relation search operates
tags:
- semaev-polynomial
- index-calculus
- monodromy
- galois
- chebotarev
- relation-rate
- ecdlp
- prime-field
- elliptic-curve
- scoped-negative
- toy-scale
- derivation
confidence: established
confidence_note: >-
  established for the DERIVATION, which is elementary and was independently
  re-derived by two reviewers. NOT established as a closure of KN-OPEN-009 - see
  "What this does not settle".
internal_refs:
- EXP-MONO-4b50b6
- EV-MONO-a0a89c
- DEC-20260802-a51c82
- RQ-MONO-001
proof_status: derivation
proof_refs:
- ledger/corrections/CORR-20260802-1d8384.yaml
- experiments/EXP-MONO-4b50b6/contract.md
- experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-002/verification.json
- coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-e2702a/validation_report.md
- coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-1b4130/red_team_report.md
added: 2026-08-02
superseded_by: null
---

## The identity

For `E: y² = x³ + Ax + B` over a field of characteristic `> 3`, with
`f(x) = x³ + Ax + B` and `S_3` the third Semaev summation polynomial:

```
disc_T S_3(x1, x2, T) = 16 · f(x1) · f(x2)          in Z[x1, x2, A, B]
```

**Proof.** The two roots of `S_3(x1,x2,T)` in `T` are `x(P+Q)` and `x(P−Q)` for
`P = (x1,y1)`, `Q = (x2,y2)`. The chord formula gives
`x(P+Q) − x(P−Q) = [(y2−y1)² − (y2+y1)²]/(x2−x1)² = −4y1y2/(x1−x2)²`, so
`disc / (x1−x2)⁴ = 16 y1² y2² / (x1−x2)⁴`. ∎

**This is elementary and essentially classical — no novelty is claimed for it.**
It is recorded because it was absent from this corpus while `KN-OPEN-009` treated
the `m=3` cycle-type distribution as an open empirical question.

## Three consequences

**(1) Cycle type is a character product.** For `x1 ≠ x2`, with `χ` the quadratic
character: split iff `χ(f(x1)) = χ(f(x2)) ≠ 0`; inert iff they differ; ramified iff
`f(x1)f(x2) = 0`. `x1 = x2` is a degree drop.

**(2) Monodromy is exactly `S_2`, universally.** Over `k = F̄_p`,
`16 f(x1) f(x2)` is a product of six pairwise-distinct irreducibles of `k[x1,x2]`
(distinct ⟺ `f` squarefree ⟺ `E` non-singular), hence squarefree, hence not a
square in the fraction field; `16` is a unit for `p > 2`. So `S_3` is irreducible
over `k(x1,x2)` and the **geometric monodromy group is the full `S_2`, for every
non-singular `E` and every `p > 3`, with no exceptional locus.** The same argument
over `F_p(x1,x2)` gives arithmetic monodromy `S_2`.

**(3) An exact density law, `O(1/p)` not `O(1/√p)`.** With `Z = #{x : f(x)=0}`,
`#E(F_p) = p+1−t`, over all `p²` specializations:

```
N_split = S² + N² − (p−Z),  N_inert = 2SN,  N_ram = p² − (p−Z)² − Z,  N_degdrop = p
freq_split − 1/2 = (t² − 2pZ + Z² − 2p + 2Z) / (2p²)
```

Since `Z ∈ {0,1,3}` and `|t| ≤ 2√p`, **`|freq_split − 1/2| < 4/p` uniformly.**
Verified on 105 curves (0 mismatches) and, independently of the closed form, by
exhaustive enumeration of all `p²` pairs on 19 curves — 17 054 059 pairs, 0
disagreements. Both reviewers ran their own brute-force enumerations and agreed.

## The part that is not about `m = 3`

Every factor-base element is the `x`-coordinate of an `F_p`-rational point, so
`χ(f(x)) = +1` there. By (1) the fibre over a factor-base pair **always splits**.
More generally, and **at every `m`**:

> If `x_1,…,x_{m−1}` are `x`-coordinates of rational points `P_1,…,P_{m−1}`, the
> roots of `S_m(x_1,…,x_{m−1},T)` are `x(±P_1 ± … ± P_{m−1})` — `2^{m−2}` values,
> matching `deg_T S_m` — and every one lies in `F_p`. So `S_m` **splits completely
> over `F_p`** on the factor-base locus, unconditionally.

Verified at `m = 4` by building `S_4 = Res_X(S_3(x1,x2,X), S_3(x3,T,X))` over
`F_211` and factoring 193 specializations at triples of rational `x`-coordinates:
**193/193 split completely, root sets exactly `{x(±P1±P2±P3)}`.**

**Why this matters more than the `m=3` result.** A generic-fibre Frobenius census
samples uniform `(x_1,…,x_{m−1}) ∈ F_p^{m−1}`. Index-calculus relation search
operates entirely on the sublocus where the `x_i` are factor-base elements — a
measure-zero set on which the cycle type is **identically trivial, at every `m`**.
So the instrument `KN-OPEN-009` proposes measures a quantity that is constant where
the attack actually lives. Any `m ≥ 4` census should answer this before spending
budget.

**Corrected relation-rate model.** The quasirandom product form
`freq_split · (W_eff/p)²` understates the joint proxy by

```
(1 − 1/W_eff) / freq_split  →  2·(1 − 1/W_eff)
```

The value `1.5` measured here is the `W_eff = 4` case; **the limit is 2, and a
consumer that pins 1.5 will be wrong for any realistic factor base.** Empirically:
pooled over 2 400 000 draws the real window gives ratio 1.5313 at `z = +6.34`, a
shuffled window of identical size gives 0.7305, and the ratio of ratios is 2.0962
against a predicted `1/freq_split ≈ 2.01`. Per curve the statistic is Poisson noise
at `p ≥ 431` and supports nothing.

**Scope on "moves no exponent".** True at fixed `m` and fixed `W_eff`. A per-fibre
factor of 2 applied once per summation fibre in a Gaudry/Diem-style decomposition
over `F_{q^n}` with `n` growing compounds as `2^{n−1} = q^{Θ(1)}` and **would** move
an exponent. Never quote the phrase without this scope.

## What this does not settle

- **`KN-OPEN-009` is not closed and is not superseded.** It asks about the `m`-th
  cover. Only the `m = 3` slice is answered — and `m = 3` is **the degenerate
  slice**: `deg_T S_3 = 2`, and a transitive group of degree 2 is *primitive by
  definition*, so the imprimitivity / block-system / resolvent mechanism the open
  problem hunts **cannot exist at `m = 3` for degree reasons**, before any curve is
  examined. At `m ≥ 4`, `deg_T = 2^{m−2} ≥ 4` and that question is genuinely open.
- **No `AGENTS.md` rule 12 review exists.** Both reviews of the underlying run
  resolved to the same model as the producer, so a closure claim could not be
  reviewed to the standard rule 12 requires. This entry is a derivation at claim
  tier `toy`, not a closure result.
- **Nothing about ECDLP hardness, in either direction.** No attack advantage over
  Pollard rho is claimed or implied; the relation-rate correction is a correction
  to a *planning model*. Largest prime exercised is 1601 (11 bits).

## Attribution

The identity, the density law and the factor-base observation came from
`RUN-MONO-4b50b6-001`. **The group-theoretic statement (2), the `m ≥ 4`
generalisation, the `2(1−1/W_eff)` form, and the observation that `m=3` is the
degenerate slice all came from the batch's independent reviewers**
(`TASK-20260802-1b4130`, `TASK-20260802-e2702a`), not from the producer. Recorded
that way because the strongest content in this entry is theirs.
