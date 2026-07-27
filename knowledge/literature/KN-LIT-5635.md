---
id: KN-LIT-5635
type: literature
title: "Onion ORAM: A Constant Bandwidth Blowup"
authors:
  - "Oblivious RAM"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present Onion ORAM, an Oblivious RAM (ORAM) with constant worst-case bandwidth blowup that leverages poly-logarithmic server computation to circumvent the logarithmic lower bound on ORAM bandwidth blowup. Our construction does not require fully homomorphic encryption, but employs an additively homomorphic encryption scheme such as the Damgård-Jurik cryptosystem, or alternatively a BGV-style somewhat homomorphic encryption scheme without bootstrapping.

## Key claims (as reported)
- At the core of our construction is an ORAM scheme that has “shallow circuit depth” over the entire history of ORAM accesses.
- We also propose novel techniques to achieve security against a malicious server, without resorting to expensive and non-standard techniques such as SNARKs.
- To the best of our knowledge, Onion ORAM is the first concrete instantiation of a constant bandwidth blowup ORAM under standard assumptions (even for the semi-honest setting).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620747 (1).pdf`
- `downloads/95620747.pdf`
