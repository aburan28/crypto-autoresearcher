---
id: KN-LIT-5838
type: literature
title: "Practical Cryptanalysis of the Open Smart Grid Protocol"
authors:
  - "Philipp Jovanovic"
  - "Samuel Neves"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper analyses the cryptography used in the Open Smart Grid Protocol (OSGP). The authenticated encryption (AE) scheme deployed by OSGP is a non-standard composition of RC4 and a homebrewed MAC, the “OMA digest”.

## Key claims (as reported)
- We present several practical key-recovery attacks against the OMA digest.
- The first and basic variant can achieve this with a mere 13 queries to an OMA digest oracle and negligible time complexity.
- A more sophisticated version breaks the OMA digest with only 4 queries and a time complexity of about 225 simple operations.
- A different approach only requires one arbitrary valid plaintext-tag pair, and recovers the key in an average of 144 message verification queries, or one ciphertext-tag pair and 168 ciphertext verification queries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400109 (4).pdf`
- `downloads/85400109 (5).pdf`
