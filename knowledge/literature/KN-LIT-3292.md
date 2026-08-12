---
id: KN-LIT-3292
type: literature
title: "Cryptanalytic Time-Memory-Data Tradeoffs for FX-Constructions with Applications to PRINCE and PRIDE Itai Dinur"
authors: []
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The FX-construction was proposed in 1996 by Kilian and Rogaway as a generalization of the DESX scheme. The construction increases the security of an n-bit core block cipher with a κ-bit key by using two additional n-bit masking keys.

## Key claims (as reported)
- Recently, several concrete instances of the FX-construction were proposed, including PRINCE (proposed at Asiacrypt 2012) and PRIDE (proposed at CRYPTO 2014).
- These ciphers have n = κ = 64, and are proven to guarantee about 127 − d bits of security, assuming that their core ciphers are ideal, and the adversary can obtain at most 2d data.
- In this paper, we devise new cryptanalytic time-memory-data tradeoff attacks on FX-constructions.
- While our attacks do not contradict the security proof of PRINCE and PRIDE, nor pose an immediate threat to their users, some specific choices of tradeoff parameters demonstrate that the security margin of the ciphers against practical attacks is smaller than expected.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560148 (1).pdf`
- `downloads/90560148.pdf`
