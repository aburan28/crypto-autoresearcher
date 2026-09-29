---
id: KN-FIND-4b8d73
type: internal_finding
title: "A dispersion criterion is a joint property of (observable, arithmetic route, family): three independent escapes across two independent review sessions"
tags: [dispersion-criterion, admissibility-gate, g-var, g-var2, am-11, am-16, floating-point, family-conditionality, fibre-condition, instrument-design, null-object, observable-invariance, review-replication, ml-kem, negative-result, toy-scale, correction]
confidence: derivation_plus_two_session_replicated_conclusion_with_single_source_mechanisms
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-9e3584, BATCH-cbe023, TASK-20260809-cda2f6, TASK-20260809-444fe7, TASK-20260809-3f1dc4, TASK-20260812-aadafd, TASK-20260812-da8c3b]
internal_refs: [EV-MLKEM-9346bb, EV-MLKEM-e45478, DEC-20260809-afe29b, DEC-20260812-15d3b2, DEC-20260812-7c4a1e, DEC-20260808-05b684]
sibling_findings_narrowed: [KN-FIND-2a35aa, KN-FIND-f38a89]
sibling_findings_note: "`internal_refs` carries LEDGER records only, which is the shape the validator checks and the shape `KN-FIND-2a35aa` itself uses when it narrows `KN-FIND-f38a89`. The two sibling findings this entry narrows are named here and throughout the body; neither is edited and neither `superseded_by` is set."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_relabel_witness.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-da8c3b/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-3f1dc4/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-da8c3b/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/red_team_report.md
added: '2026-08-12'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured at
`q <= 3329`, `d in {20, 30, 40, 100, 140}`, the frozen `(k, beta)` grid, 8 frozen
bases per lattice, no reduction beyond the frozen HKZ pipeline at `d <= 40`. There
is no cryptographic baseline in the batch, so `dominated_by` and `sota_delta` are
`null` **for that reason** and not by omission. No number here transports to
`beta = 606`, `d = 1420` or any other parameter set by any route.

The finding, in one sentence:

> A between-basis dispersion criterion is a **joint property of the triple
> (observable, arithmetic route, family)**. In `GOAL-MLKEM-005` all three were
> undeclared free parameters of the gate, and the same operationalization was
> defeated through **each** of them, by **three structurally different
> constructions**, produced by **two independent review sessions that did not read
> each other**.

## 1. Why this entry exists, and what it narrows

`KN-FIND-2a35aa` records the first of the three escapes (the arithmetic route). It
was written by a Coordinator that had seen **one** review wave. A second,
independent review wave over the **identical producer bytes** under the **identical
frozen cards** subsequently produced two further escapes and one boundary that entry
does not carry. This entry narrows `KN-FIND-2a35aa` in exactly three places, by
reference:

1. **`KN-FIND-2a35aa` states the `G-VAR` refusal without naming the FAMILY as a
   condition.** It is family-conditional (§3 below).
2. **Its opening paragraph carries "no admissibility claim is reportable from that
   gate in either direction."** Only the PASS side was demonstrated; the gate's
   REFUSAL side is untested and its false-refusal rate has never been measured, so
   that phrasing closes more than was shown (§4).
3. **Its §6.1 declares the counterexample SINGLE-SOURCE and asks a successor to
   re-run `probe_nullroute.py`.** That request is **still open** — the second wave
   did not re-run it and did not test routes R2, R4 or R5. What the second wave
   supplied instead is *different* escapes, which is a stronger result than a
   re-run and does **not** substitute for one.

`KN-FIND-2a35aa` is immutable and is **not edited**; its `superseded_by` stays
`null`, exactly as it left `KN-FIND-f38a89`'s. The adjudication is
`DEC-20260812-7c4a1e`.

## 2. The three escapes, kept apart

All three attack the same clause — `AM-11` of `DEC-20260808-05b684`, "an admissible
observable must have non-zero dispersion across the frozen bases at fixed
`(d, k, beta, q)`", implemented in `BATCH-9e3584` as `G-VAR` with `tau_var` exactly
`0`, decided by **bit identity of 8 IEEE-754 doubles**. They are otherwise unrelated,
and **none is a replication of another.**

| # | what is perturbed | what is held fixed | result | source |
|---|---|---|---|---|
| E1 | the **arithmetic route** | the function, the family | 3 of 6 routes to `X_null` are `0 of 38` bit-identical and are **ADMITTED**, while reproducing the notarized reference table at **304 of 304** entries and walking `G-REL1` 10/10 and `G-REL2` 19/19 | wave 1, red team, `probe_nullroute.py` |
| E2 | the **observable**, by `+1e-9·A[0,0]/q` (relative size ~`1e-10`) | the route, the family | not bit-identical at **any** of the 38 cells (max between-basis float `sd` `3.91e-10`); **ADMITTED**; passes `G-REL1` 10/10 and `G-REL2` 19/19 under every aggregation rule including the strictest | wave 2, validator, finding `O-2` |
| E3 | the **family**, by one entry: `m_i[0] = q + i` | the observable, the route, the `A_i` draw, every threshold | `G-VAR` fires **38 of 38** on `rdet` and `X_null` in `F0` and **0 of 38** on both in `F1`, while they still read **zero entries of `A_i`** in either family | wave 2, red team, `RT-R1`, `probe_gvar_family.py` |

