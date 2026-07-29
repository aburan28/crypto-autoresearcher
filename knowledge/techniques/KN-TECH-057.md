---
id: KN-TECH-057
type: technique
title: The unspent-involution screen — why the HAWK-type symmetry attack cannot reach prime-field ECDLP
tags: [screen, symmetry, involution, galois, automorphism, weil-descent, hawk, module-lip, negation-map, prime-field, ecdlp, closure, ideation-discipline]
confidence: reported
complexity: not a computational technique — a pre-compute screen. Cost is one lookup of the symmetry group acting on the secret-bearing object and one count of how many of its involutions the literature has already quotiented
applicability: >-
  Screening any proposal that claims an advantage from a "hidden," "unused," or
  "overlooked" symmetry of the instance. Applies wherever a group acts on the
  object that hides the secret — curve automorphisms, base-field Galois
  actions, endomorphisms, field automorphisms of a number field.
source_refs: [KN-LIT-7592, KN-TECH-018, KN-TECH-005, KN-TECH-016, KN-OPEN-005]
added: 2026-07-28
superseded_by: null
---

## The screen

**An attack of the HAWK type exists only where the symmetry group acting on the
secret-bearing object contains an involution the literature has not already
spent. Count the involutions; count the ones already quotiented; if the
difference is zero, the proposal is dead before any compute is allocated.**

## Where the criterion comes from

[[KN-LIT-7592]] (Straznickas–Weis, 2026-07-28) recovers HAWK-`n` keys by reducing
to exact-SVP in dimension `n/2 + 1`, roughly halving the scheme's effective key
strength. The mechanism is a **second order-2 Galois involution**. `Gal(K_n/Q)`
for `K_n = Q(ζ_{2^ℓ})` contains three involutions — complex conjugation `c`, the
map `τ : ζ ↦ -ζ`, and `σ = cτ`. **Every prior module-LIP cryptanalysis used only
`c`.** The `τ`-cocycle `V_τ = B^{-1}τ(B)` turns out to lie in a publicly
computable lattice of near-hypercubic shape, for which Ducas's block reduction is
better than generic — so the unused involution converts the problem into a class
that already had a specialized algorithm waiting.

The reason to treat "number of unspent involutions" as *the* operative quantity,
rather than as one reading among several, is that **the paper's own scope
statement is a statement about involution counts**. It reports that conductors
`m ∈ {p^k, 2p^k}` for odd prime `p` — exactly the `m > 4` with **cyclic**
`(Z/m)^×` — evade the attack. A cyclic group has **exactly one** element of order
2. So the attack exists precisely where the Galois group has more than one
involution, and fails precisely where it has one. The authors did not frame it
this way; the criterion is read off their evasion condition.

## Applying the screen to the ECDLP

For the program's target family — a random ordinary elliptic curve of prime order
over a prime field `F_p` — the count is **one, and it is already spent.**

| Symmetry source | Group | Involutions | Status |
|---|---|---|---|
| Curve automorphisms `Aut(E)` | `{±1}` for `j ≠ 0, 1728` | 1 (negation `P ↦ -P`) | **Spent.** `KN-TECH-018`: rho walks on classes mod `Aut`, and the program's own baseline convention `0.886·√n` already includes the `√2` negation factor |
| Base-field Galois `Gal(F_p/F_p)` | trivial | 0 | Nothing to spend |
| CM / Frobenius endomorphisms | larger only for special curves | — | Excluded by the target family (`KN-TECH-018`: "generic ordinary prime-field curves have `|Aut| = 2`"), and worth `√|Aut|` — a constant, not an exponent |

Both halves of this table were already in the corpus. `KN-TECH-018` records the
`|Aut| = 2` fact and correctly files the `√|Aut|` discount as **"baseline-tightening
facts, not non-generic mechanisms."** What was missing is *why* that is the whole
story rather than an accident: it is the same criterion that decides whether the
HAWK attack exists, evaluated on a different object and returning zero.

## The consequence worth stating

