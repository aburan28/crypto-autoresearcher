---
id: KN-LIT-2203
type: literature
title: "A Provable-Security Analysis of Intel’s Secure Key RNG"
authors:
  - "Thomas Shrimpton"
  - "R. Seth Terashima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide the first provable-security analysis of the Intel Secure Key hardware RNG (ISK-RNG), versions of which have appeared in Intel processors since late 2011. To model the ISK-RNG, we generalize the PRNG-with-inputs primitive, introduced by Dodis et al. at CCS’13 for their /dev/[u]random analysis.

## Key claims (as reported)
- The concrete security bounds we uncover tell a mixed story.
- We find that ISK-RNG lacks backward-security altogether, and that the forward-security bound for the “truly random” bits fetched by the RDSEED instruction is potentially worrisome.
- On the other hand, we are able to prove stronger forward-security bounds for the pseudorandom bits fetched by the RDRAND instruction.
- En route to these results, our main technical efforts focus on the way in which ISK-RNG employs CBCMAC as an entropy extractor.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560124 (1).pdf`
- `downloads/90560124.pdf`
