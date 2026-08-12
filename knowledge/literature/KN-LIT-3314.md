---
id: KN-LIT-3314
type: literature
title: "Cryptographic Smooth Neighbors"
authors:
  - "Giacomo Bruno"
  - "Maria Corte-Real Santos⋆"
  - "Craig Costello"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [isogeny, lattice, pqc, protocol, provable-security, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the problem of finding two consecutive B-smooth integers by giving an optimised implementation of the Conrey-Holmstrom-McLaughlin “smooth neighbors” algorithm. While this algorithm is not guaranteed to return the complete set of B-smooth neighbors, in practice it returns a very close approximation to the complete set but does so in a tiny fraction of the time of its exhaustive counterparts.

## Key claims (as reported)
- We exploit this algorithm to find record-sized solutions to the pure twin smooth problem, and subsequently to produce instances of cryptographic parameters whose corresponding isogeny degrees are significantly smoother than prior works.
- Our methods seem well-suited to finding parameters for the SQISign signature scheme, especially for instantiations looking to minimise the cost of signature generation.
- We give a number of examples, among which are the first parameter sets geared towards efficient SQISign instantiations at NIST’s security levels III and V.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438075 (1).pdf`
- `downloads/14438075.pdf`
