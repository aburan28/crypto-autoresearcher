---
id: KN-LIT-6466
type: literature
title: Secure Sketch for Biometric Templates
authors:
- Qiming Li
- Yagiz Sutcu
- Nasir Memon
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- biometrics
- fuzzy-extractor
- secure-sketch
- applied-security
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
There have been active discussions on how to derive a consistent cryptographic key from noisy data such as biometric templates, with the help of some extra information called a sketch. It is desirable that the sketch reveals little information about the biometric templates even in the worst case (i.e., the entropy loss should be low).

## Key claims (as reported)
- The main difficulty is that many biometric templates are represented as points in continuous domains with unknown distributions, whereas known results either work only in discrete domains, or lack rigorous analysis on the entropy loss.
- A general approach to handle points in continuous domains is to quantize (discretize) the points and apply a known sketch scheme in the discrete domain.
- However, it can be difficult to analyze the entropy loss due to quantization and to find the “optimal” quantizer.
- In this paper, instead of trying to solve these problems directly, we propose to examine the relative entropy loss of any given scheme, which bounds the number of additional bits we could have extracted if we used the optimal parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840099 (1).pdf`
- `downloads/42840099 (2).pdf`
- `downloads/42840099 (3).pdf`
- `downloads/42840099.pdf`
