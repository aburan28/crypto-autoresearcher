---
id: KN-LIT-6385
type: literature
title: "Scrypt is Maximally Memory-Hard"
authors:
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Memory-hard functions (MHFs) are hash algorithms whose evaluation cost is dominated by memory cost. As memory, unlike computation, costs about the same across different platforms, MHFs cannot be evaluated at significantly lower cost on dedicated hardware like ASICs.

## Key claims (as reported)
- MHFs have found widespread applications including password hashing, key derivation, and proofs-of-work.
- This paper focuses on scrypt, a simple candidate MHF designed by Percival, and described in RFC 7914.
- It has been used within a number of cryptocurrencies (e.g., Litecoin and Dogecoin) and has been an inspiration for Argon2d, one of the winners of the recent password-hashing competition.
- Despite its popularity, no rigorous lower bounds on its memory complexity are known.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210233 (1).pdf`
- `downloads/10210233.pdf`
