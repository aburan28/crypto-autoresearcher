---
id: KN-LIT-1855
type: literature
title: "Round-Optimal Subversion-Resilient UC PAKE from Malleable Trapdoor Smooth Projective Hash Functions"
authors:
  - "Behzad Abdolmaleki"
  - "Suvradip Chakraborty"
  - "Shahram Khazaei"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1047"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1047"
tags: [hash, mpc, protocol, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Password-Authenticated Key Exchange (PAKE) allows two parties to establish a common high-entropy secret from a possibly lowentropy pre-shared secret such as a password. In this paper, we revisit the question of constructing PAKE protocols with subversion resilience in the framework of universal composability (UC), where the latter roughly means that UC security still holds even if one of the two parties is malicious and the honest party’s code has been subverted (in an undetectable manner).

## Key claims (as reported)
- The latter goal was recently achieved by Chakraborty, Magliocco, Magri and Venturi (ASIACRYPT 2024), based on sanitation of oblivious transfer protocols and dual-mode cryptosystems via cryptographic reverse firewalls (Mironov and Stephens-Davidowitz, EUROCRYPT 2015).
- Our contributions are as follows: – We introduce so-called malleable trapdoor smooth projective hash functions (M-TSPHF), as an enhancement of trapdoor smooth projective hash functions (Benhamouda et al., CRYPTO 2013).
- Our extension incorporates new properties including key malleability and element rerandomizability. – We give a generic construction of subversion-resilient UC PAKE based on M-TSPHF and other standard cryptographic primitives.
- As we demonstrate, our PAKE protocol can be instantiated efficiently yielding an improved round and communication complexity with respect to the previous protocol of Chakraborty et al.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1047.pdf`
