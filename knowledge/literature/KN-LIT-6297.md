---
id: KN-LIT-6297
type: literature
title: "Robust Property-Preserving Hash Functions for Hamming Distance and More"
authors:
  - "Nils Fleischhacker"
  - "Mark Simkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, hash, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Robust property-preserving hash (PPH) functions, recently introduced by Boyle, Lavigne, and Vaikuntanathan [ITCS 2019], compress large inputs x and y into short digests h(x) and h(y) in a manner that allows for computing a predicate P on x and y while only having access to the corresponding hash values. In contrast to locality-sensitive hash functions, a robust PPH function guarantees to correctly evaluate a predicate on h(x) and h(y) even if x and y are chosen adversarially after seeing h.

## Key claims (as reported)
- Our main result is a robust PPH function for the exact hamming distance predicate ( 1 if d(x, y) ≥ t t HAM (x, y) = 0 Otherwise where d(x, y) is the hamming-distance between x and y.
- Our PPH function compresses n-bit strings into O(tλ)-bit digests, where λ is the security parameter.
- The construction is based on the q-strong bilinear discrete logarithm assumption.
- Along the way, we construct a robust PPH function for the set intersection predicate ( 1 if |X ∩ Y | > n − t t INT (X, Y ) = 0 Otherwise which compresses sets X and Y of size n with elements from some arbitrary universe U into O(tλ)-bit long digests.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960293 (1).pdf`
- `downloads/126960293.pdf`
