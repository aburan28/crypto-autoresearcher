---
id: KN-LIT-2927
type: literature
title: "Clustering Effect in Simon and Simeck"
authors:
  - "Gaëtan Leurent"
  - "Clara Pernot"
  - "André Schrottenloher"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Simon and Simeck are two lightweight block ciphers with a simple round function using only word rotations and a bit-wise AND operation. Previous work has shown a strong clustering effect for differential and linear cryptanalysis, due to the existence of many trails with the same inputs and outputs.

## Key claims (as reported)
- In this paper, we explore this clustering effect by exhibiting a class of high probability differential and linear trails where the active bits stay in a fixed window of w bits.
- Instead of enumerating a set of good trails contributing to a differential or a linear approximation, we compute the probability distribution over this space, including all trails in the class.
- This results in stronger distinguishers than previously proposed, and we describe key recovery attacks against Simon and Simeck improving the previous results by up to 7 rounds.
- In particular, we obtain an attack against 42-round Simeck64, leaving only two rounds of security margin, and an attack against 45-round Simon96/144, reducing the security margin from 16 rounds to 9 rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900269 (1).pdf`
- `downloads/130900269.pdf`
