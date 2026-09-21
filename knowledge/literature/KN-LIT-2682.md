---
id: KN-LIT-2682
type: literature
title: "Better Steady than Speedy: Full break of SPEEDY-7-192"
authors:
  - "Christina Boura"
  - "Nicolas David"
  - "Rachelle Heim Boissier"
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
Differential attacks are among the most important families of cryptanalysis against symmetric primitives. Since their introduction in 1990, several improvements to the basic technique as well as many dedicated attacks against symmetric primitives have been proposed.

## Key claims (as reported)
- Most of the proposed improvements concern the key-recovery part.
- However, when designing a new primitive, the security analysis regarding differential attacks is often limited to finding the best trails over a limited number of rounds with branch and bound techniques, and a poor heuristic is then applied to deduce the total number of rounds a differential attack could reach.
- In this work we analyze the security of the SPEEDY family of block ciphers against differential cryptanalysis and show how to optimize many of the steps of the key-recovery procedure for this type of attacks.
- For this, we implemented a search for finding optimal trails for this cipher and their associated multiple probabilities under some constraints and applied non-trivial techniques to obtain optimal data and key-sieving.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004164 (1).pdf`
- `downloads/14004164.pdf`
