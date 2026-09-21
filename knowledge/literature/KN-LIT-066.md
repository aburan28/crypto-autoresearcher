---
id: KN-LIT-066
type: literature
title: A Direct Key Recovery Attack on SIDH (arbitrary starting curve)
authors: [Maino Luciano, Martindale Chloe, Panny Lorenz, Pope Giacomo, Wesolowski Benjamin]
year: 2023
venue: EUROCRYPT 2023, LNCS 14008, pp. 448-471 (draft ePrint 2022/1026)
identifiers:
  eprint: iacr:2023/640
  doi: 10.1007/978-3-031-30589-4_16
  url: https://eprint.iacr.org/2023/640
tags: [sidh, cryptanalysis, torsion-points, arbitrary-starting-curve, key-recovery, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Removes the special-starting-curve assumption of Castryck-Decru (KN-LIT-065):
a direct key-recovery attack on SIDH for an ARBITRARY (random) starting curve,
via isogenies between polarized products of two supersingular elliptic curves.

## Key claims (as reported)
- Subexponential complexity for an arbitrary starting curve; polynomial time
  (under GRH) when the starting curve's endomorphism ring is known.
- Applies to any scheme publishing images of points under the secret isogeny
  (e.g. Seta, B-SIDH) but NOT to CSIDH, CSI-FiSh, or SQIsign.
- Two forms: the arbitrary-starting-curve draft (Maino-Martindale, ePrint
  2022/1026, 2 authors) and this merged EUROCRYPT 2023 paper (5 authors, ePrint
  2023/640).

## Relevance to this program
Shows the auxiliary-information attack does not need a privileged starting curve
-- generic extra structure (torsion images) suffices -- broadening the collapse
of SIDH's presumed hardness. Reinforces the program's theme that published
auxiliary data changes cryptanalytic complexity (KN-OPEN-015). Adjacent to the
ECDLP mission (supersingular isogeny setting).

## Not verified here
Full paper not read; the arbitrary-curve complexity and scheme scope relayed from
the abstracts (hence confidence: reported). Fields for both the draft (2022/1026)
and merged (2023/640) forms confirmed against IACR ePrint / Springer DOI via
search, not by fetching the primary pages.
