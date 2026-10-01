# Preflight note for NA-5 — can the kappa experiment run here at all?

**Task:** TASK-20260918-c74971
**Discharges:** nothing. This is INPUT to NA-5 of `DEC-20260917-793ae2`, not NA-5 itself.
**Question addressed:** `KN-OPEN-ac409f`. **Idea it bears on:** `IDEA-20260916-b84e2d`.
**Run by:** the orchestrating session, 2026-09-18, on branch
`claude/ecc2k-130-quasi-subfield-poly-nhcj1f` at `3fb8d7f59`.

---

## THIS IS NOT A RESULT

Nothing here measures a chain system, an eliminant degree, or kappa. It is a
**feasibility probe on random coefficients** plus an environment inventory. It
establishes only what a design can assume about the tooling available in this
container.

**No number in this note may be cited as evidence about `H-QSP-645a07`, its
heuristic H1, its closure reading (E), or `kappa`.** In particular the Sylvester
timings below are on random field elements, not on the system
`S^{(k)} = phi(S^{(k-1)})` of KN-LIT-0a321c Section 3.1, whose coefficients are
structured and whose behaviour may differ.

It is recorded because it was run before a design dispatch that then failed on an
API rate limit, and the two findings would otherwise have survived only in a
conversation and a scratchpad file the container discards.

---

## Finding 1 — the recorded engine impediment is real, and unchanged

`IDEA-20260916-b84e2d` is `status: proposed`, `recommended_priority: low`, blocked
on a Groebner engine; its `estimated_cost` names "a Macaulay2 driver over
toField(...) whose viability is unverified". Verified, and it is worse than
unverified — there is nothing to drive.

    M2 ABSENT   Singular ABSENT   magma ABSENT   sage ABSENT   gp ABSENT   maxima ABSENT
    sympy 1.14.0 present;  galois ABSENT   flint ABSENT   numpy ABSENT

Raw capture: `out/engines.txt`.

So any protocol requiring Groebner bases **cannot run in this container**, and a
design that writes one is writing a protocol whose expensive half is
known-unrunnable.

## Finding 2 — but the m = 2 cells do not need one

NA-5 records the red team's assessment that "the smallest useful measurement is
the eliminant degree at (m, d) = (2, 2) or (2, 3), where a resultant suffices and
no Groebner engine is needed." That is now checked rather than assumed.

Bit-packed `F_{2^n} = F_2[z]/(f)` with a Sylvester-matrix determinant by Gaussian
elimination over that field, all hand-rolled, no external dependency:

| n  | deg_X | Sylvester | wall  |
|----|-------|-----------|-------|
| 17 | 16    | 32x32     | 0.011 s |
| 23 | 16    | 32x32     | 0.015 s |
| 29 | 16    | 32x32     | 0.024 s |

Script `code/preflight_resultant.py`, capture `out/preflight_resultant.txt`.
Deterministic part: `res != 0` on every trial. Wall-clock varies run to run; the
figures above are one capture and are indicative, not pre-registered.

**Consequence for the design:** the cheapest informative cell is reachable today.
The impediment blocks the ladder, not the discriminating measurement.

## Finding 3 — a trap that would return confident garbage

**`sympy.GF(2**k)` is the ring of integers modulo `2**k`, NOT the field extension
`F_{2^k}`.** Demonstrated, not asserted (`code/sympy_domain_trap.py`,
`out/sympy_domain_trap.txt`):

    GF(2**4).characteristic()  ->  16        (a field of order 16 has characteristic 2)
    2 * 8 mod 16               ->  0         (2 is a zero divisor; F_16 has none)
    2 ** -1                    ->  NotInvertible: zero divisor

sympy IS correct over the prime field `F_2`, and computes bivariate resultants
there quickly — `Res_X` of a degree-6 example in milliseconds. The danger is
precisely that it half-works: a protocol that used `GF(2**n)` for the extension
would compute in `Z/2^n` and emit plausible numbers with no error raised.

**Any contract descending from this note must forbid `sympy.GF(2**k)` as a model
of `F_{2^k}` by name, and require explicit extension arithmetic.**

---

## What this does and does not license

**Does:** a design restricted to cells a resultant can reach, with everything
needing a Groebner engine declared out of scope and the impediment named.

**Does not:** any claim about kappa, any promotion of (E), or any relaxation of
promotion gate (2). `EV-QSP-a6aa4b`'s obstruction stands, `DEC-20260917-793ae2`
stands at `weaken`, and `H-QSP-645a07` Part II remains
`conditional_unvalidated_not_promotable`.

**Still unaddressed, and the honest limit of the whole line of attack:** an
eliminant degree measured at toy `n` is not an asymptotic exponent. Whatever
contract NA-5 produces must state that transfer assumption explicitly rather than
smuggling it, and must carry the asymmetry `KN-OPEN-ac409f` records — a collapse
at `m = 2` is strong evidence against `kappa >= 1`; a non-collapse is weak
evidence for it.

## Status of NA-5 itself

**NOT DISCHARGED.** The design dispatch failed on an API weekly rate limit before
it read any record. `H-QSP-e15e15` and `EXP-QSP-bb346d` are minted and verified
free but **unused — no such records exist**. NA-5 remains open.
