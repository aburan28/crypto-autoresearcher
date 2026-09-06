---
id: KN-OPEN-d6ad3f
type: open_problem
title: >-
  Does KN-FIND-006's 8*dim(V) rank deficit survive to a prime field in a
  DESCENDED presentation? The descended prime-field object was never built, and
  the digit twin cannot separate characteristic 2 from descent multiplicity
tags: [semaev, weil-descent, chained-system, rank-deficit, syzygy, characteristic-2, descent-multiplicity, prime-field, digit-presentation, confounded-design, open, ecdlp]
confidence: established
status: open
source_refs: [EV-PFDR-e67f06, DEC-20260904-63a809, H-PFDR-9aadc0, EXP-PFDR-20ee58, KN-FIND-006, KN-FIND-b0c3c9]
added: 2026-09-04
superseded_by: null
---

## Statement

`KN-FIND-006` records, for Weil-descended chained Semaev systems over `GF(2)`
(`t = 3`, `k = dim V`), a Macaulay rank deficit that is exactly closed-form at
low degree: `deficit(3) = 1`, `deficit(4) = 8k − 1`, cumulative
`8k = 8*dim(V)`, measured-exact for `k = 3..7` and **stated only for FULL
systems** (exactly `n` quadrics plus `n` cubics in `nb = 2n` variables).

**OPEN: does that law have a prime-field analogue in a DESCENDED presentation?**

`EXP-PFDR-20ee58` was designed to answer it and cannot, for a reason its own
review made precise. It built a prime-field *digit* twin — two chained `S_3`
equations with a free internal node and base-2 digit leaves — and measured
`deficit = 0` on all 246 draws at every tested cell, on an instrument
demonstrably able to return values in `0..805` at that exact shape. The
attribution to characteristic does **not** follow:

> Holding `p = 2`, the ring, the convention and the meter fixed and varying only
> the number of descended quadrics, the deficit is exactly `[0, 0, 0]` for
> `j = 2, 3, …, 11` and becomes `[0, 1, 32]` only at `j = 12`, the complete
> descent block. **Two generators return deficit 0 at `p = 2` as well** — on the
> very object where the deficit is known to exist, and where the Boolean
> idempotent law and Frobenius-linear squaring are both PRESENT.

So "deficit 0 on the twin" is fully reproduced without invoking characteristic
at all. The design varied **characteristic, generator count and encoding
together**, and its zero cannot discriminate:

- **H_char** — the mechanism is characteristic-2 specific (Frobenius-linearity
  of squaring, the Boolean identity `P(1 + P) = 0`), or
- **H_count** — the mechanism needs a descent block of many generators, which
  the digit twin lacks at any characteristic.

Stated narrowly: a subsystem need not inherit a syzygy of the whole system, so
the generator-count ladder does **not prove** `H_count`. It shows the experiment
does not separate the two.

A second, independent reason the twin is the wrong instrument: the
identification that makes it a test at all — that the digit parameter `s`
instantiates `KN-FIND-006`'s `k` — is **asserted, not derived**, and unnumbered.
In `KN-FIND-006`, `k` is simultaneously `dim V`, the number of descended
equations per `S_3`, and the variable count per leaf. The twin reproduces only
the third and sets the second to **1** — and the generator-count ladder shows
the second is the load-bearing one at `p = 2`. The experiment fixed the
parameter that carries the law and varied the ones that do not.

## Resolution criterion — the object that was never built

**The descent-separation control.** Build the prime-field Weil-descent analogue
and measure the same quantity with the same instrument:

- `E` over `F_{p^k}` with `p > 3`; leaves restricted to an `F_p`-subspace `V` of
  dimension `v`; the two chained `S_3` equations descended over `F_p` into `2k`
  generators of total degree 4. Squaring is **not** `F_p`-linear for `p > 2`, so
  the degrees do **not** collapse as they do at `p = 2`.
- Measure `deficit(D) = rows(D) − rank(Mac_D) − koszul(D)` under the same
  cumulative convention and the same meter, as a function of `k`, with the
  planted-defect ladder of `KN-TECH-1cd4bb` attached as its positive control.
- Feasibility at toy scale is established: `k = v = 2` gives 4 quartics in
  `3v + k = 8` ordinary variables, so at `D = 8` rows `= 4 * C(12,4) = 1980` and
  columns `= C(16,8) = 12870` — inside the 60 000-column cap and minutes of CPU.
  `k = v = 3` needs a `D <= 6` restriction (546 × 18 564).

Outcomes, both informative:

- **NONZERO deficit there** isolates **descent multiplicity** as the carrier and
  refutes the characteristic-2 attribution.
- **ZERO deficit there, at `k = 2` and `k = 3`**, is the first evidence that
  would actually support the characteristic-2 attribution.

Either way it converts an open objection into a measurement. Nothing else in or
near this battery does.

## What must NOT be said in the meantime

- **Not:** "the `8*dim(V)` law has no prime-field analogue." The descended
  prime-field object was never built.
- **Not:** "the obstruction is the absence of the Boolean idempotent law or of
  Frobenius-linear squaring." That is the named obstruction, and it is not the
  measured one.
- **Supportable instead:** the route through *that particular digit twin* is
  closed at its tested cells (`m = 3`, `d = 2`, `s ∈ {3,4,5}` at `D <= 8` and
  `s = 6` at `D <= 6`, `p ∈ {4099, 16411, 65537}`) — and on the reported
  quantity that twin is not distinguishable from a support-matched null, a
  topology-matched null, a singular non-curve cubic or an ordinary random
  quartic pair, so it is not a statement about summation polynomials, elliptic
  curves or the ECDLP either.

## Related open surface

- `KN-OPEN-002` is **not** touched by any of this and is not narrowed.
- The `(S2)`-`(S3)` baseline of `H-PFDR-9aadc0` is part rigorous (the
  trivial-syzygy COUNT: one Koszul pair, no third generator, no Frobenius family
  for `p > 2`) and part heuristic (that the rank ATTAINS the bound — Fröberg /
  Bardet–Faugère–Salvy genericity, false for four structured objects built in
  the same ring at the same degrees, with deficits up to 289). Reconciling the
  `DERIVED` tag with `HEUR-001` is a prerequisite for any record calling the
  Koszul-only baseline derived.
- `p = 2` is **not** a member of the digit twin's `(s, p)` family: there the
  digit leaves collapse to their lowest bit (six of nine digit variables vanish
  at `s = 3`) and the generator degree drops from 4 to 3. Any future attempt to
  read the twin as a family in `p` must exclude it.
