---
id: KN-LIT-1302
type: literature
title: "Solving McEliece-1409 in One Day — Cryptanalysis with the"
authors:
  - "Hiroki Furue"
  - "Yusuke Aikawa"
  - "Kazuhide Fukushima"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/393"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/393"
tags: [cryptanalysis, isogeny, pqc, sidh-csidh, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Syndrome decoding problem (SDP) is the security assumption of the code-based cryptography. Three out of the four NIST-PQC round 4 candidates are code-based cryptography.

## Key claims (as reported)
- Information set decoding (ISD) is known for the fastest existing algorithm to solve SDP instances with relatively high code rate.
- Security of code-based cryptography is often constructed on the asymptotic complexity of the ISD algorithm.
- However, the concrete complexity of the ISD algorithm has hardly ever been known.
- Recently, Esser, May and Zweydinger (Eurocrypt ’22) provided the first implementation of the representation-based ISD, such as May–Meurer–Thomae (MMT) or Becker–Joux–May–Meurer (BJMM) algorithm and solved the McEliece-1284 instance in the decoding challenge, revealing the practical efficiency of these ISDs.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-393.pdf`
