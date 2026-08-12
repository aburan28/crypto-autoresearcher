---
id: KN-LIT-3215
type: literature
title: "Cryptanalysis of a Message Authentication Code"
authors:
  - "Simon R. Blackburn"
  - "Kenneth G. Paterson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, finite-field, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A cryptanalysis is given of a MAC proposal presented at CRYPTO 2003 by Cary and Venkatesan. A nice feature of the CaryVenkatesan MAC is that a lower bound on its security can be proved when a certain block cipher is modelled as an ideal cipher.

## Key claims (as reported)
- Our attacks find collisions for the MAC and yield MAC forgeries, both faster than a straightforward application of the birthday paradox would suggest.
- For the suggested parameter sizes (where the MAC is 128 bits long) we give a method to find collisions using about 248.5 MAC queries, and to forge MACs using about 255 MAC queries.
- We emphasise that our results do not contradict the lower bounds on security proved by Cary and Venkatesan.
- Rather, they establish an upper bound on the MAC’s security that is substantially lower than one would expect for a 128-bit MAC.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170445 (1).pdf`
- `downloads/30170445 (2).pdf`
- `downloads/30170445.pdf`
