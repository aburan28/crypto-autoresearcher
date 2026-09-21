---
id: KN-LIT-3287
type: literature
title: "Cryptanalysis on HMAC/NMAC-MD5 and MD5-MAC?"
authors:
  - "Haina Zhang"
  - "Tao Zhan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pollard-rho, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present the first distinguishing attack on HMAC and NMAC based on MD5 without related keys, which distinguishes the HMAC/NMAC-MD5 from HMAC/NMAC with a random function. The attack needs 297 queries, with a success probability 0.87, while the previous distinguishing attack on HMAC-MD5 reduced to 33 rounds takes 2126.1 messages with a success rate of 0.92.

## Key claims (as reported)
- Furthermore, we give distinguishing and partial key recovery attacks on MDx-MAC based on MD5.
- The MDx-MAC was proposed by Preneel and van Oorschot in Crypto’95 which uses three subkeys derived from the initial key.
- We are able to recover one 128-bit subkey with 297 queries.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790122 (1).pdf`
- `downloads/54790122 (2).pdf`
- `downloads/54790122 (3).pdf`
- `downloads/54790122.pdf`
