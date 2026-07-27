---
id: KN-LIT-3341
type: literature
title: "CTIDH: faster constant-time"
authors:
  - "Tanja Lange"
  - "Michael Meyer"
  - "Benjamin Smith"
  - "Jana Sotáková"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hyperelliptic, implementation, isogeny, pairing, pqc, protocol, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a new key space for CSIDH and a new algorithm for constant-time evaluation of the CSIDH group action. The key space is not useful with previous algorithms, and the algorithm is not useful with previous key spaces, but combining the new key space with the new algorithm produces speed records for constant-time CSIDH.

## Key claims (as reported)
- For example, for CSIDH-512 with a 256-bit key space, the best previous constant-time results used 789000 multiplications and more than 200 million Skylake cycles; this paper uses 438006 multiplications and 125.53 million cycles.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ctidh-20210513.pdf`
