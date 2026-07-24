---
id: KN-LIT-077
type: literature
title: Faster Algorithms for Isogeny Problems Using Torsion Point Images
authors: [Petit Christophe]
year: 2017
venue: ASIACRYPT 2017, LNCS 10625, pp. 330-353
identifiers:
  eprint: iacr:2017/571
  doi: 10.1007/978-3-319-70697-9_12
  url: https://eprint.iacr.org/2017/571
tags: [torsion-points, sidh, overstretched, unbalanced, cryptanalysis, isogeny, break-precursor, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Observes that SIDH-type isogeny problems come with extra input absent from the
general problem -- the images of certain torsion points of order coprime to the
isogeny -- and gives new algorithms EXPLOITING this to speed up solving, showing
some instances (unbalanced / "overstretched" parameter regimes) become easier
than the general case.

## Key claims (as reported)
- Widely regarded as the CONCEPTUAL SEED of the 2022 polynomial-time SIDH breaks
  (KN-LIT-065, KN-LIT-067).
- Framed as asymptotic/conditional improvements over specific parameter families,
  NOT a break of standard SIDH parameters (in 2017).

## Relevance to this program
The canonical demonstration that revealed torsion-point images weaken isogeny
problems below general-case hardness -- central to the program's theme of
auxiliary information altering cryptanalytic complexity (KN-OPEN-015). Documents
the five-year arc from "torsion images make unbalanced cases easier" (2017) to
"torsion images break everything in poly time" (2022). Adjacent to the ECDLP
mission.

## Not verified here
Full paper not read; the torsion-image speedups and overstretched-regime results
relayed from the abstract (hence confidence: reported). Fields confirmed against
IACR ePrint 2017/571 and the Springer DOI via search, not by fetching the primary
pages.
