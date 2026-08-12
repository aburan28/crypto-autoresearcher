---
id: KN-TECH-060
type: technique
title: Néron–Tate canonical heights on elliptic curves and abelian varieties
tags: [height, neron-tate, mordell-weil, heegner-point, bsd, xedni, lattice, foundational, number-theory]
confidence: established
complexity: structural / arithmetic — naive height pairing is poly(log |coords|); cryptographic utility unproven
applicability: abelian varieties over number fields (and function fields); not a finite-field ECDLP solver by itself
source_refs: [KN-LIT-7621, KN-LIT-7622, KN-LIT-020, KN-LIT-021]
added: 2026-07-31
superseded_by: null
---

## Method
On an abelian variety A over a number field K, the Néron–Tate (canonical)
height ĥ_L associated to a symmetric ample line bundle L is a positive
semi-definite quadratic form on A(K)⊗R that vanishes exactly on the torsion
subgroup. It is obtained as a limit of Weil heights and is compatible with
the Mordell–Weil lattice.

## Why it matters for this program
Heights are the arithmetic side of several program threads:

- **Gross–Zagier** (KN-LIT-7622) equates Heegner-point heights with
  L-derivatives — classical, not an attack.
- **Xedni / lift-and-lattice** proposals (KN-LIT-020, KN-LIT-021) try to
  manufacture relations by lifting finite-field points to characteristic zero
  and reading lattice structure from heights. Those routes are historically
  dead for ECDLP; the height formalism itself is not the novelty.
- Any new proposal that “uses canonical heights” must state the lift, the
  lattice rank/cost, and a baseline comparison — the height pairing alone is
  `known`.

## Applicability limits
Canonical heights live over global fields. Passing from E(F_q) to a lift
E/Q (or a number field) is an additional, lossy choice; nothing in the
definition of ĥ yields a sub-rho algorithm on random prime-field curves.
BSD / Gross–Zagier give arithmetic information about ranks, not discrete logs
in E(F_q).

## Verified vs reported
Quadraticity / positive-definiteness on E(K)/tors is textbook
(`confidence: established` via KN-LIT-7621). Gross–Zagier’s height formula is
`reported` from KN-LIT-7622. No height computations were performed here.
