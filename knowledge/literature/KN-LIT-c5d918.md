---
id: KN-LIT-c5d918
type: literature
title: "Improving the parallelized Pollard lambda search on anomalous binary curves"
authors:
  - "Robert Gallant"
  - "Robert Lambert"
  - "Scott Vanstone"
year: 2000
venue: "Mathematics of Computation 69:1699-1705"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1090/S0025-5718-99-01119-9"
  url: null
tags: [pollard-rho, koblitz, frobenius, equivalence-classes, binary-field, anomalous-binary-curve, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Independently of Wiener-Zuccherato, shows how to use the Frobenius endomorphism together with negation on anomalous binary (Koblitz) curves inside parallel collision search, reducing expected iterations by sqrt(2m) for curves over F_{2^m}. This is the reduction used for ECC2K-130 and the 113-bit Koblitz-curve record.

## Key claims (as reported)

- sqrt(2m) fewer iterations on Koblitz curves over F_{2^m}.

## Relevance to this program

The √(2m) speed-up of parallel rho/lambda on Koblitz (anomalous binary) curves via Frobenius classes — the mechanism ECC2K-130's 2^60.9 estimate rests on. The Koblitz correction factor worked out at review time in EV-ICPERF-390707 (O-12) is this paper's result; proposals to 'walk on Frobenius orbits' are known.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
