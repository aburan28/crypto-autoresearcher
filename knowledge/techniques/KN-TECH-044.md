---
id: KN-TECH-044
type: technique
title: Charging memory in lattice attacks - full cost applied to sieving
tags: [full-cost, memory, sieving, cost-model, kissing-number, enumeration, crossover, ram-model, area-time, cross-domain, lattice, ecdlp]
confidence: reported
complexity: sieving needs 2^(0.2075n) memory at minimum (kissing-number floor) against enumeration's polynomial space; the exponent gap in space is comparable to the exponent gap in time
applicability: any comparison between a sieving-based and an enumeration-based lattice attack, and any lattice cost quoted for comparison against a memory-light baseline
source_refs: [KN-LIT-094, KN-TECH-035, KN-LIT-104, KN-LIT-122, KN-LIT-110, KN-TECH-042, KN-TECH-043]
added: 2026-07-24
superseded_by: null
---

## Method
Apply the full-cost discipline of KN-TECH-035 -- price hardware quantity
multiplied by time occupied, not processor steps -- to lattice attacks. This
entry exists because the corpus previously charged memory on the ECDLP side and
not on the lattice side, and the two halves of the program should not use
different accounting.

## Why lattices are the sharper case
Wiener's result (KN-LIT-094) is that a `sqrt(n)`-element table cannot be reached
in unit time, which turns baby-step giant-step's `n^(1/2)` step count into an
`n^(2/3+o(1))` full cost. Lattice sieving is the same trade-off in a more
extreme form:

- **The memory is not optional.** Gauss Sieve's space is provably proportional
  to the kissing constant `tau_n`, bounded below by `2^(0.2075n)` (KN-LIT-104).
  A sieve must hold its near-neighbour list; this is structural, not an
  implementation artifact.
- **The competitor uses polynomial space.** Enumeration's advantage is precisely
  that it does not store anything (KN-TECH-042). So the enumeration/sieving
  crossover at dimension 70 is a *step-count* crossover. Under an accounting
  that charges the memory and the wiring to reach it, the crossover moves to
  higher dimension -- by how much is not answered by anything in this corpus.
- **The community partially knows this.** "Min-space" sieve variants are costed
  at a worse time exponent (`0.368` classical) precisely to buy space back, and
  KN-LIT-122 costs quantum sieving at the circuit level and finds the realisable
  speedup small. But the headline `2^(0.292b)` used in core-SVP (KN-TECH-040)
  charges nothing for the memory or its access pattern.

## What follows for this program
A lattice security level quoted in core-SVP units is a step count with
unpriced exponential memory. That is acceptable for *parameter selection*, where
undercharging the attacker is conservative. It is not acceptable for a claim
that one algorithm beats another, which is exactly the claim the program's goals
are about. Any internal comparison involving a sieving-based attack must state
whether memory is charged, in the same sentence as the cost -- the same rule
already imposed on index-calculus relation storage in KN-TECH-035.

## Applicability limits
Full cost is an asymptotic instrument with unextracted constants; it identifies
which side of a trade-off is undercharged, and cannot settle a claimed
constant-factor advantage. Wiener's wiring model assumes three spatial
dimensions and a specific technology abstraction, and real sieving is also
bandwidth- and latency-bound in ways the model does not itemise. For concrete
budgeting the public records (KN-TECH-049) remain the better instrument.

## Verified vs reported
The full-cost results and the BSGS example are read from KN-LIT-094 and are that
paper's proven results; the kissing-number space bound is KN-LIT-104's proven
result. **The central claim of this entry -- that charging memory moves the
enumeration/sieving crossover, and by how much -- is this program's own
reasoning and has not been computed.** No source in this corpus performs that
calculation; see KN-OPEN-017. Nothing here has been measured internally.
