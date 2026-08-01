---
id: KN-LIT-460
type: literature
title: "Constraining Pseudorandom Functions Privately"
authors:
  - "Dan Boneh"
  - "Kevin Lewi"
  - "David J. Wu"
year: 2015
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2015/116"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2015/116"
tags: [lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a constrained pseudorandom function (PRF), the master secret key can be used to derive constrained keys, where each constrained key k is constrained with respect to some Boolean circuit C. A constrained key k can be used to evaluate the PRF on all inputs x for which C(x) = 1.

## Key claims (as reported)
- In almost all existing constrained PRF constructions, the constrained key k reveals its constraint C.
- In this paper we introduce the concept of private constrained PRFs, which are constrained PRFs with the additional property that a constrained key does not reveal its constraint.
- Our main notion of privacy captures the intuition that an adversary, given a constrained key k for one of two circuits C0 and C1 , is unable to tell which circuit is associated with the key k.
- We show that constrained PRFs have natural applications to searchable symmetric encryption, cryptographic watermarking, and much more.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101750469 (1).pdf`
- `downloads/101750469 (2).pdf`
- `downloads/101750469 (3).pdf`
- `downloads/101750469 (4).pdf`
- `downloads/101750469.pdf`
