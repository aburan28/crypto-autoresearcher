---
id: KN-LIT-5577
type: literature
title: "On the Security of OAEP"
authors:
  - "Alexandra Boldyreva"
  - "Marc Fischlin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Currently, the best and only evidence of the security of the OAEP encryption scheme is a proof in the contentious random oracle model. Here we give further arguments in support of the security of OAEP.

## Key claims (as reported)
- We first show that partial instantiations, where one of the two random oracles used in OAEP is instantiated by a function family, can be provably secure (still in the random oracle model).
- For various security statements about OAEP we specify sufficient conditions for the instantiating function families that, in some cases, are realizable through standard cryptographic primitives and, in other cases, may currently not be known to be achievable but appear moderate and plausible.
- Furthermore, we give the first non-trivial security result about fully instantiated OAEP in the standard model, where both oracles are instantiated simultaneously.
- Namely, we show that instantiating both random oracles in OAEP by modest functions implies non-malleability under chosen plaintext attacks for random messages.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840209 (1).pdf`
- `downloads/42840209 (2).pdf`
- `downloads/42840209 (3).pdf`
- `downloads/42840209.pdf`
