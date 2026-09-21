---
id: KN-LIT-2408
type: literature
title: "Algebraic Techniques for Short(er) Exact Lattice-Based Zero-Knowledge Proofs"
authors:
  - "Jonathan Bootle"
  - "Vadim Lyubashevsky"
  - "Gregor Seiler"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pqc, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A key component of many lattice-based protocols is a zeroknowledge proof of knowledge of a vector ~s with small coefficients satisfying A~s = ~ u mod q. While there exist fairly efficient proofs for a relaxed version of this equation which prove the knowledge of ~s0 and c satisfying A~s0 = ~ uc where k~s0 k k~sk and c is some small element in the ring over which the proof is performed, the proofs for the exact version of the equation are considerably less practical.

## Key claims (as reported)
- The best such proof technique is an adaptation of Stern’s protocol (Crypto ’93), for proving knowledge of nearby codewords, to larger moduli.
- The scheme is a Σ-protocol, each of whose iterations has soundness error 2/3, and thus requires over 200 repetitions to obtain soundness error of 2−128 , which is the main culprit behind the large size of the proofs produced.
- In this paper, we propose the first lattice-based proof system that significantly outperforms Stern-type proofs for proving knowledge of a short ~s satisfying A~s = ~ u mod q.
- Unlike Stern’s proof, which is combinatorial in nature, our proof is more algebraic and uses various relaxed zeroknowledge proofs as sub-routines.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940397 (1).pdf`
- `downloads/116940397.pdf`
