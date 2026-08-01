---
id: KN-LIT-2226
type: literature
title: "A Side-Channel Assisted Cryptanalytic Attack Against QcBits"
authors:
  - "Rambus Cryptography Research"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, factoring, hash, implementation, lattice, pairing, pqc, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
QcBits is a code-based public key algorithm based on a problem thought to be resistant to quantum computer attacks. It is a constanttime implementation for a quasi-cyclic moderate density parity check (QC-MDPC) Niederreiter encryption scheme, and has excellent performance and small key sizes.

## Key claims (as reported)
- In this paper, we present a key recovery attack against QcBits.
- We first used differential power analysis (DPA) against the syndrome computation of the decoding algorithm to recover partial information about one half of the private key.
- We then used the recovered information to set up a system of noisy binary linear equations.
- Solving this system of equations gave us the entire key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529133 (1).pdf`
- `downloads/10529133.pdf`
