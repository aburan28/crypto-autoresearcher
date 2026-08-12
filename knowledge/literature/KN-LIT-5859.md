---
id: KN-LIT-5859
type: literature
title: "Practical Schnorr Threshold Signatures Without the Algebraic Group Model"
authors:
  - "Hien Chu"
  - "Paul Gerhart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, ecdsa, mov-fr, pairing, provable-security, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold signatures are digital signature schemes in which a set of n signers specify a threshold t such that any subset of size t is authorized to produce signatures on behalf of the group. There has recently been a renewed interest in this primitive, largely driven by the need to secure highly valuable signing keys, e.g., DNSSEC keys or keys protecting digital wallets in the cryptocurrency ecosystem.

## Key claims (as reported)
- Of special interest is FROST, a practical Schnorr threshold signature scheme, which is currently undergoing standardization in the IETF and whose security was recently analyzed at CRYPTO’22.
- We continue this line of research by focusing on FROST’s unforgeability combined with a practical distributed key generation (DKG) algorithm.
- Existing proofs of this setup either use non-standard heuristics, idealized group models like the AGM, or idealized key generation.
- Moreover, existing proofs do not consider all practical relevant optimizations that have been proposed.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850373 (1).pdf`
- `downloads/140850373.pdf`
