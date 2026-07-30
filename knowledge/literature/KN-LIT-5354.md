---
id: KN-LIT-5354
type: literature
title: "On Homomorphic Secret Sharing from Polynomial-Modulus LWE"
authors:
  - "Thomas Attema"
  - "Pedro Capitão"
  - "Lisa Kohl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Homomorphic secret sharing (HSS) is a form of secret sharing that supports the local evaluation of functions on the shares, with applications to multi-server private information retrieval, secure computation, and more. Insisting on additive reconstruction, all known instantiations of HSS from “Learning with Error (LWE)”-type assumptions either have to rely on LWE with superpolynomial modulus, come with non-negligible error probability, and/or have to perform expensive ciphertext multiplications, resulting in bad concrete efficiency.

## Key claims (as reported)
- In this work, we present a new 2-party local share conversion procedure, which allows to locally convert noise encoded shares to non-noise plaintext shares such that the parties can detect whenever a (potential) error occurs and in that case resort to an alternative conversion procedure.
- Building on this technique, we present the first HSS for branching programs from (Ring-)LWE with polynomial input share size which can make use of the efficient multiplication procedure of Boyle et al.
- (Eurocrypt 2019) and has no correctness error.
- Our construction comes at the cost of a – on expectation – slightly increased output share size (which is insignificant compared to the input share size) and a more involved reconstruction procedure.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940177 (1).pdf`
- `downloads/13940177.pdf`
