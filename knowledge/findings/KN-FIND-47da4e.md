---
id: KN-FIND-47da4e
type: internal_finding
title: "Parameterising a Frobenius orbit union as (representative, shift) is cost-neutral for m = 2 point decomposition: the one-hot shift-encoded system costs what the n gauge-fixed subspace systems it replaces cost, plus about one conflict per shift ruled out -- ratio 1.02, 1.02, 1.47, 1.15 on CaDiCaL at n = 13, 17, 19, 23 and 1.00 to 1.21 on WDSat in both search modes at n = 19 and 23, never below 1, approaching 1 from above"
tags: [ecdlp, frobenius, koblitz, subfield-curve, index-calculus, factor-base, orbit-union, point-decomposition, semaev, weil-descent, sat, wdsat, xor-gauss, cadical, relabelling, toy-tier, negative-result, promotion-gate-unmet]
confidence: unverified
confidence_note: >-
  `unverified` is the honest label and the reason is provenance, not the
  numbers. One agent wrote the instruments, the exporter and the runner and read
  the results, in one interactive session, outside the experiment lifecycle. No
  frozen contract, no harness run record, no validator or red team in this
  program has read any of it. The internal cross-checks below are real -- two
  independent solvers, two search modes, solver-free ground truth, a planted
  positive control, an exact re-run -- and they are still not this ledger's
  independence check.
promotion_gate: >-
  NOT MET, STATED HERE SO NO READER HAS TO INFER IT. knowledge/README.md
  promotes a finding only from an evidence record of strength `replicated` or
  `strong` and only on a Coordinator decision. EV-FROB-b6e1e9 is `preliminary`
  and unreviewed, and no decision composes it. This entry is therefore a
  DEPOSIT of a measurement and its provenance in the place a later reader will
  look, not a promoted result: it may not support a hypothesis status change,
  may not discharge a completion criterion, and may not be cited as internal
  ground truth. DEC-20260918-4b7e21 blocked exactly that propagation for a
  record of this provenance class.
evidence_level: toy_tier_measurement_single_unreviewed_instrument
source_refs: []
source_refs_note: >-
  Empty for the reason KN-FIND-9cba50 states for itself: the instruments are
  `python3` invocations of scripts committed under
  analysis/frobenius-orbit-union/, not runs of this program's harness, so no
  TASK-* or RUN-* exists and inventing one would be a fabrication under
  AGENTS.md rule 5. Content binding by sha256 is in EV-FROB-b6e1e9's
  external_provenance block.
internal_refs: [EV-FROB-b6e1e9]
internal_refs_note: >-
  Held to the EV-/DEC-/EXP- classes knowledge/README.md names for this field, and
  in fact to the single evidence record this entry is distilled from. The
  campaign and question it bears on are GOAL-FROB-6333a9 and RQ-FROB-7d8dd4,
  named in related_refs and in the body; neither is touched by this entry.
