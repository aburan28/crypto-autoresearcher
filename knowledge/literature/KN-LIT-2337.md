---
id: KN-LIT-2337
type: literature
title: "Adaptive Trapdoor Functions and Chosen-Ciphertext Security"
authors:
  - "Eike Kiltz"
  - "Payman Mohassel"
  - "Adam O’Neill"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of adaptive trapdoor functions (ATDFs); roughly, ATDFs remain one-way even when the adversary is given access to an inversion oracle. Our main application is the black-box construction of chosenciphertext secure public-key encryption (CCA-secure PKE).

## Key claims (as reported)
- Namely, we give a black-box construction of CCA-Secure PKE from ATDFs, as well as a construction of ATDFs from correlation-secure TDFs introduced by Rosen and Segev (TCC ’09).
- Moreover, by an extension of a recent result of Vahlis (TCC ’10), we show that ATDFs are strictly weaker than the latter (in a black-box sense).
- Thus, adaptivity appears to be the weakest condition on a TDF currently known to yield the first implication.
- We also give a black-box construction of CCA-secure PKE from a natural extension of ATDFs we call tag-based ATDFs that, when applied to our constructions of the latter from either correlation-secure TDFs, or lossy TDFs introduced by Peikert and Waters (STOC ’08), yield precisely the CCA-secure PKE schemes in these works.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320180 (1).pdf`
- `downloads/66320180 (2).pdf`
- `downloads/66320180 (3).pdf`
- `downloads/66320180.pdf`
