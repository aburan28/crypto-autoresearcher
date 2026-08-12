---
id: KN-LIT-5108
type: literature
title: "New Cryptographic Primitives Based on Multiword T-functions"
authors:
  - "Alexander Klimov"
  - "Adi Shamir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mov-fr, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A T-function is a mapping from n-bit words to n-bit words in which for each 0 ≤ i < n bit i of the output can depend only on bits 0, 1, . . . , i of the input. All the boolean operations and most of the numeric operations in modern processors are T-functions, and their compositions are also T-functions.

## Key claims (as reported)
- In earlier papers we considered ‘crazy’ T-functions such as f (x) = x + (x2 ∨ 5), proved that they are invertible mappings which contain all the 2n possible states on a single cycle for any word size n, and proposed to use them as primitive building blocks in a new class of software-oriented cryptographic schemes.
- The main practical drawback of this approach is that most processors have either 32 or 64 bit words, and thus even a maximal length cycle (of size 232 or 264 ) may be too short.
- In this paper we develop new ways to construct invertible T-functions on multiword states whose iteration is guaranteed to yield a single cycle of arbitrary length (say, 2256 ).
- Such mappings can lead to stream ciphers whose software implementation on a standard Pentium 4 processor can encrypt more than 5 gigabits of data per second, which is an order of magnitude faster than previous designs such as RC4.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170001 (1).pdf`
- `downloads/30170001 (2).pdf`
- `downloads/30170001.pdf`
