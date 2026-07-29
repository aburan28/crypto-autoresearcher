---
id: KN-LIT-4597
type: literature
title: "Key-Recovery Attack on the ASASA Cryptosystem With Expanding S-Boxes"
authors:
  - "Henri Gilbert"
  - "Jérôme Plût"
  - "Joana Treger"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, groebner, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a cryptanalysis of the ASASA public key cipher introduced at Asiacrypt 2014 [3]. This scheme alternates three layers of affine transformations A with two layers of quadratic substitutions S.

## Key claims (as reported)
- We show that the partial derivatives of the public key polynomials contain information about the intermediate layer.
- This enables us to present a very simple distinguisher between an ASASA public key and random polynomials.
- We then expand upon the ideas of the distinguisher to achieve a full secret key recovery.
- This method uses only linear algebra and has a complexity dominated by the cost of computing the kernels of 226 small matrices with entries in F16 .

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160238 (1).pdf`
- `downloads/92160238 (2).pdf`
- `downloads/92160238.pdf`
