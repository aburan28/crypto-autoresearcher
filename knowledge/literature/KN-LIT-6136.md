---
id: KN-LIT-6136
type: literature
title: "Randomized Half-Ideal Cipher on Groups with applications to UC (a)PAKE"
authors:
  - "Bruno Freitas Dos Santos"
  - "Yanqi Gu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An Ideal Cipher (IC) is a cipher where each key defines a random permutation on the domain. Ideal Cipher on a group has many attractive applications, e.g., the Encrypted Key Exchange (EKE) protocol for Password Authenticated Key Exchange (PAKE) [8], or asymmetric PAKE (aPAKE) [33, 31].

## Key claims (as reported)
- However, known constructions for IC on a group domain all have drawbacks, including key leakage from timing information [12], requiring 4 hash-onto-group operations if IC is an 8-round Feistel [22], and limiting the domain to half the group [9] or using variable-time encoding [47, 39] if IC is implemented via (quasi-) bijections from groups to bitstrings [33].
- We propose an IC relaxation called a (Randomized) Half-Ideal Cipher (HIC), and we show that HIC on a group can be realized by a modified 2-round Feistel (m2F), at a cost of 1 hash-onto-group operation, which beats existing IC constructions in versatility and computational cost.
- HIC weakens IC properties by letting part of the ciphertext be non-random, but we exemplify that it can be used as a drop-in replacement for IC by showing that EKE [8] and aPAKE of [33] realize respectively UC PAKE and UC aPAKE even if they use HIC instead of IC.
- The m2F construction can also serve as IC domain extension, because m2F constructs HIC on domain D from an RO-indifferentiable hash onto D and an IC on 2κ-bit strings, for κ a security parameter.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004316 (1).pdf`
- `downloads/14004316.pdf`
