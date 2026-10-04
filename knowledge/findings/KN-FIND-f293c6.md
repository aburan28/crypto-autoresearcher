---
id: KN-FIND-f293c6
type: internal_finding
title: >-
  Under the JMV (2005) branch-(a) proven, GRH-conditional eigenvalue bound,
  a stated field-operation cost model concretely evaluated at
  q = 2^{64..512}: the walk-length separation log(k/c) is robustly vacuous
  at q=2^256 for small swept polynomial-degree parameter delta, becomes
  robustly non-vacuous only at the grid's largest swept delta (and only for
  4 of 5 swept values of the unpinned Lemma 4.1 constant), and the
  primary per-step cost model shows a genuine crossover against sqrt(n)
  at 192 bits within that regime -- zero curve instances tested, cost
  model only
tags:
  - jmv
  - isogeny-expander
  - random-self-reduction
  - grh-conditional
  - cost-model-evaluation
  - reduction-cost-audit
  - zero-instance
  - derivation
  - convention-dependence
  - analytic
confidence: established
confidence_note: >-
  Established via three independent checks converging on the same
  arithmetic: (1) the deterministic 400-cell computation itself, at 60
  decimal digits of mpmath precision with zero
  INDETERMINATE_AT_PRECISION-flagged cells; (2) a second Executor session's
  independent byte-for-byte re-execution of the full grid plus an
  independent hand-recomputation of one cell (bits=256, delta=1.0,
  convention=bits, C=1.0) from first principles, matching the archived
  value exactly (manifest.yaml DEV-3); (3) VAL-20260907-b0832b, an
  independent digit-level check of every load-bearing transcribed source
  statement against the actual retrieved, sha256-pinned
  arXiv:math/0411378v3 PDF, by a reviewer who did not produce the
  transcription. This is "established" as a statement about a deterministic
  cost model's arithmetic at declared parameters, GRH-conditional
  throughout (Lemma 4.1's bound is GRH-conditional as held and as
  confirmed against the source) and bearing on nothing outside that model
  -- it is not a claim that GRH is true, that any curve is weak, or that
  any attack exists or improves. Every cited numeric value is asymptotically
  consistent with the source (VAL-20260907-b0832b), with one disclosed,
  numerically-inert transcription/derivation inaccuracy corrected by
  CORR-20260907-b7e0f3 (see below).
internal_refs:
  - H-JMV-002
  - RQ-JMV-001
  - EXP-JMV-004
  - EV-JMV-05a150
  - DEC-20260907-43a1e0
