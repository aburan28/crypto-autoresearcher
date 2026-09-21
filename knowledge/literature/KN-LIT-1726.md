---
id: KN-LIT-1726
type: literature
title: "Lynx: Symmetric Primitive for Shorter and Faster VOLE-in-the-Head Signatures"
authors:
  - "Lin Jiao"
  - "Hongsen Yang"
  - "Hongrui Cui"
  - "Yituo He"
  - "Yonglin Hao"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1099"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1099"
tags: [cryptanalysis, dlp, finite-field, pairing, pqc, quantum, rsa, signature, survey, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
VOLE-in-the-Head (VOLEitH) is one of the most promising frameworks to design post-quantum digital signatures based on symmetric primitives. However, all existing symmetric primitives do not capture the specialized characteristics of the VOLEitH framework and are not VOLEitH-friendly, leaving room for improving the efficiency of VOLEitH-based signatures.

## Key claims (as reported)
- In this paper, we propose a VOLEitHfriendly symmetric primitive called Lynx, which is optimal in terms of the number of required VOLE correlations that directly determines the efficiency of VOLEitH-based signature schemes.
- In particular, Lynx adopts a multi-branch structure featuring a new truncation function: (a) nonlinear components are customized to minimize the witness length and polynomial degree, as well as the number of finite-field multiplications; (b) linear layers are strategically interleaved to strengthen security.
- The security of Lynx is rigorously validated by covering all possible attacks in the presence of both classical and quantum adversaries.
- Built upon Lynx, we design a post-quantum signature scheme, Lynxer, in the VOLEitH framework, which is shorter and faster than all known post-quantum signature schemes from symmetric primitives.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1099.pdf`
