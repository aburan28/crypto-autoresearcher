---
id: KN-LIT-3784
type: literature
title: "Fast and Simple Point Operations on Edwards448 and E448"
authors:
  - "Luying Li"
  - "Wei Yu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, endomorphism, pairing, protocol, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since Edwards curves were introduced in elliptic curve cryptography, they have attracted a lot of attention. The twisted Edwards curves are defined by the equation Ea,d : ax2 + y 2 = 1 + dx2 y 2 .

## Key claims (as reported)
- Twisted Edwards curve is the state-of-the-art for a = −1, and even for a ̸= −1.
- E448 and Edwards448 are NIST standard curve in 2023 and TLS 1.3 standard curve in 2018.
- They both can be converted to d = −1, but can not be converted to a = −1 through isomorphism.
- The motivation of using a curve with d = −1 is that we want to improve the efficiency of E448, and Edwards448, especially to achieve a great saving in terms of the number of field multiplications (M) and field squarings (S).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602014 (1).pdf`
- `downloads/14602014.pdf`
