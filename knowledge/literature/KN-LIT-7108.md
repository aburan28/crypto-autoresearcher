---
id: KN-LIT-7108
type: literature
title: "Threshold Decryption and Zero-Knowledge Proofs for Lattice-Based Cryptosystems"
authors:
  - "Rikke Bendlin"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, implementation, lattice, mov-fr, mpc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a variant of Regev’s cryptosystem first presented in [Reg05], but with a new choice of parameters. By a recent classical reduction by Peikert we prove the scheme semantically secure based on the worst-case lattice problem GapSVP.

## Key claims (as reported)
- From this we construct a threshold cryptosystem which has a very efficient and non-interactive decryption protocol.
- We prove the threshold cryptosystem secure against passive adversaries corrupting all but one of the players, and againts active adversaries corrupting less than one third of the players.
- We also describe how one can build a distributed key generation protocol.
- In the final part of the paper we show how one can, in zero-knowledge - prove knowledge of the plaintext contained in a given ciphertext from Regev’s original cryptosystem or our variant.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59780198 (1).pdf`
- `downloads/59780198 (2).pdf`
- `downloads/59780198 (3).pdf`
- `downloads/59780198.pdf`
