---
id: KN-FIND-6b3e17
type: internal_finding
title: "A pencil of plane cubics through 8 rational points certifies rank EXACTLY 12 over Q, and its base rank over Q(t) is EXACTLY 8 by Shioda-Tate: the world record over Q is bought with base rank, not sieve volume, and no amount of sieving a rational elliptic surface can supply it"
tags: [elliptic-curves, mordell-weil-rank, rank-over-Q, rational-elliptic-surface, pencil-of-cubics, shioda-tate, mestre-nagao, sieving, two-descent, height-regulator, specialisation, rank-records, negative-result, proven-ceiling, calibration-fixture]
confidence: exhibited_point_certificates_re_derived_independently_by_two_reviewers_plus_an_unconditional_ellrank_upper_bound
evidence_level: exact_on_curve_certificates_plus_numerical_regulators_plus_one_derivation_from_exactly_verified_invariants
source_refs: [RUN-ECQ-81141a-001, RUN-ECQ-81141a-002, RUN-ECQ-81141a-003, RUN-ECQ-81141a-004, RUN-ECQ-81141a-005, RUN-ECQ-81141a-007, RUN-a7a9e8-004-augment-full, RUN-ECRANK-e1e30e-003, GOAL-ECQ-001]
internal_refs: [RQ-ECQ-80f23c, H-ECQ-cec3c4, EV-ECQ-0d142e, DEC-20260822-564044, EV-ECRANK-b6c9b6, DEC-20260822-5a5635, DEC-20260822-d9bf63]
sibling_findings_narrowed: [KN-FIND-fd382f]
sibling_findings_note: "KN-FIND-fd382f records that a Mestre-Nagao prefilter over 364,756 squarefree twists of five small-conductor curves produced no twist of rank >= 5. That statement stands within its own scope and is not contradicted here. What this entry narrows is the generalisation a later reader could draw from it -- that the statistic does not order usefully. It does, on a family with a fixed, provably-capped base rank. The two measurements are different measurements."
proof_status: certificate
proof_refs:
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-81141a/certified_curves.json
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-81141a/qt_family.json
  - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/highrank_pool.json
review_refs:
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-0de988/validation_report.yaml
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-53748a/red_team_report.md
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/archives/TASK-20260822-66bacf/receipt.yaml
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/CORRECTION-review-dispatch-errors.md
added: '2026-08-22'
superseded_by: null
---

# Rank over Q from a rational elliptic surface: 12, exactly, and why 31 is a different regime

## The thing to read first

**Rank ≥ 31 over Q is an OPEN WORLD RECORD and nothing here approaches it.** The
largest rank known for an explicit curve over Q is **30** (Alpöge–Howell 2026),
after 29 (Elkies–Klagsbrun 2024) and 28 (Elkies 2006). This entry records a
certified rank of **12**, a shortfall of **19**, and — more usefully — the reason
the shortfall is not a matter of running the same search for longer.

## The construction and the two numbers

Take the 8 rational points

```
(4:0:1) (-1:2:1) (-3:-2:1) (0:-1:1) (-2:-1:1) (2:0:1) (-4:2:1) (1:-2:1)
```

in general position in P². The cubics through them form a pencil (the
8×10 system has kernel dimension 2), the pencil's members meet in a 9th base
point `(197684347 : -60668562 : -45807609)` — computed by resultant and verified
by exact substitution, not assumed — and the resulting Weierstrass family over
`Q(t)` is

```
y² = x³ - 27·c4(t)·x - 54·c6(t),      deg c4 = 4, deg c6 = 6, deg Δ = 12
```

**Axis 1 — base rank over Q(t) is exactly 8, and 8 is a ceiling, not an
achievement.** `deg c4 = 4, deg c6 = 6, deg Δ = 12` is the signature of a
*rational* elliptic surface, so Mordell–Weil rank over `Q̄(t)` is at most 8. Here
it is attained *and* it is exact, because the discriminant is **squarefree**
(`gcd(Δ, Δ') ` of degree 0), so all 12 singular fibres are irreducible `I₁` and
Shioda–Tate has nothing to subtract. Every input to that derivation was verified
in exact rational arithmetic by an independent reviewer. The published record
ladder rests on base ranks of roughly 18–20 (recalled literature, *background,
not measured by this program*) — a gap of 10 to 12 that **sieving cannot close**,
because it is a property of the surface. Exceeding 8 needs a K3 or higher
elliptic surface.

**Axis 2 — sieve volume, measured.** 97,640 specialisations `t = p/q`,
`gcd(p,q)=1`, `|p| ≤ 2000`, `q ≤ 40`, scored at **1.028 ms** each; a matched
tier-2 box of 1,548; **140 descent attempts on 137 distinct fibres, 84 timeouts,
56 completed** at ~7.5 s per descent; 1,993.0 s and 1.22 GB peak RSS in total.
**Certification, not scoring, is the binding cost** — scoring the whole tier-2
domain costs 1.59 s against 327 s of descent in one arm.

## The certificate

Best curve, `t = -65/22`:

```
y² = x³ - 518228207838672723·x + 141005837549331272675978478
```

20 exhibited points (8 specialised sections + 12 from 2-descent), **12
independent**, 12×12 regulator ≈ 5.833522605e9, least eigenvalue ≈ 0.3462.

The rank is **exactly 12**, not merely ≥ 12: an independent blind re-derivation
started from the a-invariants alone and PARI's own `ellrank` returned `[12, 12]`
at two efforts, with **two different 12-point sets**, neither of them the
producer's. `r_high = 12` is an unconditional upper bound, so the lower bound is
sharp and no better point search could have beaten it.