related_refs: [RQ-FROB-7d8dd4, GOAL-FROB-6333a9, H-FROB-a5bf86, EXP-FROB-30006a, DEC-20260920-cf8ded, IDEA-20260906-a77711, IDEA-20260918-9abf42, IDEA-20260918-6c07e1, KN-LIT-796]
sibling_findings_narrowed: []
sibling_findings_note: >-
  Narrows no existing finding. It fills a hole: the REP+INDEX arm of
  EXP-FROB-ORBIT-1 in research/ideas/frobenius_orbit_experiment_matrix.md was
  written down and never run, and the slate's own kill criteria name this
  outcome ("representative/index parameterization increases solver branching
  enough to erase the orbit saving") without anyone having measured it.
proof_status: empirical_only
proof_refs: []
proof_status_note: >-
  Empirical only, and the caveat is load-bearing. A conflict count is a property
  of a SEARCH, not of the algebra. It is not a solving degree, not a first-fall
  degree, and not a lower bound: a better encoding or a better solver could move
  any row. The additive-overhead reading in "Why it is cost-neutral" is an
  interpretation of the measurement and is labelled as one.
review_refs: []
review_refs_note: >-
  None, in this program or anywhere. Unlike KN-FIND-9cba50 there is not even an
  automated review on a producing pull request to point at; the only checks are
  the instrument's own, listed under "What was checked".
added: '2026-09-21'
superseded_by: null
---

# The orbit-union shift encoding relabels the work instead of removing it

## The setting, and why the family exists at all

At the ECC2K-130 degree no Frobenius-stable `F_2`-**subspace** of
index-calculus dimension exists. `ord_131(2) = 130`, so `T^131 - 1` has two
irreducible factors over `F_2` and the stable subspaces are exactly four, of
dimensions `0, 1, 130, 131` (`IDEA-20260918-9abf42`; the same arithmetic
reaches the root-set version in `IDEA-20260918-6c07e1`). Every dimension an
index calculus would want is empty.

Frobenius-stable **sets** are not empty, and that is the opening this entry
tests. `131` is prime, so every element outside `F_2` has an orbit of size
exactly `131`, and a union of `k` orbits is stable at any size. The
Galbraith–Granger–Merz–Petit collapse (`KN-LIT-796`) asks only for
`π(F) = F`, so it is available on such a union. What a union lacks is a cheap
algebraic description the decomposition solver can use, and the natural
candidate is to parameterise a point as `(orbit representative, shift)` and
let the solver choose the shift.

## What was measured

Over toy Koblitz curves at `m = 2`, with `S` the orbit union of a random
subspace `V'` sized so `|S| ≈ 2^{n/2}`:

- **baseline** — the `n` separate Semaev systems `x_1 ∈ V'`, `x_2 ∈ σ^j(V')`.
  The global Frobenius gauge fixes the first summand, so these cover the
  target's whole orbit and any conjugate's relation is as good as the
  target's. This is the `n^{m-1}` system count the encoding must beat.
- **one-hot** — one system with `n` shift bits, exactly one true.

Mean conflicts per refuted target, one-hot divided by the summed baseline:

| n | CaDiCaL 1.5.3 | WDSat plain | WDSat XG-ext |
|---|---|---|---|
| 13 | 1.017 | — | — |
| 17 | 1.017 | — | — |
| 19 | 1.467 | 1.017 | 1.212 |
| 23 | 1.150 | 1.000 | 1.033 |

Eight cells, two solvers, two search modes. The ratio is at or above one in
every cell and approaches one from above as the degree grows. It is never
below one.

## Why it is cost-neutral, and why that is more informative than a loss

The gap is additive. On WDSat the one-hot arm costs the baseline plus 95, 18,
22 and 22 conflicts on the four rows, and three of those are within one of
`n - 1`. An additive term of about one conflict per discarded shift is what a
search that enumerates the same tree as the `n` separate searches, closing each
wrong shift once, would cost.

Read that way the encoding is not losing. It is doing precisely the same work
under a different name, which is the `relabelling` class in the sibling
repository's reporting taxonomy: the headline system count falls from `n` to
one while total work does not move. That is also the first measurement behind
`IDEA-20260906-a77711`'s standing argument that Frobenius is an equivariance
between the systems of **conjugate** targets rather than a symmetry of the
system of one fixed target, and the first taken on a non-linear stable factor
base rather than a linear one.

Two secondary facts matter for anyone repeating this:

- **XOR-native reasoning does not rescue it.** WDSat's XG-ext mode cuts the
  baseline by 69 times at `n = 19` and 220 times at `n = 23`, and the one-hot
  arm by 58 and 213. Both arms gain, so the ratio survives. This closes the
  obvious escape from a conventional-solver-only negative.
- **Branching order dominates, and the table above is the encoding's best
  case.** With the solver's default variable order the one-hot arm costs 2.5 to
  15 times the baseline. Every row above instead hands the shift bits a
  branching-priority prefix.

## What was checked

Every target in the largest cells refutes, so verdict agreement alone would
also be satisfied by a solver that never finds anything. Ground truth is an
exhaustive solve of the quadratic `S_3` over every `x_1 ∈ V'`, computed with no
solver, and all arms match it everywhere. Four decompositions were then
**planted** with both summands in the required sets: each was found by exactly
the predicted shift and no other, and every model verifies as a genuine
decomposition. The exported WDSat instances are confirmed identical to the
instances the conventional solver measured, target by target. The `n = 19` cell
reproduces to the exact conflict after an unrelated output-parsing fix.

One arm was discarded and the reason is the solver, not the encoding. The
binary shift encoding carries degree-7 monomials; on WDSat its two search modes
disagree on satisfiability and the default mode returns a model violating 11 of
an instance's 32 rows. Degree 7 is outside the degree 3–4 envelope every
shipped `config.h` profile targets.

## What this does NOT claim

- **Nothing at any cryptographic degree.** The reachable range is `n ≤ 23`
  against targets at 131 and above. The largest subgroup touched is 23 bits.
- **`m = 2` only.** The chained system at `m ≥ 3`, which is where an index
  calculus at a cryptographic degree would have to live and which carries
  `(m-2)·n` extra unknowns, is not built at all. The additive-overhead reading
  predicts the overhead grows with `n` and not with `m`; that is untested and is
  the natural next cell.
- **One parameterisation of one family.** It prices `(representative, shift)`
  coordinates. It says nothing about orbit unions used with a materialised
  meet-in-the-middle oracle, which is a different trade and is priced elsewhere,
  and nothing about any use of the orbit structure that changes the coordinate
  **blocks** rather than the index over shifts. The cheapness of the shift
  overhead is precisely what leaves that direction open.
- **Nothing about the linear stable factor bases.** `H-FROB-a5bf86` and
  `EXP-FROB-30006a` test `ker g(σ)` at `n = 41` and `43` against the null
  `2^{m l}/m!`. Different object, different cells, different null. This entry
  scores none of that hypothesis's predictions and must not be read as
  anticipating its result.
- **No exponent moves in either direction, and no lane closes.** The
  factor-base and linear-algebra constants of `KN-LIT-796` are not in question
  and are not measured here. `RQ-FROB-7d8dd4`'s decision target is unmet: its
  target (a) requires a matched null object, a curve over `F_{q^n}` defined over
  no proper subfield, which these instruments do not build.
- **A separate arithmetic exclusion is adjacent and not claimed here.** The
  Couveignes–Lercier constructions that `KN-LIT-796` §4.2 reproduces need a
  one-dimensional commutative group over the base field with a rational point of
  order `n`; over `F_2` at `n = 131` the torus route needs `131 | q + 1 = 3` and
  the elliptic route needs a multiple of 131 inside the Hasse interval, so both
  fail by the paper's own stated conditions. An enumeration extending that to
  abelian varieties of dimension up to four is incomplete at dimension three
  (211 of the 215 known classes) and belongs in its own entry with that caveat,
  not in this one.

## Successors

1. The `m = 3` cell of the same comparison.
2. A design task turning this arm into a frozen contract with the null object
   `RQ-FROB-7d8dd4` requires, so a repeat is a run and not a session artifact.
3. The pointer in `EV-FROB-b6e1e9`'s `resource_check`: under XG the **baseline**
   sits 12 and 24 times below its own orbit-naive enumeration bound at `n = 19`
   and `23`, while the same instances in plain mode sit 5.6 and 9.0 times above
   it. Whether that gap holds for the linear stable `V` at `H-FROB-a5bf86`'s
   cells is cheap to check and bears on how that experiment's null should be
   read.
