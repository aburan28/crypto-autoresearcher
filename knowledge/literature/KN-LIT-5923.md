---
id: KN-LIT-5923
type: literature
title: "Privately Puncturing PRFs from Lattices:"
authors:
  - "Adaptive Security"
  - "Collusion Resistant"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A private puncturable pseudorandom function (PRF) enables one to create a constrained version of a PRF key, which can be used to evaluate the PRF at all but some punctured points. In addition, the constrained key reveals no information about the punctured points and the PRF values on them.

## Key claims (as reported)
- Existing constructions of private puncturable PRFs are only proven to be secure against a restricted adversary that must commit to the punctured points before viewing any information.
- It is an open problem to achieve the more natural adaptive security, where the adversary can make all its choices on-the-fly.
- In this work, we solve the problem by constructing an adaptively secure private puncturable PRF from standard lattice assumptions.
- To achieve this goal, we present a new primitive called explainable hash, which allows one to reprogram the hash function on a given input.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004016 (1).pdf`
- `downloads/14004016.pdf`
