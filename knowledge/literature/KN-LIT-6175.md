---
id: KN-LIT-6175
type: literature
title: "Recovering NTRU Secret Key From Inversion Oracles"
authors:
  - "Petros Mol"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, provable-security, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the NTRU encryption scheme as lately suggested for use, and study the connection between inverting the NTRU primitive (i.e., the one-way function over the message and the blinding information which underlies the NTRU scheme) and recovering the NTRU secret key (universal breaking). We model the inverting algorithms as black-box oracles and do not take any advantage of the internal ways by which the inversion works (namely, it does not have to be done by following the standard decryption algorithm).

## Key claims (as reported)
- This allows for secret key recovery directly from the output on several inversion queries even in the absence of decryption failures.
- Our oracles might be queried on both valid and invalid challenges e, however they are not required to reply (correctly) when their input is invalid.
- We show that key recovery can be reduced to inverting the NTRU function.
- The efficiency of the reduction highly depends on the specific values of the parameters.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390018 (1).pdf`
- `downloads/49390018 (2).pdf`
- `downloads/49390018 (3).pdf`
- `downloads/49390018.pdf`
