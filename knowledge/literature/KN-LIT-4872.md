---
id: KN-LIT-4872
type: literature
title: "McBits Revisited Tung Chou"
authors:
  - "Osaka Prefecture"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a constant-time fast implementation for a high-security code-based encryption system. The implementation is based on the “McBits” paper by Bernstein, Chou, and Schwabe in 2013: we use the same FFT algorithms for root finding and syndrome computation, similar algorithms for secret permutation, and bitslicing for low-level operations.

## Key claims (as reported)
- As opposed to McBits, where a high decryption throughput is achieved by running many decryption operations in parallel, we take a different approach to exploit the internal parallelism in one decryption operation for the use of more applications.
- As the result, we manage to achieve a slightly better decryption throughput at a much higher security level than McBits.
- As a minor contribution, we also present a constant-time implementation for encryption and key-pair generation, with similar techniques used for decryption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529147 (1).pdf`
- `downloads/10529147.pdf`
