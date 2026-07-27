---
id: KN-LIT-1687
type: literature
title: "Identity-Based Encryption from Isogenies"
authors:
  - "Shweta Agrawal⋆"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1457"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1457"
tags: [elliptic-curve, hash, isogeny, mpc, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide the first construction of identity-based encryption from isogeny-based assumptions. Security of our construction relies on a novel assumption called the “CDH with Mismatched Torsion” (CDHwMT) assumption, which we introduce.

## Key claims (as reported)
- At a high level, the assumption posits the hardness of solving a CDH-like problem [12] even when the adversary is given some additional “safe” leakage.
- We justify our assumption by showing that, in the Algebraic Isogeny Model [1], our assumption reduces to well-known assumptions from the literature.
- As a bonus feature, our identity-based encryption enjoys anonymity, which means that the ciphertexts hide not only the message but also the target identity.
- We additionally obtain the first isogeny based constructions of laconic oblivious transfer [29], as well as public-key encryption that simultaneously satisfies security against high-rate key leakage [6, 53] and key-dependent message/circular security [18, 11, 10] from the CDHwMT assumption.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1457.pdf`
