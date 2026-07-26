---
id: KN-LIT-5296
type: literature
title: "On 2-Round Secure Multiparty Computation"
authors:
  - "Rosario Gennaro"
  - "Yuval Ishai"
  - "Eyal Kushilevitz"
  - "Tal Rabin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Substantial efforts have been spent on characterizing the round complexity of various cryptographic tasks. In this work we study the round complexity of secure multiparty computation in the presence of an active (Byzantine) adversary, assuming the availability of secure point-to-point channels and a broadcast primitive.

## Key claims (as reported)
- It was recently shown that in this setting three rounds are sufficient for arbitrary secure computation tasks, with a linear security threshold, and two rounds are sufficient for certain nontrivial tasks.
- This leaves open the question whether every function can be securely computed in two rounds.
- We show that the answer to this question is “no”: even some very simple functions do not admit secure 2-round protocols (independently of their communication and time complexity) and thus 3 is the exact round complexity of general secure multiparty computation.
- Yet, we also present some positive results by identifying a useful class of functions which can be securely computed in two rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420178 (1).pdf`
- `downloads/24420178 (2).pdf`
- `downloads/24420178.pdf`
