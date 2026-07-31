---
id: KN-LIT-3267
type: literature
title: "Cryptanalysis of the GPRS Encryption"
authors:
  - "Algorithms GEA"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents the first publicly available cryptanalytic attacks on the GEA-1 and GEA-2 algorithms. Instead of providing full 64bit security, we show that the initial state of GEA-1 can be recovered from as little as 65 bits of known keystream (with at least 24 bits coming from one frame) in time 240 GEA-1 evaluations and using 44.5 GiB of memory.

## Key claims (as reported)
- The attack on GEA-1 is based on an exceptional interaction of the deployed LFSRs and the key initialization, which is highly unlikely to occur by chance.
- This unusual pattern indicates that the weakness is intentionally hidden to limit the security level to 40 bit by design.
- In contrast, for GEA-2 we did not discover the same intentional weakness.
- However, using a combination of algebraic techniques and list merging algorithms we are still able to break GEA-2 in time 245.1 GEA-2 evaluations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960325 (1).pdf`
- `downloads/126960325.pdf`
