---
id: KN-LIT-1659
type: literature
title: "Finite-Field Arithmetic in CKKS"
authors:
  - "Tim Seuré"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1102"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1102"
tags: [binary-field, fhe, finite-field, implementation, lattice, pqc, provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a CKKS-based technique for evaluating arithmetic over finite fields Fpr with small characteristic p under homomorphic encryption. The core of our approach is a pair of complementary ciphertext representations.

## Key claims (as reported)
- In the so-called spectral encoding, ciphertext addition and multiplication realize addition and multiplication in the field Fpr .
- In another encoding, coefficient encoding, the same operations act as slotwise addition and multiplication in the slot algebra Frp .
- We show that one can switch homomorphically between these encodings at cost linear in r, and that Fp -linear maps, such as taking p-th powers in Fpr , can be folded into these switches or applied directly in either representation.
- We complement the construction with theoretical and practical correctness-management techniques.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1102.pdf`
