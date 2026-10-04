---
id: KN-FIND-9643e7
type: internal_finding
title: >-
  Semaev's chain length t is not a free cost parameter: under eq. (11) shortening
  the chain costs k - log2(t) bits of yield per link while every solving-cost saving
  in the paper has decreasing increments, so t = m is optimal at concrete
  cryptographic n and not merely asymptotically indifferent
tags: [semaev, chained-system, chain-length, summation-polynomials, yield, eq-11,
  relation-collection, exponential-versus-polynomial, obstruction, measured-obstruction,
  negative-result, scoped-closure, characteristic-two, ecdlp, sembin, symmetry-factor,
  coset-typed-factor-base]
confidence: proved
evidence_level: derivation
proof_status: derivation
proof_refs:
  - >-
    EV-SEMBIN-1d36a3 obstruction block -- the analytic derivation
    A(t-1)/A(t) = 2^{-k} t from Semaev 2015 eq. (11), giving k - log2(t) bits per
    removed link in the unsaturated regime.
  - >-
    RUN-SEMBIN-aa5161 -- the numeric sweep the derivation is checked against: agreement
    to 1e-6 at nearly every step and 0.346 bits worst case over
    n in [250,600] x m in [2,20] x t in [2,m], with 0 saturated cells and
    max log2 A = -1.0.
  - >-
    TASK-20260913-da3982 (validator, joint J4, verdict holds) -- independent
    re-derivation of the same law and an independent optimizer, written from the
    published formulas and sharing no code with the producer, agreeing on t* = m* at
    every n and on m* = 7, 7, 9, 10 at n = 283, 310, 409, 571.
  - >-
    NOT A CERTIFICATE. proof_status is derivation, not certificate: this is a closed-form
    argument about a published cost model, checked numerically. No curve was
    instantiated, no relation computed, no solve performed, and Semaev's Assumption 1 is
    consumed unvalidated throughout (docs/claims-and-verification.md, bound_kind
    heuristic_estimate).
source_refs: [EV-SEMBIN-1d36a3, RUN-SEMBIN-aa5161, EXP-SEMBIN-81dc96, H-SEMBIN-b1708c,
  DEC-20260913-74e208, KN-LIT-fa346d, KN-OPEN-94f456, KN-TECH-b18366]
internal_refs: [DEC-20260913-74e208, DEC-20260913-ebd639, EV-SEMBIN-1d36a3]
review_refs: [TASK-20260913-da3982, TASK-20260913-cf9d98]
added: '2026-09-13'
superseded_by: null
closes_scoped: KN-OPEN-94f456
---

## Purpose

`KN-OPEN-94f456` asked whether Semaev's chain length `t` is a free cost
parameter — he identifies the `t < m` trade-off in Section 3 step 3, quantifies
it in Table 2, and declines it as asymptotically irrelevant. This record closes
that question **as an optimization question under eq. (11)**, and records the
measured obstruction that closes it, so a later session does not reopen the lane
by intuition.

It is a negative result and it is scoped. It says nothing about chain length
under any yield law other than eq. (11), and the measurement that could invert it
has not been made.

## The finding

Write Semaev's eq. (11) yield as `P = 1 - exp(-A(t))` with
`A(t) = 2^{tk-n} / t!`. Then

    A(t-1)/A(t) = 2^{-k} · t,

so in the regime `A << 1`, where eq. (11) linearises to `P ≈ A`, **removing one
link from the chain costs exactly `k - log2(t)` bits of relation probability**.
Cumulatively from `m` down to `t` that is `(m-t)k - log2(m!/t!)`, which at
`k ≈ n/m` is `≈ n(1 - t/m)` — linear in `n` **in the exponent**, hence
exponential in `n`.

Against that, every solving-cost saving available in Semaev's own text has
**decreasing** per-unit increments. At `n = 409, m = 20` the saving per removed
link runs

    42.4, 11.3, 6.8, 4.9, 3.8, 3.1, 2.6, 2.3, 2.0, …

so the cumulative saving grows like `log(m - t)` and the cost *ratio* is
polynomial in `(m - t)`. An exponential charge cannot be paid by a logarithmic
credit.

