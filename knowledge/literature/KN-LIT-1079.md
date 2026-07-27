---
id: KN-LIT-1079
type: literature
title: "CDLS: Proving Knowledge of Committed Discrete Logarithms with Soundness"
authors:
  - "Sofia Celi"
  - "Shai Levin"
  - "Joe Rowell"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1595"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1595"
tags: [cryptanalysis, dlp, elliptic-curve, mov-fr, pairing, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Σ-protocols, a class of interactive two-party protocols, which are used as a framework to instantiate many other authentication schemes, are automatically a proof of knowledge (PoK) given that they satisfy the special-soundness property. This fact provides a convenient method to compose Σ-protocols and PoKs for complex relations.

## Key claims (as reported)
- However, composing in this manner can be error-prone.
- While they must satisfy specialsoundness, this is unfortunately not the case for many recently proposed composed practical schemes.
- Here we explore two schemes: ZKAttest’s [FLM22] and Agrawal et al.’s [AGM18], and show that their Σprotocol’s suffer from several security misdesigns which invalidate their security proofs, and state a practical cheap attack on ZKAttest’s implementation.
- By exploring and resolving their misdesigns, we propose CDLS, a sound and secure variant of their protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1595.pdf`
