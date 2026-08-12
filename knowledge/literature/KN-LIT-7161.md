---
id: KN-LIT-7161
type: literature
title: "Time- and Space-Efficient Arguments from Groups of Unknown Order"
authors:
  - "Alexander R. Block"
  - "Justin Holmgren"
  - "Alon Rosen"
  - "Ron D. Rothblum"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, lattice, number-theory, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct public-coin time- and space-efficient zero-knowledge arguments for NP. For every time T and space S non-deterministic RAM computation, the prover runs in time T · polylog(T ) and space S · polylog(T ), and the verifier runs in time n · polylog(T ), where n is the input length.

## Key claims (as reported)
- Our protocol relies on hidden order groups, which can be instantiated with a trusted setup from the hardness of factoring (products of safe primes), or without a trusted setup using class groups.
- The argument-system can heuristically be made non-interactive using the Fiat-Shamir transform.
- Our proof builds on DARK (Bünz et al., Eurocrypt 2020), a recent succinct and efficiently verifiable polynomial commitment scheme.
- We show how to implement a variant of DARK in a time- and space-efficient way.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826416 (1).pdf`
- `downloads/12826416.pdf`
