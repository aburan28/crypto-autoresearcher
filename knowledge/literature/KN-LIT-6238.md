---
id: KN-LIT-6238
type: literature
title: "Resynchronization Attacks on WG and LEX ?"
authors:
  - "Hongjun Wu"
  - "Bart Preneel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
WG and LEX are two stream ciphers submitted to eStream – the ECRYPT stream cipher project. In this paper, we point out security flaws in the resynchronization of these two ciphers.

## Key claims (as reported)
- The resynchronization of WG is vulnerable to a differential attack.
- For WG with 80-bit key and 80-bit IV, 48 bits of the secret key can be recovered with about 231.3 chosen IVs .
- For each chosen IV, only the first four keystream bits are needed in the attack.
- The resynchronization of LEX is vulnerable to a slide attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40470425 (1).pdf`
- `downloads/40470425 (2).pdf`
- `downloads/40470425 (3).pdf`
- `downloads/40470425.pdf`
