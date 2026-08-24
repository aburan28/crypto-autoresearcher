---
id: KN-FIND-031
type: internal_finding
title: An empirical survival function's lowest nonzero value is 1/N, so a measured
  "floor" at log2 P = -log2 N is the estimator's resolution limit and not a property
  of the distribution; the Carrier Fig 4.1 Pwrong floor is exactly this
tags:
- methodology
- instrument-artifact
- controls-before-belief
- rare-event
- survival-function
- sampling-resolution
- dual-attack
- carrier
- pwrong
- kyber
- ml-kem
- kn-open-016
- experiment-design
- scoped-negative
confidence: unverified
internal_refs:
- EV-MLKEM-017
- DEC-20260802-735e6a
- EV-MLKEM-011
- H-MLKEM-010
proof_status: derivation
proof_refs:
- knowledge/findings/KN-FIND-012.md
- knowledge/open-problems/KN-OPEN-016.md
- experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out
- coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-104/red_team_report.yaml
- coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-104/objections.md
- ledger/evidence/EV-MLKEM-017.yaml
claim_tier: theory
added: 2026-08-02
superseded_by: null
status: WITHDRAWN_PENDING_RULE_12_REVIEW
withdrawn_by: CORR-20260802-d8ba0e
withdrawn_on: '2026-08-02'
---

## WITHDRAWN — this entry is not official knowledge

This entry was promoted by DEC-20260802-735e6a. It is **withdrawn** by
CORR-20260802-d8ba0e and carries no official standing.

An independent execution of the same batch reached the same arithmetic but
declined to promote it, on grounds this session missed: the result supersedes
coverage statistics carried by `KN-FIND-012` and `KN-FIND-014`, which makes it a
**contradiction between validated evidence records**, and AGENTS.md rule 12 gates
that behind an independent `review-breakthrough` review at `max` effort.
Promoting it through an ordinary batch decision routed around that gate. The
authoritative record for the batch is `EV-MLKEM-017` / `DEC-20260802-15cadd` on
`origin/main`, whose `knowledge_promotion.not_warranted` states the gate.

**Nothing below is retracted as arithmetic.** `log2(4000 · 241³) = 35.7045`
against a recorded floor of `−35.70` is exact, and two independent red teams
derived it separately. What is withdrawn is its promotion to official knowledge
standing, and with it any authority to qualify `KN-FIND-012`'s or
`KN-FIND-014`'s reading. Restoring this entry requires the rule-12 review, not a
further batch decision.

## A note on how KN-FIND-012 and KN-OPEN-016 are cited here

They are named throughout the prose below and carried in `proof_refs` as paths,
and they are **deliberately absent from `internal_refs`**. This is a schema fact,
not a judgement about relevance: `internal_refs` entries must resolve against
`ctx.ids` in `tools/validate_ledger.py`, which indexes ledger records and not
knowledge entries. `KN-FIND-030` records the same constraint for the same reason.

## The statement

Let a simulation draw `N` independent samples and report an empirical survival
function `Ŝ(t) = #{samples > t} / N`. The smallest nonzero value `Ŝ` can take is
`1/N`. Every `t` beyond the largest observed sample reports exactly `0`. So the
last `t` at which `Ŝ(t) > 0` carries the value `1/N`, always, for any underlying
distribution whatsoever.

Consequently: **a plotted "floor" sitting at `log2 Ŝ = -log2 N` is a statement
about the sample budget, not about the tail being estimated.** It would appear
identically if the true tail continued smoothly for another two hundred bits.
Reading such a floor as the point where the distribution stops is a
category error, and the tell is arithmetic — compute `log2 N` and compare.

## The instance that produced this entry

`KN-FIND-012` records, from the archived Carrier et al. Fig 4.1 left-panel
outputs (`Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out`):

| quantity | recorded value |
|---|---|
| last `T` with `Pwrong > 0` | 1802 |
| `log2(Pwrong)` at that floor | ≈ **−35.70** |
| Kyber-512 CC `log2(Pwrong)` (Table C.2) | −119.57 |
| "bits below toy floor" | ≈ **84** |

The simulation's sample budget is `4000` targets at `q = 241`, `m = 40` with the
plotted score built over `241^3` bins:

```
log2(4000 · 241³) = log2(55 990 084 000) = 35.7045
```

That is the recorded floor to two decimal places. The agreement is not a
coincidence to be explained; it is the identity above.

**What this does and does not do to `KN-FIND-012`.** `KN-FIND-012` is immutable
and is not overwritten. Its *coverage* observation is untouched and correct: the
measured `Pwrong` `T`-range and the `Pgood` operating scores are disjoint, and
`fraction_inside = 0` remains true (it is a statement about which `T` values were
plotted, not about probability values). What this entry qualifies is the
*interpretation of the floor value*, and with it the framing of the "≈ 84 bits
below the toy floor" quantity: that gap measures the distance from a
cryptographic-scale modelled probability down to a toy simulation's
sampling-resolution limit. It is a statement about how few samples the published
validation drew, not about a discontinuity in the tail.

## Why the distinction is load-bearing here

`KN-OPEN-016`'s residual — measure `Pwrong` near the aligned `Pgood` operating
threshold — reads differently under the two interpretations:

- *Floor as distribution property*: something changes about `Pwrong` past
  `T ≈ 1802`, and measuring there is exploratory.
- *Floor as resolution limit* (correct): nothing changes; the published run
  simply could not resolve below `2^-35.70`. The residual becomes a **costed**
  question rather than an open one — reaching the aligned operating threshold
  requires either enough samples to resolve the relevant probability, or an
  importance-sampling / analytic route that does not pay `1/P` in samples.

This converts "unmeasured" into "unmeasured, and here is the sample budget that
would measure it", which is strictly more actionable and is the honest reading.

## The generalisable rule

Before treating any measured rare-event floor as a finding, compute the sample
budget's resolution limit and compare. If the floor equals `1/N`, the instrument
hit its own bottom and the observation is uninformative about the tail. This is
the same failure class as `KN-FIND-008`, from the other direction: there, a
density gate could not be reached because the sample size needed grows like
`p^α`; here, a sample budget silently imposed a probability floor that was then
read as data. Both are cases where the *sample budget determined the result* and
the result was reported as if it were about the object.

It is also a direct instance of the `docs/inventor-protocol.md` obligation
"controls before belief": the null-object control for a reported floor is to ask
what floor a distribution with no interesting tail behaviour would have produced
under the same budget. Here the answer is: exactly this one.

## Boundaries

- This is arithmetic about estimators. It is **not** a claim about the
  correctness of Carrier et al.'s analysis, their heuristics, their cost model,
  or their headline security figures, none of which this entry examines.
- It is **not** evidence about ML-KEM's security margin in either direction, and
  must never be cited as such. `KN-OPEN-016` remains open.
- The `N = 4000 · 241³` reading of the sample budget is taken from the archived
  filename parameters and the published figure caption. It is consistent with
  the recorded floor to two decimals, which is strong but is a consistency
  argument, not an independent count of the samples the authors drew.
- Derived by the `TASK-20260802-104` red team and re-derived by the Coordinator;
  it has not had a second independent review pass of its own.

## What would refute it

An authoritative statement that the archived Fig 4.1 left panel drew a sample
budget materially different from `4000 · 241³`, leaving the agreement with
`−35.70` unexplained. Cheapest check: recount the sample budget directly from
the archived `.out` files in `experiments/EXP-MLKEM-011/vendor-lock/data/`.
