---
id: KN-LIT-6164
type: literature
title: "Rebound Attack on JH42"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hash function JH [20] is one of the five finalists of the NIST SHA-3 hash competition. It has been recently tweaked for the final by increasing its number of rounds from 35.5 to 42.

## Key claims (as reported)
- The previously best known results on JH were semi-free-start near-collisions up to 22 rounds using multi-inbound rebound attacks.
- In this paper we provide a new differential path on 32 rounds.
- Using this path, we are able to build various semi-free-start internal-state near-collisions and the maximum number of rounds that we achieved is up to 37 rounds on 986 bits.
- Moreover, we build distinguishers in the full 42-round internal permutation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730251 (1).pdf`
- `downloads/70730251 (2).pdf`
- `downloads/70730251 (3).pdf`
- `downloads/70730251.pdf`
