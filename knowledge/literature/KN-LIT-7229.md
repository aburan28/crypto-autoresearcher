---
id: KN-LIT-7229
type: literature
title: "Towards Sound Fresh Re-Keying with Hard (Physical)"
authors:
  - "Anthony Journault"
  - "Daniel Masny"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mpc, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Most leakage-resilient cryptographic constructions aim at limiting the information adversaries can obtain about secret keys. In the case of asymmetric algorithms, this is usually obtained by secret sharing (aka masking) the key, which is made easy by their algebraic properties.

## Key claims (as reported)
- In the case of symmetric algorithms, it is rather key evolution that is exploited.
- While more efficient, the scope of this second solution is limited to stateful primitives that easily allow for key evolution such as stream ciphers.
- Unfortunately, it seems generally hard to avoid the need of (at least one) execution of a stateless primitive, both for encryption and authentication protocols.
- As a result, fresh re-keying has emerged as an alternative solution, in which a block cipher that is hard to protect against side-channel attacks is re-keyed with a stateless function that is easy to mask.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98150263 (1).pdf`
- `downloads/98150263.pdf`
