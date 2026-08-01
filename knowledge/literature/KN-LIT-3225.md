---
id: KN-LIT-3225
type: literature
title: "Cryptanalysis of Candidate Obfuscators for Affine Determinant Programs"
authors:
  - "Li Yao"
  - "Yilei Chen"
  - "Yu Yu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, fhe, lattice, mpc, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At ITCS 2020, Bartusek et al. proposed a candidate indistinguishability obfuscator (iO) for affine determinant programs (ADPs). The candidate is special since it directly applies specific randomization techniques to the underlying ADP, without relying on the hardness of traditional cryptographic assumptions like discrete-log or learning with errors.

## Key claims (as reported)
- It is relatively efficient compared to the rest of the iO candidates.
- However, the obfuscation scheme requires further cryptanalysis since it was not known to be based on any well-formed mathematical assumptions.
- In this paper, we show cryptanalytic attacks on the iO candidate provided by Bartusek et al.
- Our attack exploits the weakness of one of the randomization steps in the candidate.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760166 (1).pdf`
- `downloads/132760166.pdf`
