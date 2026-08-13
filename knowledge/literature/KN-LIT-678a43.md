---
id: KN-LIT-678a43
type: literature
title: "Solving the supersingular isogeny problem in time p^{2/5+o(1)} using bivariate multipoint evaluation"
authors:
  - "Aleksei Udovenko"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1575"
identifiers:
  eprint: iacr:2026/1575
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1575"
tags: [isogeny, supersingular, ecdlp, multipoint-evaluation, endomorphism, attack]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Presents a new unconditional attack on the supersingular isogeny problem
(OneEnd / endomorphism ring recovery) with expected time and memory
complexity p^{2/5+o(1)}. Builds on Eisenträger–Hallgren–Leonardi–Morrison–Park
(2020) and Fuselier–Iezzi–Kozek–Morrison–Namoijam (2025), and is related to
the recent heuristic p^{1/3+o(1)} attack of Wesolowski (ePrint 2026/1486):
all search for a separable isogeny from a curve to its Galois conjugate to
form a non-scalar endomorphism.

## Key claims (as reported)
- Unconditional (not heuristic) attack: time AND memory p^{2/5+o(1)}.
- Uses highly theoretical multivariate multipoint evaluation algorithms
  (Kedlaya–Umans 2008/2011; Bhargava–Ghosh–Guo–Kumar–Umans 2022; Ghosh–Harsha–
  Herdade–Kumar–Saptharishi 2023), so the attack is *not* a practical threat to
  isogeny cryptosystems; it is of theoretical interest only.
- Compared with the Wesolowski heuristic p^{1/3}: if both were instantiated,
  isogeny-based cryptosystem security would degrade; realism caveat applies.

## Relevance
- Core to the program's hard-problem baseline: supersingular isogeny (SI/LDBP).
  Records the current *unconditional* state of the art for the exponent of SSI:
  p^{2/5+o(1)} (unconditional) vs p^{1/3+o(1)} (heuristic, Wesolowski 2026/1486,
  in corpus as KN-LIT-7564).
- Combinations: any novelty claim for OneEnd at sub-exponential exponents must sit
  below this. Also the "time AND memory" phrasing underlines that memory is no
  longer cheap.

## Not verified here
- The parameter details of multipoint evaluation (details before p.5) not re-readable from
  extracted first page. Complexity bound and attribution relayed from the abstract.