Consequence: **`t* = m*` at every integer `n` in [250, 600], under all three
solving-cost readings, with no interior optimum anywhere.** Semaev's choice of
`t = m` is optimal under his own cost model at concrete cryptographic `n`, not
merely asymptotically indifferent. The trade-off he declined would not have paid.

## The measured obstruction

Stated as a measurement rather than a verdict, so a later reader can re-scope it.

| quantity | value | where measured |
|---|---|---|
| yield loss per removed link, at `m*` | **27.68 / 28.27 / 33.72 / 44.00 bits** at `n = 310 / 283 / 409 / 571` (`m* = 10 / 9 / 11 / 12`, `k = ceil(n/m)`) | `RUN-SEMBIN-aa5161`, re-derived in `TASK-20260913-da3982` |
| solving-cost saving per link at `t = m` | 2.26–2.59 (`macaulay4`), 2.04 (`f4_std`), **0.000** (`block_n4w`) bits | same |
| solving-cost saving, maximum over all `t` | 31–32 (`macaulay4`), 12 (`f4_std`), 0 (`block_n4w`) bits | same |
| measured solving-time drops, frozen source Tables 1–2 (`m ≤ 5`, `t` reaching 2) | 3.75 to 13.87 bits — **bracketed by the two model readings** | `TASK-20260913-da3982` |
| unsaturated-regime margin | `max log2 A = -1.0` exactly; **0 saturated cells** over `n ∈ [250,600] × m ∈ [2,20] × t ∈ [2,m]` | `TASK-20260913-da3982` |
| analytic law versus exact eq. (11) | agrees to `1e-6` at nearly every step, **0.346 bits worst case** over the whole sweep | `TASK-20260913-da3982` |

**Scope.** `n ∈ [250,600]` integer; `m ∈ [2,30]`; `t ∈ [2,m]`; `k = ceil(n/m)`;
`ω ∈ {2.376, 2.807, 3.0}`; solving-cost readings `macaulay4`, `f4_std`,
`block_n4w`; Semaev 2015 eq. (11) and eqs. (15)–(17) **as published and
unvalidated by measurement**. Claimed nowhere else.

## Why the premise is verified rather than assumed

The exponential-versus-polynomial argument only bites while eq. (11) is
unsaturated: once `A ≳ 1`, `P` saturates and shortening the chain is free. That
premise is checked rather than asserted. Since `k = ceil(n/m)` gives
`mk - n ≤ m - 1` while `log2(m!) > m - 1` for `m ≥ 4`, `A < 1` **already at
`t = m`**, and falls by a further `2^{-k}·t` per link. A full sweep finds zero
saturated cells and a maximum `log2 A` of exactly `-1.0`, attained only at the
`m = t = 2` corner where `m` is never optimal (`m*` is 9–12 at these `n`).

This matters because the closure standard in `AGENTS.md` requires a named
obstruction with a measured value, not a fatigue report. The regime check is what
makes "exponential" earned rather than asserted.

## The obstruction re-read as a resource

Required by the inventor protocol, and the answer is uncomfortable, which is why
it is recorded here rather than left implicit.

The blocking quantity is the **symmetry factor `t!` inside eq. (11)** — the same
object that `H-SEMBIN-c59e50` claims a coset-typed factor base
(Galbraith–Gebregiyorgis, `inputs/GG-2014-806/`) removes at zero cost in a
chained presentation carrying no symmetrised coordinates. Two readings follow:

1. **The typed construction closes this lane HARDER, not looser.** With `t!`
   removed, `A(t) = 2^{tk-n}` and the ratio becomes exactly `2^{-k}`, so the
   per-link charge **rises** from `k - log2(t)` to `k` — from 33.72 to 37.18 bits
   at `n = 409, m = 11`. Anyone reaching for coset typing in order to open an
   interior optimum in `t` should expect the opposite. This is a cheap falsifiable
   consequence of the typing claim.
