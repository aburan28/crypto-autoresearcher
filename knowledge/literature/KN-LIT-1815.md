---
id: KN-LIT-1815
type: literature
title: "Profiling-Device-Free SASCA Framework for ML-KEM"
authors:
  - "Yuxuan Wang"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/981"
  doi: "10.1145/nnnnnnn.nnnnnnn"
  arxiv: null
  url: "https://eprint.iacr.org/2026/981"
tags: [cryptanalysis, lattice, pqc, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In side-channel analysis of ML-KEM (a NIST-standard PQC algorithm), SASCA is a powerful profiling attack. However, obtaining a profiling device strictly matching the target is challenging in practice.

## Key claims (as reported)
- To address this, we propose the first profiling-device-free SASCA framework for ML-KEM.
- The framework first controls the NTT input by choosing ciphertexts and trains a leakage model.
- Subsequently, leveraging the similarity between NTT and INTT, it uses adversarial unsupervised domain adaptation to fine-tune the model for INTT and recover its secret input.
- Validated on real embedded devices, the framework achieves effective key recovery using a comparable number of traces to profiling SASCA.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-981.pdf`
