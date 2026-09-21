---
id: KN-LIT-6574
type: literature
title: "Share conversion, pseudorandom secret-sharing and applications to secure distributed computing"
authors:
  - "Ronald Cramer"
  - "Ivan Damgård"
  - "Yuval Ishai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a method for converting shares of a secret into shares of the same secret in a different secret-sharing scheme using only local computation and no communication between players. In particular, shares in a replicated scheme based on a CNF representation of the access structure can be converted into shares from any linear scheme for the same structure.

## Key claims (as reported)
- We show how this can be combined with any pseudorandom function to create, from initially distributed randomness, any number of Shamir secret-sharings of (pseudo)random values without communication.
- We apply this technique to obtain efficient non-interactive protocols for secure computation of low-degree polynomials, which in turn give rise to other applications in secure computation and threshold cryptography.
- For instance, we can make the Cramer-Shoup threshold cryptosystem by Canetti and Goldwasser fully non-interactive, or construct noninteractive threshold signature schemes secure without random oracles.
- The latter solutions are practical only for a relatively small number of players.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_342 (1).pdf`
- `downloads/3378_342 (2).pdf`
- `downloads/3378_342 (3).pdf`
- `downloads/3378_342.pdf`
