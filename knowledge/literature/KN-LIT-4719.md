---
id: KN-LIT-4719
type: literature
title: "Light-Weight Instruction Set Extensions for Bit-Sliced Cryptography"
authors:
  - "Philipp Grabher"
  - "Johann Großschädl"
  - "Dan Page"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, elliptic-curve, hash, implementation, pairing, prime-field, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bit-slicing is a non-conventional implementation technique for cryptographic software where an n-bit processor is considered as a collection of n 1-bit execution units operating in SIMD mode. Particularly when implementing symmetric ciphers, the bit-slicing approach has several advantages over more conventional alternatives: it often allows one to reduce memory footprint by eliminating large look-up tables, and it permits more predictable performance characteristics that can foil time based side-channel attacks.

## Key claims (as reported)
- Both features are attractive for mobile and embedded processors, but the performance overhead that results from bit-sliced implementation often represents a significant disadvantage.
- In this paper we describe a set of light-weight Instruction Set Extensions (ISEs) that can improve said performance while retaining all advantages of bit-sliced implementation.
- Contrary to other crypto-ISE, our design is generic and allows for a high degree of algorithm agility: we demonstrate applicability to several well-known cryptographic primitives including four block ciphers (DES, Serpent, AES, and PRESENT), a hash function (SHA-1), as well as multiplication of ternary polynomials.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540327 (1).pdf`
- `downloads/51540327 (2).pdf`
- `downloads/51540327 (3).pdf`
- `downloads/51540327.pdf`
