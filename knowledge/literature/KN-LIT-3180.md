---
id: KN-LIT-3180
type: literature
title: "Correlation of Quadratic Boolean Functions: Cryptanalysis of All Versions of Full MORUS"
authors:
  - "Danping Shi"
  - "Siwei Sun"
  - "Yu Sasaki"
  - "Chaoyun Li"
  - "Lei Hu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the correlation of any quadratic Boolean function can be read out from its so-called disjoint quadratic form. We further propose a polynomial-time algorithm that can transform an arbitrary quadratic Boolean function into its disjoint quadratic form.

## Key claims (as reported)
- With this algorithm, the exact correlation of quadratic Boolean functions can be computed efficiently.
- We apply this method to analyze the linear trails of MORUS (one of the seven finalists of the CAESAR competition), which are found with the help of a generic model for linear trails of MORUS-like key-stream generators.
- In our model, any tool for finding linear trails of block ciphers can be used to search for trails of MORUS-like key-stream generators.
- As a result, a set of trails with correlation 2−38 is identified for all versions of full MORUS, while the correlations of previously published best trails for MORUS-640 and MORUS-1280 are 2−73 and 2−76 respectively (ASIACRYPT 2018).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940192 (1).pdf`
- `downloads/116940192.pdf`
