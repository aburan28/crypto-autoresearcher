---
id: KN-LIT-2654
type: literature
title: "Banquet: Short and Fast Signatures from AES"
authors:
  - "Emmanuela Orsini"
  - "Peter Scholl"
  - "Greg Zaverucha"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdsa, finite-field, hash, isogeny, lattice, mpc, pairing, pqc, quantum, rsa, signature, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work introduces Banquet, a digital signature scheme with post-quantum security, constructed using only symmetric-key primitives. The design is based on the MPC-in-head paradigm also used by Picnic (CCS 2017) and BBQ (SAC 2019).

## Key claims (as reported)
- Like BBQ, Banquet uses only standardized primitives, namely AES and SHA-3, but signatures are more than 50% shorter, making them competitive with Picnic (which uses a non-standard block cipher to improve performance).
- The MPC protocol in Banquet uses a new technique to verify correctness of the AES S-box computations, which is efficient because the cost is amortized with a batch verification strategy.
- Our implementation and benchmarks also show that both signing and verification can be done in under 10ms on a current x64 CPU.
- We also explore the parameter space to show the range of trade-offs that are possible with the Banquet design, and show that Banquet can nearly match the signature sizes possible with Picnic (albeit with slower, but still practical run times) or have speed within a factor of two of Picnic (at the cost of larger signatures).

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110235 (1).pdf`
- `downloads/127110235.pdf`
