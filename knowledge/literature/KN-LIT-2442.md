---
id: KN-LIT-2442
type: literature
title: "Amortizing Randomness Complexity in Private Circuits"
authors:
  - "Sebastian Faust"
  - "Clara Paglialonga"
  - "Tobias Schneider"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, complexity-theory, mpc, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptographic implementations are vulnerable to Side Channel Analysis (SCA), where an adversary exploits physical phenomena such as the power consumption to reveal sensitive information. One of the most widely studied countermeasures against SCA are masking schemes.

## Key claims (as reported)
- A masking scheme randomizes intermediate values thereby making physical leakage from the device harder to exploit.
- Central to any masking scheme is the use of randomness, on which the security of any masked algorithm heavily relies.
- But since randomness is very costly to produce in practice, it is an important question whether we can reduce the amount of randomness needed while still guaranteeing standard security properties such as t-probing security introduced by Ishai, Sahai and Wagner (CRYPTO 2003).
- In this work we study the question whether internal randomness can be re-used by several gadgets, thereby reducing the total amount of randomness needed.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240306 (1).pdf`
- `downloads/106240306.pdf`