2. **The per-link charge is a calibrated ruler for whether the typing works at
   all.** The ratio of typed to untyped achievable-sum counts is exactly the
   quantity arm D of `EXP-SEMBIN-92724f` enumerates exhaustively, and the yield
   law fixes what that ratio must be if the symmetry factor is genuinely gone. An
   obstruction measured under the *optimization* question therefore becomes a
   control for the *mechanism* question.

Reading (2) is a consistency handle and **not** evidence that the typing removes
anything. It inherits eq. (11) exactly as the obstruction does.

## What would reopen the lane

- **A realized-yield measurement showing eq. (11) overstates yield MORE at
  `t = m` than at `t < m`.** This is the one confound that inverts the whole
  result, it is unmeasured, and `EXP-SEMBIN-354a75` exists to measure it by
  exhaustive enumeration.
- **Any yield law other than eq. (11).** The closure is conditional on it
  throughout. `KN-OPEN-94f456` stays open in that direction.
- **A solving-cost reading with INCREASING per-link increments.** None of the
  three readings drawn from the frozen text has them; a fourth reading that did
  would break the argument at its joint. `block_n4w` has no `t`-dependence at
  all, so under that reading the result is vacuous and the real content lives in
  `macaulay4` and `f4_std`.
- **A cost model pushing `m*` down toward 2.** The `m = 2` corner is the only
  region within one bit of saturation and the only place the linear yield law is
  inaccurate (worst case 0.346 bits). It does not matter today because `m = 2` is
  never optimal.

## How it was checked

Two implementations sharing no code agree at every `n` and every reading: the
producer's `joint_balance.py` and an independent optimizer written from the
published formulas in `TASK-20260913-da3982`, which also matches on `m*`
(7, 7, 9, 10 at `n = 283, 310, 409, 571` under `macaulay4`).

Because a bug that ignored `t` would produce `t* = m*` everywhere and pass the
run's own known-false control, the optimizer's sweep over `t` was established
**positively**, four ways: an independent optimizer; a no-yield null that moves
`t*` from `m` to 2 at every `n`; a targeted probe charging 400 bits for every `t`
but one, which recovers `t = 2, 3, 5, 7` exactly with 19 distinct `t` evaluated
per solve; and a proves-too-much object under which shortening must pay, which
moves `t*` by 28 links. That object's flip threshold matches the yield law
derived here at **5 of 5** parameter sets.

## Non-claims

- **This is not a statement about the security of any curve, in either
  direction.** It locates the minimum of a published cost model. No curve was
  instantiated, no relation computed, no Gröbner basis run, no solve performed,
  and **no certificate attaches to any number here** (`bound_kind:
  heuristic_estimate` under `docs/claims-and-verification.md`).
- **No degree was measured and none is asserted.** Semaev's Assumption 1
  (degree bound ≤ 4) is consumed unchanged and unvalidated; there is no Gröbner
  engine on the host that produced this (`IMP-SEMBIN-ENGINE`). Nothing here bears
  on Assumption 2 or on the asymptotic bound (17).
- **No exponent moves.** The joint `(m, t)` re-optimization recovers exactly
  Semaev's published choice, so the crossover does not move and the fitted `c` is
  unchanged at 1.6986.
- The four published quantifications in `RUN-SEMBIN-aa5161` that needed
  correction are corrected in `EV-SEMBIN-1d36a3` (O-8 through O-14) and are
  **not** part of this finding. In particular the yield-loss range is 27.7–44.0
  bits and not the 25–28 the run published, and the "2–3 bits per unit of `t`"
  figure is a derivative at `t = m` rather than a bound over `t`.

## Provenance

Promoted from `EV-SEMBIN-1d36a3` under `DEC-20260913-74e208`, which composed
`REVIEW-SEMBIN-20260913-9d649f`. The mechanism was independently re-derived by
the validator on joint J4 (`TASK-20260913-da3982`, verdict `holds`) and the
fitted-`c` machinery independently confirmed by the red team on joint J5
(`TASK-20260913-cf9d98`, verdict `holds`); neither reviewer read the other's
report. The hypothesis that proposed this experiment, `H-SEMBIN-b1708c`, is
**rejected in scope** — it predicted a strict interior optimum — so this finding
is the negation of its own originating claim.