**E1 detail.** The six routes to `log|det B|` are all exactly `(d-k) log q` for every
`A` under `B = [[I_k, A],[0, q I_{d-k}]]`. R0 closed form: 38/38, REFUSED. R1
`slogdet(B)`: rel. dev. `1.1e-15`, 38/38, REFUSED. **R2 QR of `B^T`**: `5.07e-14`,
**0/38, admitted**. R3 `slogdet(UB)`, `U` unimodular: `9.8e-16`, 38/38, REFUSED.
**R4 `0.5 slogdet(BB^T)`**: `2.35e-09`, **0/38, admitted**. **R5 `slogdet(BH)`,
`H` an ambient isometry**: `3.11e-14`, **0/38, admitted**. `R5` is the transform the
gate's own `G-INV` `T1` clause applies. Escaping-route between-basis float `sd`:
`1.20e-13` (R2) and `5.44e-14` (R5), against `hkz`'s committed `0.023888` at
`L7 beta = 5`.

**E3 detail.** A separate witness probe reports `F1`'s `X_null` taking **8 distinct
IEEE-754 values strictly increasing in the basis index** at 6 of 6 cells tested,
against **1 distinct value** at 6 of 6 in `F0`: its entire between-basis variation is
a monotone relabelling of the index. Cost `0.24 s` per candidate at `d <= 140`, no
reduction.

**The producer's own committed artifact already carried E1's mechanism**
(`results_relvar.json`, `forced_arithmetic`): `rdet_T1_ambient_isometry_residual =
3.865352482534945e-12` while the `T2` and `T3` residuals are exactly `0.0` — a
non-zero residual that a bit test cannot see, in the batch's own numbers.

## 3. The bound neither wave could state alone

`DEC-20260809-afe29b` amendment **`AM-16`** already replaces `G-VAR` with `G-VAR2`,
a **scaled** criterion — between-basis `sd` against the candidate's own between-cell
range at fixed `(d, k)`, reported as a per-cell profile — and `AM-16(d)` requires it
to be validated, before it governs anything, against `probe_nullroute.py`'s six
routes. **That fixture lives entirely inside `F0`.**

Escape **E3** is not repaired by scaling. In `F1` the dispersion is genuinely large,
so a scaled criterion **admits** `rdet` and `X_null` there while they still read no
entry of the instance. So:

- **`G-VAR2` as specified inherits the defect `E3` names, and the `AM-16(d)` fixture
  cannot detect it.** Wave 1 wrote `AM-16` without `F1`; wave 2 built `F1` without
  ever reading `AM-16`. This composition is visible only from both chains at once.
- **The named separator** — wave 2's, and it has been **named and never scored** —
  is dispersion **on the fibre of the family over the observable's own declared
  arguments**: `X` must be non-constant on the fibre, evaluated on a family
  constructed to hold that argument fixed. A functional of `|det B|` alone must be
  scored on a family that holds `|det B|` fixed, whatever else varies.
- Carried as amendment **`AM-17`** in `DEC-20260812-7c4a1e`: `AM-16` stands, its
  validation fixture is **extended to both** `F0` and `F1`, the fibre clause is
  added, and **every dispersion criterion must declare the family it is evaluated
  on as part of the criterion.**

**A prediction, declared before the run and not a result.** On the committed numbers,
`E2`'s `V_evade` carries a between-basis float `sd` of `3.91e-10` against a
between-cell range of order `1`, so a *scaled* criterion is predicted to **REFUSE**
it — i.e. `E2` defeats `G-VAR` but not its replacement, while `E3` defeats both.
**Falsification condition:** if the successor's scaled criterion admits `V_evade`,
`AM-16(a)` needs its own replacement and not merely the fibre extension. **Nobody
has measured this**; it is a derivation from two committed numbers.

## 4. The closure that was too wide

"No admissibility claim is reportable from this gate **in either direction**" is a
**closure**, and `docs/inventor-protocol.md` §4 holds a closure to a named
obstruction, an argument, and forward guidance. What was demonstrated is that
**passing** the gate carries no information: a blind closed form clears every clause.
**Nothing was shown about the refusal side.** A candidate the gate rejects is
rejected by a criterion whose **false-refusal rate has never been measured**.

The citable decomposition, which replaces the compressed phrase:

1. the gate's **PASS side is uninformative on the frozen family `F0`** — a
   parameter-determined closed form and an **unplanted** member of the frozen
   candidate list both clear every clause evaluated;
