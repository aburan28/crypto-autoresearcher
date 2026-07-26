---
id: KN-LIT-2000
type: literature
title: "A Block-Cipher Mode of Operation for Parallelizable Message Authentication"
authors:
  - "John Black"
  - "Phillip Rogaway"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define and analyze a simple and fully parallelizable blockcipher mode of operation for message authentication. Parallelizability does not come at the expense of serial efficiency: in a conventional, serial environment, the algorithm’s speed is within a few percent of the (inherently sequential) CBC MAC.

## Key claims (as reported)
- The new mode, PMAC, is deterministic, resembles a standard mode of operation (and not a CarterWegman MAC), works for strings of any bit length, employs a single block-cipher key, and uses just max{1, d|M |/ne} block-cipher calls to MAC a string M ∈ {0, 1}∗ using an n-bit block cipher.
- We prove PMAC secure, quantifying an adversary’s forgery probability in terms of the quality of the block cipher as a pseudorandom permutation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/pmac (1).pdf`
- `downloads/pmac (2).pdf`
- `downloads/pmac.pdf`
