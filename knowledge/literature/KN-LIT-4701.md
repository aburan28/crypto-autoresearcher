---
id: KN-LIT-4701
type: literature
title: "Leakage-Tolerant Interactive Protocols?"
authors:
  - "Nir Bitansky"
  - "Ran Canetti"
  - "Shai Halevi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, side-channel, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We put forth a framework for expressing security requirements from interactive protocols in the presence of arbitrary leakage. This allows capturing different levels of leakage-tolerance of protocols, namely the preservation (or degradation) of security, under coordinated attacks that include various forms of leakage from the secret states of participating components.

## Key claims (as reported)
- The framework extends the universally composable (UC) security framework.
- We also prove a variant of the UC theorem that enables modular design and analysis of protocols even in face of general, non-modular leakage.
- We then construct leakage-tolerant protocols for basic tasks, such as secure message transmission, message authentication, commitment, oblivious transfer and zero-knowledge.
- A central component in several of our constructions is the observation that resilience to adaptive party corruptions (in some strong sense) implies leakage-tolerance in an essentially optimal way.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940128 (1).pdf`
- `downloads/71940128 (2).pdf`
- `downloads/71940128 (3).pdf`
- `downloads/71940128.pdf`
