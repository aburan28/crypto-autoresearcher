---
id: KN-LIT-3487
type: literature
title: "DualMS: Efficient Lattice-Based Two-Round Multi-Signature with Trapdoor-Free Simulation"
authors:
  - "Yanbo Chen⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pqc, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A multi-signature scheme allows multiple signers to jointly sign a common message. In recent years, two lattice-based two-round multi-signature schemes based on Dilithium-G were proposed: DOTT by Damgård, Orlandi, Takahashi, and Tibouchi (PKC’21) and MuSig-L by Boschini, Takahashi, and Tibouchi (Crypto’22).

## Key claims (as reported)
- In this work, we propose a new lattice-based two-round multi-signature scheme called DualMS.
- Compared to DOTT, DualMS is likely to significantly reduce signature size, since it replaces an opening to a homomorphic trapdoor commitment with a Dilithium-G response in the signature.
- Compared to MuSig-L, concrete parameters show that DualMS has smaller public keys, signatures, and lower communication, while the first round cannot be preprocessed offline as in MuSig-L.
- The main reason behind such improvements is a trapdoor-free “dual signing simulation” of our scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850494 (1).pdf`
- `downloads/140850494.pdf`
