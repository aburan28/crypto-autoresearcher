---
id: KN-LIT-2692
type: literature
title: "Beyond quadratic speedups in quantum attacks on symmetric schemes"
authors:
  - "Xavier Bonnetain"
  - "André Schrottenloher"
  - "Ferdinand Sibleyras"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, pqc, provable-security, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we report the first quantum key-recovery attack on a symmetric block cipher design, using classical queries only, with a more than quadratic time speedup compared to the best classical attack. We study the 2XOR-Cascade construction of Gaži and Tessaro (EUROCRYPT 2012).

## Key claims (as reported)
- It is a key length extension technique which provides an n-bit block cipher with 5n bits of security out of an n-bit block cipher 2 with 2n bits of key, with a security proof in the ideal model.
- We show that the offline-Simon algorithm of Bonnetain et al.
- (ASIACRYPT 2019) can be extended to, in particular, attack this construction in quantum time e O(2n ), providing a 2.5 quantum speedup over the best classical attack.
- Regarding post-quantum security of symmetric ciphers, it is commonly assumed that doubling the key sizes is a sufficient precaution.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760030 (1).pdf`
- `downloads/132760030.pdf`
