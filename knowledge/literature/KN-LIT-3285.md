---
id: KN-LIT-3285
type: literature
title: "Cryptanalysis of Unbalanced RSA with Small CRT-Exponent"
authors:
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present lattice-based attacks on RSA with prime factors p and q of unbalanced size. In our scenario, the factor q is smaller than N β and the decryption exponent d is small modulo p − 1.

## Key claims (as reported)
- We introduce two approaches that both use a modular bivariate polynomial equation with a small root.
- Extracting this root is in both methods equivalent to the factorization of the modulus N = pq.
- Applying a method of Coppersmith, one can construct from a bivariate modular equation a bivariate polynomial f (x, y) over Z that has the same small root.
- In our first method, we prove that one can extract the desired root of f (x, y) in √ polynomial time.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420242 (1).pdf`
- `downloads/24420242 (2).pdf`
- `downloads/24420242.pdf`
