---
id: KN-LIT-6442
type: literature
title: "Secure Linear Algebra Using Linearly Recurrent Sequences"
authors:
  - "Eike Kiltz"
  - "Payman Mohassel"
  - "Enav Weinreb"
  - "Matthew Franklin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we present secure two-party protocols for various core problems in linear algebra. Our main result is a protocol to obliviously decide singularity of an encrypted matrix: Bob holds an n × n matrix, encrypted with Alice’s secret key, and wants to learn whether or not the matrix is singular (while leaking nothing further).

## Key claims (as reported)
- We give an interactive protocol between Alice and Bob that solves the above problem in O(log n) communication rounds and with overall communication complexity of roughly O(n2 ) (note that the input size is n2 ).
- Our techniques exploit certain nice mathematical properties of linearly recurrent sequences and their relation to the minimal and characteristic polynomial of the input matrix, following [Wiedemann, 1986].
- With our new techniques we are able to improve the round complexity of the communication efficient solution of [Nissim and Weinreb, 2006] from O(n0.275 ) to O(log n).
- At the core of our results we use a protocol that securely computes the minimal polynomial of an encrypted matrix.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/43920291 (1).pdf`
- `downloads/43920291 (2).pdf`
- `downloads/43920291 (3).pdf`
- `downloads/43920291.pdf`
