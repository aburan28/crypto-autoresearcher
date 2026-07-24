---
id: KN-TECH-015
type: technique
title: Coppersmith small-root lattice methods
tags: [coppersmith, small-roots, lattice, lll, howgrave-graham, windowed, summation-polynomial, ecdlp]
confidence: established
complexity: LLL on a dimension-D shift lattice with B-bit entries, ~O~(D^6 * B^3) classical; recovers all roots below an explicit bound (e.g. root < N^{1/d})
applicability: certified-complete enumeration of small/windowed roots of modular or bivariate integer polynomials
source_refs: [KN-LIT-037]
added: 2026-07-22
superseded_by: null
---

## Method
To find roots of a polynomial that are small (below an explicit bound), build a
lattice of polynomial shifts x^i * y^j * f(x,y) that all share the target root
modulo the modulus, and run LLL. By the Howgrave-Graham lemma, a resulting
low-norm combination has the small root *exactly over the integers*, so its
integer roots are read off directly. The method is *complete within its bound*:
it certifiably finds every root in the window (a property resultant elimination
lacks).

## Program usage
The engine of the program's windowed relation-finding candidate (round-2 B3,
EXP-COPP-001): apply a Howgrave-Graham shift lattice to the bivariate Semaev
polynomial S_3(x_1,x_2) restricted to a window [0,X]x[0,Y] and certifiably list
all relations inside it. The win condition: windowed relation density rho_W must
exceed the equidistribution baseline (XY/p^2) by enough that the per-window
lattice cost beats full enumeration.

## Applicability limits
The bound is a hard archimedean window (e.g. XY < p^{...}); outside it the method
says nothing. The value is entirely contingent on relations CONCENTRATING in a
window -- which tensions against the equidistribution / quasirandomness
expectation (KN-TECH-016, KN-LIT-038): if Semaev-relation coordinates
equidistribute (the generic expectation), rho_W = XY/p^2 and the lattice overhead
loses to plain enumeration. LLL cost grows steeply in the shift degree, so only
low-degree windows are practical.
