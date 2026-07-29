---
id: KN-LIT-1990
type: literature
title: "4-Round Luby-Rackoff Construction is a qPRP"
authors:
  - "Akinori Hosoyamada"
  - "Tetsu Iwata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, pqc, provable-security, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Luby-Rackoff construction, or the Feistel construction, is one of the most important approaches to construct secure block ciphers from secure pseudorandom functions. The 3- and 4-round Luby-Rackoff constructions are proven to be secure against chosen-plaintext attacks (CPAs) and chosen-ciphertext attacks (CCAs), respectively, in the classical setting.

## Key claims (as reported)
- However, Kuwakado and Morii showed that a quantum superposed chosen-plaintext attack (qCPA) can distinguish the 3-round LubyRackoff construction from a random permutation in polynomial time.
- In addition, Ito et al. recently showed a quantum superposed chosenciphertext attack (qCCA) that distinguishes the 4-round Luby-Rackoff construction.
- Since Kuwakado and Morii showed the result, a problem of much interest has been how many rounds are sufficient to achieve provable security against quantum query attacks.
- This paper answers to this fundamental question by showing that 4-rounds suffice against qCPAs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210319 (1).pdf`
- `downloads/119210319.pdf`
