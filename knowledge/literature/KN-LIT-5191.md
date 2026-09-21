---
id: KN-LIT-5191
type: literature
title: "Non-Interactive Secure Computation of Inner-Product from LPN and LWE"
authors:
  - "Geoffroy Couteau"
  - "Maryam Zarezadeh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, pairing, pqc, protocol, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We put forth a new cryptographic primitive for securely computing inner-products in a scalable, non-interactive fashion: any party can broadcast a public (computationally hiding) encoding of its input, and store a secret state. Given their secret state and the other party’s public encoding, any pair of parties can non-interactively compute additive shares of the inner-product between the encoded vectors.

## Key claims (as reported)
- We give constructions of this primitive from a common template, which can be instantiated under either the LPN (with non-negligible correctness error) or the LWE (with negligible correctness error) assumptions.
- Our construction uses a novel twist on the standard non-interactive key exchange based on the Alekhnovich cryptosystem, which upgrades it to a non-interactive inner product protocol almost for free.
- In addition to being non-interactive, our constructions have linear communication (with constants smaller than all known alternatives) and small computation: using LPN or LWE with quasi-cyclic codes, we estimate that encoding a length-220 vector over a 32-bit field takes less that 2s on a standard laptop; decoding amounts to a single cheap inner-product.
- We show how to remove the non-negligible error in our LPN instantiation using a one-time, logarithmic-communication preprocessing.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910076 (1).pdf`
- `downloads/137910076.pdf`
