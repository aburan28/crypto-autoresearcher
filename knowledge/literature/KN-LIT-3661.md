---
id: KN-LIT-3661
type: literature
title: "EKE Meets Tight Security in the Universally Composable Framework"
authors:
  - "Xiangyu Liu"
  - "Shengli Liu"
  - "Shuai Han"
  - "Dawu Gu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
(Asymmetric) Password-based Authenticated Key Exchange ((a)PAKE) protocols allow two parties establish a session key with a preshared low-entropy password. In this paper, we show how Encrypted Key Exchange (EKE) compiler [Bellovin and Merritt, S&P 1992] meets tight security in the Universally Composable (UC) framework.

## Key claims (as reported)
- We propose a strong 2DH variant of EKE, denoted by 2DH-EKE, and prove its tight security in the UC framework based on the CDH assumption.
- The efficiency of 2DH-EKE is comparable to the original EKE, with only O(λ) bits growth in communication (λ the security parameter), and two (resp., one) extra exponentiation in computation for client (resp., server).
- We also develop an asymmetric PAKE scheme 2DH-aEKE from 2DH-EKE.
- The security reduction loss of 2DH-aEKE is N , the total number of client-server pairs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940168 (1).pdf`
- `downloads/13940168.pdf`
