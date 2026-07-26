---
id: KN-LIT-1514
type: literature
title: "A Complexity-Theoretic Approach to Proofs of Space"
authors:
  - "Marshall Ball∗"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1470"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1470"
tags: [complexity-theory, hash, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Proof of Space, PoS, as introduced by Dziembowski et al. [CRYPTO’15], is a two-phase protocol that enables a Prover to convince an efficient Verifier that it has allocated a large amount of persistent memory to storing some information.

## Key claims (as reported)
- To our knowledge, all existing PoS protocols are only known to be secure in the random oracle model (or under ad hoc assumptions about cryptographic assumptions).
- We provide an elementary framework for constructing PoS from a combination of derandomization assumptions and cryptographic assumptions.
- We provide a few simple instantiations of the framework.
- We show that non-trivial PoS follow from (a) E = DTIME[2O(n) ] is hard for exponential-size nondeterministic circuits (an assumption introduced to show AM = NP), and (b) collision-resistant hash functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1470.pdf`