Rank histogram over all 137 certified fibres: `8:93, 9:14, 10:17, 11:12, 12:1`.
Two reviewers re-derived all 137 with implementations sharing no code with the
producer or with each other: **0 points off curve, 0 rank mismatches, twice.**
Every rank is a lower bound from exhibited points *on that exact curve*; the
rank-8 floor is re-exhibited on each specialisation and never inherited from the
generic fibre by Silverman specialisation, verified on all 137. All 83 timed-out
fibres claim exactly 8 and not one point more.

## The reversal that matters: Mestre–Nagao works *here* and failed *there*

This program had already measured `S(N)` ordering poorly — `KN-FIND-fd382f` /
`EV-ECRANK-b6c9b6`: 364,756 squarefree twists, `ellrank` on the top 400 per
curve, **no twist of rank ≥ 5**. The review plan for this batch therefore
pre-registered "if the producer reports a large sieve yield, that is the first
thing to disbelieve". It was attacked on the prior's behalf and **the prior lost**:

| arm (same 1,548-fibre domain, same 8 s alarm) | n | timeouts | rank ≥ 9 / completed | rank ≥ 11 / completed | max |
|---|---|---|---|---|---|
| MN top-60 | 60 | 31 (51.7 %) | 28/29 = 0.966 | 12/29 = 0.414 | 11 |
| uniform random 60 | 60 | 35 (58.3 %) | 16/25 = 0.640 | 0/25 = 0 | 10 |
| **MN bottom-20** (added by review) | 20 | 11 (55.0 %) | **0/9 = 0.000** | 0/9 = 0 | **8** |

Fisher exact, top vs bottom at rank ≥ 9: **p = 6.1e-8**; random vs bottom
p = 9.3e-4; top vs random at rank ≥ 11 p = 1.5e-4.

Three things make this a measurement rather than an artifact:

1. **The gap widens under conditioning on descent completion**, and the MN arm
   had *fewer* timeouts, so censoring cannot be inflating it.
2. **The censor was identified.** Spearman(log|a6|, timeout) = **+0.765**;
   Spearman(score, timeout) = **−0.104**. Timeout is driven by coefficient size
   and is essentially orthogonal to the score.
3. **The timeout rate is FLAT across the ordering** (51.7 / 58.3 / 55.0 %) while
   yield decays monotonically 0.966 → 0.640 → 0.000. A confound constant along
   the ordering cannot produce a monotone response along it.

And the effect behaves the way the mechanism says it should. The BSD-flavoured
model predicts a per-rank shift of `Σ_{p≤1000} log p / p = 5.6095`; the observed
mean-score steps by certified rank are **+5.26, +3.91, +2.61** (compression at
the top is the expected selection effect), with Spearman(score, rank | completed)
= **+0.779**.

**Why the two measurements differ, structurally rather than statistically.**
`S(N)` is a rank-*excess* detector. The twist search asked it for a `0 → ≥5`
excursion in the top 0.11 % of a **rank-0** family at conductor ~10¹¹. Here every
fibre already has rank 8 and the ask is `+1…+3` in the top 3.9 % at modest
conductor. A **fixed, provably-capped base rank is exactly what makes the score
legible**: every fibre shares a base, so the score's variance is the excess and
nothing else. The earlier negative result stands in its own scope; the
generalisation from twists to families does not.

## The obstruction read the other way

The cap that kills this route as a record attempt is what makes it useful as an
instrument. This pencil is a **cheap, fully descendable calibration fixture for
Mestre–Nagao sieve design**: `N`, acceptance threshold and arm size can be tuned
at 1.028 ms/score and ~7.5 s/descent *with ground truth available*, because
2-descent closes here — certified rank equals `r_low` equals `r_high` on all 54
completed descents. Contrast the Mestre-style route below, where 31/31
upper-bound descents timed out at `a4 ~ 1e19`. Tuning belongs on a fixture where
the answer is knowable, before it is spent on a K3 base where it is not. *This is
a proposal, tested on nothing; it is recorded as a lead, not as a result.*

## Scope, and what this entry is not

- **n = 1 family.** One pencil, one 8-point configuration, one seed (81141), one
  arm size (K = 60), one tier-2 box (`|p| ≤ 150, q ≤ 8`), PARI/GP 2.15.4
  `ellrank` under 8 s and 20 s alarms. A second-configuration replication was
  specified by the review and **not run**.
- **The headline 12 is censored at 60 %** (84 of 140 attempted descents timed
  out) and came from the tier-1 top arm at a **20 s** alarm; the matched 8 s arms
  max out at 11. Un-censoring can only raise ranks, so every published figure is
  a lower bound.
- **12 is a within-family maximum for this pencil and is NOT this program's best
  certified rank over Q.** In the same snapshot, a Mestre-style construction
  commissioned under `GOAL-ECRANK-002` certifies **13** (two curves), with 29 at
  rank 12 and 425 at rank 11 over 34,740 scanned, in 1,218 s — independently
  re-certified. On the headline axis this pencil route is **dominated** by that
  baseline. What it holds that the baseline does not: an *exact* rank, a *proven*
  ceiling, and an affordable descent regime.
- **The closure claim is narrowed by one quantifier.** Shioda–Tate caps the
  *base* rank over `Q̄(t)`. It caps nothing about `8 + extra` for a
  specialisation over Q, and the only support for "extra stays small" is
  `extra ≤ 4` over 56 completed descents — while the published ladder is built
  from `extra` of order +10 to +12 on higher surfaces. The supported statement is
  **"31 is unreachable by this search as run"**, not "unreachable by this
  surface".
- Regulator determinants from this batch are quoted to no more than ~16
  significant digits: an unexplained uniform ~17th-digit divergence between two
  internally stable computations was found and its obvious cause (a float64
  round-trip) was tested and **falsified**. No rank is affected — ranks are
  integers read off a ~115-order-of-magnitude eigenvalue split.
