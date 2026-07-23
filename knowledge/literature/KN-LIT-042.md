---
id: KN-LIT-042
type: literature
title: Faster Attacks on Elliptic Curve Cryptosystems
authors: [Wiener Michael J., Zuccherato Robert J.]
year: 1998
venue: SAC 1998, LNCS 1556, pp. 190-200
identifiers:
  eprint: null
  doi: 10.1007/3-540-48892-8_15
  url: https://doi.org/10.1007/3-540-48892-8_15
tags: [pollard-rho, negation, automorphism, equivalence-class, rho-speedup, baseline, ecdlp]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Shows parallel collision search / Pollard rho for the ECDLP can be sped up by
walking on *equivalence classes* under the group automorphisms -- chiefly the
free negation map P -> -P. Walking modulo automorphisms shrinks the effective
search space.

## Key claims (as reported)
- ~sqrt(2) factor for arbitrary curves (negation); ~sqrt(2d) for subfield curves;
  larger sqrt(2m)-type factors for Koblitz/anomalous-binary curves via Frobenius.
- Practical caveat: negation-based walks can hit "fruitless cycles" needing
  handling.
- Larger automorphism orders: Duursma-Gaudry-Morain, "Speeding up the Discrete
  Log Computation on Curves with Automorphisms," ASIACRYPT 1999, LNCS 1716:103-121
  (doi:10.1007/978-3-540-48000-6_10) -- ~sqrt(m) for automorphism order m, incl.
  hyperelliptic curves.

## Relevance to this program
The origin of the sqrt(|Aut|) automorphism speedup of rho -- precisely the
constant adjustment the program's baseline must incorporate. The program's
convention ("0.886*sqrt(n), negation") already reflects the negation sqrt(2)
factor (KN-TECH-006, KN-TECH-018). Any claimed prime-field advantage must beat
the *automorphism-adjusted* rho constant, not the un-discounted one.

## Not verified here
Full paper not read; the negation/equivalence-class speedup is textbook-level in
ECC cryptanalysis (hence confidence: established). Fields (incl. Duursma-Gaudry-
Morain) confirmed against Springer DOI records via search, not by fetching the
primary pages.
