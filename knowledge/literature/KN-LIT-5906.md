---
id: KN-LIT-5906
type: literature
title: "Privacy-Preserving Pattern Matching on Encrypted Data"
authors:
  - "Anis Bkakria"
  - "Nora Cuppens"
  - "Frédéric Cuppens"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pattern matching is one of the most fundamental and important paradigms in several application domains such as digital forensics, cyber threat intelligence, or genomic and medical data analysis. While it is a straightforward operation when performed on plaintext data, it becomes a challenging task when the privacy of both the analyzed data and the analysis patterns must be preserved.

## Key claims (as reported)
- In this paper, we propose new provably correct, secure, and relatively efficient (compared to similar existing schemes) public and private key based constructions that allow arbitrary pattern matching over encrypted data while protecting both the data to be analyzed and the patterns to be matched.
- That is, except the pattern provider (resp. the data owner), all other involved parties in the proposed constructions will learn nothing about the patterns to be searched (resp. the data to be inspected).
- Compared to existing solutions, the constructions we propose has some interesting properties: (1) the size of the ciphertext is linear to the size of plaintext and independent of the sizes and the number of the analysis patterns; (2) the sizes of the issued trapdoors are constant on the size of the data to be analyzed; and (3) the search complexity is linear on the size of the data to be inspected and is constant on the sizes of the analysis patterns.
- The conducted evaluations show that our constructions drastically improve the performance of the most efficient state of the art solution.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491153 (1).pdf`
- `downloads/12491153.pdf`
