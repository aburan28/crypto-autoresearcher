---
id: KN-LIT-1925
type: literature
title: "Threshold Signatures in the Head"
authors:
  - "Thibauld Feneuil"
  - "Matthieu Rivain"
  - "Damien Vergnaud"
  - "Auguste Warmé-Janville"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1125"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1125"
tags: [dlp, hash, isogeny, lattice, mpc, pairing, pqc, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold cryptography distributes trust among multiple parties by enabling joint cryptographic operations without reconstructing secret keys. While post-quantum signature schemes based on the MPC-in-the-Head (MPCitH) paradigm are highly generic, recent impossibility results show that their thresholdization either incurs prohibitive distributed symmetric computations or leads to signature sizes growing with the number of signers.

## Key claims (as reported)
- Achieving practical tradeoffs in this setting remains challenging.
- In this paper, we propose a generic framework for threshold MPCitH signatures based on Merkle-tree commitments.
- Our approach adapts the PIOP+PCS paradigm to the distributed setting by introducing and instantiating the notion of threshold polynomial commitment schemes (TPCS).
- We present a generic compiler combining a PIOP, a TPCS, and an arithmetic black box into a threshold signature scheme, and prove its unforgeability from the security of its components.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1125.pdf`
