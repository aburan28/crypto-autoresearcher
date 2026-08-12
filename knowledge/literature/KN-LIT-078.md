---
id: KN-LIT-078
type: literature
title: Computing isogenies between supersingular elliptic curves over F_p (Delfs-Galbraith)
authors: [Delfs Christina, Galbraith Steven D.]
year: 2016
venue: Designs, Codes and Cryptography, 78(2):425-440
identifiers:
  eprint: null
  doi: 10.1007/s10623-014-0010-1
  arxiv: "1310.7789"
  url: https://arxiv.org/abs/1310.7789
tags: [supersingular, isogeny-problem, path-finding, meet-in-the-middle, classical-baseline, cryptanalysis, isogeny, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A classical algorithm to compute an isogeny between two supersingular elliptic
curves over F_p, exploiting the subgraph of F_p-rational curves within the
supersingular isogeny graph.

## Key claims (as reported)
- Full-graph meet-in-the-middle over F_{p^2} costs expected Otilde(p^{1/2}) time
  and space; descending to the F_p-rational subgraph gives Otilde(p^{1/4}) for the
  F_p case.
- Complexities are heuristic/expected asymptotics; establishes the CLASSICAL
  baseline hardness of the pure supersingular isogeny problem WITHOUT auxiliary
  torsion data.

## Relevance to this program
The reference point (~square-root, improved to p^{1/4} over F_p) against which
torsion-aided attacks (KN-LIT-076, KN-LIT-077) and the full break are measured --
i.e. how much cheaper the problem gets once auxiliary information is available
(KN-OPEN-015). Its meet-in-the-middle structure is kin to the program's
birthday/collision cost models. Adjacent to the ECDLP mission.

## Not verified here
Full paper not read; the p^{1/2} / p^{1/4} costs relayed from the abstract (hence
confidence: reported). The IACR ePrint number could NOT be confirmed and is
omitted (the sometimes-cited "2013/506" is a DIFFERENT paper); identifiers are the
DCC DOI 10.1007/s10623-014-0010-1 and arXiv:1310.7789, both confirmed via search.
