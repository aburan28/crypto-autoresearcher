---
id: KN-OPEN-f008ae
type: open_problem
title: H-CREP-001's z_R has a genuinely improved but still over-cap meet-in-the-middle construction (Theta(B^3) two-pairs / Theta(B^2) one-pair); the online-cost accounting ambiguity is resolved
tags: [ecdlp, h-crep-001, exp-crep-001, resultant, semaev, meet-in-the-middle, construction-cost, obj-8]
confidence: unverified
status: open
source_refs: [KN-OPEN-701adf, DEC-20260830-69fb4d]
added: 2026-08-30
superseded_by: KN-OPEN-2f5e66
---

## Statement

`TASK-20260830-53a818` (idea-generator), investigating `OBJ-5` (does a
compact/implicit representation of `z_R = gcd(g_I, r_R)` exist within
`H-CREP-001`'s exponent caps?), found a genuine, independently re-verified
improvement over naive direct materialization: combining a classical
resultant root-product identity (`r_R(t_a)` computed as a product over the
pair-decks' roots, never building a coefficient vector) with a
meet-in-the-middle decomposition exploiting Semaev's `S_3` relation having
FIXED degree 2 in each variable (independently confirmed against
`knowledge/techniques/KN-TECH-002.md`) gives:

- **Two-pairs reading**: `Theta(B^3)` online — down from naive `Theta(B^4)`.
- **One-pair reading**: `Theta(B^2)` online — same exponent as naive
  materialization, but coefficient-vector-free.

**Both bounds still exceed `H-CREP-001`'s declared
`fresh_target_online_exponent_cap_in_B: 1.25`** by 1.75 and 0.75 in
exponent respectively. No impossibility is claimed; disposition is
correctly `no_construction_found_inconclusive`.

## OBJ-8 resolved

`KN-OPEN-701adf`'s producer flagged an ambiguity in how `H-CREP-001`'s own
cap language should be read (per-single-query vs. whole-target-set
accounting), which would determine whether a `Theta(B)`-per-query result
(not actually found this round) would matter. `DEC-20260830-69fb4d`
resolves this: `H-CREP-001.yaml`'s own `falsification_conditions` state
the cap is exceeded when "total fresh-target work or peak workspace,
**including all replay calls**, exceeds `B^(5/4+o(1))`" (aggregate
language), and `EXP-CREP-001/specification.yaml`'s `V6_cost_caps`
predicate separately tracks `replay_calls_per_tuple` as a distinct
`test_boundary` parameter from the cap itself — consistent only with the
cap summing over potentially many tuples in one online phase. This
**forecloses** the per-query reading; whole-target-set accounting is the
frozen, authoritative interpretation.

## A control precision gap (disclosed, not load-bearing)

The producer's proves-too-much control claimed that substituting a
hypothetical growing-degree relation for `S_3`'s fixed degree 2 degrades
the method back to "exactly" the naive cost under both readings.
Independently re-checked: true for the two-pairs case (`B^4 = B^4`), but
the one-pair degraded case actually gives `Theta(B^3)`, strictly *worse*
than the real one-pair naive baseline of `Theta(B^2)` — not an exact
match. The control's directional conclusion (the speedup genuinely depends
on `S_3`'s fixed degree) survives; its one-pair precision claim does not
and should be corrected if this control is cited or reused.

## The open question, precisely

Does ANY construction (not just this specific meet-in-the-middle
approach, whose ceiling is now derived in `TASK-20260830-53a818`'s
`proof-search-map.yaml`) reach `H-CREP-001`'s declared
`1.25`/`2.25` exponent caps for `z_R`, under either reading? The gap
narrowed from a full exponent (naive `B^4` to `B^3`) but a further full
exponent (`B^3` to `B^1.25`, or `B^2` to `B^1.25`) remains.

## What would resolve this

A genuinely new structural idea distinct from this round's meet-in-the-
middle approach (whose own ceiling has been derived and should not be
re-attempted absent a new insight), or a genuine derived lower-bound
argument (with its own correctly-executed proves-too-much control) showing
no construction can reach cap under either reading.

## Provenance

- `knowledge/open-problems/KN-OPEN-701adf.md` (kb — the superseded, narrower framing before this round's improvement)
- `ledger/decisions/DEC-20260830-69fb4d.yaml` (kb — this round's independent verification and closeout)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-COMPACT-ZR-CONSTRUCTION-20260830-53a818/tasks/TASK-20260830-53a818/derivation-report.yaml`, `proof-search-map.yaml` (kb — the originating construction and its method-ceiling audit)
- `knowledge/techniques/KN-TECH-002.md` (kb — Semaev S_3's fixed degree-2 fact)
- `ledger/hypotheses/H-CREP-001.yaml`, `experiments/EXP-CREP-001/specification.yaml` (retrieved — the frozen cap language resolving OBJ-8)
