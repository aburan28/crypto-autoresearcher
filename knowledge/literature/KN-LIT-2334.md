---
id: KN-LIT-2334
type: literature
title: "Adaptive Security with Quasi-Optimal Rate"
authors:
  - "Brett Hemenway"
  - "Rafail Ostrovsky"
  - "Silas Richelson"
  - "Alon Rosen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A multiparty computation protocol is said to be adaptively secure if it retains its security in the presence of an adversary who can adaptively corrupt participants as the protocol proceeds. This is in contrast to a static corruption model where the adversary is forced to choose which participants to corrupt before the protocol begins.

## Key claims (as reported)
- A central tool for constructing adaptively secure protocols is non-committing encryption (Canetti, Feige, Goldreich and Naor, STOC ’96).
- The original protocol of Canetti et al. had ciphertext expansion O(k2 ) where k is the security parameter, and prior to this work, the best known constructions had ciphertext expansion that was either O(k) under general assumptions, or alternatively O(log(n)), where n is the length of the message, based on a specific factoring-based hardness assumption.
- In this work, we build a new non-committing encryption scheme from lattice problems, and specifically based on the hardness of (Ring) Learning With Errors (LWE).
- Our scheme achieves ciphertext expansion as small as polylog(k).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620514 (1).pdf`
- `downloads/95620514.pdf`
