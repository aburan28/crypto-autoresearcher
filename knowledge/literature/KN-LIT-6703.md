---
id: KN-LIT-6703
type: literature
title: "Sliding right into disaster: Left-to-right sliding windows leak"
authors:
  - "Daniel J. Bernstein"
  - "Joachim Breitner"
  - "Daniel Genkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, implementation, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It is well known that constant-time implementations of modular exponentiation cannot use sliding windows. However, software libraries such as Libgcrypt, used by GnuPG, continue to use sliding windows.

## Key claims (as reported)
- It is widely believed that, even if the complete pattern of squarings and multiplications is observed through a side-channel attack, the number of exponent bits leaked is not sufficient to carry out a full key-recovery attack against RSA.
- Specifically, 4-bit sliding windows leak only 40% of the bits, and 5-bit sliding windows leak only 33% of the bits.
- In this paper we demonstrate a complete break of RSA-1024 as implemented in Libgcrypt.
- Our attack makes essential use of the fact that Libgcrypt uses the left-to-right method for computing the sliding-window expansion.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529194 (1).pdf`
- `downloads/10529194.pdf`
- `downloads/slidingright-20170628.pdf`
