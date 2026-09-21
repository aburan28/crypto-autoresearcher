---
id: KN-LIT-3233
type: literature
title: "Cryptanalysis of Full Sprout"
authors:
  - "Virginie Lallemand"
  - "Marı́a Naya-Plasencia"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A new method for reducing the internal state size of stream cipher registers has been proposed in FSE 2015, allowing to reduce the area in hardware implementations. Along with it, an instantiated proposal of a cipher was also proposed: Sprout.

## Key claims (as reported)
- In this paper, we analyze the security of Sprout, and we propose an attack that recovers the whole key more than 210 times faster than exhaustive search and has very low data complexity.
- The attack can be seen as a divide-and-conquer evolved technique, that exploits the non-linear influence of the key bits on the update function.
- We have implemented the attack on a toy version of Sprout, that conserves the main properties exploited in the attack.
- The attack completely matches the expected complexities predicted by our theoretical cryptanalysis, which proves its validity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160328 (1).pdf`
- `downloads/92160328 (2).pdf`
- `downloads/92160328.pdf`
