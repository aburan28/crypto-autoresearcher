---
id: KN-TECH-072
type: technique
title: Algebraic and fast algebraic attacks on LFSR-based stream ciphers - annihilators, algebraic immunity, and the precomputation trade
tags: [algebraic-attack, stream-cipher, lfsr, annihilator, algebraic-immunity, fast-algebraic-attack, berlekamp-massey, boolean-function, correlation-attack, filter-generator, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "classical: linearisation over D = sum_{i<=d} binom(n,i) monomials, time ~ D^omega with d the annihilator degree and n the LFSR state length; fast algebraic: relations of the form f*g = h with deg g = e << d reduce the online system to degree e, at the cost of a precomputation that eliminates the degree-d part"
applicability: keystream generators whose state update is linear (LFSR/filter/combiner constructions) and whose nonlinearity is confined to a Boolean output function; not applicable to designs with nonlinear state update unless the update linearises
source_refs: [KN-TECH-053, KN-TECH-071, KN-LIT-2389, KN-LIT-3781, KN-LIT-6276, KN-LIT-2390, KN-LIT-4452, KN-LIT-3062, KN-LIT-3544, KN-LIT-2401, KN-LIT-5745, KN-LIT-7431, KN-LIT-5484, KN-LIT-3792]
added: 2026-07-31
superseded_by: null
---

## Method

The setting is the classical keystream generator: an `n`-bit **linear** state
update (one or more LFSRs) with a **nonlinear** Boolean output function `f`.
Because the update is linear, the state at time `t` is a known linear function
`L^t(s)` of the initial state `s`, so each keystream bit gives one equation

  `f(L^t(s)) = z_t`

of degree `deg f` in the `n` unknowns. Collecting enough of them and solving is
the whole attack. Direct linearisation costs `D^ω` with
`D = Σ_{i≤deg f} C(n,i)` monomials, which for a well-chosen `f` is too large.

**The Courtois–Meier insight** (`KN-LIT-2389`): you do not have to use `f`. If
there is a low-degree `g ≠ 0` with `f · g = 0` — an **annihilator** of `f` — then
multiplying the equation by `g` gives, whenever `z_t = 1`, an equation of degree
`deg g` only. Symmetrically, an annihilator of `f ⊕ 1` handles the `z_t = 0`
positions. The attack's degree is therefore not `deg f` but

  **`AI(f)` = the minimum degree of a nonzero annihilator of `f` or of `f ⊕ 1`**,

the **algebraic immunity**. Complexity becomes `D^ω` with
`D = Σ_{i≤AI(f)} C(n,i)`. Two facts fix the design landscape: `AI(f) ≤ ⌈n/2⌉`
always, so the parameter is bounded; and high nonlinearity does **not** imply
high algebraic immunity, so a function chosen only against correlation attacks
can be algebraically weak. Computing `AI` efficiently is itself a studied
problem (`KN-LIT-3062`, `KN-LIT-3544`, and for S-boxes `KN-LIT-2401`), as is
constructing functions that maximise it (`KN-LIT-5745`, `KN-LIT-7431`) — and
maximising it trades against other criteria (`KN-LIT-5484`).

**Fast algebraic attacks** (Courtois, `KN-LIT-3781`) go further. Look for a
relation `f · g = h` with `deg g = e` **small** and `deg h = d` possibly large.
The high-degree part `h` is then eliminated by a **precomputation**: because the
`h`-contributions satisfy a linear recurrence in `t`, a Berlekamp–Massey-style
step finds a combination of consecutive keystream equations in which they
cancel, leaving a system of degree `e` in the state bits. The cost moves from
online solving into offline precomputation, and the online system becomes much
smaller. The precomputation's own complexity is the subject of continuing
analysis (`KN-LIT-6276`, `KN-LIT-4452`), and the same idea extends to
summation-generator constructions (`KN-LIT-2390`).

**Position among stream-cipher attacks.** Algebraic attacks are one of two
families that exploit a linear state update; the other is **correlation and fast
correlation attacks**, which treat the keystream as a noisy LFSR codeword and
decode (`KN-LIT-3792`). The two make different demands — algebraic attacks want
low `AI`, correlation attacks want a biased approximation — and a design must
resist both.

## Program usage

- **The clearest instance in this corpus of a hard problem made easy by a
  representation change, with a *provable* handle on when.** The attack does not
  solve the system it is given; it finds a different, lower-degree system with
  the same solutions. The program's inventor protocol (`KN-TECH-056`) is built
  around exactly this move — object-first search with a lossy-projection test —
  and algebraic immunity is a rare case where the field has a **computable
  invariant** saying how far the move can go. When a proposal in this program
  claims a representation change buys degree, `AI` is the precedent for asking
  what invariant bounds the gain.
- **Solver continuity.** The linearised systems here are exactly the MQ/Boolean
  systems of `KN-TECH-053`, and the `D^ω` cost has the same shape as the
  linear-algebra step in index calculus (`KN-TECH-008`). The `ω` in that formula
  is a cost-model choice, and quoting `ω = 2` where the implementation is
  Gaussian is the same defect `KN-TECH-035` catalogues.
- **Precomputation must be charged.** Fast algebraic attacks move work offline;
  under this program's full-cost rules an offline phase is still a cost and is
  reported beside the online figure, never instead of it.

## Applicability limits

- **Linear state update is the load-bearing hypothesis.** Modern designs
  (Trivium, Grain) use nonlinear update precisely to break it; against those the
  relevant tools are cube and division-property methods (`KN-TECH-073`,
  `KN-TECH-074`), not this entry.
- **`AI(f)` bounds the degree, not the attack's feasibility.** `D` grows
  combinatorially in `n`, so a moderate `AI` with a large state is out of reach;
  the numbers must be computed for the actual parameters.
- **Keystream requirement.** Enough keystream must be available under one key to
  build the system — a data constraint that frame-based protocols often violate.
- **`ω` is an assumption.** The `D^ω` figure inherits whichever
  matrix-multiplication or sparse-linear-algebra model is assumed
  (`KN-TECH-008`).

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The annihilator construction, the
definition and `⌈n/2⌉` bound of algebraic immunity, the `D^ω` linearisation cost
and the structure of the fast-algebraic precomputation are standard published
results, written from established knowledge and not re-derived or measured in
this program. `KN-LIT-2389` and `KN-LIT-3781` are the corpus's records for the
two originating papers, both carried at **title level**; no complexity figure
from either is quoted here. All other cited records are title-level per the
family note. The reading of algebraic immunity as a computable invariant
bounding a representation change, and the comparison to `KN-TECH-056` and
`KN-TECH-008`, are this program's own reasoning.
