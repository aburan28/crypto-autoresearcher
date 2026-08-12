---
id: KN-TECH-076
type: technique
title: Automated trail search (MILP / SAT / SMT / CP) and the reporting gap between an optimal trail and a real advantage
tags: [automated-search, milp, sat, smt, constraint-programming, trail-search, active-sboxes, model-correctness, clustering-effect, search-hygiene, tooling, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "no closed-form cost: the output is a solver verdict on an encoding, and run time is instance-specific. A proved-optimal trail bounds only trails, never the differential or hull that an attack exploits"
applicability: searching for differential/linear trails, active-S-box lower bounds, impossible-differential and zero-correlation distinguishers, division-property propagation, and cube selection; the standard implementation layer beneath most of KN-TECH-062 through KN-TECH-074, KN-TECH-077, and KN-TECH-079
source_refs: [KN-TECH-062, KN-TECH-063, KN-TECH-064, KN-TECH-068, KN-TECH-069, KN-TECH-074, KN-LIT-385, KN-LIT-2644, KN-LIT-2567, KN-LIT-2646, KN-LIT-3896, KN-LIT-1034, KN-LIT-3165, KN-LIT-2927, KN-LIT-4389, KN-LIT-5934, KN-LIT-3730, KN-LIT-2642]
added: 2026-07-31
superseded_by: null
---

## Method

Since about 2011 the search step of symmetric cryptanalysis has been delegated
to general-purpose combinatorial solvers. The move is uniform across the family:
express propagation as constraints, express the objective as a cost, and let a
solver return an optimum with a proof of optimality *within the model*.

**The encodings, and what each is good for.**

- **MILP.** Mouha–Wang–Gu–Preneel's word-level active-S-box counting was the
  opening; Sun et al. (`KN-LIT-385`) moved it to bit level by modelling S-box
  differential transitions as linear inequalities (derived from the DDT's
  support, typically via convex-hull computation), which brought related-key
  characteristic search into scope. MILP is now the default for active-S-box
  bounds, division-property propagation (`KN-LIT-2567`, `KN-LIT-2646`,
  `KN-LIT-3165`) and cube selection (`KN-LIT-4389`).
- **SAT/SMT.** Better where the constraint is bit-logical and the objective is
  a threshold rather than a linear cost — the natural fit for ARX designs, where
  modular addition has a clean bit-level differential characterisation
  (`KN-LIT-2644`, best trails for Speck).
- **Constraint programming.** Strongest where the structure is combinatorial and
  the propagation is naturally table-driven: related-key boomerangs
  (`KN-LIT-1034`), Demirci–Selçuk meet-in-the-middle configurations
  (`KN-LIT-5934`, `KN-LIT-3730`), key-bridging (`KN-LIT-2642`).
- **Unified distinguisher search.** One model can emit impossible-differential,
  zero-correlation and integral distinguishers together (`KN-LIT-3896`), which
  is the practical payoff of the equivalences catalogued in `KN-TECH-069`.

**Two-stage practice.** Real searches usually run in two stages: first minimise
the number of active S-boxes (a coarse, cheap model), then instantiate the
surviving patterns with actual differences to obtain a probability. Conflating
the stages — quoting an active-S-box bound as a probability — is a common
reporting slip.

## The reporting gap — the reason this entry exists

An automated search returns *the best trail in the model*. Four distinct things
that is not:

1. **Not the differential's probability, nor the hull's correlation.** Attacks
   exploit sums over trails (`KN-TECH-062`, `KN-TECH-068`); clustering can put
   the real quantity well above the best single trail, as documented for Simon
   and Simeck (`KN-LIT-2927`), and cancellation can put it below. A search
   result is a **single term**, and calling it the answer is the same category
   error `KN-TECH-053` records for solver exponents versus end-to-end exponents.
2. **Not a security proof.** "No trail better than `2^{-x}` up to `r` rounds"
   bounds trails under the model's assumptions. It does not exclude attacks that
   are not trail-shaped — invariant, integral, algebraic, meet-in-the-middle —
   which is precisely the scope lesson of `KN-TECH-070`.
3. **Not independent of the encoding's correctness.** The verdict is about the
   model. A wrong inequality set for an S-box, a missing constraint on the key
   schedule, or an unsound modular-addition encoding produces a confident,
   optimal, wrong answer. Independent re-encoding, or verification of found
   trails against a reference implementation, is the standard check — and a
   found trail is *checkable in one evaluation*, which makes its absence in a
   report notable.
4. **Not a complexity statement.** Solver run time on these models has no useful
   a-priori bound. A reported wall-clock time is an observation about one
   instance, one encoding and one solver version.

**And the asymmetry that matters most: a solver timeout proves nothing.**
"No trail found within the budget" is not "no trail exists" unless the search
terminated with a proof of optimality. This is the exact rule `AGENTS.md`
already binds this program to — timeouts are never negative mathematical
evidence — arriving from the symmetric side.

## Program usage

- **Directly reusable tooling.** This program already solves structured search
  and feasibility problems (mixed-volume and polyhedral methods in
  `KN-TECH-007`, sparse linear algebra in `KN-TECH-008`, MQ/Boolean solving in
  `KN-TECH-053`). The symmetric field's experience with MILP/SAT/CP encodings —
  particularly the discipline of *proving the encoding correct separately from
  running it* — transfers to any experiment here that hands a research question
  to a general-purpose solver.
- **A model of how to report a solver-backed result.** The mature papers in this
  line state: the encoding, the solver and version, whether optimality was
  proved or the search was truncated, and the gap between the trail found and
  the quantity of interest. That list is a good template for this program's own
  run records, and maps onto the manifest requirements already in force.
- **Precedent for the inventor protocol's closure standard.** `KN-TECH-056`
  demands real closure rather than exhaustion of patience; a proved-optimal MILP
  bound is a closure, a timed-out search is not, and the difference is exactly
  what the protocol asks proposals to state in advance.

## Applicability limits

- **Model size is the binding constraint.** Bit-level models of large states
  over many rounds routinely exceed practical solver limits, which is why
  word-level abstractions and two-stage searches persist.
- **The abstraction chosen decides what can be found.** An activity-pattern
  model cannot find a distinguisher that depends on difference values; a
  fixed-key phenomenon is invisible to an averaged-key model.
- **Optimality is relative to the objective.** Minimising active S-boxes and
  maximising differential probability are different objectives and can select
  different trails.
- **Reproducibility is fragile.** Solver version, seed, symmetry breaking and
  time limit all affect what is returned; a result reported without them is not
  independently checkable.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The encoding techniques, the
two-stage search practice and the trail-versus-differential gap are standard
published knowledge of the public literature, written from established knowledge;
**no model in this entry was implemented, run, or checked in this program.**
Mouha–Wang–Gu–Preneel's originating MILP paper is named in prose, this corpus
holding no entry for it; no identifier was minted. All cited `KN-LIT` records are
title-level per the family note — the technique-to-target attributions (Speck
trails to `KN-LIT-2644`, Simon/Simeck clustering to `KN-LIT-2927`, unified
impossible/zero-correlation/integral search to `KN-LIT-3896`) are read from
titles, and no complexity, bound, or run time from any of them is quoted. The
mapping of the timeout asymmetry onto `AGENTS.md`, and of solver-result reporting
onto this program's run-record requirements, is this program's own reasoning.
