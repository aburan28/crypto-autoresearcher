---
id: KN-LIT-3914
type: literature
title: "Floating-Point LLL Revisited"
authors:
  - "Phong Q. Nguy ̃ên"
  - "Damien Stehlé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Lenstra-Lenstra-Lovász lattice basis reduction algorithm (LLL or L3 ) is a very popular tool in public-key cryptanalysis and in many other fields. Given an integer d-dimensional lattice basis with vectors of norm less than B in an n-dimensional space, L3 outputs a socalled L3 -reduced basis in polynomial time O(d5 n log3 B), using arithmetic operations on integers of bit-length O(d log B).

## Key claims (as reported)
- This worst-case complexity is problematic for lattices arising in cryptanalysis where d or/and log B are often large.
- As a result, the original L3 is almost never used in practice.
- Instead, one applies floating-point variants of L3 , where the long-integer arithmetic required by Gram-Schmidt orthogonalisation (central in L3 ) is replaced by floating-point arithmetic.
- Unfortunately, this is known to be unstable in the worst-case: the usual floating-point L3 is not even guaranteed to terminate, and the output basis may not be L3 -reduced at all.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/34940217 (1).pdf`
- `downloads/34940217 (2).pdf`
- `downloads/34940217 (3).pdf`
- `downloads/34940217.pdf`
