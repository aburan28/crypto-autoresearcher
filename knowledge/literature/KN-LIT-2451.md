---
id: KN-LIT-2451
type: literature
title: "An Algebraic Attack on Ciphers with Low-Degree Round Functions: Application to Full MiMC Maria Eichlseder1( )"
authors:
  - "Morten Øygarden( )"
  - "Christian Rechberger( )"
  - "Markus Schofnegger( )"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mpc, prime-field, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Algebraically simple PRFs, ciphers, or cryptographic hash functions are becoming increasingly popular, for example due to their attractive properties for MPC and new proof systems (SNARKs, STARKs, among many others). In this paper, we focus on the algebraically simple construction MiMC, which became an attractive cryptanalytic target due to its simplicity, but also due to its use as a baseline in a competition for more recent algorithms exploring this design space.

## Key claims (as reported)
- For the first time, we are able to describe key-recovery attacks on all full-round versions of MiMC over F2n , requiring half the code book.
- In the chosen-ciphertext scenario, recovering the key from this data for the n-bit full version of MiMC takes the equivalent of less than 2n−log2 (n)+1 calls to MiMC and negligible amounts of memory.
- The attack procedure is a generalization of higher-order differential cryptanalysis, and it is based on two main ingredients.
- First, we present a higher-order distinguisher which exploits the fact that the algebraic degree of MiMC grows significantly slower than originally believed.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491240 (1).pdf`
- `downloads/12491240.pdf`
