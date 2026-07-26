---
id: KN-LIT-5662
type: literature
title: "Optimal Security Proofs for Signatures from Identification Schemes"
authors:
  - "Eike Kiltz"
  - "Daniel Masny"
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We perform a concrete security treatment of digital signature schemes obtained from canonical identification schemes via the FiatShamir transform. If the identification scheme is random self-reducible and satisfies the weakest possible security notion (hardness of key-recoverability), then the signature scheme obtained via Fiat-Shamir is unforgeable against chosen-message attacks in the multi-user setting.

## Key claims (as reported)
- Our security reduction is in the random oracle model and loses a factor of roughly Qh , the number of hash queries.
- Previous reductions incorporated an additional multiplicative loss of N , the number of users in the system.
- Our analysis is done in small steps via intermediate security notions, and all our implications have relatively simple proofs.
- Furthermore, for each step, we show the optimality of the given reduction in terms of model assumptions and tightness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98150031 (1).pdf`
- `downloads/98150031.pdf`
