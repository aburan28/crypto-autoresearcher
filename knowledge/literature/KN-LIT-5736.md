---
id: KN-LIT-5736
type: literature
title: "Password-Authenticated Session-Key Generation on the Internet in the Plain Model"
authors:
  - "Vipul Goyal"
  - "Abhishek Jain"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The problem of password-authenticated key exchange (PAKE) has been extensively studied for the last two decades. Despite extensive studies, no construction was known for a PAKE protocol that is secure in the plain model in the setting of concurrent self-composition, where polynomially many protocol sessions with the same password may be executed on the distributed network (such as the Internet) in an arbitrarily interleaved manner, and where the adversary may corrupt any number of participating parties.

## Key claims (as reported)
- In this paper, we resolve this long-standing open problem.
- In particular, we give the first construction of a PAKE protocol that is secure (with respect to the standard definition of Goldreich and Lindell) in the fully concurrent setting and without requiring any trusted setup assumptions.
- We stress that we allow polynomially-many concurrent sessions, where polynomial is not fixed in advance and can be determined by an adversary an an adaptive manner.
- Interestingly, our proof, among other things, requires important ideas from Precise Zero Knowledge theory recently developed by Micali and Pass in their STOC’06 paper.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230276 (1).pdf`
- `downloads/62230276 (2).pdf`
- `downloads/62230276 (3).pdf`
- `downloads/62230276.pdf`
