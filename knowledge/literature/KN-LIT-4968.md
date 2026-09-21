---
id: KN-LIT-4968
type: literature
title: "MPSign: A Signature from"
authors:
  - "Damien Stehlé"
  - "Ron Steinfeld"
  - "Zhenfei Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, lattice, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a digital signature scheme MPSign, whose security relies on the conjectured hardness of the Polynomial Learning With Errors problem (PLWE) for at least one defining polynomial within an exponential-size family (as a function of the security parameter). The proposed signature scheme follows the Fiat-Shamir framework and can be viewed as the Learning With Errors counterpart of the signature scheme described by Lyubashevsky at Asiacrypt 2016, whose security relies on the conjectured hardness of the Polynomial Short Integer Solution (PSIS) problem for at least one defining polynomial within an exponential-size family.

## Key claims (as reported)
- As opposed to the latter, MPSign enjoys a security proof from PLWE that is tight in the quantum-access random oracle model.
- The main ingredient is a reduction from PLWE for an arbitrary defining polynomial among exponentially many, to a variant of the MiddleProduct Learning with Errors problem (MPLWE) that allows for secrets that are small compared to the working modulus.
- We present concrete parameters for MPSign using such small secrets, and show that they lead to significant savings in signature length over Lyubashevsky’s Asiacrypt 2016 scheme (which uses larger secrets) at typical security levels.
- As an additional small contribution, and in contrast to MPSign (or MPLWE), we present an efficient key-recovery attack against Lyubashevsky’s scheme (or the inhomogeneous PSIS problem), when it is used with sufficiently small secrets, showing the necessity of a lower bound on secret size for the security of that scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110263 (1).pdf`
- `downloads/12110263.pdf`
