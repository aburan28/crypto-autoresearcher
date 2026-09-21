---
id: KN-LIT-6867
type: literature
title: "Subspace LWE"
authors:
  - "Krzysztof Pietrzak"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The (decisional) learning with errors problem (LWE) asks to distinguish “noisy” inner products of a secret vector with random vectors from uniform. The learning parities with noise problem (LPN) is the special case where the elements of the vectors are bits.

## Key claims (as reported)
- In recent years, the LWE and LPN problems have found many applications in cryptography.
- In this paper we introduce a (seemingly) much stronger adaptive assumption, called “subspace LWE” (SLWE), where the adversary can learn the inner product of the secret and random vectors after they were projected into an adaptively and adversarially chosen subspace.
- We prove that, surprisingly, the SLWE problem mapping into subspaces of dimension d is almost as hard as LWE using secrets of length d (the other direction is trivial.) This result immediately implies that several existing cryptosystems whose security is based on the hardness of the LWE/LPN problems are provably secure in a much stronger sense than anticipated.
- As an illustrative example we show that the standard way of using LPN for symmetric CPA secure encryption is even secure against a very powerful class of related key attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940166 (1).pdf`
- `downloads/71940166 (2).pdf`
- `downloads/71940166 (3).pdf`
- `downloads/71940166.pdf`