correction_note: >-
  CORR-20260907-b7e0f3 is cited in prose below and corrects a stated
  derivation/mechanism defect in source_statements.md and cost_model.md
  (Section 4.3's k-formula) that VAL-20260907-b0832b found; it is
  numerically inert for every cell this finding cites (this run's own
  |D|=4q convention always lands in the source's own e=2 case). Per the
  established convention (see KN-FIND-c2e9a7), it is not listed in
  internal_refs since it is not a ctx.ids-tracked ledger record type in
  that sense.
proof_status: derivation
proof_refs:
  - experiments/EXP-JMV-004/runs/RUN-JMV-004-a/cost_model.md
  - experiments/EXP-JMV-004/runs/RUN-JMV-004-a/crossover.csv
  - experiments/EXP-JMV-004/reviews/VAL-20260907-b0832b.yaml
added: '2026-09-07'
superseded_by: null
---

## The finding

Under the Jao-Miller-Venkatesan (2005, arXiv:math/0411378) branch-(a)
proven, GRH-conditional Lemma 4.1 eigenvalue bound, evaluated as a fully
stated, cited, deterministic field-operation cost model (Proposition 3.1's
walk-length inequality times a per-step modular-polynomial root-finding
cost `O(l^3)` at typical `l ~ Theta(m)`, `m = (log q)^{2+delta}`) over the
grid `q_bit_sizes in {64,...,512}`, `delta in {0.25, 0.5, 1.0, 2.0}`, the
unpinned Lemma 4.1 implied constant `C in {0.5, 1, 2, 4, 8}`, and both
logarithm conventions for `m`'s formula:

- **The proven walk-length separation `log(k/c)` is robustly VACUOUS
  (`<= 0`) at `q = 2^256` for `delta in {0.25, 0.5}`**, across the entire
  swept `C` range and both logarithm conventions -- 10/10 cells negative
  at each `delta`, zero convention flips of any kind.
- **It becomes robustly NON-VACUOUS (`> 0`) only at the grid's largest
  swept `delta = 2.0`, and only for 4 of the 5 swept `C` values
  (`C in {0.5, 1, 2, 4}`)** -- agreeing under both logarithm conventions
  AND both degree conventions (8/8 cells, zero flips). At `C = 8.0` the
  PRIMARY degree convention (`k = Li(m)/2`) still gives a negative sign but
  the ALT convention (`k = Li(m)`) gives positive, making that one cell
  CONVENTION-DEPENDENT rather than a settled directional result.
- `delta = 1.0` does not produce a convention-robust conclusion in either
  direction at low `C` (`C=0.5` flips between logarithm conventions;
  `C=1.0` flips between degree conventions under `bits` but is a clean
  negative under `natural`); it is a clean vacuity at `C in {2, 4, 8}`.
- **A genuine crossover against `sqrt(n)` exists inside the non-vacuous
  regime**: at `delta=2.0, C=1.0`, PRIMARY per-step model (`phi_l O(l^3)`,
  typical `l`), the modelled reduction cost exceeds `rho = 2^{bits/2}` at
  160 bits (`cost_over_rho = 4152.6`) and falls below it from 192 bits
  onward (`cost_over_rho = 0.610` at 192 bits, `6.4e-5` at 224 bits),
  identically under both logarithm conventions. No crossover exists at
  all for `delta in {0.25, 0.5, 1.0}` at `C=1.0`, because the sign never
  turns positive there at any grid bit size.
- All three of `H-JMV-002`'s own pre-registered quantitative predictions
  (a robust negative cell at `q >= 2^128, delta <= 1`; a crossover ratio
  `>= 1` at some `q >= 128` bits; the `delta` needed for non-vacuity at
  `q=2^256` strictly exceeding the smallest tested `delta`) are satisfied
  by this grid.

**What this is not.** Zero curve instances are tested at any size
(`claim_tier: not_applicable`, permanently, per `specification.yaml`'s own
binding ruling). Every statement is `q` as a *parameter of a deterministic
model*, never a measurement on P-256 or any curve. Every quantitative
statement is GRH-conditional. Where vacuous, the correct reading is that
Corollary 1.2's concrete walk-length guarantee is asymptotically sound but
concretely UNPROVEN at the evaluated size under this model -- never that
the corollary is false or the reduction fails in practice. This is a
reduction cost audit, not an attack: it produces no ECDLP attack, no
attack-cost improvement, and bears on GRH not at all. It is explicitly
detached from `GOAL-ECDLP-001` and `GOAL-CRYPTO-001` (`RQ-JMV-001`'s own
structural constraint) and must not be read as evading the D1 or
BAR-AMORT-D2 barriers, which concern attacks.

## Scope, stated exactly

Branch (a) ONLY -- the proven, explicit-constant GRH-conditional Lemma 4.1
bound. Branch (b) (a constant `EXP-JMV-003` would measure) is not
approved, not executed, and not consumed anywhere. The grid is exactly
`q_bit_sizes in {64, 96, 128, 160, 192, 224, 256, 320, 384, 512}`,
`delta in {0.25, 0.5, 1.0, 2.0}`, `C in {0.5, 1, 2, 4, 8}`, both logarithm
conventions, PRIMARY degree convention `k = Li(m)/2` with the ALT
convention (`k = Li(m)`) reported only as an E2-CONVENTION sensitivity
check. Nothing is claimed about any unswept `delta`, `C`, or `q` outside
this grid. The crossover finding is scoped to the free-precomputation cost
variant only; the with-precomputation variant is reported only as an
order-of-magnitude coefficient count (`Phi_l` storage `~ m^2` per step,
`~ k_half * m^2` for the full generating set), not converted to a
field-operation figure, because no per-coefficient bit-size formula is
held in this program's corpus.

## The Section 4.3 correction folded in

`VAL-20260907-b0832b` found that this run's Section 4.3 transcription
states an incorrect MECHANISM for the `k ~ pi(m)/2` approximation ("a
split prime contributes one generator") against the source's own actual
mechanism (a split prime contributes TWO ideals of norm `p`; the `/2`
comes from dividing by the unit-count constant `e`, which the source
proves equals 2 whenever `|disc(O)| > 4`). **This is numerically inert for
every cell cited in this finding**, because this run's own `|D| = 4q`
convention makes `|disc(O)| = 4q > 4` for every `q >= 2^64` in the grid,
which always satisfies the source's own condition for `e = 2` --
mechanically identical numerically to the held (incorrect) derivation in
this run's own parameter regime, but not for the right reason.
`CORR-20260907-b7e0f3` documents the correct mechanism and recommends `e`
be added as an explicit constant in any future run reusing this cost
model; `source_statements.md`, `cost_model.md`, and `constants_table.csv`
are not edited.

## What survives, distinctly

The convention-robust findings above (vacuity at `delta in {0.25, 0.5}`;
non-vacuity plus crossover at `delta = 2.0, C <= 4`) survive on their own
terms independent of the Section 4.3 correction, because the correction
does not change any already-computed cell. The convention-DEPENDENT cells
(`delta=1.0` at low `C`; `delta=2.0, C=8`) are explicitly not claimed as
directional findings in either direction and remain open questions inside
this same grid, not resolved by this finding.

## Resource check

No active theory in this program currently takes a vacuous-at-2^256 or
non-vacuous-at-2^256 finding about the branch-(a) JMV separation as its
own premise. `KN-TECH-ee6696` (F3 row, committed 2026-09-05) explicitly
names this as an open gap ("no `KN-*` record names the obstruction for the
plain isogeny-walk-to-a-weaker-curve family... The open question is
`RQ-JMV-001`"). `H-ECTD-001`/`H-ECTD-19017a` (active) cite JMV's
qualitative expander-mixing theorem only as weak motivation for a distinct
heuristic and explicitly disclaim relying on it alone. `H-JMV-71b222`
(proposed, same track) is orthogonal in scope (source-transcription
verification and cross-level connectivity) and is not premised on this
concrete cost-model conclusion. This finding is a new, currently unconsumed
datum (`EV-JMV-05a150.obstruction.resource_check`).

## Attribution

Cost model, grid computation, and archival: Executor
(`TASK-20260906-a29dee`, two sessions, per `manifest.yaml` DEV-3).
Independent source-transcription (control C1) review: `VAL-20260907-b0832b`
(fresh session, did not produce the held transcription). Composition into
this evidence record, the Section 4.3 correction, and this finding:
Coordinator, `EV-JMV-05a150` / `DEC-20260907-43a1e0` / `CORR-20260907-b7e0f3`.
