---
id: KN-LIT-2533
type: literature
title: "Analyzing Multi-Key Security Degradation"
authors:
  - "Atul Luykx"
  - "Bart Mennink"
  - "Kenneth G. Paterson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The multi-key, or multi-user, setting challenges cryptographic algorithms to maintain high levels of security when used with many different keys, by many different users. Its significance lies in the fact that in the real world, cryptography is rarely used with a single key in isolation.

## Key claims (as reported)
- A folklore result, proved by Bellare, Boldyreva, and Micali for public-key encryption in EUROCRYPT 2000, states that the success probability in attacking any one of many independently keyed algorithms can be bounded by the success probability of attacking a single instance of the algorithm, multiplied by the number of keys present.
- Although sufficient for settings in which not many keys are used, once cryptographic algorithms are used on an internet-wide scale, as is the case with TLS, the effect of multiplying by the number of keys can drastically erode security claims.
- We establish a sufficient condition on cryptographic schemes and security games under which multi-key degradation is avoided.
- As illustrative examples, we discuss how AES and GCM behave in the multi-key setting, and prove that GCM, as a mode, does not have multi-key degradation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240138 (1).pdf`
- `downloads/106240138.pdf`
