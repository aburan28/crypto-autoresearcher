---
id: KN-LIT-6768
type: literature
title: "Speeding up XTR"
authors:
  - "Martijn Stam"
  - "Arjen K. Lenstra"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, mov-fr, pairing, prime-field, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper describes several speedups and simplifications for XTR. The most important results are new XTR double and single exponentiation methods where the latter requires a cheap precomputation.

## Key claims (as reported)
- Both methods are on average more than 60% faster than the old methods, thus more than doubling the speed of the already fast XTR signature applications.
- An additional advantage of the new double exponentiation method is that it no longer requires matrices, thereby making XTR easier to implement.
- Another XTR single exponentiation method is presented that does not require precomputation and that is on average more than 35% faster than the old method.
- Existing applications of similar methods to LUC and elliptic curve cryptosystems are reviewed.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/22480125 (1).pdf`
- `downloads/22480125 (2).pdf`
- `downloads/22480125.pdf`
