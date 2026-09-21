---
id: KN-LIT-1295
type: literature
title: "Reducing Overdefined Systems of Polynomial Equations Derived from Small Scale Variants of the AES via Data Mining Methods"
authors:
  - "Jana Berušková"
  - "Martin Jureček"
  - "Olha Jurečková"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/809"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/809"
tags: [cryptanalysis, finite-field, prime-field, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper deals with reducing the secret key computation time of small scale variants of the AES cipher using algebraic cryptanalysis, which is accelerated by data mining methods. This work is based on the known plaintext attack and aims to speed up the calculation of the secret key by processing the polynomial equations extracted from plaintext-ciphertext pairs.

## Key claims (as reported)
- Specifically, we propose to transform the overdefined system of polynomial equations over GF(2) into a new system so that the computation of the Gröbner basis using the F4 algorithm takes less time than in the case of the original system.
- The main idea is to group similar polynomials into clusters, and for each cluster, sum the two most similar polynomials, resulting in simpler polynomials.
- We compare different data mining techniques for finding similar polynomials, such as clustering or locality-sensitive hashing (LSH).
- Experimental results show that using the LSH technique, we get a system of equations for which we can calculate the Gröbner basis the fastest compared to the other methods that we consider in this work.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-809.pdf`