2. the gate's **REFUSAL side is untested in either direction**;
3. **no admissibility claim about any candidate is made by either wave.**

The cheapest test of the untested side, named and priced by wave 2 and not run by it:
build one observable informative by construction and structurally refused — e.g. a
statistic over the leading `k` raw-GSO log-norms, which depends on `A` and on `k` but
takes no `beta` argument and so fails `REL-1` by algebra exactly as `rdet` and
`lam1n` do. Minutes of numpy, one QR per basis, no reduction.

## 5. Scope and limits — read before citing

1. **THE CONCLUSION IS TWO-SESSION REPLICATED; EVERY MECHANISM IS SINGLE-SOURCE.**
   "The frozen dispersion operationalization does not repair the gate" was reached
   independently in both waves. `E1`, `E2` and `E3` are each **one probe, one run,
   one reviewer**, reproduced by no party independent of the reviewer that built it.
   Any citation must carry this split. Re-running `probe_nullroute.py` costs `0.31 s`
   and `probe_gvar_family.py` costs `0.24 s`; a successor should run both.
2. **INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** AGENTS.md rule 12 is
   **UNMET AND UNWAIVED** in this goal. All four reviewer sessions across the two
   waves, all four producers and every Coordinator involved resolve to the **same
   model**, and every review records `model_verified: false`. **Two review waves is
   two independent SESSIONS on ONE model with identical frozen cards and identical
   inputs — not two models**, and nothing in this entry may be cited as model-level
   corroboration.
3. **`R-OUT-1`'s measured core is not disturbed and is now five-implementation
   replicated within `F0`:** `X_null` and the unplanted `rdet` are bit-identical
   across all 8 frozen bases at all 38 scored cells with `float_sd` exactly `0.0`,
   while walking `G-REL1` 10/10 and `G-REL2` 19/19. What this entry bounds is its
   **portability**, not its arithmetic.
4. **Derivations, not theorems, and no impossibility claim.** That distinct float
   routes to one exact quantity differ in their last ULPs is elementary; that a
   criterion thresholded at exactly zero cannot separate "no information" from
   "information at `1e-16`" is elementary; `E3` is a construction. **Nothing here
   says a dispersion criterion cannot work** — §3 names one that might, and it is
   untested.
5. **Reproducibility, not portability.** Every probe in both waves ran on the
   producers' own `python 3.11.15 / numpy 2.4.6 / scipy 1.17.1` stack. Separately,
   **`fpylll` was absent in both wave-2 sessions**, so `lam1n` and `hkz` were not
   independently re-derived there; that is **lost coverage and never counterevidence**
   (AGENTS.md rule 5). The wave-1 Validator, which had `fpylll 0.6.4`, re-executed the
   lead end to end and reproduced `results_relvar.json` **bitwise** except wall-clock
   timings — through the producer's own code, so it cannot catch a specification error.
6. **`AM-3` IS NOT RETIRED**, `BATCH-a44d08` IS NOT RESCORED in any respect, and
   `AM4-OBS-1` is cited only through `KN-FIND-f38a89`. Nothing here bears on them.
7. **One direct contradiction between the two waves is open and is not settled by
   this entry**: the two validators disagree on how many `G-REL2` cells fall below
   `6x` of `tau_rel` (fifteen of nineteen against two of twenty-nine entries), from
   the same committed file. Neither count is citable until the seconds-long
   tabulation named in `DEC-20260812-7c4a1e` C-1 has run. The **corrected range
   `4.87x` to `31.03x`** — and the falsity of the report's "6 to 31" — is agreed by
   both and *is* citable.

## Identifier provenance

`KN-FIND-4b8d73` was drawn **without scanning state** (AGENTS.md rule 14), then
confirmed by **two scopes**: worktree `tools/allocate_id.py --check` (well-formed,
0 occurrences across 12,143 files) **and** a cross-ref sweep run by the dispatching
session (0 hits across the 25 most-recently-updated remote branches; not tracked
under `knowledge/findings/` on `origin/main`). The second scope is recorded because
**`--check` scans the working tree only and never other refs** — the defect that let
the same tool report `EV-MLKEM-9346bb` and `DEC-20260809-afe29b` "free across the
union" while both were already bound on a pushed branch. A passing `--check` is
necessary and **not** sufficient, and this entry does not claim `--check` alone.

## Superseding relationship

This entry **narrows** `knowledge/findings/KN-FIND-2a35aa.md` in the three places
listed in §1, and inherits its narrowing of `knowledge/findings/KN-FIND-f38a89.md`
§4 item 3. Neither prior entry is edited and neither `superseded_by` is set: both
remain correct on what they measured, and both are extended rather than corrected.
**Declared cost of that discipline**, restated because it compounds with each link: a
reader arriving at `KN-FIND-f38a89` or `KN-FIND-2a35aa` first is not pointed forward
to this entry. That is an accepted consequence of immutability; the links exist here
and in `DEC-20260812-7c4a1e.knowledge_promotion`.
