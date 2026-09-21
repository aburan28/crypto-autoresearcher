---
id: KN-LIT-5495
type: literature
title: "On the Impossibility of Constructing Efficient"
authors:
  - "Key Encapsulation"
  - "Programmable Hash"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we discuss the (im)possibility of constructing chosen ciphertext secure (CCA secure) key encapsulation mechanisms (KEMs) with low ciphertext overhead. More specifically, we rule out the existence of algebraic black-box reductions from the (bounded) CCA security of a natural class of KEMs to any non-interactive problem.

## Key claims (as reported)
- The class of KEMs captures the structure of the currently most efficient KEMs defined in standard prime order groups, but restricts an encapsulation to consist of a single group element and a string.
- This result suggests that we cannot rely on existing techniques to construct a CCA secure KEM in standard prime order groups with a ciphertext overhead lower than two group elements.
- Furthermore, we show how the properties of an (algebraic) programmable hash function can be used to construct a simple, efficient and CCA secure KEM based on the hardness of the decisional Diffie-Hellman problem with a ciphertext overhead of just a single group element.
- Since this KEM construction is covered by the above mentioned impossibility result, this enables us to derive a lower bound on the hash key size of an algebraic programmable hash function, and rule out the existence of algebraic (poly, n)-programmable hash functions in prime order groups for any integer n.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170807 (1).pdf`
- `downloads/74170807 (2).pdf`
- `downloads/74170807 (3).pdf`
- `downloads/74170807.pdf`
