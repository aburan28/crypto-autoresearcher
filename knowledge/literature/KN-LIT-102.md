---
id: KN-LIT-102
type: literature
title: Lattice Enumeration Using Extreme Pruning
authors: [Gama Nicolas, Nguyen Phong Q., Regev Oded]
year: 2010
venue: EUROCRYPT 2010, LNCS 6110, Springer, pages 257-278
identifiers:
  eprint: null
  doi: 10.1007/978-3-642-13190-5_13
  url: https://www.iacr.org/archive/eurocrypt2010/66320257/66320257.pdf
tags: [enumeration, extreme-pruning, pruning, svp, cvp, lattice-reduction, bkz, speedup, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Revisits lattice enumeration -- the most basic exact-SVP/CVP algorithm, used
both standalone and as the BKZ inner loop -- and shows that an exponential
speedup is available in both theory and practice via *extreme pruning*: run
enumeration with a pruning profile so aggressive that the success probability
per run is tiny, and compensate by many randomised restarts. Also gives what
the authors describe as the first sound analysis of pruning, a technique
introduced by Schnorr et al. in the 1990s but not rigorously analysed.

## Key claims (as reported)
- Extreme pruning yields "surprising exponential speedups" over unpruned
  enumeration, both asymptotically and in implementation.
- The paper provides the first sound analysis of pruning; earlier pruning
  heuristics lacked one.
- Enumeration remains the basic subroutine for hard lattice problems and is used
  as a subroutine inside lattice reduction algorithms -- which is why the
  speedup propagates directly into BKZ (adopted immediately by KN-LIT-101).

## Relevance to this program
Enumeration is the algorithm family that sieving eventually displaced, and the
displacement point is a quantitative question the program should not guess at.
This paper marks the high-water mark of enumeration: it is the reason
enumeration stayed competitive for another decade, and the reason the
crossover with sieving occurs where it does (reported at dimension 70 in
KN-LIT-106). It matters methodologically too: enumeration is superexponential
(`2^Theta(n log n)`) but with small constants, sieving is single-exponential
with large constants and exponential memory. A cost comparison that reports
only an asymptotic exponent ranks these two wrongly at every dimension anyone
has ever computed. Compare KN-TECH-035: this is the same "the exponent is not
the cost" discipline the program applies to ECDLP.

## Not verified here
The complete published abstract was read; the pruning analysis, the success
probability computation, and the claimed speedup factors were not re-derived or
reproduced. The specific pruning profiles and their optimisation are not
summarised here.
