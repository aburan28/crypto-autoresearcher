---
id: KN-TECH-06bb4e
type: technique
title: "Lifting-obstruction taxonomy for prime-field ECDLP: Silverman's four characteristic-zero faces plus the function-field fifth face"
tags: [ecdlp, lifting, xedni, obstruction-taxonomy, formal-group, canonical-height, masser, mazur, serre, function-field, elliptic-surface, prime-field, methodology, dedup-instrument]
confidence: literature_derived
complexity: not applicable; this record is a classification instrument, not an algorithm
applicability: any proposal that lifts a prime-field ECDLP instance out of F_p, in any characteristic
source_refs: [KN-LIT-6935a1, KN-OPEN-019, KN-OPEN-3417fc, KN-TECH-3b593f, KN-TECH-73630e, KN-FIND-003, KN-FIND-008, KN-FIND-011]
added: 2026-08-09
superseded_by: null
---

## What the technique is

A classification instrument, not an algorithm. Every proposal that "lifts the
ECDLP out of `F_p`" is assigned to a cell of a grid, and each cell carries a
*named* obstruction that the proposal must explicitly remove. It exists so that
new lifting ideas can be deduplicated against a closed enumeration instead of
against 400 free-text idea records.

`KN-LIT-6935a1` (Silverman, ECC 2007) supplies the characteristic-zero grid:
axes **local vs global** and **torsion vs nontorsion**, four cells, five
obstructions (global-nontorsion splits into an easy and a hard sub-method).

## The grid

| # | Cell | Named obstruction | One-line statement |
|---|---|---|---|
| F1 | local, nontorsion | **consistency** | Lifting `S, T` mod `p^k` is easy and `p`-ambiguous at each step; only one of the `p` choices for `T_{k+1}` preserves `T = mS`, and selecting it is not known to be possible without `m`. |
| F2 | local, torsion | **formal-group annihilation** | The order-`n` lift is unique and preserves `T̂ = mŜ`, but the only known route to a computable logarithm multiplies by `n` and yields `Ô = mÔ`. |
| F3 | global, torsion | **field degree** | Mazur: `#Ê(Q)_tors <= 16`. Serre: order-`n` torsion generally needs `[K:Q] >= c·n^4`. |
| F4a | global, nontorsion, "easy" | **Masser independence** | Prescribed independent sections are dependent only on a density-zero parameter set; heuristically below `1/p`. |
| F4b | global, nontorsion, "hard" (xedni-flavoured) | **canonical height** | `T̂ = mŜ` forces `ĥ(T̂) = m^2 ĥ(Ŝ)`, so the sought lift has size exponential in `m^2`, and no search algorithm is known even when existence is granted. |

## The fifth face this program actually occupies

Silverman's grid is over characteristic-zero rings (`Z_p`, `Z`, `O_K`). This
program's xedni lane does **not** live in any of those cells: `EXP-XEDN-*` and
`KN-FIND-003`/`004`/`005`/`010`/`011` lift to the function field `F_p(t)` and
work with sections of an elliptic surface. Call this

- **F5** — global, nontorsion, **function-field** (`R̂ = F_p[t]`, `K̂ = F_p(t)`).

F5 is not covered by F1–F4 and its obstructions are *not* inherited:

- The **F3** bound does not apply: torsion of an elliptic surface over `F_p(t)`
  is not constrained by Mazur or Serre in the same form.
- The **F4b** height obstruction changes character: canonical height becomes a
  *degree*, and this program's measurements repeatedly found Mordell–Weil
  relations with `max |coeff| = 1` (infinity-norm 1) with **no observed
  coefficient growth** at `p ∈ {7,13,19,31}` (`KN-FIND-003`, `004`, `005`, `010`,
  `011`). Under F4b's logic a relation carrying the scalar cannot be that small.
- The **F4a** Masser obstruction has a function-field analogue but this program
  has not measured whether it is the operative one in F5.

The taxonomy therefore produces a sharp, cheap question rather than a
reassurance: **relations were found in F5 that F4b says should not exist, so
either F5 escapes the height obstruction, or the recovered relations are
target-blind.** That question is filed as `ECDLP-IDEA-435` and its decisive
control is the coefficient on the *target* section.

## How to use it

1. Assign the proposal to F1–F5. A proposal that cannot be assigned is either not
   a lifting proposal or has an unstated ring.
2. Require the proposal to name which obstruction it removes and by what
   mechanism. "Different software / precision / lift shape" is a control, not a
   removal.
3. Cross-check against existing lane records before minting an idea:
   - F2 is further closed by `KN-TECH-3b593f` for group-theoretic invariants and
     reopened only for coordinate/valuation invariants as `KN-OPEN-3417fc`.
   - F4b is the obstruction named by active idea `ECDLP-IDEA-005`.
   - F1 is the obstruction named by active ideas `ECDLP-IDEA-004`/`160`
     (prime-to-`p` annihilation and orientation).

## Scope and limits

`LITERATURE-DERIVED` and `MODEL-BOUND`. Silverman's talk asserts F1–F4 as an
exhaustive enumeration of characteristic-zero lifting attacks; that assertion is
the author's framing and is **not** a theorem that no lift can work, and this
program does not treat it as one. F5 is this program's own addition and is not
claimed to complete the enumeration either. Nothing here is evidence for or
against any candidate algorithm, and nothing here is a breakthrough claim.
