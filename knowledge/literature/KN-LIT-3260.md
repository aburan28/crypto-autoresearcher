---
id: KN-LIT-3260
type: literature
title: "Cryptanalysis of stream ciphers with linear masking"
authors:
  - "Don Coppersmith"
  - "Shai Halevi"
  - "Charanjit Jutla"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a cryptanalytical technique for distinguishing some stream ciphers from a truly random process. Roughly, the ciphers to which this method applies consist of a “non-linear process” (say, akin to a round function in block ciphers), and a “linear process” such as an LFSR (or even fixed tables).

## Key claims (as reported)
- The output of the cipher can be the linear sum of both processes.
- To attack such ciphers, we look for any property of the “non-linear process” that can be distinguished from random.
- In addition, we look for a linear combination of the linear process that vanishes.
- We then consider the same linear combination applied to the cipher’s output, and try to find traces of the distinguishing property.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420517 (1).pdf`
- `downloads/24420517 (2).pdf`
- `downloads/24420517.pdf`
