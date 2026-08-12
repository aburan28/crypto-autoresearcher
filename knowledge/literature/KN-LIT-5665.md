---
id: KN-LIT-5665
type: literature
title: "Optimal Tightness for Chain-Based Unique Signatures"
authors:
  - "Fuchun Guo"
  - "Willy Susilo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, protocol, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Unique signatures are digital signatures with exactly one unique and valid signature for each message. The security reduction for most unique signatures has a natural reduction loss (in the existentially unforgeable against chosen-message attacks, namely EUF-CMA, security model under a non-interactive hardness assumption).

## Key claims (as reported)
- In Crypto 2017, Guo et al. proposed a particular chain-based unique signature scheme where each unique signature is composed of n BLS signatures computed sequentially like a blockchain.
- Under the computational Diffie-Hellman 1/n assumption, their reduction loss is n · qH for qH hash queries and it is logarithmically tight when n = log qH .
- However, it is currently unknown whether a better reduction than logarithmical tightness for the chain-based unique signatures exists.
- We show that the proposed chain-based unique signature scheme by Guo et al. must have the reduction loss q 1/n for q signature queries when each unique signature consists of n BLS signatures.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760035 (1).pdf`
- `downloads/132760035.pdf`
