---
id: KN-LIT-2993
type: literature
title: "Compact Proofs of Retrievability"
authors:
  - "Hovav Shacham"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a proof-of-retrievability system, a data storage center convinces a verifier that he is actually storing all of a client’s data. The central challenge is to build systems that are both efficient and provably secure – that is, it should be possible to extract the client’s data from any prover that passes a verification check.

## Key claims (as reported)
- In this paper, we give the first proof-of-retrievability schemes with full proofs of security against arbitrary adversaries in the strongest model, that of Juels and Kaliski.
- Our first scheme, built from BLS signatures and secure in the random oracle model, has the shortest query and response of any proof-of-retrievability with public verifiability.
- Our second scheme, which builds elegantly on pseudorandom functions (PRFs) and is secure in the standard model, has the shortest response of any proof-of-retrievability scheme with private verifiability (but a longer query).
- Both schemes rely on homomorphic properties to aggregate a proof into one small authenticator value.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500093 (1).pdf`
- `downloads/53500093 (2).pdf`
- `downloads/53500093 (3).pdf`
- `downloads/53500093.pdf`
