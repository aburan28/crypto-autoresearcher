---
id: KN-LIT-4218
type: literature
title: "Higher-Order Threshold Implementations"
authors:
  - "Vincent Rijmen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, implementation, mpc, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Higher-order differential power analysis attacks are a serious threat for cryptographic hardware implementations. In particular, glitches in the circuit make it hard to protect the implementation with masking.

## Key claims (as reported)
- The existing higher-order masking countermeasures that guarantee security in the presence of glitches use multi-party computation techniques and require a lot of resources in terms of circuit area and randomness.
- The Threshold Implementation method is also based on multi-party computation but it is more area and randomness efficient.
- Moreover, it typically requires less clock-cycles since all parties can operate simultaneously.
- However, so far it is only provable secure against 1st -order DPA.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730288 (1).pdf`
- `downloads/88730288 (2).pdf`
- `downloads/88730288 (3).pdf`
- `downloads/88730288.pdf`
