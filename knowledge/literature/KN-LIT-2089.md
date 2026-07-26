---
id: KN-LIT-2089
type: literature
title: "A kilobit hidden SNFS discrete logarithm computation"
authors:
  - "Joshua Fried"
  - "Pierrick Gaudry"
  - "Nadia Heninger"
  - "Emmanuel Thomé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, factoring, finite-field, number-theory, prime-field, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We perform a special number field sieve discrete logarithm computation in a 1024-bit prime field. To our knowledge, this is the first kilobit-sized discrete logarithm computation ever reported for prime fields.

## Key claims (as reported)
- This computation took a little over two months of calendar time on an academic cluster using the open-source CADO-NFS software.
- Our chosen prime p looks random, and p−1 has a 160-bit prime factor, in line with recommended parameters for the Digital Signature Algorithm.
- However, our p has been trapdoored in such a way that the special number field sieve can be used to compute discrete logarithms in F∗p , yet detecting that p has this trapdoor seems out of reach.
- Twenty-five years ago, there was considerable controversy around the possibility of backdoored parameters for DSA.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210146 (1).pdf`
- `downloads/10210146.pdf`
