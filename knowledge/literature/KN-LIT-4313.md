---
id: KN-LIT-4313
type: literature
title: "How to Watermark Cryptographic Functions"
authors:
  - "Ryo Nishimaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, pairing, point-decomposition, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a scheme for watermarking cryptographic functions. Informally speaking, a digital watermarking scheme for cryptographic functions embeds information, called a mark, into functions such as (trapdoor) one-way functions and decryption functions of public-key encryption.

## Key claims (as reported)
- It is required that a mark-embedded function is functionally equivalent to the original function and it is difficult for adversaries to remove the embedded mark without damaging the function.
- In spite of its importance and usefulness, there have only been a few theoretical studies on watermarking for functions (or program), and we do not have rigorous and meaningful definitions of watermarking for cryptographic functions and concrete constructions.
- To solve the above problem, we introduce a notion of watermarking for cryptographic functions and define its security.
- We present a lossy trapdoor function (LTF) based on the decisional linear (DLIN) problem and a watermarking scheme for the LTF.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810105 (1).pdf`
- `downloads/78810105 (2).pdf`
- `downloads/78810105 (3).pdf`
- `downloads/78810105.pdf`
