---
id: KN-LIT-6265
type: literature
title: "Revisiting the Constant-sum Winternitz One-time Signature with Applications to SPHINCS+ and XMSS"
authors:
  - "Kaiyi Zhang"
  - "Hongrui Cui"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, pairing, pqc, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Hash-based signatures offer a conservative alternative to postquantum signatures with arguably better-understood security than other post-quantum candidates. As a core building block of hash-based signatures, the efficiency of one-time signature (OTS) largely dominates that of hash-based signatures.

## Key claims (as reported)
- The WOTS+ signature scheme (Africacrypt 2013) is the current state-of-the-art OTS adopted by the signature schemes standardized by NIST—XMSS, LMS, and SPHINCS+ .
- A natural question is whether there is (and how much) room left for improving one-time signatures (and thus standard hash-based signatures).
- In this paper, we show that WOTS+ one-time signature, when adopting the constant-sum encoding scheme (Bos and Chaum, Crypto 1992), is size-optimal not only under Winternitz’s OTS framework, but also among all tree-based OTS designs.
- Moreover, we point out a flaw in the DAG-based OTS design previously shown to be size-optimal at Asiacrypt 1996, which makes the constant-sum WOTS+ the most size-efficient OTS to the best of our knowledge.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850262 (1).pdf`
- `downloads/140850262.pdf`
