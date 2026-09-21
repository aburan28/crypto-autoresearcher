---
id: KN-TECH-1cd4bb
type: technique
title: >-
  Planted-defect instrument-adequacy ladder - prove a measurement instrument can
  MOVE at the exact shape being measured, by planting defects that must fire at
  PREDICTED degrees, before any null result is read
tags: [instrument-validation, positive-control, null-object, macaulay, syzygy, rank-deficit, first-fall-degree, closure, method-ceiling, negative-result, proves-too-much, review-methodology]
confidence: established
complexity: >-
  seconds to minutes per planted object at toy shapes; the ladder in its
  reference use ran four objects in under a second each against a measurement
  that took hours
applicability: >-
  any experiment whose headline is an ABSENCE - deficit 0, no early fall, no
  rank drop, no relation found - measured by a graded-rank, syzygy, closure or
  search instrument at a fixed object shape
source_refs: [KN-FIND-b0c3c9, KN-FIND-64bad4, EV-PFDR-e67f06, EV-PFDR-99c699, EV-PFDR-acc71a, DEC-20260904-63a809]
added: 2026-09-04
superseded_by: null
---

## The problem it solves

An experiment whose result is a **zero** inverts the usual artifact discipline.
The standard tell — a signal that fails to decay when the structure is removed —
cannot fire, because there is no signal. The risk is the opposite one: an
instrument that could not have returned anything else. A null-object control
answers "would a structureless object give the same reading?" and is necessary,
but it is not sufficient: if the instrument is blind, the null and the treatment
agree for a reason that has nothing to do with the objects.

`docs/inventor-protocol.md` asks for the **method ceiling** — the largest value
the instrument could report at this shape. The ladder below is the cheap,
constructive way to establish it, and it must be run **before** the zero is
interpreted, not after it is challenged.

## The technique

1. **Fix everything except the defect.** Same ring, same field, same generator
   degrees, same multiplier convention, same meter build, same degree range as
   the measured arm. Only the object changes.
2. **Plant a defect whose signature you can PREDICT, not merely detect.** Choose
   a construction whose parameter sets the degree at which the instrument must
   respond — a common factor of degree `g` in two generators makes the syzygy
   first fit at a known degree; a generator of degree above `D_max` makes a fall
   that must be *refused* by a completeness certificate.
3. **Verify the plant as an identity before measuring it.** Confirm the planted
   relation holds as a polynomial identity, so a null reading is a fact about
   the instrument and not about a botched construction.
4. **Run a ladder, not one point.** Vary the defect parameter so the response
   moves through the degree range. A single planted object shows the instrument
   is not dead; a ladder shows it is *calibrated*.
5. **Run the negative leg too.** A structureless object of the same shape must
   return the measured value. Without it, "the instrument fires on my plant"
   does not establish that it is silent for the right reason.
6. **Report the observed range and resolution beside the zero, always.** "0"
   read next to "observed range 0..805, resolution 1" is a measurement; "0"
   alone reads as an instrument that cannot move.

## Reference uses (all from the RQ-PFDR-ae2fba battery review, 2026-09-04)

Three independent reviewers, on three different instruments, each closed a
method-ceiling gap this way — and in each case the gap was **open at the time
the numbers were first read**.

- **Graded-rank deficit meter, mixed ring, two quartics (EXP-PFDR-20ee58).**
  Objects `A(g)`: `E1 = h*q1`, `E2 = h*q2` with `deg h = g`, so the syzygy has
  multiplier degree `4 − g` and first fits at `D = 8 − g`. Measured
  `A1 → [0,0,1,10]`, `A2 → [0,1,11,56]`, `A3 → [1,11,57,186]`,
  `D1 → [2,20,95,289]` at `D = 5..8` — **each firing at exactly the predicted
  degree** — against the twin's `[0,0,0,0]` and a random quartic pair's
  `[0,0,0,0]`. Observed range at `D = 8`: 0..805 against a ceiling of 884,
  resolution 1. The meter's own validation note had run only in squarefree and
  ordinary modes with base quadrics, never at the measured shape.
- **Completeness certificate, HKY closure (EXP-PFDR-cbdefb).** A planted LATE
  fall (`n = 10`, `g = u f1 + v f2 + h` of degree 8, true fall at `D = 8`) run
  at `D_max = 7`: the certificate **refused** — `dim V_7 = 112` against
  `dim(I ∩ B_{<=7}) = 582`, `C1` false, `right_censored` true — and run to
  `D = 9` recovered `falls = [8]`. This is the mutation that would have exposed
  a certificate biased toward flatness, and it did not fire.
- **p-sensitivity of a fixed-shape meter (EXP-PFDR-fd901a).** The contract's
  positive control had **no dynamic range on the axis it was supposed to gate**
  (`d_ff = B + 2` is a function of `B` alone, and `B = round(sqrt(p))`). The
  substitute: run the METER itself on the sweep's own construction at `p = 2`
  and `p = 3`. It returns a different profile at `p = 2` (0 of 24 at the
  reference) and reproduces the `p = 3` drop (23 of 24), matching an independent
  implementation draw for draw.

## What it does and does not establish

- **Does:** the instrument can return values in a stated range at the exact
  shape measured, with a stated resolution; a null reading is therefore a
  measurement. It also yields the method ceiling for free.
- **Does not:** it says nothing about whether the null reading *attributes* to
  the mechanism the experiment names. In the reference use above, the ladder
  established that `deficit = 0` was a real measurement, and a **separate**
  control (varying generator count at fixed characteristic) then showed the zero
  does not attribute to characteristic at all. Instrument adequacy and causal
  attribution are different questions and a passing ladder answers only the
  first.
- **Does not:** it does not enlarge the space of relations the measurement
  excludes. In the reference use the twin's entire trivial-syzygy budget at
  `D = 8` was one Koszul pair; the exclusion is real and small.
- A ladder run by a REVIEWER closes the gap **in the claim's favour** but does
  not retroactively close it for the producing session. Record that the control
  was absent when the numbers were read; it is a protocol fact, not a
  reflection on the result.

## Practical notes

- Plant into the **same manifest lineage** where a contract requires it, or the
  control does not discharge the contract's own required input.
- Prefer a defect parameter that indexes DEGREE over one that indexes magnitude:
  a wrong degree is a sharper failure than a small value.
- If the ladder's objects satisfy the derivation's stated premises verbatim and
  still return nonzero, that is a second finding: the premises do not imply the
  conclusion, and the implication step is a heuristic. In the reference use,
  four such objects made exactly that point.
- Keep the planted objects and their outputs in the review directory; they are
  re-runnable in about a second each and are the cheapest thing a successor
  round can inherit.
