---
id: KN-LIT-5808
type: literature
title: "Post-Quantum Security of Key Encapsulation Mechanism against CCA Attacks with a Single Decapsulation Query?"
authors:
  - "Haodong Jiang"
  - "Zhi Ma"
  - "Zhenfeng Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, pqc, protocol, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, in post-quantum cryptography migration, it has been shown that an IND-1-CCA-secure key encapsulation mechanism (KEM) is required for replacing an ephemeral Diffie-Hellman (DH) in widely-used protocols, e.g., TLS, Signal, and Noise. IND-1-CCA security is a notion similar to the traditional IND-CCA security except that the adversary is restricted to one single decapsulation query.

## Key claims (as reported)
- At EUROCRYPT 2022, based on CPA-secure public-key encryption (PKE), Huguenin-Dumittan and Vaudenay presented two IND-1-CCA KEM constructions called TCH and TH , which are much more efficient than the widely-used IND-CCA-secure Fujisaki-Okamoto (FO) KEMs.
- The security of TCH was proved in both random oracle model (ROM) and quantum random oracle model (QROM).
- However, the QROM proof of TCH relies on an additional ciphertext expansion.
- While, the security of TH was only proved in the ROM, and the QROM proof is left open.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438009 (1).pdf`
- `downloads/14438009.pdf`
