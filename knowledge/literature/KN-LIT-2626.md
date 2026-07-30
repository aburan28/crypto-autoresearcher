---
id: KN-LIT-2626
type: literature
title: "Authenticated and Misuse-Resistant Encryption of Key-Dependent Data"
authors:
  - "Mihir Bellare"
  - "Sriram Keelveedhi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper provides a comprehensive treatment of the security of authenticated encryption (AE) in the presence of key-dependent data, considering the four variants of the goal arising from the choice of universal nonce or random nonce security and presence or absence of a header. We present attacks showing that universal-nonce security for key-dependent messages is impossible, as is security for key-dependent headers, not only ruling out security for three of the four variants but showing that currently standarized and used schemes (all these target universal nonce security in the presence of headers) fail to provide security for key-dependent data.

## Key claims (as reported)
- To complete the picture we show that the final variant (random-nonce security in the presence of key-dependent messages but key-independent headers) is efficiently achievable.
- Rather than a single dedicated scheme, we present a RO-based transform RHtE that endows any AE scheme with this security, so that existing implementations may be easily upgraded to have the best possible seurity in the presence of key-dependent data.
- RHtE is cheap, software-friendly, and continues to provide security when the key is a password, a setting in which key-dependent data is particularly likely.
- We go on to give a key-dependent data treatment of the goal of misuse resistant AE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410607 (1).pdf`
- `downloads/68410607 (2).pdf`
- `downloads/68410607 (3).pdf`
- `downloads/68410607.pdf`
