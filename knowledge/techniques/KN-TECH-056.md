---
id: KN-TECH-056
type: technique
title: Syndrome decoding and the code-based hardness baseline
tags: [code-based, syndrome-decoding, npc, gilbert-varshamov, lpn, random-codes, baseline, hardness-assumption, pqc]
confidence: reported
complexity: NP-complete in the worst case (Berlekamp-McEliece-van Tilborg); best known average-case algorithms are exponential, 2^{cn(1+o(1))} with c a small constant depending on rate and error regime (KN-TECH-057)
applicability: any security claim about McEliece/Niederreiter, BIKE, HQC, LPN-based constructions, or code-based signatures
source_refs: [KN-LIT-7564, KN-LIT-7565, KN-LIT-7566, KN-LIT-7572, KN-LIT-6717, KN-LIT-5999, KN-LIT-1137, KN-LIT-6503]
added: 2026-07-27
superseded_by: null
---

## The problem
**Syndrome decoding (SD).** Given a parity-check matrix `H` in `F_2^{(n-k) x n}`,
a syndrome `s`, and a weight bound `w`, find `e` with `He^T = s` and
`wt(e) <= w`. The equivalent primal form (**general decoding**) asks for a
codeword within distance `w` of a received word. Both are NP-complete in the
worst case.

Two parameter regimes behave differently and must never be conflated:

| Regime | `w` relative to `n` | Where it appears |
| --- | --- | --- |
| **Half distance** | `w ~ d/2`, unique solution | McEliece/Niederreiter KEMs |
| **Full distance** | `w ~ d`, still ~unique at GV | asymptotic exponent comparisons |
| **High error rate** | `w = Theta(n)`, many solutions | LPN, code-based signatures (KN-LIT-7571) |

An algorithmic improvement in one regime does not transfer to the others. This
is the single most common scoping error in code-based cost claims.

## Why NP-completeness is not the security argument
Worst-case NP-completeness says nothing about the random instances that
cryptosystems actually use. The operative assumption is **average-case**: that
decoding a *random* linear code at the scheme's rate and error weight is hard.
That assumption has no worst-case-to-average-case reduction of the kind lattices
enjoy (KN-TECH-021), so its support is empirical -- sixty-four years of ISD
refinement that has moved the exponent very little (KN-TECH-057, KN-OPEN-019).

The corpus does hold partial theory in this direction: KN-LIT-6717 reports
worst-case sub-exponential hardness for LPN via smoothing arguments, and
KN-LIT-5999 reports pseudorandomness results for decoding. Neither is a
worst-case-to-average-case reduction at deployed parameters. Do not cite them as
if they were.

## The Gilbert-Varshamov reference point
The GV bound fixes the weight at which the expected number of solutions passes
one, and is therefore the natural normalization for "hard" instances. Exponent
comparisons between ISD variants are quoted at the *worst rate* -- the rate
maximizing the exponent -- which is why published exponents are single numbers
rather than curves. When a paper quotes one number, it is a maximum over rate,
not a statement about any particular scheme's rate. Concrete parameters are set
by estimators (KN-TECH-061), never by these maxima.

## Variants that matter
- **LPN** -- decoding at high error rate with an unbounded sample oracle; the
  corpus has extensive coverage (KN-LIT-4821, KN-LIT-3822, KN-LIT-5675).
- **Regular syndrome decoding (RSD)** -- the error vector is constrained to one
  nonzero per block. Cheaper to prove things about, and the basis of several
  modern signatures (KN-LIT-1137, KN-LIT-6591, KN-LIT-6232); the constraint also
  gives attackers structure to exploit (KN-LIT-3819).
- **Quasi-cyclic SD** -- the instance is quasi-cyclic, shrinking keys by a factor
  of the block count. This is a *structural* assumption on top of SD; see
  KN-TECH-060 and KN-OPEN-020.

## Applicability limits
Nothing above is verified in this program. The complexity classifications are
textbook; the average-case claims are `reported` from the cited literature. No
run in this corpus has measured an SD instance at any size. Treat every number
in this entry as a pointer to a source, not as a program result.
