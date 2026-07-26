---
id: KN-LIT-7210
type: literature
title: "Towards compressed permutation oracles"
authors:
  - "Dominique Unruh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Compressed oracles (Zhandry, Crypto 2019) are a powerful technique to reason about quantum random oracles, enabling a sort of lazy sampling in the presence of superposition queries. A long-standing open question is whether a similar technique can also be used to reason about random (efficiently invertible) permutations.

## Key claims (as reported)
- In this work, we make a step towards answering this question.
- We first define the compressed permutation oracle and illustrate its use.
- While the soundness of this technique (i.e., the indistinguishability from a random permutation) remains a conjecture, we show a curious 2-for-1 theorem: If we use the compressed permutation oracle methodology to show that some construction (e.g., Luby-Rackoff) implements a random permutation (or strong qPRP), then we get the fact that this methodology is actually sound for free.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438298 (1).pdf`
- `downloads/14438298.pdf`
