---
id: KN-LIT-079
type: literature
title: A Quantum Algorithm for Computing Isogenies between Supersingular Elliptic Curves
authors: [Biasse Jean-Francois, Jao David, Sankar Anirudh]
year: 2014
venue: INDOCRYPT 2014, LNCS 8885, pp. 428-442
identifiers:
  eprint: null
  doi: 10.1007/978-3-319-13039-2_25
  url: https://link.springer.com/chapter/10.1007/978-3-319-13039-2_25
tags: [quantum, supersingular, isogeny-problem, claw-finding, quantum-baseline, cryptanalysis, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A quantum algorithm computing an isogeny between any two supersingular elliptic
curves over a finite field, combining a Delfs-Galbraith-style descent to the
F_p-rational subgraph (KN-LIT-078) with quantum search / claw-finding.

## Key claims (as reported)
- Complexity Otilde(p^{1/4}), an asymptotic improvement over the prior
  Otilde(p^{1/2}) classical/quantum bounds; heuristic/asymptotic.
- A quantum SPEEDUP for the general supersingular isogeny problem, not a practical
  break.

## Relevance to this program
Fixes the best-known QUANTUM baseline for the auxiliary-information-free
supersingular isogeny problem, complementing the classical bound (KN-LIT-078) and
framing how much torsion-aided attacks (KN-LIT-076, KN-LIT-077) improve on the
generic case (KN-OPEN-015). Note the contrast with the COMMUTATIVE branch, where
the quantum attack is subexponential (KN-LIT-071): the supersingular
(non-commutative) isogeny problem has only a p^{1/4} quantum attack, which is why
it was chosen for SIDH. Adjacent to the ECDLP mission.

## Not verified here
Full paper not read; the p^{1/4} quantum complexity relayed from the abstract
(hence confidence: reported). No IACR ePrint located. Fields confirmed against the
INDOCRYPT/Springer DOI and DBLP records via search, not by fetching the primary
page.
