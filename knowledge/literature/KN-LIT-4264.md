---
id: KN-LIT-4264
type: literature
title: "How to Build Fully Secure Tweakable Blockciphers from Classical Blockciphers"
authors:
  - "Lei Wang"
  - "Jian Guo"
  - "Guoyan Zhang"
  - "Jingyuan Zhao"
  - "Dawu Gu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper focuses on building a tweakable blockcipher from a classical blockcipher whose input and output wires all have a size of n bits. The main goal is to achieve full 2n security.

## Key claims (as reported)
- Such a tweakable blockcipher was proposed by Mennink at FSE’15, and it is also the only tweakable blockcipher so far that claimed full 2n security to our best knowledge.
- However, we find a key-recovery attack on Mennink’s proposal (in the proceeding version) with a complexity of about 2n/2 adversarial queries.
- The attack well demonstrates that Mennink’s proposal has at most 2n/2 security, and therefore invalidates its security claim.
- In this paper, we study a construction of tweakable blockciphers denoted as e that is built on s invocations of a blockcipher and additional simple E[s] XOR operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031246 (1).pdf`
- `downloads/10031246.pdf`
