---
id: KN-LIT-1843
type: literature
title: "Reassessing the Security of LPN-C and its HHE-Oriented Variants"
authors:
  - "Orr Dunkelman"
  - "Semira Einsele"
  - "Hans Heum"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1130"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1130"
tags: [binary-field, cryptanalysis, fhe, pqc, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The idea of Hybrid Homomorphic Encryption (HHE) is to reduce the computational cost of Fully Homomorphic Encryption (FHE) by encrypting bulk data symmetrically while only encrypting the short symmetric key homomorphically. Its efficiency depends on the multiplicative depth of the symmetric cipher’s decryption circuit, motivating FHE-friendly designs.

## Key claims (as reported)
- The Learning Parity with Noise (LPN) problem is a natural candidate for such designs, as it gives rise to simple encryption and decryption circuits over binary fields.
- In this context, Fouque, Hadjibeyli, and Kirchner proposed LPN-based symmetric encryption schemes based on the LPN-C cryptosystem of Gilbert et al.
- LPN-C is attractive for HHE while allowing parameter choices that bound decryption failures.
- However, the concrete security of LPN-C and its HHE-oriented variants remains poorly understood.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1130.pdf`
