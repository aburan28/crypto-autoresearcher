---
id: KN-LIT-6771
type: literature
title: "Sponge-based pseudo-random number generators"
authors:
  - "Guido Bertoni"
  - "Joan Daemen"
  - "Michaël Peeters"
  - "Gilles Van Assche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes a new construction for the generation of pseudo-random numbers. The construction is based on sponge functions and is suitable for embedded security devices as it requires few resources.

## Key claims (as reported)
- We propose a model for such generators and explain how to define one on top of a sponge function.
- The construction is a novel way to use a sponge function, and inputs and outputs blocks in a continuous fashion, allowing to interleave the feed of seeding material with the fetch of pseudo-random numbers without latency.
- We describe the consequences of the sponge indifferentiability results to this construction and study the resistance of the construction against generic state recovery attacks.
- Finally, we propose a concrete example based on a member of the Keccak family with small width.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250031 (1).pdf`
- `downloads/62250031 (2).pdf`
- `downloads/62250031 (3).pdf`
- `downloads/62250031.pdf`