**The HAWK mechanism and Weil descent are the same move**: both exploit a
nontrivial Galois action on the object that carries the secret. HAWK is
vulnerable because it lives over a cyclotomic field whose Galois group is
`(Z/2^ℓ)^× ≅ Z/2 × Z/2^{ℓ-2}` — non-cyclic, hence multiple involutions.
Prime-field ECDLP is immune to the entire class because `Gal(F_p/F_p)` is trivial
and `Aut(E) = {±1}` is already quotiented. Extension-field ECDLP *is* exposed to
it — `Gal(F_{q^n}/F_q)` is nontrivial — and that is exactly where Weil
descent/GHS and summation-polynomial index calculus live (`KN-TECH-016`), which
is exactly the only setting in which ECDLP has ever moved.

So the three facts the program tracks separately — HAWK fell, prime-field ECDLP
has not moved, extension-field ECDLP is the one place progress happened — are one
fact about where the base field carries symmetry.

## How to use it

Apply **before** allocating compute, alongside the GGM-simulability screen
(`KN-TECH-005`, `KN-OPEN-005`). The two catch different classes: simulability
kills proposals that add an oracle the generic model can already answer; this one
kills proposals that invoke a symmetry that either does not exist or has already
been charged to the baseline.

A proposal claiming advantage from a "hidden," "unused," or "overlooked" symmetry
of a prime-field ECDLP instance must, to survive, **exhibit the group, exhibit
the involution, and show it is not the negation map.** For random ordinary
`E/F_p` no such involution is known, and the screen returns *closed* by default.

**Procedural requirement, learned the hard way on the first run.** Screen
`ledger/evidence/` alongside `ledger/proposals/` and `ledger/hypotheses/`, always.
The first run of this screen (`docs/screen-runs/SCREEN-20260728-involution.md`)
read specifications only and reported two findings that the program had already
recorded — one of them, in `EV-GGM-002`, diagnosed more sharply than the screen
managed. Both were retracted the same day. A specification states what was
intended; the evidence record states what was found and what was withdrawn, and a
screen that skips it manufactures known defects as new ones.

## Forward guidance

The class is not dead in general — only on this object. It remains live where a
symmetry group with unspent involutions can be found:

1. **Extension fields.** Known lane, already the program's main non-generic
   effort (`KN-TECH-016`, `KN-OPEN-001`). This screen explains why that lane is
   the productive one rather than merely observing that it is.
2. **CM / Koblitz curves.** Larger `Aut`, but excluded from the target family and
   worth only `√|Aut|` — a constant (`KN-TECH-018`, `KN-TECH-005`).
3. **Symmetry somewhere other than the curve.** The HAWK involution acts on the
   *key lattice*, not on a group of points. The untried analogue is a symmetry
   acting on a derived object — the relation space, the solution space, the
   summation-polynomial variety — rather than on `E(F_p)` itself. `KN-OPEN-009`
   (monodromy of the Semaev cover) is the nearest existing instance and is the
   natural first place to apply this screen constructively rather than
   destructively.

## Status and limits

- **Novelty: `adaptation`, and probably folklore.** Every ingredient is
  established. `Aut(E) = {±1}` for `j ≠ 0, 1728` is textbook; that Weil descent
  needs an extension field is standard; that the negation speedup is a constant
  is `KN-TECH-018`. The HAWK paper is one day old, so the *join* cannot be older
  than that in written form — but the underlying observation is the kind of thing
  ECC researchers are likely to regard as obvious once stated. **No literature
  search for a prior statement of this screen has been performed.** It is
  recorded because it is not in this corpus and it changes what the corpus does,
  not because it is claimed to be new to the field.
- **Not a theorem, and not a substitute for one.** This screen does not prove
  that no non-generic prime-field attack exists — `KN-TECH-005` is explicit that
  the generic bound is a barrier, not such a proof, and `KN-OPEN-001` remains
  open. It closes one *mechanism class* on one object, by naming the quantity
  that mechanism requires and observing that the quantity is zero.
- **Falsification is cheap and decisive.** Exhibit a nontrivial automorphism, or
  any unspent involution, acting on a random prime-order `E/F_p` instance in a
  way not reducible to negation. That single exhibit voids this entry.
- **Reported, not verified.** `KN-LIT-7592` has not been independently
  re-derived or re-run by this program, and the reading of its evasion condition
  as an involution count is this program's inference, **not a claim the paper
  makes**. If that reading is wrong the screen loses its source, though the
  ECDLP-side table stands on `KN-TECH-018` regardless.
