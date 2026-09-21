---
id: KN-LIT-4480
type: literature
title: "Indifferentiability of Truncated Random Permutations"
authors:
  - "Wonseok Choi"
  - "Byeonghak Lee"
  - "Jooyoung Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One of natural ways of constructing a pseudorandom function from a pseudorandom permutation is to simply truncate the output of the permutation. When n is the permutation size and m is the number of truncated bits, the resulting construction is known to be indistinguishn+m able from a random function up to 2 2 queries, which is tight.

## Key claims (as reported)
- In this paper, we study the indifferentiability of a truncated random permutation where a fixed prefix is prepended to the inputs.
- We prove that this construction is (regularly) indifferentiable from a public random n+m function up to min{2 3 , 2m , 2` } queries, while it is publicly indifferenn+m n tiable up to min{max{2 3 , 2 2 }, 2` } queries, where ` is the size of the fixed prefix.
- Furthermore, the regular indifferentiability bound is proved to be tight when m + ` n. m Our results significantly improve upon the previous bound of min{2 2 , 2` } given by Dodis et. al (FSE 2009), allowing us to construct, for instance, an n2 -to- n2 bit random function that makes a single call to an n-bit permutation, achieving n2 -bit security.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210144 (1).pdf`
- `downloads/119210144.pdf`
