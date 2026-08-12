---
id: KN-LIT-6145
type: literature
title: "Rate-1 Fully Local Somewhere Extractable Hashing from DDH"
authors:
  - "Pedro Branco"
  - "Nico Döttling"
  - "Akshayaram Srinivasan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, mpc, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Somewhere statistically binding (SSB) hashing allows us to sample a special hashing key such that the digest statistically binds the input at m secret locations. This hash function is said to be somewhere extractable (SE) if there is an additional trapdoor that allows the extraction of the input bits at the m locations from the digest.

## Key claims (as reported)
- Devadas, Goyal, Kalai, and Vaikuntanathan (FOCS 2022) introduced a variant of somewhere extractable hashing called rate-1 fully local SE hash functions.
- The rate-1 requirement states that the size of the digest is m + poly(λ) (where λ is the security parameter).
- The fully local property requires that for any index i, there is a “very short” opening showing that i-th bit of the hashed input is equal to b for some b ∈ {0, 1}.
- The size of this opening is required to be independent of m and in particular, this means that its size is independent of the size of the digest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602168 (1).pdf`
- `downloads/14602168.pdf`
