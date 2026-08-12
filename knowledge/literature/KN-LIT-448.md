---
id: KN-LIT-448
type: literature
title: "Two-sources Randomness Extractors for Elliptic Curves"
authors:
  - "Abdoul Aziz Ciss"
year: 2014
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1404.2226"
  url: "https://arxiv.org/abs/1404.2226"
tags: [binary-field, elliptic-curve, finite-field, hash, prime-field, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper studies the task of two-sources randomness extractors for elliptic curves defined over a finite field K, where K can be a prime or a binary field. In fact, we introduce new constructions of functions over elliptic curves which take in input two random points from two different subgroups.

## Key claims (as reported)
- In other words, for a given elliptic curve E defined over a finite field Fq and two random points P ∈ P and Q ∈ Q, where P and Q are two subgroups of E(Fq ), our function extracts the least significant bits of the abscissa of the point P ⊕ Q when q is a large prime, and the k-first Fp coefficients of the abscissa of the point P ⊕ Q when q = pn , where p is a prime greater than 5.
- We show that the extracted bits are close to uniform.
- Our construction extends some interesting randomness extractors for elliptic curves, namely those defined in [7] and [9,10], when P = Q.
- The proposed constructions can be used in any cryptographic schemes which require extraction of random bits from two sources over elliptic curves, namely in key exchange protocol , design of strong pseudo-random number generators, etc.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1404.2226v2.pdf`
