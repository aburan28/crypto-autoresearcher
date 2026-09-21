---
id: KN-LIT-1413
type: literature
title: "Issuer Hiding for BBS-Based Anonymous Credentials"
authors:
  - "Jonathan Katz"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2080"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2080"
tags: [complexity-theory, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Anonymous-credential schemes allow users to obtain credentials on various attributes, and then use those credentials to give unlinkable proofs about the values of some attributes without leaking anything about others. They have recently received interest from companies including Google, Apple, and Cloudflare, and are being actively evaluated both at the IETF and in the EU.

## Key claims (as reported)
- Anonymous credentials based on BBS signatures are a leading candidate for standardization.
- In some natural applications of anonymous credentials, it is beneficial to hide even the issuer of a credential, beyond revealing the fact that the issuer is in some pre-determined set specified by a verifier.
- Sanders and Traoré recently showed a construction of such issuer-hiding anonymous credentials based on the Pointcheval–Sanders signature scheme.
- In this work we show how to achieve issuer hiding for BBS-based anonymous credentials.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2080.pdf`
