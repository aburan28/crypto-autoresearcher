---
id: KN-LIT-7569
type: literature
title: On insecurity of cryptosystems based on generalized Reed-Solomon codes
authors: [Sidelnikov Vladimir M., Shestakov Sergey O.]
year: 1992
venue: Discrete Mathematics and Applications, 2(4):439-444
identifiers:
  eprint: null
  doi: 10.1515/dma.1992.2.4.439
  url: https://doi.org/10.1515/dma.1992.2.4.439
tags: [code-based, structural-attack, key-recovery, reed-solomon, niederreiter, cryptanalysis, foundational]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
A polynomial-time structural key-recovery attack against code-based
cryptosystems instantiated with generalized Reed-Solomon codes: the secret
support and multiplier vectors are recovered directly from the public matrix,
without ever solving a decoding instance. This breaks the GRS instantiation
suggested in KN-LIT-7565 while leaving the binary Goppa instantiation standing.

## Key claims (as reported)
- The unknown matrices defining the public key are recoverable in polynomial
  arithmetic cost in the code parameters.
- The break is structural: it exploits the algebraic transparency of GRS codes,
  not any weakness in the syndrome decoding problem.

## Relevance to this program
The canonical demonstration that code-based security has two independent legs
and that the algebraic one is the fragile one. Every subsequent structural
result in the corpus -- KN-LIT-5792 (Wild McEliece over quadratic extensions),
KN-LIT-2395 and KN-LIT-2383 (algebraic attacks on compact-key and special-Goppa
variants), KN-LIT-3281 (Sidelnikov's Reed-Muller system) -- repeats this shape
on a different code family. Recorded in KN-TECH-059. For this program the
transferable lesson is a screen, not a result: any proposal that buys efficiency
by adding algebraic structure to a hard-problem instance must be checked against
the possibility that the structure is itself the attack surface.

## Not verified here
Primary paper not fetched. Authors, title, venue, volume/issue/pages, year, and
DOI confirmed via search against the De Gruyter DOI record and Semantic Scholar.
The complexity statement is relayed from secondary summaries.
