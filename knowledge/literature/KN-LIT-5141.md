---
id: KN-LIT-5141
type: literature
title: "New Realizations of Somewhere Statistically"
authors:
  - "Binding Hashing"
  - "Positional Accumulators"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A somewhere statistically binding (SSB) hash, introduced by Hubáček and Wichs (ITCS ’15), can be used to hash a long string x to a short digest y = Hhk (x) using a public hashing-key hk. Furthermore, there is a way to set up the hash key hk to make it statistically binding on some arbitrary hidden position i, meaning that: (1) the digest y completely determines the i’th bit (or symbol) of x so that all pre-images of y have the same value in the i’th position, (2) it is computationally infeasible to distinguish the position i on which hk is statistically binding from any other position i0 .

## Key claims (as reported)
- Lastly, the hash should have a local opening property analogous to Merkle-Tree hashing, meaning that given x and y = Hhk (x) it should be possible to create a short proof π that certifies the value of the i’th bit (or symbol) of x without having to provide the entire input x.
- A similar primitive called a positional accumulator, introduced by Koppula, Lewko and Waters (STOC ’15) further supports dynamic updates of the hashed value.
- These tools, which are interesting in their own right, also serve as one of the main technical components in several recent works building advanced applications from indistinguishability obfuscation (iO).
- The prior constructions of SSB hashing and positional accumulators required fully homomorphic encryption (FHE) and iO respectively.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520314 (1).pdf`
- `downloads/94520314.pdf`
