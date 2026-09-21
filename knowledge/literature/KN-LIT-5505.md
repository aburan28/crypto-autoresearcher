---
id: KN-LIT-5505
type: literature
title: "On the Indifferentiability of Key-Alternating Ciphers"
authors:
  - "Elena Andreeva"
  - "Andrey Bogdanov"
  - "Yevgeniy Dodis"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Advanced Encryption Standard (AES) is the most widely used block cipher. The high level structure of AES can be viewed as a (10-round) key-alternating cipher, where a t-round key-alternating cipher KAt consists of a small number t of fixed permutations Pi on n bits, separated by key addition: KAt (K, m) = kt ⊕ Pt (. . . k2 ⊕ P2 (k1 ⊕ P1 (k0 ⊕ m)) . . . ), where (k0 , . . . , kt ) are obtained from the master key K using some key derivation function.

## Key claims (as reported)
- For t = 1, KA1 collapses to the well-known Even-Mansour cipher, which is known to be indistinguishable from a (secret) random permutation, if P1 is modeled as a (public) random permutation.
- In this work we seek for stronger security of key-alternating ciphers — indifferentiability from an ideal cipher — and ask the question under which conditions on the key derivation function and for how many rounds t is the key-alternating cipher KAt indifferentiable from the ideal cipher, assuming P1 , . . . , Pt are (public) random permutations?
- As our main result, we give an affirmative answer for t = 5, showing that the 5-round key-alternating cipher KA5 is indifferentiable from an ideal cipher, assuming P1 , . . . , P5 are five independent random permutations, and the key derivation function sets all rounds keys ki = f (K), where 0 ≤ i ≤ 5 and f is modeled as a random oracle.
- Moreover, when |K| = |m|, we show we can set f (K) = P0 (K) ⊕ K, giving an n-bit block cipher with an n-bit key, making only six calls to n-bit permutations P0 , P1 , P2 , P3 , P4 , P5 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420131 (1).pdf`
- `downloads/80420131 (2).pdf`
- `downloads/80420131 (3).pdf`
- `downloads/80420131.pdf`
